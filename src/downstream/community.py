"""Community stream: local multipliers and school spending.

Moretti's multiplier is a LEVEL ratio for a *net metro-level change*
in tradable jobs. It does not identify the effect of replacing one
worker with another in an existing job. It converts a documented net
job change to a service-employment count at the boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import replace
import math

from .ledger import DIRECT, Ledger, start
from .params import ParameterSet

LOCAL_MULTIPLIER = "displacement->local_service_jobs"
SCHOOL_SPENDING = "school_spending->child_earnings"

# Moretti publishes class-specific multipliers, and the stored row carries
# both at its band edges: low = 1.6 (manufacturing), high = ~5 (high-tech).
# They are different estimands, so a caller must declare which job class the
# documented loss names. Class values are read from the invariant band edges
# (not the sampleable point) so declared-class results stay fixed under
# parameter sampling instead of silently varying across the cross-class span.
JOB_CLASSES = ("manufacturing", "high_tech")


def service_jobs_lost(
    params: ParameterSet, net_tradable_jobs_lost: float, job_mix: str
) -> dict:
    """Local non-traded service jobs implied by a net tradable-job loss.

    A count, additive in n, for ONE declared job class. The row's 1.6-5.0
    span crosses job classes and is not uncertainty around a shared
    estimand, so the undeclared call is refused rather than answered with
    a cross-class band.
    """
    if job_mix not in JOB_CLASSES:
        raise ValueError(
            "local service-job conversion requires a declared job class "
            "('manufacturing' or 'high_tech'); the published 1.6-5.0 span "
            "crosses job classes and is not uncertainty around one estimand"
        )
    p = params.by_link(LOCAL_MULTIPLIER)
    value = p.low if job_mix == "manufacturing" else p.high
    return {
        "outcome": "local_service_jobs_lost",
        "unit": "jobs",
        "job_class": job_mix,
        "point": net_tradable_jobs_lost * value,
        "low": net_tradable_jobs_lost * value,
        "high": net_tradable_jobs_lost * value,
        "citation": p.citation,
        "tier": p.tier,
        "population_scope": p.population_scope,
        "support_note": (
            "single published class estimate; the row's 1.6-5.0 span "
            "crosses job classes and is not an uncertainty band"
        ),
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
        population_scope=p.population_scope,
        evidence_role=p.evidence_role,
    )
