"""Sensitivity must refit the same scenario without changing its scientific scope."""
import csv
import json
import math
import shutil

import pytest

from downstream.cli import main
from downstream.county_rates import load_county_mortality_posteriors
from downstream.employer import DocumentedExposure, compute_entity_counts
from downstream.mortality import excess_deaths_profile
from downstream.mortality_profiles import load_profiles
from downstream.params import default_dir, load_all
from downstream.place import load_places
from downstream.policy import PolicyCase, compare_policies
from downstream.scenario import ScenarioInput, compute_counts, sample_counts
from downstream.worker import mortality_profile


@pytest.fixture
def parts():
    return load_all()


def compute(parts, scenario=None, **kwargs):
    return compute_counts(parts["params"], parts["baselines"], scenario or ScenarioInput(1000), **kwargs)


def drivers(row):
    return {d["input_id"]: d for d in row["sensitivity"]["effect_drivers"]}


def test_all_mortality_phases_are_exact_individual_refits(parts):
    before = parts["params"]
    row = compute(parts)["modeled"]["excess_deaths"]
    profile = mortality_profile(before)
    odds = {phase: p.point for phase, p in profile.items()}
    risk = row["baseline"]["annual_probability"]
    report = row["sensitivity"]
    point = excess_deaths_profile(1000, risk, odds, 20)
    assert report["reference_point"] == point
    assert len(drivers(row)) == 5
    for phase, p in profile.items():
        d = drivers(row)[p.link]
        assert d["citation"] == p.citation
        assert d["input_value"] == p.point
        removed = excess_deaths_profile(1000, risk, {**odds, phase: 1}, 20)
        assert d["effect_removed"]["point"] == pytest.approx(removed)
        assert d["effect_removed"]["reference_minus_variant"] == pytest.approx(point - removed)
        for bound in ("low", "high"):
            at = d["supported_range"][f"at_input_{bound}"]
            expected = excess_deaths_profile(1000, risk, {**odds, phase: getattr(p, bound)}, 20)
            assert at["point"] == pytest.approx(expected)
            assert at["change_from_reference"] == pytest.approx(expected - point)
    late = drivers(row)["earnings_shock->mortality_sustained"]["effect_removed"]
    assert late["point"] == pytest.approx(20.52335161286114)
    assert late["point"] == pytest.approx(row["persistence_sensitivity"]["variants"]["no_sustained_excess"]["point"], abs=.005)
    assert sum(d["effect_removed"]["reference_minus_variant"] for d in drivers(row).values()) != pytest.approx(point)
    assert parts["params"] is before


@pytest.mark.parametrize("workers,years", [(0, 20), (.125, 20), (1000, 0), (1000, 6)])
def test_zero_fractional_and_timing_boundaries(parts, workers, years):
    row = compute(parts, ScenarioInput(workers, exposure_years=years))["modeled"]["excess_deaths"]
    late = drivers(row)["earnings_shock->mortality_sustained"]
    if workers == 0 or years <= 6:
        assert late["effect_removed"]["change_from_reference"] == 0
        assert late["supported_range"]["endpoint_span"] == 0
    else:
        assert 0 < late["effect_removed"]["reference_minus_variant"] < .002
    json.dumps(row, allow_nan=False)


def test_null_compatible_and_protective_estimates_keep_their_sign(parts):
    scenario = ScenarioInput(1000, child_income_quartile=3, income_rank_definition="source-matched fixture")
    row = compute(parts, scenario)["modeled"]["child_lifetime_earnings_lost_usd"]
    d = drivers(row)["displacement->child_earnings"]
    assert row["point"] < 0
    assert d["input_value"] > 1
    assert d["effect_removed"]["point"] == 0
    assert d["effect_removed"]["reference_minus_variant"] < 0
    assert d["supported_range"]["outcome_low"] < 0 < d["supported_range"]["outcome_high"]
    assert "source-matched" in row["sensitivity"]["fixed_inputs"]["income_rank_definition"]


