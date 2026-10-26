# @ref:code-child-gap-view
# Rationale: @link:paper-children.
# Software contract: @link:doc-child-gap-view.
# Verification: @link:test-child-gap-view; @link:test-child-gap-cli.
# @tag:children
"""Side-by-side earnings gaps with the same contexts as scenario counts.

This view combines explanations, not effect sizes. Descendant gaps are
structural projections; they never acquire invented populations or dollar totals.
"""

from __future__ import annotations

from copy import deepcopy

from .child_applicability import select_child_contrast
from .children import child_line
from .params import Baseline, ParameterSet
from .scenario import ScenarioInput, compute_counts

CHILD_DOLLARS = "child_lifetime_earnings_lost_usd"
HOUSING_LINK = "foreclosure_order->house_price_gap"


def child_gap_view(
    params: ParameterSet,
    baselines: dict[str, Baseline],
    scenario: ScenarioInput,
    *,
    places=None,
    place_key=None,
    mortality_profiles=None,
    county_mortality=None,
    params_dir=None,
) -> dict:
    """Return a JSON-serializable child/descendant explanation report.

    Inputs and refusal rules are those of ``compute_counts``. Relative gaps
    need no dollar baseline. Known-incompatible child/target demographics
    withhold all three generations. Unknown demographics retain an explicitly
    illustrative reference. Dollar conversion applies only to children.
    """
    result = compute_counts(
        params, baselines, scenario, places=places, place_key=place_key,
        mortality_profiles=mortality_profiles, county_mortality=county_mortality,
        params_dir=params_dir,
    )
    selected = select_child_contrast(params, scenario.child_income_quartile, params_dir)
    modifier = None
    if place_key is not None:
        from .place import modifier_parameter

        modifier = modifier_parameter(selected, places, place_key)["parameter"]
    line = child_line(selected, modifier, scenario.place_application)
    blockers = [row["reason"] for row in result["blocked"] if row["outcome"] == CHILD_DOLLARS]
    target = scenario.target_population
    target_incompatible = target is not None and (
        target["sex"] != "Male" or target["children_sex"] != "Male"
        or target["exposure_type"] != "firm closure"
    )
    incompatible = target_incompatible or result["child_applicability"]["status"] == "incompatible" or any(
        reason == "target demographics do not match the admitted effect" for reason in blockers
    )
    child_dollars = result["modeled"].get(CHILD_DOLLARS)
    eligibility = deepcopy(child_dollars["applicability"]) if child_dollars else {
        "status": "illustrative_reference_calculation", "eligible_for_public_headline": False,
        "reason": "; ".join(blockers) or "Target transport has not been reviewed.",
    }
    rows = []
    for generation in ("child", "grandchild", "greatgrandchild"):
        ledger = line[generation]
        source_status = deepcopy(line["evidence_status"][generation])
        status = source_status["status"]
        from .source_support import UnavailableLedger
        source_blocked = isinstance(ledger, UnavailableLedger)
        if modifier is not None and not source_blocked:
            status = "exploratory_place_projection" if generation == "child" else "structural_projection_with_exploratory_place"
        available = not incompatible and not source_blocked
        rows.append({
            "generation": generation,
            "available": available,
            "reason": "Child or target demographics are incompatible with the source path." if incompatible else str(ledger.source_error) if source_blocked else None,
            "evidence_status": status,
            "entry_evidence": source_status,
            "unit": "percent_earnings_gap_vs_no_displacement",
            "sign_convention": "positive = earnings below reference; negative = earnings above reference",
            "value": {
                "point": 100 * (1 - ledger.point),
                "low": 100 * (1 - ledger.high),
                "high": 100 * (1 - ledger.low),
            } if available else None,
            "earnings_multiplier": {
                "point": ledger.point, "low": ledger.low, "high": ledger.high,
            } if available else None,
            "horizon": "adult earnings in this generation; not an annual dollar loss",
            "eligible_for_public_headline": bool(
                available and generation == "child" and modifier is None
                and eligibility["eligible_for_public_headline"]
            ),
            "steps": [step.as_dict() for step in ledger.steps],
            "dollar_conversion": deepcopy(child_dollars) if generation == "child" and available else None,
            "dollar_conversion_reason": (
                "; ".join(blockers) if generation == "child" and not child_dollars
                else "No descendant population or compatible earnings baseline is declared."
                if generation != "child" else None
            ),
        })
    return {
        "schema_version": "child_gap_view.v1",
        "label": scenario.label,
        "engine_version": result["engine_version"],
        "parameter_set_version": result["parameter_set_version"],
        "input_content_sha256": result["input_content_sha256"],
        "composition": "side_by_side_only",
        "combined_total": None,
        "combined_total_reason": (
            "Generation-specific relative gaps are not additive. Divorce, family-size, "
            "school and housing pathways are not added to the direct child estimate; "
            "overlap, counterfactual incidence and a compatible joint estimand are unresolved."
        ),
        "uncertainty": {
            "band_kind": "parameter-support envelope, not a confidence interval",
            "meaning": "Transformed marginal support ranges propagated by the existing ledger; not probability bounds.",
            "fixed_inputs": deepcopy(result["uncertainty"]["fixed_inputs"]),
            "excluded": deepcopy(result["uncertainty"]["excluded"]) + [
                "transport uncertainty", "descendant population uncertainty",
            ],
        },
        "target_population": deepcopy(result["target_population"]),
        "child_applicability": deepcopy(result["child_applicability"]),
        "child_transport": eligibility,
        "child_valuation": deepcopy(result.get("child_valuation")),
        "place": deepcopy(result["place"]),
        "place_application": scenario.place_application,
        "rows": rows,
        "blocked": deepcopy(result["blocked"]),
        "housing_chain": housing_chain_requirements(params),
    }


