"""Community stream: local multipliers and school spending.

Moretti's multiplier is a LEVEL ratio (service jobs per displaced
tradable job). It converts a worker count to a job count at the
boundary — it must never be chained as a multiplier (the audit
rejects that shape).
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import replace
import math

from .ledger import DIRECT, Ledger, start
from .params import ParameterSet

LOCAL_MULTIPLIER = "displacement->local_service_jobs"
SCHOOL_SPENDING = "school_spending->child_earnings"


def service_jobs_lost(
    params: ParameterSet, displaced_tradable: float
) -> dict:
    """Local non-traded service jobs implied by displaced tradable jobs.

    A count, additive in n. Band spans Moretti's own range
    (manufacturing 1.6 to high-tech 5.0).
    """
    p = params.by_link(LOCAL_MULTIPLIER)
    return {
        "outcome": "local_service_jobs_lost",
        "unit": "jobs",
        "point": displaced_tradable * p.point,
        "low": displaced_tradable * p.low,
        "high": displaced_tradable * p.high,
        "citation": p.citation,
        "tier": p.tier,
        "population_scope": p.population_scope,
    }


@dataclass(frozen=True)
class SchoolExposure:
    """A school-spending shock. spend_pct is in percent points (e.g. 10
    for a 10% cut); exposure_years is how long it persisted."""

    spend_pct: float          # negative = spending cut
    exposure_years: float     # sustained years (JJP effect is per 12y)

    def __post_init__(self):
        for name in ("spend_pct", "exposure_years"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
        if self.exposure_years < 0:
            raise ValueError("exposure_years must be nonnegative")


def school_spending_child_earnings(params: ParameterSet, exposure: SchoolExposure) -> Ledger:
    """Adult-earnings effect of a school-spending change.

    JJP 2016: +10% per-pupil for all 12 years -> ~+7% adult earnings.
    Linear normalization in spending intensity and exposure duration;
    both are assumptions declared here and flagged in outputs.
    """
    p = params.by_link(SCHOOL_SPENDING)
    intensity = exposure.spend_pct / 10.0
    duration = exposure.exposure_years / 12.0
    low = 1 + (p.low - 1) * intensity * duration
    high = 1 + (p.high - 1) * intensity * duration
    scaled = replace(p,
        point=1 + (p.point - 1) * intensity * duration,
        low=min(low, high),
        high=max(low, high),
        notes=p.notes + " | linear-normalized in intensity x duration",
    )
    return start("school_spending_child_earnings", "gap_multiplier").apply(DIRECT, scaled)


def youth_crime_delta(params: ParameterSet, wage_pct_delta: float) -> Ledger:
    """Percent change in youth crime participation for a local-wage move.

    Elasticity application: %Δcrime = elasticity × %Δwage. Counts need
    the youth_crime_participation baseline (pending).
    """
    p = params.by_link("youth_wages->youth_crime")
    point = p.point * wage_pct_delta
    lo = p.high * wage_pct_delta if wage_pct_delta >= 0 else p.low * wage_pct_delta
    hi = p.low * wage_pct_delta if wage_pct_delta >= 0 else p.high * wage_pct_delta
    return Ledger(
        label="youth_crime_pct_delta",
        unit="percent_delta",
        point=point,
        low=min(lo, hi),
        high=max(lo, hi),
        steps=(_step_from(p, point, min(lo, hi), max(lo, hi)),),
    )


def _step_from(p, point: float, low: float, high: float):
    from .ledger import Step

    return Step(
        link=p.link,
        kind="elasticity",
        citation=p.citation,
        tier=p.tier,
        param=(p.point, p.low, p.high),
        value=(point, low, high),
    )
