"""Global sensitivity analysis: Sobol variance decomposition.

Which parameters DRIVE the uncertainty in an outcome? The answer
powers the tornado view in explanations and tells us where a full-text
extraction buys the most precision.

Estimator: Saltelli's (2002) scheme over an (N+2)-section base design
— A, B, and the N single-column refits. First-order S_i (main effect)
and total-order T_i (all effects including interactions). Pure stdlib;
the model evaluates in microseconds so brute-force designs are fine.

Methodology anchor: Sobol 2001; Saltelli 2002; Saltelli et al. 2008
(sampling and estimators); LHS base design per McKay et al. 1979.
"""

from __future__ import annotations

import random
from typing import Callable

from .distributions import sample_unit_interval
from .params import ParameterSet


def sobol_indices(
    params: ParameterSet,
    compute: Callable[[ParameterSet], float],
    nodes: dict,
    base: int = 256,
    seed: int = 1901,
) -> dict:
    """First-order + total Sobol indices per parameter.

    `base` = rows in each of the (N+2) sections; model evals =
    base * (N+2). All indices are unit-free shares of output variance.
    """
    rows = list(params.parameters)
    n = len(rows)
    rng = random.Random(seed)

    def matrix() -> list[list[float]]:
        # LHS-style stratification per column (better behaved than IID
        # at small base sizes; the estimator only needs independence
        # BETWEEN sections).
        cols = []
        for _ in range(n):
            strata = [(i + rng.random()) / base for i in range(base)]
            rng.shuffle(strata)
            cols.append(strata)
        return [[cols[j][i] for j in range(n)] for i in range(base)]

    def run(u_row: list[float]) -> float:
        ps = params
        for j, p in enumerate(rows):
            lo, hi = sorted((p.low, p.high))
            ps = ps.with_param(p.link, sample_unit_interval(_dist(j), u_row[j], lo, hi))
        return compute(ps)

    dists = [
        _dist_for_param(p, nodes) for p in rows
    ]

    def _dist(j: int) -> str:
        return dists[j]

    A = matrix()
    B = matrix()
    fA = [run(row) for row in A]
    fB = [run(row) for row in B]

    total_var = _var(fA + fB)
    out = []
    for j in range(n):
        # AB_j = A with column j drawn from B (the standard pairing).
        fj = []
        for i in range(base):
            u = list(A[i])
            u[j] = B[i][j]
            fj.append(run(u))
        # Saltelli estimators:
        #   S_j  = sum_i fB_i * (f_AB_i - fA_i) / (base * Var)
        #   T_j  = sum_i (fA_i - f_AB_i)^2 / (2 * base * Var)
        s_first = sum(fB[i] * (fj[i] - fA[i]) for i in range(base)) / (base * total_var)
        t_total = 0.5 * sum((fA[i] - fj[i]) ** 2 for i in range(base)) / (base * total_var)
        out.append(
            {
                "link": rows[j].link,
                "S_first": round(s_first, 4),
                "S_total": round(t_total, 4),
            }
        )
    out.sort(key=lambda r: -r["S_total"])
    return {
        "base": base,
        "seed": seed,
        "model_evals": base * (n + 2),
        "output_variance": round(total_var, 8),
        "indices": out,
        "note": (
            "S_total is the share of output variance driven by each "
            "parameter including interactions; negative or >1 values at "
            "small base are estimator noise, not signal."
        ),
    }


def _dist_for_param(p, nodes: dict) -> str:
    from .distributions import dist_for

    node = nodes.get(p.to_node)
    return dist_for(p, node.unit if node else None)


def _var(xs: list[float]) -> float:
    m = sum(xs) / len(xs)
    return sum((x - m) ** 2 for x in xs) / len(xs)
