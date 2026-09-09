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

from .distributions import materialize_parameter_set, plan
from .params import Correlation, ParameterSet, spearman_matrix


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
        return compute(materialize_parameter_set(params, nodes, u_row, dists))

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
        "assumes_independent_parameters": True,
        "correlation_note": (
            "Classical Sobol indices require independent inputs. Declared "
            "correlations are intentionally not applied; this is not a "
            "decomposition of the correlated production-MC distribution."
        ),
    }


def correlated_block_sobol(
    params: ParameterSet,
    compute: Callable[[ParameterSet], float],
    nodes: dict,
    correlations: list[Correlation],
    base: int = 256,
    seed: int = 1901,
) -> dict:
    """Sobol attribution for independent *blocks* of dependent parameters.

    Classical individual Sobol indices are undefined under dependent inputs.
    Rather than quietly dropping the declared copula, this groups every
    connected correlated component into one joint input and estimates Sobol
    effects for those blocks.  It is deliberately not presented as individual
    Shapley attribution; a conditional-distribution model is required before
    splitting a dependent block fairly.
    """
    rows = list(params.parameters)
    index = {p.link: i for i, p in enumerate(rows)}
    adjacency = {i: set() for i in range(len(rows))}
    for c in correlations:
        if c.spearman == 0:
            continue
        a, b = index[c.from_param], index[c.to_param]
        adjacency[a].add(b)
        adjacency[b].add(a)
    seen: set[int] = set()
    blocks: list[list[int]] = []
    for root in range(len(rows)):
        if root in seen:
            continue
        stack, component = [root], []
        seen.add(root)
        while stack:
            i = stack.pop()
            component.append(i)
            for nxt in adjacency[i]:
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        blocks.append(sorted(component))

    spearman = spearman_matrix(params, correlations)
    a_plan = plan(params, nodes, base, seed, spearman=spearman)
    b_plan = plan(params, nodes, base, seed + 1, spearman=spearman)
    dists = a_plan.dists

    def run(u_row: list[float]) -> float:
        return compute(materialize_parameter_set(params, nodes, u_row, dists))

    f_a = [run(row) for row in a_plan.u]
    f_b = [run(row) for row in b_plan.u]
    total_var = _var(f_a + f_b)
    if total_var <= 0:
        raise ValueError("output has zero variance; no sensitivity decomposition exists")
    effects = []
    for block in blocks:
        f_ab = []
        for i in range(base):
            row = list(a_plan.u[i])
            for j in block:
                row[j] = b_plan.u[i][j]
            f_ab.append(run(row))
        first = sum(f_b[i] * (f_ab[i] - f_a[i]) for i in range(base)) / (base * total_var)
        total = .5 * sum((f_a[i] - f_ab[i]) ** 2 for i in range(base)) / (base * total_var)
        effects.append({
            "links": [rows[j].link for j in block],
            "S_first": round(first, 4),
            "S_total": round(total, 4),
        })
    effects.sort(key=lambda row: -row["S_total"])
    return {
        "base": base,
        "seed": seed,
        "model_evals": base * (len(blocks) + 2),
        "output_variance": round(total_var, 8),
        "blocks": effects,
        "method": "correlation-aware independent-block Sobol",
        "correlations_applied": sum(c.spearman != 0 for c in correlations),
        "note": (
            "Connected correlated parameters are one joint input. This preserves "
            "the declared production copula without pretending their individual "
            "Sobol indices are defined. Conditional Shapley attribution is a "
            "future extension once a citable conditional dependence model exists."
        ),
    }


def sobol_ci(
    params: ParameterSet,
    compute: Callable[[ParameterSet], float],
    nodes: dict,
    base: int = 128,
    seed: int = 1901,
    replicates: int = 5,
) -> dict:
    """Sobol S_total with estimator-noise bands (seed-replicate spread).

    Runs `sobol_indices` on consecutive seeds and reports, per link,
    the mean and sample sd of S_total across designs. The sd is DESIGN
    noise (how much the estimate moves under a fresh sample), not a
    posterior on the true index. A ranking is stable when the top
    links' means separate by more than their sds. Cheap: the model
    evaluates in microseconds.
    """
    if replicates < 2:
        raise ValueError(f"replicates must be >= 2, got {replicates}")
    runs = [
        sobol_indices(params, compute, nodes, base=base, seed=seed + r)
        for r in range(replicates)
    ]
    links = [r["link"] for r in runs[0]["indices"]]
    out = []
    for link in links:
        vals = []
        for run in runs:
            match = [i for i in run["indices"] if i["link"] == link]
            if not match:
                raise ValueError(f"link {link!r} vanished between replicates")
            vals.append(match[0]["S_total"])
        mean = sum(vals) / replicates
        sd = (sum((v - mean) ** 2 for v in vals) / (replicates - 1)) ** 0.5
        out.append(
            {
                "link": link,
                "S_total_mean": round(mean, 4),
                "S_total_sd": round(sd, 4),
                "values": [round(v, 4) for v in vals],
            }
        )
    out.sort(key=lambda r: -r["S_total_mean"])
    return {
        "base": base,
        "seed": seed,
        "replicates": replicates,
        "model_evals": runs[0]["model_evals"] * replicates,
        "indices": out,
        "note": (
            "sd is across independent sampling designs (design noise), "
            "not a confidence interval on a true index. Use it to check "
            "that a ranking separates by more than its noise."
        ),
        "assumes_independent_parameters": True,
    }


def _dist_for_param(p, nodes: dict) -> str:
    from .distributions import dist_for

    node = nodes.get(p.to_node)
    return dist_for(p, node.unit if node else None)


def _var(xs: list[float]) -> float:
    m = sum(xs) / len(xs)
    return sum((x - m) ** 2 for x in xs) / len(xs)
