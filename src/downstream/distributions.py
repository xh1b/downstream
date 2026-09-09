"""Parameter distributions and uncertainty propagation.

Methodology (each choice cited in SPEC §7):
- Latin Hypercube Sampling over the parameter space (McKay, Beckman &
  Conover 1979) — strata coverage instead of naive IID draws.
- Positive quantities (rate ratios, odds ratios, level ratios) sample
  in LOG space by default: a ratio is multiplicative, so its
  uncertainty is multiplicative. A linear-uniform sample of a ratio
  is biased toward its upper band.
- Optional declared shape per row: parameters.csv carries a `dist`
  column (v1.27). Rows whose band is a reported 95% CI declare the
  shape that CI implies — `normal` for linear-space CIs (band = point
  +/- 1.96 SE), `lognormal` for multiplier rows whose band is
  exp(beta +/- 1.96 SE). Rows with DECLARED bands (rounding bands,
  cross-study spreads, evidence-widened bands) declare nothing: a
  flat density is the only honest shape when the paper reports no
  standard error.
- Rank-correlation induction between parameters (Iman & Conover 1982):
  preserves each marginal exactly (LHS strata survive) while applying
  a declared Spearman matrix. Correlations enter only with a citation
  (citable direction) or an explicit `declared` magnitude marker, via
  params/correlations.csv — mc.simulate loads it by default and stamps
  the sampler `lhs+iman-conover` when any pair applies.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from .params import Parameter

NORMAL = "normal"
UNIFORM = "uniform"
LOGUNIFORM = "loguniform"
LOGNORMAL = "lognormal"

# Every distribution a row may declare; the audit rejects other tokens.
KNOWN_DISTS = {NORMAL, UNIFORM, LOGUNIFORM, LOGNORMAL}

# Node units that must sample in log space (positive, multiplicative).
LOG_SPACE_UNITS = {"rate_ratio", "odds_ratio", "level_ratio"}


def dist_for(param: Parameter, unit: str | None) -> str:
    """Effective distribution for a parameter row."""
    declared = getattr(param, "dist", "") or ""
    if declared:
        return declared
    if unit in LOG_SPACE_UNITS:
        return LOGUNIFORM
    return UNIFORM


def sample_unit_interval(
    dist: str, u: float, low: float, high: float, point: float | None = None
) -> float:
    """Inverse CDF at u in (0,1) for the declared band.

    `point` centers the CI-shaped distributions (normal, lognormal) on
    the reported estimate; when omitted, normal centers on the band
    midpoint and lognormal on the geometric mean.
    """
    lo, hi = sorted((low, high))
    if dist not in KNOWN_DISTS:
        raise ValueError(f"unknown distribution {dist!r}; known: {sorted(KNOWN_DISTS)}")
    if dist in (LOGUNIFORM, LOGNORMAL):
        if lo <= 0:
            raise ValueError(f"log-space band requires positive bounds, got [{lo}, {hi}]")
        if dist == LOGUNIFORM:
            return math.exp(math.log(lo) + u * (math.log(hi) - math.log(lo)))
        # lognormal: the reported exp(beta +/- 1.96 SE) shape — normal in
        # log space with SE = (log hi - log lo) / 3.92, clamped into the
        # band (the CI edges ARE the +/-1.96 sigma points by construction).
        log_mid = math.log(point) if point is not None else (math.log(lo) + math.log(hi)) / 2
        z = max(-1.96, min(1.96, _probit(u)))
        v = math.exp(log_mid + z * (math.log(hi) - math.log(lo)) / 3.92)
        return min(hi, max(lo, v))
    if dist == NORMAL:
        se = (hi - lo) / (2 * 1.96)
        center = point if point is not None else (lo + hi) / 2
        z = _probit(u)
        v = center + z * se
        return min(hi, max(lo, v))
    return lo + u * (hi - lo)


def materialize_parameter_set(params, nodes: dict, u_row: list[float], dists: list[str]):
    """Apply one resolved draw consistently across every sampling surface."""
    rows = list(params.parameters)
    if len(u_row) != len(rows) or len(dists) != len(rows):
        raise ValueError("draw dimensions must match parameter count")
    out = params
    for p, u, dist in zip(rows, u_row, dists):
        lo, hi = sorted((p.low, p.high))
        out = out.with_param(p.link, sample_unit_interval(dist, u, lo, hi, point=p.point))
    return out


def _probit(u: float) -> float:
    """Inverse standard normal CDF (Acklam-style rational approximation,
    adequate for sampling; not for tail probabilities)."""
    if not 0.0 < u < 1.0:
        raise ValueError("probit needs u in (0,1)")
    a = [-3.969683028665376e01, 2.209460984245205e02, -2.759285104469687e02,
         1.383577518672690e02, -3.066479806614716e01, 2.506628277459239e00]
    b = [-5.447609879822406e01, 1.615858368580409e02, -1.556989798598866e02,
         6.680131188771972e01, -1.328068155288572e01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e00,
         -2.549732539343734e00, 4.374664141464968e00, 2.938163982698783e00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00,
         3.754408661907416e00]
    plow, phigh = 0.02425, 1 - 0.02425
    if u < plow:
        q = math.sqrt(-2 * math.log(u))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if u > phigh:
        return -_probit(1 - u)
    q = u - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
           (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)


def lhs_matrix(n_cols: int, n_rows: int, rng: random.Random) -> list[list[float]]:
    """Latin Hypercube: each column is a jittered permutation of strata
    centers, so every marginal covers [0,1) evenly at any sample size."""
    cols = []
    for _ in range(n_cols):
        strata = [(i + rng.random()) / n_rows for i in range(n_rows)]
        rng.shuffle(strata)
        cols.append(strata)
    return [[cols[j][i] for j in range(n_cols)] for i in range(n_rows)]


def _cholesky(matrix: list[list[float]]) -> list[list[float]]:
    """Lower-triangular Cholesky; raises on non-PSD input."""
    n = len(matrix)
    lower = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = sum(lower[i][k] * lower[j][k] for k in range(j))
            if i == j:
                v = matrix[i][i] - s
                if v <= 0:
                    raise ValueError("correlation matrix is not positive semi-definite")
                lower[i][j] = math.sqrt(v)
            else:
                lower[i][j] = (matrix[i][j] - s) / lower[j][j]
    return lower


def apply_rank_correlation(u: list[list[float]], spearman: list[list[float]],
                           rng: random.Random | None = None) -> list[list[float]]:
    """Iman-Conover: reorder each column of u to match the rank order of
    correlated normal scores. Marginals are preserved exactly; rank
    correlation approximates the declared matrix."""
    n_rows, n_cols = len(u), len(u[0]) if u else 0
    if n_cols != len(spearman):
        raise ValueError("correlation matrix size must match parameter count")
    # The input is Spearman rank correlation, while Cholesky operates on
    # Gaussian-copula Pearson correlation.  For a bivariate normal copula,
    # rho_S = 6/pi * asin(r/2), hence r = 2 sin(pi rho_S/6).
    latent = [[2 * math.sin(math.pi * value / 6) if i != j else 1.0
               for j, value in enumerate(row)] for i, row in enumerate(spearman)]
    lower = _cholesky(latent)

    # Independent normal scores, then mix them through the Cholesky
    # factor: Z = L X gives cov(Z) = L L^T = R.
    # Plans must draw fresh copula ranks on each seed. Reusing one rank
    # template makes the A/B designs in block Sobol almost identical.
    rng = rng if rng is not None else random.Random(0)
    w = [[rng.gauss(0, 1) for _ in range(n_cols)] for _ in range(n_rows)]
    t = [[sum(lower[j][k] * w[i][k] for k in range(n_cols)) for j in range(n_cols)]
         for i in range(n_rows)]

    order: list[list[int]] = []
    for j in range(n_cols):
        idx = sorted(range(n_rows), key=lambda i: t[i][j])
        order.append(idx)

    out = [row[:] for row in u]
    for j in range(n_cols):
        col_sorted = sorted(row[j] for row in u)
        for rank, i in enumerate(order[j]):
            out[i][j] = col_sorted[rank]
    return out


@dataclass(frozen=True)
class DrawPlan:
    """A resolved sampling plan: u-matrix + the per-column distributions."""

    u: list[list[float]]
    dists: list[str]


def plan(
    params,
    nodes: dict,
    draws: int,
    seed: int,
    spearman: list[list[float]] | None = None,
) -> DrawPlan:
    """Build the sampling matrix for a parameter set."""
    rng = random.Random(seed)
    rows = list(params.parameters)
    u = lhs_matrix(len(rows), draws, rng)
    if spearman is not None:
        u = apply_rank_correlation(u, spearman, rng=rng)
    dists = [dist_for(p, nodes.get(p.to_node).unit if p.to_node in nodes else None) for p in rows]
    return DrawPlan(u=u, dists=dists)
