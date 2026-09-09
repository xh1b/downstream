"""Odds-to-risk conversion and time-phased survival at the count boundary.

The historical ``source_aligned`` option is an incomplete source profile:
it holds follow-up years 2--5 at baseline, although the working paper has
early-year estimates that have not been extracted into this parameter set.
It also starts offset +6 one year early when displacement is follow-up
year 1. See docs/REVIEW_2026-09-10.md before interpreting that option name
as source fidelity. Numerical timing is retained pending re-extraction.
"""
from __future__ import annotations
import math


def odds_risk(baseline: float, odds_ratio: float) -> float:
    if isinstance(baseline, bool) or not isinstance(baseline, (int, float)) or not math.isfinite(baseline) or not 0 <= baseline <= 1:
        raise ValueError('annual mortality baseline must be a probability in [0, 1]')
    if isinstance(odds_ratio, bool) or not isinstance(odds_ratio, (int, float)) or not math.isfinite(odds_ratio) or odds_ratio <= 0:
        raise ValueError('mortality odds ratio must be finite and positive')
    return odds_ratio * baseline / (1 - baseline + odds_ratio * baseline)


MORTALITY_TIMINGS = {"source_aligned", "immediate_sustained"}


def mortality_phase_years(years: float, timing: str = "source_aligned") -> dict[str, float]:
    """Split a follow-up horizon into the currently implemented phases.

    Year one uses the displacement-year estimate.  The published sustained
    estimate is used from follow-up year six. ``unidentified`` is a legacy
    dictionary key for the unextracted phase, not a claim about the source.
    Fractional horizons preserve the constant-hazard interpretation.
    """
    if timing not in MORTALITY_TIMINGS:
        raise ValueError(f"unknown mortality timing {timing!r}")
    peak = min(years, 1.0)
    if timing == "immediate_sustained":
        return {"peak": peak, "unidentified": 0.0, "sustained": max(years - 1.0, 0.0)}
    unidentified = min(max(years - 1.0, 0.0), 4.0)
    return {"peak": peak, "unidentified": unidentified, "sustained": max(years - 5.0, 0.0)}


def excess_deaths(workers, baseline, peak, sustained, years, method='odds_survival',
                  timing: str = "source_aligned"):
    """Years is the total follow-up horizon, including the initial peak year.

    The sustained year-6+ coefficient is extrapolated to subsequent years.
    This explicit timing assumption is not an extracted early-year profile.
    Fractional years use constant hazards within each phase.
    """
    for name, value in (("workers", workers), ("years", years)):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ValueError(f'{name} must be finite and nonnegative')
    q_peak = odds_risk(baseline, peak)
    q_sustained = odds_risk(baseline, sustained)
    if method == 'legacy_additive':
        return workers * baseline * ((sustained - 1) * years + peak - 1)
    if method != 'odds_survival':
        raise ValueError(f'unknown mortality method {method!r}')
    if years == 0 or workers == 0:
        return 0.0
    phases = mortality_phase_years(years, timing)
    unexposed_survival = (1 - baseline) ** years
    exposed_survival = (
        (1 - q_peak) ** phases["peak"]
        * (1 - baseline) ** phases["unidentified"]
        * (1 - q_sustained) ** phases["sustained"]
    )
    result = workers * (unexposed_survival - exposed_survival)
    # Splitting an identical hazard into peak/later powers is algebraically
    # exact but can produce a one-ulp signed residual (notably OR=1). Preserve
    # protective effects, while enforcing the sign that the input ordering
    # guarantees and the universal count bound.
    result = min(workers, max(-workers, result))
    if peak >= 1 and sustained >= 1:
        return max(0.0, result)
    if peak <= 1 and sustained <= 1:
        return min(0.0, result)
    return result
