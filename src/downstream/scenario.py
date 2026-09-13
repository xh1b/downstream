"""Scenario aggregation: exposure counts -> modeled outcome counts.

A scenario describes an exposure (how many workers displaced, family
structure, shock size). Counts are computed ONLY where a cited
baseline exists; everything else is reported as blocked with the
exact missing input named. Nothing is ever estimated silently.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import random

from . import __version__
from .mortality import excess_deaths, excess_deaths_profile, rate_to_risk

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
    net_tradable_jobs_lost: float | None = None
    wage_multiplier: float | None = None   # None = JLS default band
    exposure_years: float = 20.0           # total follow-up, including initial peak year
    label: str = "scenario"
    mortality_method: str = "odds_survival"
    mortality_timing: str = "source_profile"
    mortality_profile: str | None = None
    mortality_mix: dict[str, float] | None = None
    place_application: str = "initial_only"

    def __post_init__(self):
        for name in ('displaced_workers', 'tradable_share', 'exposure_years'):
            value = getattr(self, name)
            if (isinstance(value, bool) or not isinstance(value, (int, float))
                    or not math.isfinite(value) or value < 0):
                raise ValueError(f'{name} must be finite and nonnegative')
        if isinstance(self.n_children, bool) or not isinstance(self.n_children, int) or self.n_children < 0:
            raise ValueError('n_children must be a nonnegative integer')
        if self.tradable_share > 1:
            raise ValueError('tradable_share must be in [0, 1]')
        if self.net_tradable_jobs_lost is not None and (
                isinstance(self.net_tradable_jobs_lost, bool)
                or not isinstance(self.net_tradable_jobs_lost, (int, float))
                or not math.isfinite(self.net_tradable_jobs_lost)
                or self.net_tradable_jobs_lost < 0):
            raise ValueError('net_tradable_jobs_lost must be finite and nonnegative when supplied')
        if self.wage_multiplier is not None and (not math.isfinite(self.wage_multiplier) or self.wage_multiplier <= 0):
            raise ValueError('wage_multiplier must be finite and positive')
        if self.mortality_method not in {'odds_survival', 'legacy_additive'}:
            raise ValueError('unknown mortality_method')
        if self.mortality_timing not in {'source_profile', 'source_aligned', 'immediate_sustained'}:
            raise ValueError('unknown mortality_timing')
        if self.mortality_profile is not None and (not isinstance(self.mortality_profile, str) or not self.mortality_profile):
            raise ValueError('mortality_profile must be a nonempty string when supplied')
        if self.mortality_mix is not None and not isinstance(self.mortality_mix, dict):
            raise ValueError('mortality_mix must be an object when supplied')
        if self.mortality_profile is not None and self.mortality_mix is not None:
            raise ValueError('mortality_profile and mortality_mix are mutually exclusive')
        if self.place_application not in {'initial_only', 'legacy_repeated'}:
            raise ValueError('unknown place_application')



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
    mortality_profiles: dict | None = None,
    county_mortality: dict | None = None,
    _raw: bool = False,
) -> dict:
    """Modeled counts for a displacement scenario.

    strict=True raises on the first missing baseline. Default mode
    returns computed outcomes plus an explicit blocked list.

    places + place_key (optional): the place-resolved layer. The
    baseline dict is swapped for the shrunk county baselines (same
    unit/population — no conversion) and the Chetty-Hendren mobility
    modifier scales the direct child loss in a same-place contrast
    (exploratory structural assumption). Provenance lands in the "place"
    block; absent/blocked modifiers leave the computation unchanged.

    county_mortality (optional): posterior table from
    county_rates.load_county_mortality_posteriors — under a matching
    place key, county mortality swaps in via the strict Gamma-Poisson
    contract instead of staying national.
    """
    place_block: dict | None = None
    modifier = None
    if place_key is not None:
        from .place import modifier_parameter, place_baselines

        pb = place_baselines(places, baselines, place_key,
                             county_mortality=county_mortality)
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
    line = child_line(params, place_modifier=modifier, place_application=scenario.place_application)

    computed: dict = {
        "label": scenario.label,
        "parameter_set_version": params.version,
        "engine_version": __version__,
        "uncertainty": {
            "band_kind": "parameter-support envelope, not a confidence interval",
            "fixed_inputs": ["exposure", "baseline values", "county measurements", "pooling weights"],
            "excluded": ["exposure estimation error", "baseline estimation error", "unmodeled pathways"],
        },
        "assumptions": {
            "mortality_method": scenario.mortality_method,
            "mortality_timing": (
                "source-offset profile: displacement, +1, +2–3, +4–5, and +6+; "
                "with displacement in follow-up year 1, offset +6 begins in follow-up year 7"
                if scenario.mortality_method == "odds_survival" and scenario.mortality_timing == "source_profile"
                else "legacy incomplete profile: years 2–5 at baseline and offset +6 applied from follow-up year 6"
                if scenario.mortality_method == "odds_survival" and scenario.mortality_timing == "source_aligned"
                else "sensitivity assumption: displacement-year peak followed immediately by the year-6+ odds ratio"
                if scenario.mortality_method == "odds_survival"
                else "legacy peak plus Y sustained years, linear rate approximation"
            ),
            "place_application": scenario.place_application,
            "place_counterfactual": (
                "county child-dollar contrasts use a same-place loss scaling "
                "and are exploratory; the national result is the reference"
                if modifier is not None else "national child-dollar result is the reference"
            ),
        },
        "exposure": {
            "displaced_workers": scenario.displaced_workers,
            "n_children": scenario.n_children,
            "tradable_share": scenario.tradable_share,
            "net_tradable_jobs_lost": scenario.net_tradable_jobs_lost,
            "exposure_years": scenario.exposure_years,
        },
        "modeled": {},
        "blocked": [],
        "place": place_block,
    }

    def rounded(value: float, digits: int) -> float:
        return value if _raw else round(value, digits)

    # Moretti estimates net metro-level job changes, not worker replacement.
    if scenario.net_tradable_jobs_lost is None:
        computed["blocked"].append({
            "outcome": "local_service_jobs_lost",
            "reason": "requires a documented net local loss of tradable jobs; worker displacement alone is not this exposure",
        })
    else:
        computed["modeled"]["local_service_jobs_lost"] = service_jobs_lost(
            params, scenario.net_tradable_jobs_lost
        )

    # Mortality counts: needs either the historical cited baseline or a
    # verified demographic profile / declared profile mixture.
    try:
        peak = worker["mortality_peak"]
        sustained = worker["mortality_sustained"]
        selected = scenario.mortality_profile is not None or scenario.mortality_mix is not None
        if selected:
            if mortality_profiles is None:
                raise BaselineMissing("mortality profile requested but no mortality profile registry was supplied")
            from .mortality_profiles import resolve_mix, validate_sullivan_von_wachter_applicability
            resolved = resolve_mix(mortality_profiles, scenario.mortality_profile, scenario.mortality_mix)
            applicability = validate_sullivan_von_wachter_applicability(resolved)
            component_values = []
            for profile_row, weight in resolved:
                probability = rate_to_risk(profile_row.annual_rate or 0.0)
                if scenario.mortality_method == "odds_survival" and scenario.mortality_timing == "source_profile":
                    from .worker import mortality_profile
                    causal_profile = mortality_profile(params)
                    component_values.append([weight * excess_deaths_profile(
                        scenario.displaced_workers, probability,
                        {phase: getattr(parameter, attr) for phase, parameter in causal_profile.items()},
                        scenario.exposure_years,
                    ) for attr in ("point", "low", "high")])
                else:
                    baseline = profile_row.annual_rate if scenario.mortality_method == "legacy_additive" else probability
                    component_values.append([weight * excess_deaths(
                        scenario.displaced_workers, baseline, getattr(peak, attr), getattr(sustained, attr),
                        scenario.exposure_years, scenario.mortality_method, timing=scenario.mortality_timing,
                    ) for attr in ("point", "low", "high")])
            values = [sum(component[index] for component in component_values) for index in range(3)]
            baseline_info = {"profiles": [{"id": row.profile_id, "weight": weight,
                                             "sex": row.sex, "age": row.age, "years": row.years,
                                             "cause": row.cause, "geography": row.geography,
                                             "status": row.status,
                                             "annual_rate": row.annual_rate,
                                             "population": row.population_scope, "citation": row.citation}
                                            for row, weight in resolved],
                             "effect_applicability": applicability}
            rate = sum((row.annual_rate or 0.0) * weight for row, weight in resolved)
            baseline_probability = sum(rate_to_risk(row.annual_rate or 0.0) * weight for row, weight in resolved)
        else:
            b = require_baseline(baselines, "all_cause_mortality_annual")
            if b.unit == "deaths_per_person_year":
                rate = b.value or 0.0
                baseline_probability = rate_to_risk(rate)
            elif b.unit in {"prob_per_person_year", "probability"}:
                rate = b.value or 0.0
                baseline_probability = rate
            else:
                raise BaselineMissing(f"mortality baseline unit {b.unit!r} is not an annual rate or probability")
            if scenario.mortality_method == "odds_survival" and scenario.mortality_timing == "source_profile":
                from .worker import mortality_profile
                causal_profile = mortality_profile(params)
                values = [excess_deaths_profile(
                    scenario.displaced_workers, baseline_probability,
                    {phase: getattr(parameter, attr) for phase, parameter in causal_profile.items()},
                    scenario.exposure_years,
                ) for attr in ("point", "low", "high")]
            else:
                legacy_baseline = rate if scenario.mortality_method == "legacy_additive" else baseline_probability
                values = [excess_deaths(
                    scenario.displaced_workers, legacy_baseline,
                    getattr(peak, attr), getattr(sustained, attr), scenario.exposure_years,
                    scenario.mortality_method, timing=scenario.mortality_timing,
                ) for attr in ("point", "low", "high")]
            baseline_info = {"value": rate, "annual_probability": baseline_probability,
                             "unit": b.unit, "citation": b.citation, "population": b.population}
        if scenario.mortality_method == "odds_survival" and scenario.mortality_timing == "source_profile":
            from .worker import mortality_profile
            profile = mortality_profile(params)
            mortality_steps = [{"link": p.link, "phase": phase, "point": p.point,
                                "low": p.low, "high": p.high, "citation": p.citation,
                                "tier": p.tier, "population_scope": p.population_scope}
                               for phase, p in profile.items()]
        else:
            mortality_steps = [step.as_dict() for led in (peak, sustained) for step in led.steps]
        computed["modeled"]["excess_deaths"] = {
            "point": rounded(values[0], 2), "low": rounded(min(values), 2), "high": rounded(max(values), 2),
            "unit": "deaths",
            "baseline": baseline_info,
            "steps": mortality_steps,
            "components": {"follow_up_years": scenario.exposure_years,
                           "method": scenario.mortality_method,
                           "timing": scenario.mortality_timing},
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
            "point": rounded(scenario.displaced_workers * scenario.n_children * (1 - child.point) * v, 2),
            "low": rounded(scenario.displaced_workers * scenario.n_children * (1 - child.high) * v, 2),
            "high": rounded(scenario.displaced_workers * scenario.n_children * (1 - child.low) * v, 2),
            "steps": [step.as_dict() for step in child.steps],
            "unit": "usd_2024",
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
    computed["projection_eligibility"] = line["evidence_status"]
    return computed


def sample_counts(
    params: ParameterSet,
    baselines: dict[str, Baseline],
    scenario: ScenarioInput,
    *,
    draws: int = 2_000,
    seed: int = 1901,
    strict: bool = False,
    places: dict | None = None,
    place_key: str | None = None,
    mortality_profiles: dict | None = None,
    county_mortality: dict | None = None,
    nodes: dict | None = None,
    params_dir=None,
) -> dict:
    """Return scenario counts with parameter-only 90% Monte Carlo bands.

    Exposure totals, baseline estimates, county measurements/pooling, and
    unmodeled pathways are intentionally held fixed.  They are named in the
    result rather than being smuggled into a parameter interval.
    """
    if isinstance(draws, bool) or not isinstance(draws, int) or draws < 2:
        raise ValueError("draws must be an integer of at least 2")
    from .mc import simulate_many

    result = compute_counts(params, baselines, scenario, strict=strict,
                            places=places, place_key=place_key,
                            mortality_profiles=mortality_profiles,
                            county_mortality=county_mortality)
    names = tuple(result["modeled"])

    def outcomes(sampled: ParameterSet) -> dict[str, float]:
        sampled_result = compute_counts(sampled, baselines, scenario, strict=strict,
                                         places=places, place_key=place_key,
                                         mortality_profiles=mortality_profiles,
                                         county_mortality=county_mortality, _raw=True)
        return {name: sampled_result["modeled"][name]["point"] for name in names}

    sampling = simulate_many(params, outcomes, draws=draws, seed=seed, nodes=nodes,
                             params_dir=params_dir, include_samples=True)
    raw_samples = sampling.pop("_raw_samples")
    result["parameter_uncertainty"] = {
        "interval": "central 90% Monte Carlo interval (p05–p95)",
        "scope": "parameter uncertainty only",
        "fixed": ["documented exposure", "baseline values", "county measurements", "pooling weights"],
        "excluded": ["exposure estimation error", "baseline estimation error", "structural uncertainty", "unmodeled pathways"],
        **sampling,
    }
    # Keep each headline self-contained for API/website callers.  The legacy
    # low/high fields remain support envelopes, so no existing consumer is
    # silently reinterpreted as receiving a confidence interval.
    for name, interval in sampling["outcomes"].items():
        result["modeled"][name]["parameter_interval_90"] = interval
    predictive_baselines = baselines
    if place_key is not None:
        from .place import place_baselines
        predictive_baselines = place_baselines(places, baselines, place_key,
                                               county_mortality=county_mortality)["baselines"]
    result["predictive_uncertainty"] = (
        {"available": False, "reason": "predictive mortality for demographic mixtures requires stratum-level cohort counts; expected effects are reported"}
        if scenario.mortality_profile is not None or scenario.mortality_mix is not None
        else _predictive_mortality(raw_samples.get("excess_deaths", []), predictive_baselines, scenario, seed)
    )
    return result


def _predictive_mortality(expected_excess: list[float], baselines: dict[str, Baseline],
                          scenario: ScenarioInput, seed: int) -> dict:
    """Posterior-predictive count layer for observed mortality.

    Parameter draws quantify uncertainty in the expected causal contrast.
    This layer adds binomial outcome variation for a *new cohort*.  The two
    potential outcome cohorts are sampled independently, so their difference
    is a reference-cohort contrast, not an observed individual-level causal
    effect.  Keeping it separate prevents realization noise from being
    mislabeled as parameter uncertainty.
    """
    n = scenario.displaced_workers
    if scenario.mortality_method != "odds_survival":
        return {
            "available": False,
            "reason": "predictive mortality requires odds_survival; the legacy additive contrast does not define bounded cohort probabilities",
        }
    if abs(n - round(n)) > 1e-9:
        return {
            "available": False,
            "reason": "predictive mortality counts require an integer worker cohort; expected effects remain available for fractional exposure aggregates",
        }
    baseline = baselines.get("all_cause_mortality_annual")
    if baseline is None or baseline.status != "verified" or baseline.value is None:
        return {"available": False, "reason": "no verified mortality baseline"}
    if not expected_excess:
        return {"available": False, "reason": "mortality outcome was blocked"}
    if baseline.unit == "deaths_per_person_year":
        annual_probability = rate_to_risk(baseline.value)
    elif baseline.unit in {"prob_per_person_year", "probability"}:
        annual_probability = baseline.value
    else:
        return {"available": False, "reason": f"unsupported mortality baseline unit {baseline.unit!r}"}
    cohort = int(round(n))
    p0 = 1 - (1 - annual_probability) ** scenario.exposure_years
    rng = random.Random(seed + 104729)
    exposed: list[float] = []
    counterfactual: list[float] = []
    contrasts: list[float] = []
    for effect in expected_excess:
        p1 = min(1.0, max(0.0, p0 + effect / cohort)) if cohort else p0
        e = rng.binomialvariate(cohort, p1)
        c = rng.binomialvariate(cohort, p0)
        exposed.append(e)
        counterfactual.append(c)
        contrasts.append(e - c)

    def summary(values: list[float]) -> dict[str, float]:
        values.sort()
        last = len(values) - 1
        return {"p05": values[int(.05 * last)], "p50": values[int(.50 * last)],
                "p95": values[int(.95 * last)], "mean": round(sum(values) / len(values), 4)}

    return {
        "available": True,
        "interval": "central 90% posterior-predictive simulation interval (parameter draws + binomial cohort variation)",
        "scope": "realized all-cause deaths in a new integer-sized cohort, conditional on the model's fixed baseline and timing assumptions",
        "counterfactual_design": "independent exposed and counterfactual reference cohorts; their difference is not an observable paired individual causal contrast",
        "cohort_workers": cohort,
        "baseline_annual_probability": annual_probability,
        "baseline_annual_rate": baseline.value if baseline.unit == "deaths_per_person_year" else None,
        "counterfactual_death_probability": p0,
        "exposed_deaths": summary(exposed),
        "counterfactual_deaths": summary(counterfactual),
        "reference_cohort_difference": summary(contrasts),
    }


def _pt(ledger) -> dict:
    return {"point": round(ledger.point, 4), "low": round(ledger.low, 4), "high": round(ledger.high, 4)}
