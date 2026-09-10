from pathlib import Path

import pytest

from downstream.mortality_profiles import MortalityBaselineProfile, load_profiles, resolve_mix, validate_sullivan_von_wachter_applicability
from downstream.employer import DocumentedExposure, compute_entity_counts
from downstream.params import load_all
from downstream.scenario import ScenarioInput, compute_counts, sample_counts


ROOT = Path(__file__).resolve().parent.parent


def test_profile_registry_rejects_context_only_and_supports_verified_default():
    profiles = load_profiles(ROOT / "params" / "mortality_profiles.csv")
    resolved = resolve_mix(profiles, "male_45_54_2015_2019", None)
    assert resolved[0][1] == 1.0
    with pytest.raises(ValueError, match="context_only"):
        resolve_mix(profiles, "all_ages_1999_2020_context", None)


def test_profile_selected_scenario_matches_historical_default_expected_count():
    parts = load_all(ROOT / "params")
    profiles = load_profiles(ROOT / "params" / "mortality_profiles.csv")
    baseline = compute_counts(parts["params"], parts["baselines"], ScenarioInput(100))
    profiled = compute_counts(
        parts["params"], parts["baselines"],
        ScenarioInput(100, mortality_profile="male_45_54_2015_2019"),
        mortality_profiles=profiles,
    )
    assert profiled["modeled"]["excess_deaths"]["point"] == pytest.approx(
        baseline["modeled"]["excess_deaths"]["point"], abs=.01
    )
    assert profiled["modeled"]["excess_deaths"]["baseline"]["profiles"][0]["id"] == "male_45_54_2015_2019"
    assert profiled["modeled"]["excess_deaths"]["baseline"]["effect_applicability"]["status"] == "demographic_scope_match"


def test_mortality_effect_refuses_unmatched_sex_or_age_profile():
    profile = MortalityBaselineProfile("female", "Female", "45-54 years", "2015-2019", "All causes", "US", .004,
                                       "scope", "source", "verified")
    with pytest.raises(ValueError, match="Male, 45-54"):
        validate_sullivan_von_wachter_applicability([(profile, 1.0)])


def test_profile_mix_requires_explicit_stratum_counts_for_predictive_layer():
    parts = load_all(ROOT / "params")
    profiles = load_profiles(ROOT / "params" / "mortality_profiles.csv")
    # A one-row mix is permitted and still retains the predictive safety gate.
    out = sample_counts(parts["params"], parts["baselines"],
                        ScenarioInput(100, mortality_mix={"male_45_54_2015_2019": 1.0}),
                        mortality_profiles=profiles, draws=2)
    assert out["modeled"]["excess_deaths"]["point"] > 0
    assert out["predictive_uncertainty"]["available"] is False


def test_entity_accepts_a_profile_registry():
    parts = load_all(ROOT / "params")
    profiles = load_profiles(ROOT / "params" / "mortality_profiles.csv")
    exposure = DocumentedExposure("acme", "employer", 100, "https://example.test", "reported layoffs")
    out = compute_entity_counts(
        parts["params"], parts["baselines"], exposure,
        ScenarioInput(0, mortality_profile="male_45_54_2015_2019"),
        mortality_profiles=profiles,
    )
    assert out["modeled"]["excess_deaths"]["baseline"]["profiles"][0]["id"] == "male_45_54_2015_2019"
