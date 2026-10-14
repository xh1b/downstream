"""Persistence disagreements must change assumptions, not silently replace evidence."""
from dataclasses import replace
import json
import math

import pytest

from downstream.cli import main
from downstream.employer import DocumentedExposure, compute_entity_counts
from downstream.mortality_profiles import load_profiles
from downstream.params import default_dir, load_all
from downstream.scenario import ScenarioInput, compute_counts, sample_counts


@pytest.fixture
def parts():
    return load_all()


def _mortality(parts, scenario=None, **kwargs):
    return compute_counts(parts["params"], parts["baselines"],
                          scenario or ScenarioInput(1000), **kwargs)["modeled"]["excess_deaths"]


def _fixed_odds(params, *, early=1.0, late=1.0):
    rows = []
    for p in params.parameters:
        if p.link.startswith("earnings_shock->mortality_"):
            value = late if p.link.endswith("sustained") else early
            p = replace(p, point=value, low=value, high=value)
        rows.append(p)
    return replace(params, parameters=tuple(rows))


def test_default_source_is_preserved_and_alternative_is_explicit(parts):
    original = parts["params"]
    mortality = _mortality(parts)
    report = mortality["persistence_sensitivity"]
    source = report["variants"]["source_profile"]
    alternate = report["variants"]["no_sustained_excess"]
    assert mortality["point"] == source["point"] == 28.76
    assert alternate["point"] == 20.52
    assert report["source_minus_no_sustained_point"] == 8.24
    assert all(source[k] == mortality[k] for k in ("point", "low", "high"))
    assert source["citations"] == ["sullivan2009"]
    assert alternate["evidence_status"] == "structural_assumption"
    assert alternate["motivating_citations"] == ["eliasonstorrie2009"]
    assert alternate["first_changed_follow_up_year"] == 7
    assert not report["eligible_for_public_headline"]
    assert not mortality["applicability"]["eligible_for_public_headline"]
    assert parts["params"] is original
    assert original.by_link("earnings_shock->mortality_sustained").point == 1.1354
    assert "not a confidence interval" in report["structural_point_range"]["interpretation"]
    assert any("does not establish" in note for note in report["limitations"])
    assert any("does not reproduce" in note for note in report["limitations"])


@pytest.mark.parametrize("years", [0, .5, 1, 2, 4, 5.75, 6])
def test_no_effect_of_persistence_assumption_before_offset_six(parts, years):
    report = _mortality(parts, ScenarioInput(1000, exposure_years=years),
                        _raw=True)["persistence_sensitivity"]
    source, alternate = report["variants"].values()
    assert [source[k] for k in ("point", "low", "high")] == [
        alternate[k] for k in ("point", "low", "high")]
    assert report["source_minus_no_sustained_point"] == 0


def test_late_only_effect_matches_analytic_survival_at_fractional_boundary(parts):
    parts["params"] = _fixed_odds(parts["params"], late=2)
    mortality = _mortality(parts, ScenarioInput(1000, exposure_years=6.5), _raw=True)
    report = mortality["persistence_sensitivity"]
    b = 1 - math.exp(-.004944)
    exposed_risk = 2 * b / (1 + b)
    expected = 1000 * (1 - b)**6 * ((1 - b)**.5 - (1 - exposed_risk)**.5)
    assert mortality["point"] == pytest.approx(expected)
    assert report["variants"]["no_sustained_excess"]["point"] == pytest.approx(0)
    assert report["source_minus_no_sustained_point"] == pytest.approx(expected)


def test_protective_persistence_is_retained_not_clamped_or_called_a_lower_bound(parts):
    parts["params"] = _fixed_odds(parts["params"], late=.5)
    report = _mortality(parts)["persistence_sensitivity"]
    assert report["variants"]["source_profile"]["point"] < 0
    assert report["variants"]["no_sustained_excess"]["point"] == 0
    assert report["source_minus_no_sustained_point"] < 0
    assert report["structural_point_range"]["high"] == 0


@pytest.mark.parametrize("workers", [0, .125, 1, 1000])
def test_null_profile_has_zero_contrast_at_every_exposure(parts, workers):
    parts["params"] = _fixed_odds(parts["params"])
    report = _mortality(parts, ScenarioInput(workers))["persistence_sensitivity"]
    assert report["structural_point_range"]["low"] == 0
    assert report["structural_point_range"]["high"] == 0


def test_probability_baseline_is_not_converted_as_a_rate_again(parts):
    parts["params"] = _fixed_odds(parts["params"], early=2, late=3)
    key = "all_cause_mortality_annual"
    parts["baselines"][key] = replace(parts["baselines"][key], value=.1,
                                      unit="prob_per_person_year")
    report = _mortality(parts, _raw=True)["persistence_sensitivity"]
    early_risk = .2 / 1.1
    expected = 1000 * (.9**20 - (1 - early_risk)**6 * .9**14)
    assert report["variants"]["no_sustained_excess"]["point"] == pytest.approx(expected)


