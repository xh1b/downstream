"""Analytic inference layer: exact moments, variance shares, coverage.

The Monte Carlo rebuilds the compute per draw; this module does the
same algebra SYMBOLICALLY. Because every ledger step is either a
product (level), a replacement (direct), or affine in each argument
(gap), the first two moments of a chain propagate in closed form
under parameter independence — no sampling, no seed, exact:

  level   V' = V·X        E'  = E[V]·E[X]        E2' = E2[V]·E[X²]
  direct  V' = X          moments of X
  gap     V' = 1 − T + T·V  (bilinear in independent T, V — see below)

The closed form serves three purposes:

1. CROSS-CHECK. The MC mean and quantiles must agree with the exact
   moments (to sampling error). A divergence means a sampler bug —
   this is trap-checked in the test suite, not trusted.
2. SPEED. Analytic bands cost nothing; MC exists to catch what the
   two-moment normal approximation misses (skewness, tail shape).
3. TEACHING THE COVERAGE QUESTION. A published "90% band" earns the
   label only if it covers 90% of the time. `closure_coverage` runs
   the frequentist self-test: draw truths from the parameter space,
   publish bands from independent machinery, count coverage. Under
   the model's own assumptions the coverage must be nominal to within
   binomial noise — if it is not, the interval MACHINERY is broken,
   whatever the economics. What V1 (China shock) then tests is whether
   the assumptions themselves hold against reality.

Moment identities (independent T, V):
  E[T·V] = E[T]·E[V]
  E[(T·V)²] = E[T²]·E[V²]
  V' = 1 − T + TV:
    E[V']   = 1 − E[T] + E[T]E[V]
    E[V'²]  = (1 − 2E[T] + E[T²])          (the (1−T)² term)
             + 2(E[T] − E[T²])·E[V]        (cross term, E[(1−T)TV])
             + E[T²]·E[V²]

Sampling distributions follow SPEC §7: uniform bands by default,
log-uniform for positive ratio units. Their moments are closed form;
see `_moments`.
"""

from __future__ import annotations

import math
import random
from typing import Callable

from .distributions import LOGUNIFORM, dist_for, plan, sample_unit_interval
from .params import Parameter, ParameterSet

Z95 = 1.959963984540054
Z90 = 1.6448536269514722


# ---------------------------------------------------------------- moments


def _uniform_moments(lo: float, hi: float) -> tuple[float, float]:
    """(E[X], E[X²]) for X ~ Uniform(lo, hi)."""
    if hi == lo:
        return lo, lo * lo
    m = (lo + hi) / 2
    m2 = (hi**3 - lo**3) / (3 * (hi - lo))
    return m, m2


def _loguniform_moments(lo: float, hi: float) -> tuple[float, float]:
    """(E[X], E[X²]) for X log-uniform on [lo, hi], lo > 0."""
    if lo <= 0:
        raise ValueError(f"log-uniform band requires positive bounds, got [{lo}, {hi}]")
    L = math.log(hi) - math.log(lo)
    if L == 0:
        return lo, lo * lo
    m = (hi - lo) / L
    m2 = (hi * hi - lo * lo) / (2 * L)
    return m, m2


def param_moments(p: Parameter, node_unit: str | None) -> tuple[float, float]:
    """First two raw moments of a parameter under its sampling dist."""
    lo, hi = sorted((p.low, p.high))
    if dist_for(p, node_unit) == LOGUNIFORM:
        return _loguniform_moments(lo, hi)
    return _uniform_moments(lo, hi)


# ------------------------------------------------------- chain propagation


def analytic_chain(
    params: ParameterSet,
    links: list[str],
    kinds: list[str],
    nodes: dict,
    base: float = 1.0,
    base_m2: float | None = None,
) -> dict:
    """Exact mean/variance of a composed chain, plus a normal band.

    `base`/`base_m2` seed the tracked quantity (default: a constant 1).
    Returns per-step moments so the paper can show the algebra.
    """
    if len(links) != len(kinds):
        raise ValueError("links and kinds must be the same length")
    m1, m2 = float(base), float(base) if base_m2 is None else base_m2
    steps = []
    for link, kind in zip(links, kinds):
        p = params.by_link(link)  # KeyError names a typo'd link
        node = nodes.get(p.to_node)
        t1, t2 = param_moments(p, node.unit if node else None)
        if kind == "level":
            m1, m2 = m1 * t1, m2 * t2
        elif kind == "direct":
            m1, m2 = t1, t2
        elif kind == "gap":
            v1, v2 = m1, m2
            e_t, e_t2 = t1, t2
            m1 = 1 - e_t + e_t * v1
            m2 = (1 - 2 * e_t + e_t2) + 2 * (e_t - e_t2) * v1 + e_t2 * v2
        elif kind == "rate":
            raise ValueError(
                "rate ratios are recorded, never chained — apply them to a "
                "baseline at the count boundary (SPEC §4)"
            )
        else:
            raise ValueError(f"unknown composition kind {kind!r}")
        steps.append({"link": link, "kind": kind, "E": m1, "E2": m2})
    var = m2 - m1 * m1
    if var < 0 and var > -1e-12:
        var = 0.0
    if var < 0:
        raise ArithmeticError(
            f"negative variance {var} after chain — moment algebra violated"
        )
    sd = math.sqrt(var)
    return {
        "links": links,
        "kinds": kinds,
        "mean": m1,
        "var": var,
        "sd": sd,
        "p05_normal": m1 - Z90 * sd,
        "p50_normal": m1,
        "p95_normal": m1 + Z90 * sd,
        "steps": steps,
        "note": (
            "Exact two-moment propagation under parameter independence; "
            "quantiles are a normal approximation to the true shape. The "
            "MC exists to price the skewness this misses."
        ),
    }


