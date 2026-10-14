"""Per-result counterfactual probes, separate from parameter variance attribution."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from .params import ParameterSet, default_dir, load_correlations, load_nodes


def _targets(result):
    for name, row in result["modeled"].items():
        yield name, row, lambda value, key=name: value["modeled"][key]["point"]
    if result.get("child_valuation", {}).get("available"):
        for name, row in result["child_valuation"]["projections"].items():
            yield (f"child_valuation:{name}", row,
                   lambda value, key=name: value["child_valuation"]["projections"][key]["point"])


def _links(result, name):
    if name == "local_service_jobs_lost":
        return ["displacement->local_service_jobs"]
    source = "child_lifetime_earnings_lost_usd" if name.startswith("child_valuation:") else name
    return list(dict.fromkeys(
        "neighborhood_exposure->child_outcomes_modifier" if step["link"].startswith("place:")
        else step["link"] for step in result["modeled"][source].get("steps", [])))


def _override(params, link, value):
    # Fix all three statistics so a null outside source support remains a
    # well-formed diagnostic row. Class-specific jobs read a band endpoint.
    return replace(params, parameters=tuple(
        replace(p, point=value, low=value, high=value) if p.link == link else p
        for p in params.parameters))


def attach_sensitivity(result, params, scenario, evaluate):
    """Attach experiments to each emitted count and child-dollar projection.

    evaluate(params, scenario) re-executes the actual engine without reports.
    It must retain the caller's place, baseline, subgroup and registry inputs.
    No input distributions or baseline uncertainty ranges are fabricated.
    """
    if not result["modeled"]:
        return
    reference = evaluate(params, scenario)
    cache = {}

    def changed(link, value):
        key = (link, value)
        if key not in cache:
            cache[key] = evaluate(_override(params, link, value), scenario)
        return cache[key]

    for name, row, get_point in _targets(result):
        point = get_point(reference)

        def experiment(value, input_value):
            outcome = get_point(value)
            return {"input_value": input_value, "point": outcome,
                    "change_from_reference": outcome - point,
                    "reference_minus_variant": point - outcome}

        drivers = []
        for link in _links(result, name):
            parameter = params.by_link(link)
            local_jobs = name == "local_service_jobs_lost"
            if local_jobs:
                current = (parameter.low if scenario.local_job_mix == "manufacturing"
                           else parameter.high)
                low = high = current
                unit, neutral = "service jobs per net tradable job", 0.0
            elif link == "neighborhood_exposure->child_outcomes_modifier":
                current, low, high = parameter.point, parameter.low, parameter.high
                unit, neutral = "annual place exposure coefficient", 0.0
            else:
                current, low, high = parameter.point, parameter.low, parameter.high
                unit = "odds_ratio" if name == "excess_deaths" else "earnings_ratio"
                neutral = 1.0
            at_low = experiment(changed(link, low), low)
            at_high = experiment(changed(link, high), high)
            outcome_low, outcome_high = sorted([at_low["point"], at_high["point"]])
            drivers.append({
                "input_id": link, "input_value": current, "input_unit": unit,
                "citation": parameter.citation, "tier": parameter.tier,
                "population_scope": parameter.population_scope,
                "evidence_role": parameter.evidence_role,
                "effect_removed": experiment(changed(link, neutral), neutral),
                "supported_range": {
                    "input_low": low, "input_high": high,
                    "at_input_low": at_low, "at_input_high": at_high,
                    "outcome_low": outcome_low, "outcome_high": outcome_high,
                    "endpoint_span": outcome_high - outcome_low,
                    "scope": ("One declared job class; other classes are not uncertainty."
                              if local_jobs else "One input at its source endpoints; all others fixed.")},
            })
        drivers.sort(key=lambda driver: -abs(driver["effect_removed"]["change_from_reference"]))
        if name == "excess_deaths":
            fixed = {"displaced_workers": scenario.displaced_workers,
                     "follow_up_years": scenario.exposure_years,
                     "resolved_baseline": row["baseline"],
                     "mortality_method": scenario.mortality_method,
                     "mortality_timing": scenario.mortality_timing,
                     "target_population": scenario.target_population}
        elif name == "local_service_jobs_lost":
            fixed = {"net_tradable_jobs_lost": scenario.net_tradable_jobs_lost,
                     "job_class": scenario.local_job_mix}
        else:
            fixed = {"displaced_workers": scenario.displaced_workers,
                     "children_per_worker": scenario.n_children,
                     "child_profiles": scenario.child_profiles,
                     "child_income_quartile": scenario.child_income_quartile,
                     "income_rank_definition": scenario.income_rank_definition,
                     "lifetime_baseline": result["modeled"]["child_lifetime_earnings_lost_usd"]["baseline"],
                     "place": result["place"]}
            if name.startswith("child_valuation:"):
                fixed.update(real_discount_rate=scenario.real_discount_rate,
                             valuation_year=scenario.valuation_year,
                             annual_earnings_profile=result["child_valuation"]["annual_profile_source"])
        row["sensitivity"] = {
            "schema": "downstream-result-sensitivity/1", "reference_point": point,
            "unit": row.get("unit", "usd_2024"), "method": "one-input-at-a-time engine refits",
            "effect_drivers": drivers, "fixed_inputs": fixed,
            "fixed_input_ranges": {"available": False,
                                   "reason": "No sensitivity ranges supplied for these inputs; no distributions inferred."},
            "variance_attribution": {"available": False, "reason": "Not requested.",
                                     "request": "scenario --sensitivity-base N"},
            "interpretation": "Signed changes under declared input experiments; not causal shares or confidence intervals.",
            "limitations": [
                "Removal experiments may lie outside source support and are hypothetical, not new study estimates.",
                "Other inputs are fixed; individual removal changes need not sum to the total because effects interact.",
                "Endpoint spans measure range sensitivity, not shares of uncertainty or output variance.",
                "Baseline, exposure, demographic, timing and transport uncertainty are not quantified here.",
            ],
        }


def attach_variance_attribution(result, params, scenario, evaluate, *, nodes=None,
                                params_dir=None, base=128, seed=1901):
    """Apply the existing correlation-aware block estimator to emitted outcomes.

    Restrict the design to consumed parameters and their complete declared
    correlation components. Merge draws back into the full model for refits.
    Dependent parameters remain one block, never fictitious individual shares.
    """
    from .distributions import validate_sample_count
    from .sensitivity import correlated_block_sobol

    validate_sample_count(base, "sensitivity_base")
    directory = Path(params_dir) if params_dir is not None else Path(default_dir())
    correlations = (load_correlations(directory / "correlations.csv")
                    if (directory / "correlations.csv").exists() else [])
    if nodes is None:
        nodes = load_nodes(directory / "nodes.csv") if (directory / "nodes.csv").exists() else {}
    for name, row, get_point in _targets(result):
        links = set(_links(result, name))
        while True:
            expanded = links | {link for c in correlations if c.spearman != 0
                                and (c.from_param in links or c.to_param in links)
                                for link in (c.from_param, c.to_param)}
            if expanded == links:
                break
            links = expanded
        subset = ParameterSet(params.version, tuple(p for p in params.parameters if p.link in links))
        declared = [c for c in correlations if c.from_param in links and c.to_param in links]

        def compute(sampled):
            replacements = {p.link: p for p in sampled.parameters}
            full = replace(params, parameters=tuple(replacements.get(p.link, p)
                                                    for p in params.parameters))
            return get_point(evaluate(full, scenario))

        try:
            report = correlated_block_sobol(subset, compute, nodes, declared, base=base, seed=seed)
        except ValueError as exc:
            if "zero variance" not in str(exc):
                raise
            report = {"available": False, "reason": "Outcome is constant under sampled parameters.",
                      "base": base, "seed": seed}
        else:
            report["available"] = True
            report["scope"] = "Parameter variance under declared marginals and dependence; fixed scenario inputs."
            report["estimator_limits"] = (
                "Finite-design estimates can be negative or exceed one; they are not clipped. "
                "Increase the base and compare seeds before interpreting small differences in rank. "
                "Total-order indices include interactions and need not sum to one.")
            report["excluded"] = ["exposure and baseline uncertainty", "structural model probabilities",
                                  "transport error", "unmodeled pathways"]
        row["sensitivity"]["variance_attribution"] = report
