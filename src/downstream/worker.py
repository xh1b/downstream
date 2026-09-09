"""Worker-level outcomes: earnings, mortality.

The earnings shock IS the exposure (JLS 1993 band by default; a caller
may pin a different multiplier). Mortality effects are recorded as odds
ratios — they convert to counts only at the scenario boundary, against
a cited baseline.
"""

from __future__ import annotations

from .ledger import DIRECT, RATE, Ledger, start
from .params import ParameterSet

WORKER_EARNINGS = "displacement->worker_earnings"
MORT_SUSTAINED = "earnings_shock->mortality_sustained"
MORT_PEAK = "earnings_shock->mortality_peak"


def worker_earnings(params: ParameterSet, wage_multiplier: float | None = None) -> Ledger:
    p = params.by_link(WORKER_EARNINGS)
    if wage_multiplier is None:
        return start("worker_earnings", "gap_multiplier").apply(DIRECT, p)
    # Caller pinned the shock: scale the band proportionally to the
    # pinned/point ratio so the band keeps the JLS relative spread.
    scale = wage_multiplier / p.point
    pinned = type(p)(  # same row, rescaled
        link=p.link,
        from_node=p.from_node,
        to_node=p.to_node,
        point=wage_multiplier,
        low=p.low * scale,
        high=p.high * scale,
        tier=p.tier,
        citation=p.citation,
        population_scope=p.population_scope,
        notes=p.notes + " | caller-pinned multiplier",
    )
    return start("worker_earnings", "gap_multiplier").apply(DIRECT, pinned)


def mortality_sustained(params: ParameterSet) -> Ledger:
    return (
        start("mortality_sustained", "odds_ratio")
        .apply(RATE, params.by_link(MORT_SUSTAINED))
    )


def mortality_peak(params: ParameterSet) -> Ledger:
    return start("mortality_peak", "odds_ratio").apply(RATE, params.by_link(MORT_PEAK))


def worker_outcomes(params: ParameterSet, wage_multiplier: float | None = None) -> dict:
    return {
        "worker_earnings": worker_earnings(params, wage_multiplier),
        "mortality_sustained": mortality_sustained(params),
        "mortality_peak": mortality_peak(params),
    }
