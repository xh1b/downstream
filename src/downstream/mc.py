"""Monte Carlo propagation over parameter uncertainty.

Uniform sampling within [low, high] per parameter (the v0 default;
distribution families upgrade per-parameter as full-text passes pin
them). Every draw records the parameter version — published ranges
are always reproducible.
"""

from __future__ import annotations

import random

from .ledger import Ledger
from .params import ParameterSet


def simulate_chain(
    params: ParameterSet,
    links: list[str],
    base: float,
    label: str,
    draws: int = 10_000,
    seed: int = 1901,
) -> dict:
    rng = random.Random(seed)
    samples: list[float] = []
    for _ in range(draws):
        value = base
        for link in links:
            p = params.by_link(link)
            lo, hi = sorted((p.low, p.high))
            value *= rng.uniform(lo, hi)
        samples.append(value)
    samples.sort()

    def pct(p: float) -> float:
        return samples[min(int(p * (draws - 1)), draws - 1)]

    return {
        "label": label,
        "draws": draws,
        "p05": round(pct(0.05), 4),
        "p50": round(pct(0.50), 4),
        "p95": round(pct(0.95), 4),
        "mean": round(sum(samples) / draws, 4),
    }
