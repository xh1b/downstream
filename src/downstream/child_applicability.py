# @ref:code-child-applicability
# Method: @link:doc-child-support-0-4.
# Verification: @link:test-child-applicability; @link:test-audit04-custom-inputs.
# @tag:children
"""Child eligibility and source income contrasts, without invented age curves."""
from __future__ import annotations

from dataclasses import replace
import math
from pathlib import Path

from .params import ParameterSet
from .study_library import load_library, require_contrast


def validate_child_inputs(profiles, n_children, quartile, rank_definition):
    if quartile is not None and (isinstance(quartile, bool) or not isinstance(quartile, int) or quartile not in (1, 2, 3, 4)):
        raise ValueError("child_income_quartile must be an integer from 1 to 4")
    if rank_definition is not None and (not isinstance(rank_definition, str) or not rank_definition.strip()):
        raise ValueError("income_rank_definition must be a nonempty string")
    if quartile is not None and rank_definition is None:
        raise ValueError("an income quartile requires income_rank_definition and a transport argument")
    if profiles is not None:
        if not isinstance(profiles, list) or len(profiles) != n_children:
            raise ValueError("child_profiles must contain one record per n_children")
        for child in profiles:
            if not isinstance(child, dict) or set(child) != {"age_at_displacement", "sex"}:
                raise ValueError("child profile requires exactly age_at_displacement and sex")
            age = child["age_at_displacement"]
            if age is not None and (isinstance(age, bool) or not isinstance(age, int) or not 0 <= age <= 120):
                raise ValueError("child age must be an integer 0-120 or null")
            if child["sex"] not in {"Male", "Female", "Unknown"}:
                raise ValueError("child sex must be Male, Female or Unknown")


def child_scope(profiles, quartile, rank_definition):
    incompatible = []
    unknown = []
    for i, child in enumerate(profiles or []):
        age = child["age_at_displacement"]
        if (age is not None and not 10 <= age <= 14) or child["sex"] == "Female":
            incompatible.append(i)
        elif age is None or child["sex"] == "Unknown":
            unknown.append(i)
    matched = profiles is not None and not incompatible and not unknown
    return {"source": "oreopoulos2008", "source_age_at_displacement": [10, 14],
            "source_child_sex": "Male", "source_parent_sex": "Male",
            "source_geography": "Canada", "source_event": "father firm closure 1980-1982",
            "target_child_profiles": profiles, "incompatible_children": incompatible,
            "unknown_children": unknown, "source_income_quartile": quartile,
            "income_rank_definition": rank_definition,
            "eligible_for_reviewed_transport": bool(matched and rank_definition),
            "status": "incompatible" if incompatible else "demographic_match" if matched else "unknown",
            "limitations": ["No response curve across child ages is identified by this narrow cohort.",
                            "Income groups refer to father's average pre-displacement income in 1978-1979; target rank mapping requires a transport argument.",
                            "A subgroup's nonsignificant coefficient is retained with its uncertainty, not replaced with zero."]}


def select_child_contrast(params: ParameterSet, quartile, params_dir=None) -> ParameterSet:
    if quartile is None:
        return params
    original = params.by_link("displacement->child_earnings")
    marker = f"source_contrast=oreopoulos2008_q{quartile};"
    if marker in original.notes:
        # Materialized MC draws carry this marker: never reset their point.
        return params
    row = load_library(Path(params_dir) / 'study_estimates.csv' if params_dir is not None else None)[f"oreopoulos2008_q{quartile}"]
    require_contrast(row, link=original.link, scale='log_earnings_ratio', sex='Male',
                     age_min='10', age_max='14', income_quartile=str(quartile),
                     time_horizon='son earnings averaged 1995-1999 at ages 25-33',
                     outcome_definition='log son earnings averaged 1995-1999',
                     projection_status='conditional_source_contrast_not_lifetime_path')
    beta, se = row["point"], row["standard_error"]
    selected = replace(original, point=math.exp(beta), low=math.exp(beta-1.96*se),
                       high=math.exp(beta+1.96*se), dist="lognormal",
                       population_scope=row["population_scope"], citation=row["citation"], tier="EXACT",
                       notes=f"{marker} {row['source_locator']}; SHA256 {row['source_sha256']}; beta {beta}; SE {se}; SE method: {row['standard_error_method']}; conditional source subgroup, not a lifetime earnings path")
    return replace(params, parameters=tuple(selected if p.link == original.link else p
                                           for p in params.parameters))