# --------------------------------------------------------- variance shares


def _var_log(dist: str, lo: float, hi: float) -> float:
    """Var[ln X] for the declared band."""
    if dist == LOGUNIFORM:
        if lo <= 0:
            raise ValueError(f"log-uniform band requires positive bounds, got [{lo}, {hi}]")
        return (math.log(hi) - math.log(lo)) ** 2 / 12
    # X ~ U(lo, hi): E[ln X], E[(ln X)^2] by exact integration
    def i1(x: float) -> float:
        return x * math.log(x) - x

    def i2(x: float) -> float:
        lx = math.log(x)
        return x * (lx * lx - 2 * lx + 2)

    if hi == lo:
        return 0.0
    e1 = (i1(hi) - i1(lo)) / (hi - lo)
    e2 = (i2(hi) - i2(lo)) / (hi - lo)
    return max(0.0, e2 - e1 * e1)


def logspace_variance_shares(
    params: ParameterSet,
    links: list[str],
    nodes: dict,
    kinds: list[str] | None = None,
) -> dict:
    """EXACT variance decomposition of a multiplicative chain.

    For Y = ∏ Xᵢ with independent Xᵢ, log Y = Σ ln Xᵢ, so
    Var[log Y] = Σ Var[ln Xᵢ] and the share Var[ln Xᵢ] / Var[log Y]
    is simultaneously the first-order AND total Sobol index of Xᵢ on
    log Y — no estimator, no seed, no noise. Valid for LEVEL chains
    only: gap/direct steps are not multiplicative (log Y ≠ Σ ln Xᵢ),
    and applying this decomposition to them is the level-ratio bug in
    analytic disguise. Refused loudly.
    """
    if kinds is None:
        kinds = ["level"] * len(links)
    if len(links) != len(kinds):
        raise ValueError("links and kinds must be the same length")
    bad = [(l, k) for l, k in zip(links, kinds) if k != "level"]
    if bad:
        raise ValueError(
            f"logspace shares are exact for multiplicative (level) chains "
            f"only; got non-level steps {bad}. Use the Saltelli estimator "
            f"for this chain."
        )
    rows = []
    total = 0.0
    for link in links:
        p = params.by_link(link)
        node = nodes.get(p.to_node)
        d = dist_for(p, node.unit if node else None)
        lo, hi = sorted((p.low, p.high))
        if hi == lo:
            rows.append({"link": link, "var_log": 0.0, "share": 0.0})
            continue
        v = _var_log(d, lo, hi)
        total += v
        rows.append({"link": link, "var_log": v})
    if total <= 0:
        raise ValueError("all links pinned — no variance to decompose")
    for r in rows:
        r["var_log"] = round(r["var_log"], 8)
        r["share"] = round(r["var_log"] / total, 4) if r["var_log"] else 0.0
    rows.sort(key=lambda r: -r["share"])
    return {
        "links": links,
        "var_log_total": round(total, 8),
        "shares": rows,
        "note": (
            "Exact: for independent multiplicative chains these shares ARE "
            "the Sobol indices of log Y (first-order = total). Compare "
            "against the Saltelli estimator as a machinery cross-check."
        ),
    }


# ------------------------------------------------------------ closure test


def _draw_samples(
    params: ParameterSet,
    compute: Callable[[ParameterSet], float],
    nodes: dict,
    draws: int,
    seed: int,
) -> list[float]:
    """The mc.simulate sampler, exposed as raw samples."""
    rows = list(params.parameters)
    dp = plan(params, nodes, draws, seed)
    out = []
    for k in range(draws):
        ps = params
        for j, p in enumerate(rows):
            lo, hi = sorted((p.low, p.high))
            v = sample_unit_interval(dp.dists[j], dp.u[k][j], lo, hi)
            ps = ps.with_param(p.link, v)
        out.append(compute(ps))
    return out


