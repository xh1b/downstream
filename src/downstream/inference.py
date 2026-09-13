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

from .distributions import LOGUNIFORM, dist_for, materialize_parameter_set, plan, sample_unit_interval
from .params import Parameter, ParameterSet

Z90 = 1.6448536269514722


# ---------------------------------------------------------------- moments


def _uniform_moments(lo: float, hi: float) -> tuple[float, float, float]:
    """(E[X], E[X²], E[X³]) for X ~ Uniform(lo, hi)."""
    if hi == lo:
        return lo, lo * lo, lo**3
    w = hi - lo
    m1 = (lo + hi) / 2
    m2 = (hi**3 - lo**3) / (3 * w)
    m3 = (hi**4 - lo**4) / (4 * w)
    return m1, m2, m3


def _loguniform_moments(lo: float, hi: float) -> tuple[float, float, float]:
    """(E[X], E[X²], E[X³]) for X log-uniform on [lo, hi], lo > 0."""
    if lo <= 0:
        raise ValueError(f"log-uniform band requires positive bounds, got [{lo}, {hi}]")
    L = math.log(hi) - math.log(lo)
    if L == 0:
        return lo, lo * lo, lo**3
    m1 = (hi - lo) / L
    m2 = (hi * hi - lo * lo) / (2 * L)
    m3 = (hi**3 - lo**3) / (3 * L)
    return m1, m2, m3


def param_moments(p: Parameter, node_unit: str | None) -> tuple[float, float, float]:
    """First three raw moments of a parameter under its sampling dist.

    Normal and lognormal moments include the sampler's endpoint atoms
    from clamping. Independent-step composition refuses reused random
    parameters; use Monte Carlo when that independence assumption fails.
    """
    lo, hi = sorted((p.low, p.high))
    d = dist_for(p, node_unit)
    if d == LOGUNIFORM:
        return _loguniform_moments(lo, hi)
    if d in {"normal", "lognormal"}:
        return _clamped_moments(p, logarithmic=d == "lognormal")
    if d != "uniform":
        raise NotImplementedError(f"unsupported analytic distribution {d!r}")
    return _uniform_moments(lo, hi)


def _clamped_moments(p, logarithmic=False):
    """Exact moments of the sampler's clamped normal-family marginal."""
    lo, hi = sorted((p.low, p.high))
    if lo == hi:
        return lo, lo**2, lo**3
    if logarithmic and lo <= 0:
        raise ValueError('lognormal bands must be positive')
    lower, upper = (math.log(lo), math.log(hi)) if logarithmic else (lo, hi)
    mu = math.log(p.point) if logarithmic else p.point
    sigma = (upper - lower) / 3.92
    a = max(-1.96, (lower - mu) / sigma) if logarithmic else (lower - mu) / sigma
    b = min(1.96, (upper - mu) / sigma) if logarithmic else (upper - mu) / sigma
    def cdf(z):
        return 0.5 * math.erfc(-z / math.sqrt(2))

    def pdf(z):
        return math.exp(-z*z/2) / math.sqrt(2*math.pi)
    if a > b:
        raise ValueError('parameter center must lie within its band')
    low_value, high_value = mu + sigma*a, mu + sigma*b
    if logarithmic:
        return tuple(math.exp(k*low_value)*cdf(a) + math.exp(k*high_value)*cdf(-b)
                     + math.exp(k*mu + (k*sigma)**2/2) * (cdf(b-k*sigma)-cdf(a-k*sigma))
                     for k in (1, 2, 3))
    integrals = [cdf(b)-cdf(a), pdf(a)-pdf(b),
                 cdf(b)-cdf(a)+a*pdf(a)-b*pdf(b),
                 (a*a+2)*pdf(a)-(b*b+2)*pdf(b)]
    return tuple(low_value**k*cdf(a) + high_value**k*cdf(-b) +
                 sum(math.comb(k,j)*mu**(k-j)*sigma**j*integrals[j] for j in range(k+1))
                 for k in (1, 2, 3))


# ------------------------------------------------------- chain propagation


