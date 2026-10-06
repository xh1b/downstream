"""Odds-to-risk conversion and explicitly timed survival at the count boundary."""
from __future__ import annotations
import math


def odds_risk(baseline: float, odds_ratio: float) -> float:
    if isinstance(baseline, bool) or not isinstance(baseline, (int, float)) or not math.isfinite(baseline) or not 0 <= baseline <= 1:
        raise ValueError('annual mortality baseline must be a probability in [0, 1]')
    if isinstance(odds_ratio, bool) or not isinstance(odds_ratio, (int, float)) or not math.isfinite(odds_ratio) or odds_ratio <= 0:
        raise ValueError('mortality odds ratio must be finite and positive')
    return odds_ratio * baseline / (1 - baseline + odds_ratio * baseline)


def rate_to_risk(rate: float) -> float:
    """Convert a constant event/person-time hazard to one-year death risk."""
    if isinstance(rate, bool) or not isinstance(rate, (int, float)) or not math.isfinite(rate) or rate < 0:
        raise ValueError("annual mortality rate must be finite and nonnegative")
    return 1 - math.exp(-rate)


MORTALITY_TIMINGS = {"source_aligned", "immediate_sustained"}

# Offsets in Sullivan--von Wachter Table 5 are relative to displacement.
# If displacement occupies follow-up year one, offset +6 starts follow-up
# year seven.  Keep the historical two-coefficient API below for notebooks;
# production scenarios use ``excess_deaths_profile`` with all five phases.
SOURCE_PROFILE_PHASES = (
    ("displacement", 1.0),
    ("offset_1", 1.0),
    ("offsets_2_3", 2.0),
    ("offsets_4_5", 2.0),
    ("offset_6_plus", math.inf),
)


def source_profile_phase_years(years: float) -> dict[str, float]:
    """Durations for displacement, offsets +1, +2--3, +4--5, and +6+.

    ``years`` counts follow-up years with displacement as year one.  The
    returned keys deliberately mirror source offsets, preventing the former
    off-by-one relabeling of offset +6 as follow-up year six.
    """
    if isinstance(years, bool) or not isinstance(years, (int, float)) or not math.isfinite(years) or years < 0:
        raise ValueError("years must be finite and nonnegative")
    remaining = years
    out: dict[str, float] = {}
    for name, duration in SOURCE_PROFILE_PHASES:
        take = remaining if math.isinf(duration) else min(remaining, duration)
        out[name] = take
        remaining -= take
    return out


def excess_deaths_profile(workers: float, baseline: float, odds_by_phase: dict[str, float],
                          years: float) -> float:
    """Survival contrast for a complete, source-offset mortality profile."""
    for name, value in (("workers", workers), ("years", years)):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ValueError(f"{name} must be finite and nonnegative")
    expected = {name for name, _ in SOURCE_PROFILE_PHASES}
    if set(odds_by_phase) != expected:
        raise ValueError(f"mortality profile needs exactly phases {sorted(expected)}")
    phases = source_profile_phase_years(years)
    if workers == 0 or years == 0:
        return 0.0
    exposed_survival = 1.0
    for name, duration in phases.items():
        exposed_survival *= (1 - odds_risk(baseline, odds_by_phase[name])) ** duration
    result = workers * ((1 - baseline) ** years - exposed_survival)
    return min(workers, max(-workers, result))


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


SOURCE_PROFILE_DESCRIPTION = (
    "Source-offset profile: displacement, +1, +2–3, +4–5, and +6+; "
    "displacement is follow-up year 1, so offset +6 begins in follow-up year 7. "
    "Annual baseline rates use a constant-hazard rate-to-risk conversion; "
    "odds ratios modify annual risk, and survival compounds across phases. "
    "The selected baseline age rate is held fixed over the follow-up horizon."
)


def source_profile_contract() -> dict:
    start = 0
    phases = []
    for name, duration in SOURCE_PROFILE_PHASES:
        phases.append({"phase": name, "start_offset": start,
                       "duration_years": None if math.isinf(duration) else duration,
                       "first_follow_up_year": start + 1})
        if not math.isinf(duration):
            start += int(duration)
    return {"method": "odds_survival", "timing": "source_profile",
            "baseline_conversion": "1-exp(-annual_rate)", "phases": phases,
            "description": SOURCE_PROFILE_DESCRIPTION}


def parameter_profile_counts(params, workers, annual_rate, years, bound="point"):
    """The production source profile at a declared parameter support bound."""
    from .worker import mortality_profile
    profile = mortality_profile(params)
    return excess_deaths_profile(workers, rate_to_risk(annual_rate),
                                {phase: getattr(p, bound) for phase, p in profile.items()}, years)
