"""Monte Carlo propagation over parameter uncertainty.

Uniform sampling within [low, high] per parameter (the v1 default;
distribution families upgrade per-parameter as full-text passes pin
them). Every draw rebuilds the full module compute, so nonlinear gap
composition propagates correctly. Outputs carry the parameter-set
version (marked `-sampled`), the seed, and the draw count — published
ranges are always reproducible.
"""

from __future__ import annotations

import random
from typing import Callable

from .params import ParameterSet


def simulate(
    params: ParameterSet,
    compute: Callable[[ParameterSet], float],
    draws: int = 10_000,
    seed: int = 1901,
) -> dict:
    """Run `compute` over draws of the parameter space.

    `compute` takes a perturbed ParameterSet and returns the scalar
    outcome to sample (e.g. grandchild gap point, excess-deaths count).
    """
    rng = random.Random(seed)
    samples: list[float] = []
    for _ in range(draws):
        ps = params
        for p in params.parameters:
            lo, hi = sorted((p.low, p.high))
            ps = ps.with_param(p.link, rng.uniform(lo, hi))
        samples.append(compute(ps))
    samples.sort()

    def pct(p: float) -> float:
        return samples[min(int(p * (draws - 1)), draws - 1)]

    return {
        "draws": draws,
        "seed": seed,
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
