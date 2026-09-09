"""Scenario aggregation: exposure counts -> modeled outcome counts.

A scenario describes an exposure (how many workers displaced, family
structure, shock size). Counts are computed ONLY where a cited
baseline exists; everything else is reported as blocked with the
exact missing input named. Nothing is ever estimated silently.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .children import child_line
from .community import service_jobs_lost
from .params import Baseline, ParameterSet
from .worker import worker_outcomes


class BaselineMissing(RuntimeError):
    pass


@dataclass
class ScenarioInput:
    displaced_workers: float
    n_children: int = 2
    tradable_share: float = 1.0
    wage_multiplier: float | None = None   # None = JLS default band
    exposure_years: float = 20.0           # mortality window (S&vW sustained horizon)
    label: str = "scenario"


def require_baseline(baselines: dict[str, Baseline], outcome: str) -> Baseline:
    b = baselines.get(outcome)
    if b is None:
        raise BaselineMissing(
            f"baseline {outcome!r} not in params/baselines.csv"
        )
    if b.status != "verified" or b.value is None:
        raise BaselineMissing(
            f"baseline {outcome!r} is status={b.status!r}; pin a value + "
            f"citation in params/baselines.csv before computing counts"
        )
    return b


def compute_counts(
    params: ParameterSet,
    baselines: dict[str, Baseline],
    scenario: ScenarioInput,
    strict: bool = False,
    places: dict | None = None,
    place_key: str | None = None,
) -> dict:
    """Modeled counts for a displacement scenario.

    strict=True raises on the first missing baseline. Default mode
    returns computed outcomes plus an explicit blocked list.

    places + place_key (optional): the place-resolved layer. The
    baseline dict is swapped for the shrunk county baselines (same
    unit/population — no conversion) and the Chetty-Hendren mobility
    modifier composes multiplicatively with the child-earnings chain
    (declared modeling assumption). Provenance lands in the "place"
    block; absent/blocked modifiers leave the computation unchanged.
    """
    place_block: dict | None = None
    modifier = None
    if places and place_key:
        from .place import modifier_parameter, place_baselines

        pb = place_baselines(places, baselines, place_key)
        baselines = pb["baselines"]
        mp = modifier_parameter(params, places, place_key)
        modifier = mp["parameter"]
        place_block = {
            "key": place_key,
            "baselines_applied": pb["provenance"].get("applied", True),
            "baseline_overrides": pb["provenance"].get("overrides"),
            "modifier_applied": modifier is not None,
            "modifier_reason": mp["modifier"].get("reason"),
            "mobility_percentile": mp["modifier"].get("mobility_percentile"),
            "national_percentile": mp["modifier"].get("national_percentile"),
        }
        if pb["provenance"].get("reason"):
            place_block["baselines_reason"] = pb["provenance"]["reason"]

    worker = worker_outcomes(params, wage_multiplier=scenario.wage_multiplier)
    line = child_line(params, place_modifier=modifier)
    jobs = service_jobs_lost(params, scenario.displaced_workers * scenario.tradable_share)

    computed: dict = {
        "label": scenario.label,
        "parameter_set_version": params.version,
        "exposure": {
            "displaced_workers": scenario.displaced_workers,
            "n_children": scenario.n_children,
            "tradable_share": scenario.tradable_share,
            "exposure_years": scenario.exposure_years,
        },
        "modeled": {},
        "blocked": [],
        "place": place_block,
    }

    # Local service jobs: a level ratio — no baseline needed.
    computed["modeled"]["local_service_jobs_lost"] = jobs

    # Mortality counts: needs the cited baseline rate.
    try:
        b = require_baseline(baselines, "all_cause_mortality_annual")
        rate = b.value or 0.0
        sustained = worker["mortality_sustained"].point
        peak = worker["mortality_peak"].point
        excess_sustained = (
            scenario.displaced_workers
            * rate
            * (sustained - 1)
            * scenario.exposure_years
        )
        excess_peak = scenario.displaced_workers * rate * (peak - 1)
        computed["modeled"]["excess_deaths"] = {
            "point": round(excess_sustained + excess_peak, 2),
            "unit": "deaths",
            "baseline": {
                "value": rate,
                "citation": b.citation,
                "population": b.population,
            },
            "components": {
                "sustained_window_years": scenario.exposure_years,
                "peak_year_excess": round(excess_peak, 2),
            },
        }
    except BaselineMissing as e:
        if strict:
            raise
        computed["blocked"].append({"outcome": "excess_deaths", "reason": str(e)})

    # Earnings conversion: needs cited lifetime earnings.
    try:
        b = require_baseline(baselines, "median_male_lifetime_earnings")
        v = b.value or 0.0
        child = line["child"]
        computed["modeled"]["child_lifetime_earnings_lost_usd"] = {
            "point": round(scenario.displaced_workers * scenario.n_children * (1 - child.point) * v, 2),
            "unit": "usd",
            "baseline": {"value": v, "citation": b.citation, "population": b.population},
        }
    except BaselineMissing as e:
        if strict:
            raise
        computed["blocked"].append(
            {"outcome": "child_lifetime_earnings_lost_usd", "reason": str(e)}
        )

    computed["multipliers"] = {
        "worker_earnings": _pt(worker["worker_earnings"]),
        "mortality_sustained": _pt(worker["mortality_sustained"]),
        "mortality_peak": _pt(worker["mortality_peak"]),
        "child_earnings": _pt(line["child"]),
        "grandchild_earnings": _pt(line["grandchild"]),
        "greatgrandchild_earnings": _pt(line["greatgrandchild"]),
    }
    return computed


def _pt(ledger) -> dict:
    return {"point": round(ledger.point, 4), "low": round(ledger.low, 4), "high": round(ledger.high, 4)}