def analytic_chain(
    params: ParameterSet,
    links: list[str],
    kinds: list[str],
    nodes: dict,
    base: float = 1.0,
    base_m2: float | None = None,
    base_m3: float | None = None,
) -> dict:
    """Exact mean/variance/skewness of a composed chain + quantile bands.

    `base`/`base_m2`/`base_m3` seed the tracked quantity (default: a
    constant 1). Third-moment identities (independent T, V):
      level   E3' = E3[V]·E[T³]
      direct  E3' = E[T³]
      gap     V' = (1−T) + TV; with A = 1−T, B = TV:
              E[A³]   = 1 − 3t₁ + 3t₂ − t₃
              E[A²B]  = (t₁ − 2t₂ + t₃)·v₁
              E[AB²]  = (t₂ − t₃)·v₂
              E[B³]   = t₃·v₃
              E3'     = E[A³] + 3E[A²B] + 3E[AB²] + E[B³]
    Skewness γ₁ = E[(X−μ)³]/σ³ follows from the raw moments; the
    Cornish–Fisher expansion turns it into better quantiles:
    q_α ≈ μ + σ·(z_α + (z_α² − 1)·γ₁/6). For symmetric outputs
    γ₁ = 0 and CF reduces exactly to the normal band.
    """
    if len(links) != len(kinds):
        raise ValueError("links and kinds must be the same length")
    m1 = float(base)
    m2 = m1 * m1 if base_m2 is None else float(base_m2)
    m3 = m1**3 if base_m3 is None else float(base_m3)
    steps = []
    active_links = set()
    for link, kind in zip(links, kinds):
        if kind == "direct":
            active_links.clear()
        elif link in active_links:
            raise ValueError(f"reused parameter {link!r} violates independent-step moments; use Monte Carlo")
        active_links.add(link)
        p = params.by_link(link)  # KeyError names a typo'd link
        node = nodes.get(p.to_node)
        t1, t2, t3 = param_moments(p, node.unit if node else None)
        if kind == "level":
            m1, m2, m3 = m1 * t1, m2 * t2, m3 * t3
        elif kind == "direct":
            m1, m2, m3 = t1, t2, t3
        elif kind == "gap":
            v1, v2, v3 = m1, m2, m3
            m1 = 1 - t1 + t1 * v1
            m2 = (1 - 2 * t1 + t2) + 2 * (t1 - t2) * v1 + t2 * v2
            m3 = (
                (1 - 3 * t1 + 3 * t2 - t3)
                + 3 * (t1 - 2 * t2 + t3) * v1
                + 3 * (t2 - t3) * v2
                + t3 * v3
            )
        elif kind == "rate":
            raise ValueError(
                "rate ratios are recorded, never chained — apply them to a "
                "baseline at the count boundary (SPEC §4)"
            )
        else:
            raise ValueError(f"unknown composition kind {kind!r}")
        steps.append({"link": link, "kind": kind, "E": m1, "E2": m2, "E3": m3})
    var = m2 - m1 * m1
    if -1e-12 < var < 0:
        var = 0.0
    if var < 0:
        raise ArithmeticError(
            f"negative variance {var} after chain — moment algebra violated"
        )
    sd = math.sqrt(var)
    central3 = m3 - 3 * m1 * var - m1**3
    skew = (central3 / sd**3) if sd > 0 else 0.0
    if abs(skew) > 1e9:  # degenerate pinned chain noise
        skew = 0.0
    return {
        "links": links,
        "kinds": kinds,
        "mean": m1,
        "var": var,
        "sd": sd,
        "skewness": skew,
        "p05_normal": m1 - Z90 * sd,
        "p50_normal": m1,
        "p95_normal": m1 + Z90 * sd,
        "p05_cf": _cornish_fisher(m1, sd, skew, 0.05),
        "p95_cf": _cornish_fisher(m1, sd, skew, 0.95),
        "steps": steps,
        "note": (
            "Exact three-moment propagation under parameter independence. "
            "Quantiles twice: normal, and Cornish-Fisher corrected for the "
            "exact skewness. CF reduces to normal when skewness is zero. "
            "The MC remains the referee: CF that drifts from MC quantiles "
            "is rejected, not excused."
        ),
        "assumes_independent_parameters": True,
    }


def _cornish_fisher(mean: float, sd: float, skew: float, alpha: float) -> float:
    """Cornish-Fisher quantile at `alpha` (order-1 in skewness)."""
    z = _z_alpha(alpha)
    return mean + sd * (z + (z * z - 1) * skew / 6)


def _z_alpha(alpha: float) -> float:
    """Standard normal quantile via Acklam probit (same approx as sampler)."""
    if not 0.0 < alpha < 1.0:
        raise ValueError(f"alpha must be in (0,1), got {alpha}")
    from .distributions import _probit

    return _probit(alpha)


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
    bad = [(link, kind) for link, kind in zip(links, kinds) if kind != "level"]
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
        if d not in {"uniform", LOGUNIFORM}:
            raise ValueError(
                f"logspace shares are exact only for uniform/loguniform marginals; "
                f"{link!r} declares {d!r}. Use sampled sensitivity instead."
            )
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
        "assumes_independent_parameters": True,
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
    dp = plan(params, nodes, draws, seed)
    out = []
    for k in range(draws):
        out.append(compute(materialize_parameter_set(params, nodes, dp.u[k], dp.dists)))
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
    truth_rng = random.Random(seed + 1)
    covered = {lv: 0 for lv in levels}

    # One shared band per level: the published band does not move with
    # the truth — that is the frequentist statement being tested.
    samples = _draw_samples(params, compute, nodes, draws, seed + 2)
    bands = {lv: _normal_quantile_band(samples[:], lv) for lv in levels}

    for _ in range(trials):
        ps = params
        for p in params.parameters:
            lo, hi = sorted((p.low, p.high))
            u = truth_rng.random()
            node = nodes.get(p.to_node)
            d = dist_for(p, node.unit if node else None)
            ps = ps.with_param(p.link, sample_unit_interval(d, u, lo, hi, point=p.point))
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
            "bands under an independent-input estimand. Machinery self-test "
            "only — the economics is tested by V1 retrodiction, not here."
        ),
        "assumes_independent_parameters": True,
    }


