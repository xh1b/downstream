# @ref:code-child-support
# Rationale: @link:paper-children.
# Software contract: @link:doc-child-support-0-4.
# Verification: @link:test-child-support.
# Source extraction: @link:child-source-selection.
# @tag:children
"""Inspect existing child earnings source support without inventing new effects."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import math
from pathlib import Path

from .child_applicability import child_scope
from .params import default_dir
from .scenario import ScenarioInput
from .study_library import load_library, require_contrast


def child_support_report(
    scenario: ScenarioInput | None = None,
    *,
    params_dir: str | Path | None = None,
    parent_tenure_years: float | None = None,
) -> dict:
    """Return source contrasts and target support states, without outcome totals.

    Optional numeric parent tenure makes the extracted two-year restriction
    inspectable. It does not modify the scenario engine or substitute for a
    reviewed transport decision. Unknown conditions remain unknown.
    Additional published sample restrictions are reported as unassessed, not
    inferred from target age bands, employer headcounts or a review decision.
    """
    scenario = scenario or ScenarioInput(0)
    if parent_tenure_years is not None and (
        isinstance(parent_tenure_years, bool)
        or not isinstance(parent_tenure_years, (int, float))
        or not math.isfinite(parent_tenure_years) or parent_tenure_years < 0
    ):
        raise ValueError("parent_tenure_years must be finite and nonnegative or null")
    directory = Path(params_dir) if params_dir is not None else default_dir()
    library = load_library(directory / "study_estimates.csv")
    contrasts = []
    for quartile in (None, 1, 2, 3, 4):
        study_id = "oreopoulos2008_overall" if quartile is None else f"oreopoulos2008_q{quartile}"
        source = library[study_id]
        require_contrast(
            source, citation="oreopoulos2008",
            source_sha256="ff990236c8e3aa19faff574f9f21af47665b2726f31f1d47fbc6ee9f89b7439c",
            link="displacement->child_earnings", scale="log_earnings_ratio",
            sex="Male", age_min="10", age_max="14", tenure_min_years="2",
            income_quartile="" if quartile is None else str(quartile),
            time_horizon="son earnings averaged 1995-1999 at ages 25-33",
            outcome_definition="log son earnings averaged 1995-1999",
            treatment="father displaced by firm closure", comparison="father not displaced",
            projection_status="conditional_source_contrast_not_lifetime_path",
        )
        beta, se = source["point"], source["standard_error"]
        multiplier = {"point": math.exp(beta), "low": math.exp(beta-1.96*se),
                      "high": math.exp(beta+1.96*se)}
        contrasts.append({
            "study_id": study_id, "income_quartile": quartile,
            "selected": scenario.child_income_quartile == quartile,
            "source": deepcopy(source),
            "log_earnings_ratio": {"point": beta, "standard_error": se},
            "earnings_multiplier": multiplier,
            "relative_earnings_gap_pct": {
                "point": 100*(1-multiplier["point"]),
                "low": 100*(1-multiplier["high"]),
                "high": 100*(1-multiplier["low"]),
            },
            "null_in_interval": multiplier["low"] <= 1 <= multiplier["high"],
        })
    scope = child_scope(scenario.child_profiles, scenario.child_income_quartile,
                        scenario.income_rank_definition)
    target = scenario.target_population
    refused, unknown, transport = [], [], []
    if scope["incompatible_children"]:
        refused.append("Known child age or sex is outside the source sons aged 10-14.")
    if scope["status"] == "unknown":
        unknown.append("Child age/sex profiles are absent or incomplete.")
    if target is None:
        unknown.append("Target parent sex, event, geography and calendar window are undeclared.")
    else:
        def is_unknown(value):
            return value.strip().lower() in {"unknown", "unspecified", "not known"}

        if is_unknown(target["sex"]) or is_unknown(target["children_sex"]):
            unknown.append("Target parent or child sex is unknown.")
        if any(target[key] != "Male" and not is_unknown(target[key])
               for key in ("sex", "children_sex")):
            refused.append("Target parent/child sex differs from the father-son source.")
        if is_unknown(target["exposure_type"]):
            unknown.append("Target event type is unknown.")
        elif target["exposure_type"] != "firm closure":
            refused.append("Target event differs from the source father firm closure.")
        if is_unknown(target["geography"]):
            unknown.append("Target geography is unknown.")
        elif target["geography"] != "Canada":
            transport.append("Canadian evidence must be transported to the declared target geography.")
        if is_unknown(target["calendar_window"]):
            unknown.append("Target calendar window is unknown.")
        elif target["calendar_window"] != "1980-1982":
            transport.append("The source closure window must be transported to the declared target period.")
    if parent_tenure_years is None:
        unknown.append("Numeric parent tenure is unknown; a tenure label alone does not verify the source minimum.")
    elif parent_tenure_years < 2:
        refused.append("Parent tenure is below the source minimum of two years.")
    if scenario.income_rank_definition is None:
        unknown.append("Target income-rank mapping has not been declared.")
    transport.append("Source adult earnings in 1995-1999 do not identify a lifetime earnings path.")
    decision = (scenario.applicability_decisions or {}).get("child_lifetime_earnings_lost_usd")
    state = (
        "refused" if refused else "unknown" if unknown
        else "reviewed_conditional_transport" if decision else "conditional_transport"
    )
    return {
        "schema": "downstream-child-support/1",
        "source_library_sha256": hashlib.sha256((directory / "study_estimates.csv").read_bytes()).hexdigest(),
        "support_state": state,
        "support_state_scope": "Supplied child profiles, parent/child sex, event, geography, period, tenure and income-rank mapping only.",
        "source_selection_assessment": {
            "status": "unassessed",
            "reason": "Scenario metadata does not establish the additional published sample restrictions.",
            "citation": "oreopoulos2008",
            "source_sha256": contrasts[0]["source"]["source_sha256"],
            "source_locator": "JOLE 26(3), pp. 459, 462-463 (PDF pp. 6, 9-10)",
            "conditions": [
                {"id": "father_age", "age_range": [30, 50], "reference_year": 1978},
                {"id": "father_tax_records", "requirement": "Fathers with missing tax data are excluded."},
                {"id": "initial_firm_size", "range": [2, 500], "unit": "IID fathers at the initial firm; not total employees"},
                {"id": "father_earnings_outliers", "excluded_above": 1000000,
                 "currency": "CAD", "price_year": 1999, "window": "any single year in the source sample"},
                {"id": "preclosure_unemployment_insurance", "years": [1978, 1979], "requirement": "No unemployment insurance receipt."},
                {"id": "preclosure_employer", "years": [1978, 1979], "requirement": "Father worked at the same firm in both years (p. 459)."},
                {"id": "closure_definition", "requirement": "No IID fathers at the firm in later years through 1999; exclude apparent closures if at least 35% move to the same new firm."},
            ],
        },
        "eligible_for_public_headline": False,
        "interpretation": "Source-support inspection only; no scenario total or new effect admission.",
        "source_scope": {
            "child_sex": "Male", "child_age_at_displacement": [10, 14],
            "parent_sex": "Male", "parent_minimum_tenure_years": 2,
            "event": "father firm closure", "event_window": "1980-1982",
            "country": "Canada", "income_rank": "father average pre-displacement income 1978-1979",
            "outcome": "log son earnings averaged 1995-1999", "adult_outcome_ages": [25, 33],
            "other_parent_restrictions": "Additional published restrictions appear in source_selection_assessment; their target match is unassessed.",
            "child_age_reference": "The main text specifies ages 10-14 in 1980 (p. 462); footnote 9 also states age <=14 in 1982. Exact event-age transport is unresolved.",
        },
        "target": {"population": deepcopy(target), "child_profiles": deepcopy(scenario.child_profiles),
                   "parent_tenure_years": parent_tenure_years,
                   "selected_income_quartile": scenario.child_income_quartile,
                   "income_rank_definition": scenario.income_rank_definition},
        "child_applicability": scope,
        "refused_reasons": refused, "unknown_conditions": unknown,
        "remaining_transport_conditions": transport,
        "transport_decision": deepcopy(decision),
        "contrasts": contrasts,
        "uncertainty": {
            "interval": "exp(beta +/- 1.96 * reported SE); approximate marginal 95% Wald interval",
            "gap_sign": "positive = earnings below reference; negative = earnings above reference",
            "limitations": [
                "Not a joint confidence band across income groups.",
                "Overlapping source sample; these contrasts are not independent replications.",
                "A nonsignificant coefficient is retained, not replaced with zero.",
                "Source intervals do not include transport or lifetime-profile uncertainty.",
                "Exact source transforms may differ slightly from rounded engine support endpoints.",
            ],
        },
        "unavailable_extensions": ["age-response curves", "other child sexes",
                                   "additional countries", "target assessment of additional source selection conditions"],
    }
