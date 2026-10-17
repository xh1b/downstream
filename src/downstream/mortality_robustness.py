# @ref:code-mortality-robustness
# Rationale: @link:paper-counts.
# Software contract: @link:doc-mortality-persistence-sensitivity.
# Verification: @link:test-mortality-robustness.
# @tag:mortality
"""Price a declared persistence assumption without pooling incompatible studies.

Eliason--Storrie's long-run null finding motivates a sensitivity, not an
HR-to-OR substitution or proof that a transported effect is exactly zero.
The alternative retains the source profile through offset +5 and sets its
offset +6 onward odds ratio to one. It is deliberately a hybrid assumption,
not a reproduction of the Swedish study.
"""
from __future__ import annotations

from .mortality import excess_deaths_profile, rate_to_risk
from .params import ParameterSet
from .worker import mortality_profile


def persistence_sensitivity(
    params: ParameterSet, mortality: dict, workers: float, years: float, *, raw: bool = False,
) -> dict:
    """Use the already resolved baseline, including explicit profile mixtures.

    The caller admits the population and source-profile timing before this
    comparison. No baseline is looked up again: county overrides, probability
    baselines and profile precedence must be identical in both structures.
    """
    baseline = mortality["baseline"]
    if "profiles" in baseline:
        strata = [(rate_to_risk(row["annual_rate"]), row["weight"])
                  for row in baseline["profiles"]]
    else:
        strata = [(baseline["annual_probability"], 1.0)]
    profile = mortality_profile(params)
    values = []
    for bound in ("point", "low", "high"):
        odds = {phase: getattr(parameter, bound) for phase, parameter in profile.items()}
        odds["offset_6_plus"] = 1.0
        value = sum(weight * excess_deaths_profile(workers, risk, odds, years)
                    for risk, weight in strata)
        values.append(value if raw else round(value, 2))
    source = {key: mortality[key] for key in ("point", "low", "high")}
    alternate = {"point": values[0], "low": min(values), "high": max(values)}
    difference = source["point"] - alternate["point"]
    return {
        "available": True,
        "status": "declared_structural_sensitivity",
        "eligible_for_public_headline": False,
        "unit": "deaths",
        "variants": {
            "source_profile": {
                **source,
                "evidence_status": "source_profile_with_transport_assumptions",
                "citations": sorted({key for p in profile.values() for key in p.citation_keys}),
            },
            "no_sustained_excess": {
                **alternate,
                "evidence_status": "structural_assumption",
                "motivating_citations": ["eliasonstorrie2009"],
                "assumption": "Retain source odds through offset +5; set offset +6 onward OR=1.",
                "first_changed_follow_up_year": 7,
                "fixed_late_odds_ratio": 1.0,
            },
        },
        "source_minus_no_sustained_point": difference if raw else round(difference, 2),
        "structural_point_range": {
            "low": min(source["point"], alternate["point"]),
            "high": max(source["point"], alternate["point"]),
            "interpretation": "Range of point estimates across these two assumptions; not a confidence interval or a bound on the true effect.",
        },
        "shared_inputs": ["exposure", "resolved mortality baseline", "follow-up horizon",
                          "source odds through offset +5"],
        "limitations": [
            "No probabilities or model-average weights are assigned to the structures.",
            "A nonsignificant long-run estimate does not establish an exactly zero effect.",
            "The Swedish study differs in population, design, effect scale and follow-up; this hybrid does not reproduce its estimates or substitute its hazard ratios for odds ratios.",
            "The cutoff follows the source profile's offset +6 phase, not the Swedish study's windows; persistence beyond its 12-year follow-up is an assumption in either direction.",
            "Baseline aging and target-population transport remain unresolved in both structures.",
        ],
    }