def _normal_quantile_band(samples: list[float], level: float) -> tuple[float, float]:
    samples.sort()
    n = len(samples)

    def q(p: float) -> float:
        return samples[min(int(p * (n - 1)), n - 1)]

    return q((1 - level) / 2), q(1 - (1 - level) / 2)


def closure_coverage(
    params: ParameterSet,
    compute: Callable[[ParameterSet], float],
    nodes: dict,
    trials: int = 400,
    draws: int = 2_000,
    levels: tuple[float, ...] = (0.50, 0.80, 0.90, 0.95),
    seed: int = 1901,
) -> dict:
    """Frequentist self-test of the published bands.

    Protocol (a closure test): each trial draws a 'true' parameter
    vector from the declared bands, evaluates the model at that truth,
    and asks whether the MC-published central band — built from an
    INDEPENDENT sample — covers it. Under the model's own assumptions
    (bands correct, parameters independent, sampler honest) empirical
    coverage equals nominal to within binomial noise. A deviation is a
    machinery bug. This validates the INTERVAL MACHINERY. It does not
    validate the economics: for that, see V1.

    An attacker who accepts the model's citations must accept that its
    90% bands behave like 90% bands. An attacker who rejects them is
    arguing with the literature, not the arithmetic.
    """
    rows = list(params.parameters)
    band_rng = random.Random(seed)
    truth_rng = random.Random(seed + 1)
    covered = {lv: 0 for lv in levels}

    # One shared band per level: the published band does not move with
    # the truth — that is the frequentist statement being tested.
    samples = _draw_samples(params, compute, nodes, draws, seed + 2)
    bands = {lv: _normal_quantile_band(samples[:], lv) for lv in levels}

    for _ in range(trials):
        ps = params
        for p in rows:
            lo, hi = sorted((p.low, p.high))
            u = truth_rng.random()
            node = nodes.get(p.to_node)
            d = dist_for(p, node.unit if node else None)
            ps = ps.with_param(p.link, sample_unit_interval(d, u, lo, hi))
        truth = compute(ps)
        for lv in levels:
            lo_b, hi_b = bands[lv]
            if lo_b <= truth <= hi_b:
                covered[lv] += 1
    out = []
    for lv in levels:
        emp = covered[lv] / trials
        se = math.sqrt(lv * (1 - lv) / trials)
        out.append(
            {
                "nominal": lv,
                "empirical": round(emp, 4),
                "binomial_se": round(se, 4),
                "within_2se": abs(emp - lv) <= 2 * se,
            }
        )
    return {
        "experiment": "closure_coverage",
        "trials": trials,
        "draws": draws,
        "seed": seed,
        "levels": out,
        "pass": all(r["within_2se"] for r in out),
        "note": (
            "Coverage of MC bands over truths redrawn from the declared "
            "bands. Machinery self-test only — the economics is tested by "
            "V1 retrodiction, not here."
        ),
    }


def analytic_vs_mc(
    params: ParameterSet,
    compute: Callable[[ParameterSet], float],
    analytic: dict,
    nodes: dict,
    draws: int = 20_000,
    seed: int = 1901,
) -> dict:
    """Agreement report: exact moments vs the MC estimate.

    The MC mean must sit inside its own sampling error of the exact
    mean; the MC p05/p95 vs the normal band prices the skewness the
    two-moment algebra cannot see. Both gaps publish — they are the "
    'how non-Gaussian is this output' number.
    """
    samples = _draw_samples(params, compute, nodes, draws, seed)
    n = len(samples)
    mean_mc = sum(samples) / n
    var_mc = sum((x - mean_mc) ** 2 for x in samples) / (n - 1)
    samples.sort()

    def q(p: float) -> float:
        return samples[min(int(p * (n - 1)), n - 1)]

    mean_se = math.sqrt(var_mc / n)
    return {
        "mean_analytic": analytic["mean"],
        "mean_mc": round(mean_mc, 6),
        "mean_diff_in_se": round(abs(mean_mc - analytic["mean"]) / mean_se, 3) if mean_se > 0 else 0.0,
        "sd_analytic": analytic["sd"],
        "sd_mc": round(math.sqrt(var_mc), 6),
        "p05": {"normal": analytic["p05_normal"], "mc": q(0.05)},
        "p95": {"normal": analytic["p95_normal"], "mc": q(0.95)},
        "draws": draws,
        "seed": seed,
        "note": (
            "mean_diff_in_se > 3 is a sampler bug (exact vs sampled mean). "
            "p05/p95 gaps are skewness, not error — publish them."
        ),
    }