def test_place_coefficient_is_neutralized_at_zero_and_baseline_is_preserved(parts):
    places = load_places()
    result = compute(parts, places=places, place_key="17043")
    child = result["modeled"]["child_lifetime_earnings_lost_usd"]
    d = drivers(child)["neighborhood_exposure->child_outcomes_modifier"]
    national = compute(parts)["modeled"]["child_lifetime_earnings_lost_usd"]
    assert d["effect_removed"]["input_value"] == 0
    assert d["effect_removed"]["point"] == pytest.approx(national["point"], abs=.005)
    assert child["sensitivity"]["fixed_inputs"]["place"]["key"] == "17043"
    assert child["sensitivity"]["fixed_input_ranges"]["available"] is False


def test_explicit_mortality_profile_has_same_sensitivity_as_equal_baseline(parts):
    registry = load_profiles(default_dir() / "mortality_profiles.csv")
    row = compute(parts, ScenarioInput(1000, mortality_profile="male_45_54_2015_2019"),
                  mortality_profiles=registry)["modeled"]["excess_deaths"]
    national = compute(parts)["modeled"]["excess_deaths"]
    for key, d in drivers(row).items():
        assert d["effect_removed"]["point"] == pytest.approx(drivers(national)[key]["effect_removed"]["point"])
    assert row["sensitivity"]["fixed_inputs"]["resolved_baseline"]["profiles"]


def test_county_refits_keep_the_resolved_baseline_without_repooling(parts):
    county = load_county_mortality_posteriors(default_dir() / "county_mortality.csv")
    row = compute(parts, places=load_places(), place_key="17043",
                  county_mortality=county)["modeled"]["excess_deaths"]
    assert row["baseline"]["value"] != parts["baselines"]["all_cause_mortality_annual"].value
    odds = {phase: p.point for phase, p in mortality_profile(parts["params"]).items()}
    for phase, parameter in mortality_profile(parts["params"]).items():
        expected = excess_deaths_profile(1000, row["baseline"]["annual_probability"],
                                        {**odds, phase: 1}, 20)
        assert drivers(row)[parameter.link]["effect_removed"]["point"] == pytest.approx(expected)


@pytest.mark.parametrize("job_class,coefficient", [("manufacturing", 1.6), ("high_tech", 5.0)])
def test_local_jobs_do_not_treat_cross_class_span_as_uncertainty(parts, job_class, coefficient):
    row = compute(parts, ScenarioInput(1000, net_tradable_jobs_lost=10,
                                     local_job_mix=job_class))["modeled"]["local_service_jobs_lost"]
    d = drivers(row)["displacement->local_service_jobs"]
    assert d["input_value"] == coefficient
    assert d["effect_removed"]["point"] == 0
    assert d["supported_range"]["endpoint_span"] == 0


def test_blocked_outcomes_never_acquire_diagnostics(parts):
    scenario = ScenarioInput(1000, child_profiles=[{"age_at_displacement": 50, "sex": "Female"}]*2)
    result = compute(parts, scenario)
    assert "child_lifetime_earnings_lost_usd" not in result["modeled"]
    assert "local_service_jobs_lost" not in result["modeled"]
    target = {"sex": "Female", "age": "45-54 years", "worker_tenure": "high-tenure",
              "geography": "United States", "calendar_window": "2015-2019",
              "exposure_type": "firm closure", "children_sex": "Female"}
    assert compute(parts, ScenarioInput(1000, target_population=target))["modeled"] == {}


def test_present_values_entity_and_policy_inherit_reports(parts):
    scenario = ScenarioInput(1000, child_profiles=[{"age_at_displacement": 12, "sex": "Male"}]*2,
                             real_discount_rate=.03, valuation_year=2026)
    out = compute(parts, scenario)
    for projection in out["child_valuation"]["projections"].values():
        d = drivers(projection)["displacement->child_earnings"]
        assert d["effect_removed"]["point"] == 0
        assert projection["sensitivity"]["fixed_inputs"]["real_discount_rate"] == .03
    entity = compute_entity_counts(parts["params"], parts["baselines"],
                                   DocumentedExposure("fixture", "employer", 1000, "fixture", "fixture"))
    assert entity["modeled"]["excess_deaths"]["sensitivity"]
    case = PolicyCase("fixture", "fixture", "fixture", ScenarioInput(1000))
    policy = compare_policies(parts["params"], parts["baselines"], case, case)
    assert policy["baseline"]["parameter_envelope"]["modeled"]["excess_deaths"]["sensitivity"]


