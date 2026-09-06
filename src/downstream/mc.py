"""Monte Carlo propagation over parameter uncertainty.

v1.2 methodology: Latin Hypercube Sampling over the parameter space,
log-space sampling for positive ratio parameters, and optional
declared rank correlation (Iman-Conover). Every draw rebuilds the
full module compute, so nonlinear gap composition propagates
correctly. Outputs carry the parameter-set version (marked
`-sampled`), the seed, and the draw count — published ranges are
always reproducible.
"""

from __future__ import annotations

import random
from typing import Callable

from .distributions import dist_for, plan, sample_unit_interval
from .params import ParameterSet


def simulate(
    params: ParameterSet,
    compute: Callable[[ParameterSet], float],
    draws: int = 10_000,
    seed: int = 1901,
    nodes: dict | None = None,
    spearman: list[list[float]] | None = None,
) -> dict:
    """Run `compute` over draws of the parameter space.

    `compute` takes a perturbed ParameterSet and returns the scalar
    outcome to sample. Sampling is LHS by default; pass `spearman` to
    induce declared rank correlations (Iman-Conover).
    """
    rows = list(params.parameters)
    if nodes is None:
        from .params import default_dir, load_nodes

        try:
            nodes = load_nodes(default_dir() / "nodes.csv")
        except OSError:
            nodes = {}

    dp = plan(params, nodes, draws, seed, spearman=spearman)
    samples: list[float] = []
    for k in range(draws):
        ps = params
        for j, p in enumerate(rows):
            lo, hi = sorted((p.low, p.high))
            v = sample_unit_interval(dp.dists[j], dp.u[k][j], lo, hi)
            ps = ps.with_param(p.link, v)
        samples.append(compute(ps))
    samples.sort()

    def pct(p: float) -> float:
        return samples[min(int(p * (draws - 1)), draws - 1)]

    return {
        "draws": draws,
        "seed": seed,
        "sampler": "lhs",
        "parameter_set_version": f"{params.version.split('-sampled')[0]}-sampled",
        "p05": round(pct(0.05), 4),
        "p50": round(pct(0.50), 4),
        "p95": round(pct(0.95), 4),
        "mean": round(sum(samples) / draws, 4),
    }


def simulate_chain(
    params: ParameterSet,
    links: list[str],
    base: float = 1.0,
    label: str = "chain",
    draws: int = 10_000,
    seed: int = 1901,
    kinds: list[str] | None = None,
) -> dict:
    """Convenience wrapper: sample a named chain of links.

    kinds defaults to all-level composition; pass e.g.
    ["direct","gap"] for the child line.
    """
    from .ledger import LEVEL, chain

    kinds = kinds or [LEVEL] * len(links)

    def compute(ps: ParameterSet) -> float:
        return chain(ps, links, label=label, unit="gap_multiplier", kinds=kinds).point

    out = simulate(params, compute, draws=draws, seed=seed)
    out["label"] = label
    out["links"] = links
    out["kinds"] = kinds
    return out
