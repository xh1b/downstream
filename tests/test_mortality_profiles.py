from pathlib import Path

import pytest

from downstream.mortality_profiles import (MortalityBaselineProfile, load_profiles, parse_mix_spec,
                                           resolve_mix, validate_sullivan_von_wachter_applicability)
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


def test_verified_prime_age_profile_rows_match_the_d76_pull():
    import hashlib
    import json

    profiles = load_profiles(ROOT / "params" / "mortality_profiles.csv")
    expected = {
        ("Male", "25-34 years"): 0.001751, ("Female", "25-34 years"): 0.000781,
        ("Male", "35-44 years"): 0.002453, ("Female", "35-44 years"): 0.001397,
        ("Male", "45-54 years"): 0.004944, ("Female", "45-54 years"): 0.003080,
        ("Male", "55-64 years"): 0.011119, ("Female", "55-64 years"): 0.006696,
    }
    for (sex, age), rate in expected.items():
        band = age.split()[0].replace("-", "_")
        pid = f"{'male' if sex == 'Male' else 'female'}_{band}_2015_2019"
        row = profiles[pid]
        assert row.status == "verified" and row.cause == "All causes" and row.geography == "US"
        assert row.annual_rate == pytest.approx(rate)
        assert "cdc_wonder_d76_national_year_age_sex_1999_2020" in row.citation + row.notes
    provenance = json.loads(
        (ROOT / "validation" / "cdc_wonder_d76_national_year_age_sex_1999_2020.provenance.json")
        .read_text(encoding="utf-8"))
    raw = (ROOT / "validation" / "cdc_wonder_d76_national_year_age_sex_1999_2020.xml").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == provenance["sha256"]
    assert provenance["derivation"]["verified_pools"]["male_45_54"]["deaths"] == 514314


def test_declared_mixtures_still_require_admitted_response_scope():
    profiles = load_profiles(ROOT / "params" / "mortality_profiles.csv")
    resolved = resolve_mix(profiles, None, {"female_45_54_2015_2019": 0.4,
                                            "male_45_54_2015_2019": 0.6})
    assert [p.profile_id for p, _ in resolved] == ["female_45_54_2015_2019", "male_45_54_2015_2019"]
    with pytest.raises(ValueError, match="Male, 45-54 years, All causes"):
        validate_sullivan_von_wachter_applicability(resolved)


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


def test_parse_mix_spec_refuses_duplicates_and_malformed_entries():
    assert parse_mix_spec("a:0.4, b:0.6") == {"a": 0.4, "b": 0.6}
    for bad, message in [("a:0.6,a:1.0", "duplicate"), ("a", "profile:weight"),
                         ("a:", "profile:weight"), (":0.5", "profile:weight"),
                         ("a:half", "weight"), ("", "nonempty")]:
        with pytest.raises(ValueError, match=message):
            parse_mix_spec(bad)


def test_resolve_mix_validates_weights_and_registry_status():
    profiles = load_profiles(ROOT / "params" / "mortality_profiles.csv")
    with pytest.raises(KeyError, match="unknown mortality profile"):
        resolve_mix(profiles, "no_such_profile", None)
    with pytest.raises(ValueError, match="mutually exclusive"):
        resolve_mix(profiles, "male_45_54_2015_2019", {"male_45_54_2015_2019": 1.0})
    with pytest.raises(ValueError, match="sum to 1"):
        resolve_mix(profiles, None, {"male_45_54_2015_2019": 0.7})
    with pytest.raises(ValueError, match="nonnegative weights"):
        resolve_mix({"x": profiles["male_45_54_2015_2019"]}, None, {"x": -1.0})
    with pytest.raises(ValueError, match="finite nonnegative"):
        resolve_mix({"x": profiles["male_45_54_2015_2019"]}, None, {"x": True})


def _write_registry(tmp_path, rows):
    header = ("profile_id,sex,age,years,cause,geography,annual_rate,"
              "population_scope,citation,status,notes\n")
    (tmp_path / "mortality_profiles.csv").write_text(header + rows)
    return tmp_path / "mortality_profiles.csv"


def test_load_profiles_refuses_duplicate_blank_or_unrated_verified_rows(tmp_path):
    good = "m1,Male,45-54 years,2015-2019,All causes,US,0.005,scope,cite,verified,\n"
    with pytest.raises(ValueError, match="duplicate"):
        load_profiles(_write_registry(tmp_path, good + "m1,Male,45-54 years,2015-2019,All causes,US,0.004,scope,cite,verified,\n"))
    with pytest.raises(ValueError, match="blank metadata"):
        load_profiles(_write_registry(tmp_path, "m2,,45-54 years,2015-2019,All causes,US,0.005,scope,cite,verified,\n"))
    with pytest.raises(ValueError, match="needs annual_rate"):
        load_profiles(_write_registry(tmp_path, "m3,Male,45-54 years,2015-2019,All causes,US,,scope,cite,verified,\n"))


def test_all_cause_response_refuses_cause_specific_baseline_profile():
    male = MortalityBaselineProfile("male", "Male", "45-54 years", "2015-2019", "All causes", "US",
                                    .004944, "scope", "source", "verified")
    validate_sullivan_von_wachter_applicability([(male, 1.0)])
    cancer = MortalityBaselineProfile("cancer", "Male", "45-54 years", "2015-2019", "Malignant neoplasms",
                                      "US", .0015, "scope", "source", "verified")
    with pytest.raises(ValueError, match="All causes"):
        validate_sullivan_von_wachter_applicability([(cancer, 1.0)])


def test_profile_provenance_reports_every_selected_profile_field():
    parts = load_all(ROOT / "params")
    profiles = load_profiles(ROOT / "params" / "mortality_profiles.csv")
    out = compute_counts(
        parts["params"], parts["baselines"],
        ScenarioInput(100, mortality_profile="male_45_54_2015_2019"),
        mortality_profiles=profiles,
    )
    row = out["modeled"]["excess_deaths"]["baseline"]["profiles"][0]
    assert row["weight"] == 1.0
    assert row["annual_rate"] == pytest.approx(0.004944)
    assert "CDC WONDER" in row["citation"]
    for field in ("sex", "age", "years", "cause", "geography", "status", "population"):
        assert row[field], f"provenance field {field} must be reported"


def test_cli_refuses_unknown_profile_duplicate_mix_and_bad_weights(tmp_path, capsys):
    from downstream.cli import main

    def expect_cli_error(argv, message):
        with pytest.raises(SystemExit) as exc:
            main(argv)
        assert exc.value.code == 2
        assert message in capsys.readouterr().err

    expect_cli_error(["scenario", "--workers", "10", "--mortality-profile", "no_such_profile"],
                     "unknown mortality profile")
    expect_cli_error(
        ["scenario", "--workers", "10",
         "--mortality-mix", "male_45_54_2015_2019:0.6,male_45_54_2015_2019:1.0"],
        "duplicate mortality mix profile")
    expect_cli_error(["scenario", "--workers", "10", "--mortality-mix", "male_45_54_2015_2019:half"],
                     "invalid --mortality-mix")

    exposure = tmp_path / "exposure.json"
    exposure.write_text('{"subject_id":"acme","subject_type":"employer","displaced_workers":10,'
                        '"source":"https://example.test","method":"reported"}')
    expect_cli_error(["entity", "--input", str(exposure), "--mortality-profile", "no_such_profile"],
                     "unknown mortality profile")