def test_sampling_preserves_custom_subgroup_sources_and_reports(parts, tmp_path):
    for name in ("study_estimates.csv", "nodes.csv"):
        shutil.copy(default_dir() / name, tmp_path / name)
    library = tmp_path / "study_estimates.csv"
    with library.open(newline="") as handle:
        reader = csv.DictReader(handle)
        fields, rows = reader.fieldnames, list(reader)
    for row in rows:
        if row["study_id"] == "oreopoulos2008_q3":
            row.update(point="0.2", standard_error="0.03")
    with library.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    scenario = ScenarioInput(1000, child_income_quartile=3, income_rank_definition="fixture")
    out = sample_counts(parts["params"], parts["baselines"], scenario, draws=4, params_dir=tmp_path,
                        sensitivity_base=8)
    child = out["modeled"]["child_lifetime_earnings_lost_usd"]
    driver = drivers(child)["displacement->child_earnings"]
    assert driver["input_value"] == pytest.approx(math.exp(.2))
    assert driver["supported_range"]["input_low"] == pytest.approx(math.exp(.2 - 1.96*.03))
    assert child["sensitivity"]["variance_attribution"]["available"]
    assert child["sensitivity"]["variance_attribution"]["correlations_applied"] == 0
    (tmp_path / "study_estimates.csv").unlink()
    with pytest.raises(FileNotFoundError):
        sample_counts(parts["params"], parts["baselines"], scenario, draws=4, params_dir=tmp_path)


def test_variance_attribution_preserves_complete_correlated_blocks_and_seed(parts):
    def run():
        return sample_counts(parts["params"], parts["baselines"], ScenarioInput(1000),
                             draws=4, nodes=parts["nodes"], sensitivity_base=128)
    a, b = run(), run()
    variance = a["modeled"]["excess_deaths"]["sensitivity"]["variance_attribution"]
    assert variance == b["modeled"]["excess_deaths"]["sensitivity"]["variance_attribution"]
    assert variance["available"]
    assert variance["correlations_applied"] == 2
    assert any(set(block["links"]) == {"displacement->worker_earnings",
        "earnings_shock->mortality_peak", "earnings_shock->mortality_sustained"}
        for block in variance["blocks"])
    assert all(math.isfinite(block["S_total"]) for block in variance["blocks"])
    zero = sample_counts(parts["params"], parts["baselines"], ScenarioInput(0), draws=2,
                         sensitivity_base=2)
    assert all(not row["sensitivity"]["variance_attribution"]["available"] for row in zero["modeled"].values())


def test_cli_returns_reports_and_rejects_invalid_variance_sample_count(capsys):
    assert main(["scenario", "--workers", "1000", "--draws", "2", "--sensitivity-base", "8"]) == 0
    row = json.loads(capsys.readouterr().out)["modeled"]["excess_deaths"]
    assert len(row["sensitivity"]["effect_drivers"]) == 5
    assert row["sensitivity"]["variance_attribution"]["available"]
    with pytest.raises(SystemExit) as exc:
        main(["scenario", "--workers", "1000", "--draws", "2", "--sensitivity-base", "1"])
    assert exc.value.code == 2


@pytest.mark.parametrize("timing,method", [("source_aligned", "odds_survival"),
                                          ("immediate_sustained", "odds_survival"),
                                          ("source_profile", "legacy_additive")])
def test_legacy_results_report_only_consumed_coefficients(parts, timing, method):
    row = compute(parts, ScenarioInput(1000, mortality_timing=timing,
                                      mortality_method=method))["modeled"]["excess_deaths"]
    assert set(drivers(row)) == {"earnings_shock->mortality_peak", "earnings_shock->mortality_sustained"}
    assert row["sensitivity"]["fixed_inputs"]["mortality_method"] == method