def _stress_matrix(n: int, block: list[int], rho: float) -> list[list[float]]:
    """Identity Spearman matrix with one equicorrelated `block` at `rho`.

    PSD requires rho > -1/(len(block)-1) for the block; violations are
    refused HERE, at construction, not deep inside the Cholesky.
    """
    if len(block) > 1 and rho <= -1.0 / (len(block) - 1):
        raise ValueError(
            f"equicorrelation {rho} over {len(block)} links is not "
            f"positive semi-definite (need rho > {-1.0 / (len(block) - 1):.3f})"
        )
    m = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for i in block:
        for j in block:
            if i != j:
                m[i][j] = rho
    return m


def correlation_stress(
    params: ParameterSet,
    compute: Callable[[ParameterSet], float],
    nodes: dict,
    block_links: list[str],
    rho: float,
    draws: int = 5_000,
    trials: int = 600,
    level: float = 0.90,
    seed: int = 1901,
) -> dict:
    """How much does the independence assumption cost?

    The production run may already contain declared correlations. This
    stress test retains them and changes only the requested block, bounding
    the incremental exposure to a correlation assumption:

    - induce Spearman rank correlation `rho` among `block_links`
      (Iman-Conover; marginals preserved exactly);
    - build the 90% band under the correlation;
    - redraw truths under the SAME correlation;
    - report band width vs the independent case and the empirical
      coverage of the correlated band for correlated truths.

    Interpretation: coverage should stay ~nominal (the machinery
    tracks whatever dependence it is told); the story is the WIDTH
    move — the sign and size tell an attacker exactly what an
    unmodeled correlation would buy. For gap-space chains the sign is
    NOT the naive one: the IGE step couples gradients of OPPOSITE
    sign, so positive correlation can NARROW the band. The number
    publishes either way.
    """
    rows = list(params.parameters)
    idx = {p.link: i for i, p in enumerate(rows)}
    unknown = [link for link in block_links if link not in idx]
    if unknown:
        raise KeyError(f"unknown links in stress block: {unknown}")
    block = [idx[link] for link in block_links]
    # Start from the production declared matrix, then replace just the
    # requested stress block.  This prevents a stress run from silently
    # dropping unrelated declared correlations.
    from .params import default_dir, load_correlations, spearman_matrix
    try:
        declared = load_correlations(default_dir() / "correlations.csv")
        base_spearman = spearman_matrix(params, declared)
    except OSError:
        declared, base_spearman = [], None
    base_spearman = base_spearman or _stress_matrix(len(rows), [], 0.0)
    spearman = [row[:] for row in base_spearman]
    for i in block:
        for j in block:
            if i != j:
                spearman[i][j] = rho

    def correlated_samples(n: int, sd_seed: int, with_stress: bool) -> list[float]:
        dp = plan(params, nodes, n, sd_seed, spearman=spearman if with_stress else base_spearman)
        out = []
        for k in range(n):
            out.append(compute(materialize_parameter_set(params, nodes, dp.u[k], dp.dists)))
        return out

    # "independent" below means no *additional stress*, not an erasure of
    # the production's declared correlations.
    base_samples = correlated_samples(draws, seed + 2, with_stress=False)
    base_lo, base_hi = _normal_quantile_band(base_samples[:], level)
    width_ind = base_hi - base_lo

    stressed = correlated_samples(draws, seed + 3, with_stress=True)
    s_lo, s_hi = _normal_quantile_band(stressed[:], level)
    width_rho = s_hi - s_lo

    truths = correlated_samples(trials, seed + 4, with_stress=True)
    covered = sum(1 for t in truths if s_lo <= t <= s_hi)
    se = math.sqrt(level * (1 - level) / trials)
    return {
        "experiment": "correlation_stress",
        "rho": rho,
        "block": block_links,
        "level": level,
        "band_independent": {"lo": round(base_lo, 6), "hi": round(base_hi, 6),
                              "width": round(width_ind, 6)},
        "band_stressed": {"lo": round(s_lo, 6), "hi": round(s_hi, 6),
                           "width": round(width_rho, 6)},
        "width_change": round(width_rho / width_ind - 1, 4) if width_ind > 0 else 0.0,
        "coverage_of_stressed_band": round(covered / trials, 4),
        "coverage_binomial_se": round(se, 4),
        "draws": draws,
        "trials": trials,
        "seed": seed,
        "declared_correlations_retained": len(declared),
        "note": (
            "Iman-Conover rank correlation among the block links only; "
            "marginals unchanged. Width move is the published exposure to "
            "the independence assumption. Coverage staying nominal shows "
            "the machinery tracks declared dependence; it is NOT evidence "
            "the correlation is real — that needs a citation."
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
        "assumes_independent_parameters": True,
    }