def housing_chain_requirements(params: ParameterSet) -> dict:
    """Describe the missing displacement-to-housing bridges, without totals."""
    try:
        source = params.by_link(HOUSING_LINK)
    except KeyError:
        source_row = None
    else:
        source_row = {
            "link": source.link, "point": source.point, "low": source.low,
            "high": source.high, "unit": "neighbor_house_price_multiplier_per_foreclosure",
            "citation": source.citation, "tier": source.tier,
            "population_scope": source.population_scope, "evidence_role": source.evidence_role,
            "band_meaning": "Declared parameter support; consult source notes. The shipped preferred estimate uses a rounding band, not a confidence interval.",
            "notes": source.notes,
        }
    return {
        "available": False,
        "total": None,
        "reason": "A foreclosure-to-neighbor-price boundary row does not identify a displacement-to-housing total.",
        "source_row": source_row,
        "requirements": [
            {"bridge": "displacement_to_extra_foreclosures", "required": [
                "mortgage/ownership-exposed households, not worker equivalents",
                "counterfactual foreclosure incidence in the same population and event window",
                "an identified displacement response and a target-population transport decision",
            ]},
            {"bridge": "extra_foreclosures_to_neighbor_price", "required": [
                "geocoded extra foreclosures, affected properties, distance and sale timing",
                "compatible property type, geography and timing for the Campbell boundary estimand",
                "declared treatment of overlapping radii and repeated foreclosure exposures",
            ]},
            {"bridge": "relative_price_to_aggregate_dollars", "required": [
                "counterfactual property values with a declared currency year and valuation date",
                "unique affected-property inventory and a joint response rule for multiple foreclosures",
                "a declared stock-value estimand; wealth changes are not annual earnings losses",
            ]},
            {"bridge": "housing_to_school_or_child_outcomes", "required": [
                "local assessment/tax revenue and school-finance pass-through over matching years",
                "child school-exposure histories and a compatible spending-response estimand",
                "a joint causal model addressing overlap with the direct child earnings estimate",
            ]},
        ],
    }