def test_profile_mixture_aggregates_survivals_instead_of_averaging_hazards(parts):
    profiles = load_profiles(default_dir() / "mortality_profiles.csv")
    reference = profiles["male_45_54_2015_2019"]
    profiles = {"low": replace(reference, profile_id="low", annual_rate=.001),
                "high": replace(reference, profile_id="high", annual_rate=.02)}
    scenario = ScenarioInput(1000, mortality_mix={"low": .3, "high": .7})
    row = _mortality(parts, scenario, mortality_profiles=profiles, _raw=True)
    actual = row["persistence_sensitivity"]["variants"]["no_sustained_excess"]["point"]
    strata = [_mortality(parts, ScenarioInput(1000, mortality_profile=key),
                        mortality_profiles=profiles, _raw=True)
              ["persistence_sensitivity"]["variants"]["no_sustained_excess"]["point"]
              for key in ("low", "high")]
    assert actual == pytest.approx(.3 * strata[0] + .7 * strata[1])
    profiles["average"] = replace(reference, profile_id="average", annual_rate=.0143)
    average = _mortality(parts, ScenarioInput(1000, mortality_profile="average"),
                         mortality_profiles=profiles, _raw=True)
    assert actual != pytest.approx(average["persistence_sensitivity"]
                                  ["variants"]["no_sustained_excess"]["point"])


def test_sampler_uses_paired_draws_and_keeps_uncertainty_layers_separate(parts):
    # With late OR fixed at one, the two structures are identical even
    # while early-phase parameter uncertainty remains. Independent draws
    # or subtraction of quantile endpoints would manufacture a nonzero band.
    late = parts["params"].by_link("earnings_shock->mortality_sustained")
    params = replace(parts["params"], parameters=tuple(
        replace(p, point=1, low=1, high=1) if p == late else p
        for p in parts["params"].parameters))
    result = sample_counts(params, parts["baselines"], ScenarioInput(1000),
                           draws=64, nodes=parts["nodes"])
    row = result["modeled"]["excess_deaths"]
    report = row["persistence_sensitivity"]
    left, right = report["variants"].values()
    assert left["parameter_interval_90"] == right["parameter_interval_90"] == row["parameter_interval_90"]
    assert left["parameter_interval_90"]["p05"] < left["parameter_interval_90"]["p95"]
    assert set(report["source_minus_no_sustained_parameter_interval_90"].values()) == {0}
    assert set(result["parameter_uncertainty"]["outcomes"]) == set(result["modeled"])
    assert "structural uncertainty" in result["parameter_uncertainty"]["excluded"]
    assert "same parameter draw" in report["sampling"]["comparison"]
    assert result["predictive_uncertainty"]["available"]


def test_sampled_report_is_reproducible_and_source_interval_is_preserved(parts):
    def evaluate():
        return sample_counts(parts["params"], parts["baselines"], ScenarioInput(1000),
                             draws=64, seed=13, nodes=parts["nodes"])
    first = evaluate()
    assert first == evaluate()
    row = first["modeled"]["excess_deaths"]
    report = row["persistence_sensitivity"]
    assert report["variants"]["source_profile"]["parameter_interval_90"] == row["parameter_interval_90"]
    alt = report["variants"]["no_sustained_excess"]
    assert alt["low"] <= alt["parameter_interval_90"]["p05"] <= alt["parameter_interval_90"]["p95"] <= alt["high"]


@pytest.mark.parametrize("options", [{"mortality_method": "legacy_additive"},
                                     {"mortality_timing": "source_aligned"},
                                     {"mortality_timing": "immediate_sustained"}])
def test_legacy_methods_do_not_claim_the_source_profile_comparison(parts, options):
    report = _mortality(parts, ScenarioInput(1000, **options))["persistence_sensitivity"]
    assert not report["available"]
    sampled = sample_counts(parts["params"], parts["baselines"],
                             ScenarioInput(1000, **options), draws=2)
    assert set(sampled["parameter_uncertainty"]["outcomes"]) == set(sampled["modeled"])


def test_missing_baseline_and_incompatible_cohort_cannot_gain_a_sensitivity(parts):
    baselines = dict(parts["baselines"])
    baselines.pop("all_cause_mortality_annual")
    out = sample_counts(parts["params"], baselines, ScenarioInput(1000), draws=2)
    assert "excess_deaths" not in out["modeled"]
    target = dict(sex="Female", age="45-54 years", worker_tenure="high-tenure",
                  geography="US", calendar_window="2026", exposure_type="mass layoff",
                  children_sex="Female")
    out = sample_counts(parts["params"], parts["baselines"],
                        ScenarioInput(1000, target_population=target), draws=2)
    assert "excess_deaths" not in out["modeled"]
    assert any(row["outcome"] == "excess_deaths" for row in out["blocked"])
    profiles = load_profiles(default_dir() / "mortality_profiles.csv")
    with pytest.raises(ValueError, match="applies only"):
        _mortality(parts, ScenarioInput(1000, mortality_profile="female_45_54_2015_2019"),
                   mortality_profiles=profiles)


def test_entity_and_cli_publish_the_comparison(parts, capsys):
    exposure = DocumentedExposure("fixture", "employer", 1000, "fixture", "fixture")
    result = compute_entity_counts(parts["params"], parts["baselines"], exposure)
    assert result["modeled"]["excess_deaths"]["persistence_sensitivity"]["available"]
    assert main(["scenario", "--workers", "1000", "--draws", "2"]) == 0
    cli = json.loads(capsys.readouterr().out)
    from downstream import __version__
    assert cli["engine_version"] == __version__
    assert cli["modeled"]["excess_deaths"]["persistence_sensitivity"]["sampling"]["draws"] == 2


def test_methods_companion_exposes_the_same_comparison():
    import importlib.util

    path = default_dir().parent / "scripts" / "build_methods_html.py"
    spec = importlib.util.spec_from_file_location("persistence_methods_builder", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    document = module.build()
    assert '<section id="persistence">' in document
    assert 'href="#source-eliasonstorrie2009"' in document
    assert "source profile gives 28.76" in document
    assert "alternative gives 20.52" in document
    assert "not a confidence interval or a bound on the true effect" in document
    assert "nonsignificant estimate does not establish" in document
