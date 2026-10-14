"""Contracts for a combined explanation without combined causal effects."""

from dataclasses import replace
import json
import math

import pytest

from downstream.child_gap_view import CHILD_DOLLARS, child_gap_view, housing_chain_requirements
from downstream.children import CHILD_DIRECT, child_line
from downstream.params import default_dir, load_all
from downstream.place import load_places, modifier_parameter
from downstream.scenario import ScenarioInput, compute_counts


@pytest.fixture(scope="module")
def bundle():
    return load_all()


def view(bundle, scenario=None, **kwargs):
    return child_gap_view(bundle["params"], bundle["baselines"], scenario or ScenarioInput(10), **kwargs)


def test_default_retains_existing_engine_values_and_source_steps(bundle):
    report = view(bundle)
    line = child_line(bundle["params"])
    assert report["composition"] == "side_by_side_only"
    assert report["combined_total"] is None
    assert report["uncertainty"]["band_kind"] == "parameter-support envelope, not a confidence interval"
    for row in report["rows"]:
        ledger = line[row["generation"]]
        assert row["value"]["point"] == pytest.approx(100 * (1 - ledger.point))
        assert row["value"]["low"] == pytest.approx(100 * (1 - ledger.high))
        assert row["value"]["high"] == pytest.approx(100 * (1 - ledger.low))
        assert row["steps"] == [step.as_dict() for step in ledger.steps]
        assert all(step["citation"] and step["population_scope"] for step in row["steps"])
        assert not row["eligible_for_public_headline"]
    assert [row["evidence_status"] for row in report["rows"]] == [
        "direct_estimate", "structural_projection", "structural_projection",
    ]
    counts = compute_counts(bundle["params"], bundle["baselines"], ScenarioInput(10))
    assert report["rows"][0]["dollar_conversion"] == counts["modeled"][CHILD_DOLLARS]
    assert report["input_content_sha256"] == counts["input_content_sha256"]
    assert all(row["dollar_conversion"] is None for row in report["rows"][1:])
    json.dumps(report, allow_nan=False)


def test_missing_dollar_baseline_keeps_relative_gaps_and_reports_refusal(bundle):
    baselines = {key: value for key, value in bundle["baselines"].items() if key != "median_male_lifetime_earnings"}
    report = child_gap_view(bundle["params"], baselines, ScenarioInput(10))
    assert all(row["available"] for row in report["rows"])
    assert report["rows"][0]["dollar_conversion"] is None
    assert "baseline" in report["rows"][0]["dollar_conversion_reason"]


@pytest.mark.parametrize("profile", [
    {"age_at_displacement": 20, "sex": "Male"},
    {"age_at_displacement": 12, "sex": "Female"},
])
def test_known_incompatible_child_withholds_entire_transmission(bundle, profile):
    report = view(bundle, ScenarioInput(10, n_children=1, child_profiles=[profile]))
    assert report["child_applicability"]["status"] == "incompatible"
    for row in report["rows"]:
        assert not row["available"]
        assert row["value"] is None
        assert row["earnings_multiplier"] is None
        assert row["dollar_conversion"] is None
        assert row["reason"]


def test_unknown_child_keeps_illustrative_reference(bundle):
    report = view(bundle, ScenarioInput(10, n_children=1, child_profiles=[
        {"age_at_displacement": None, "sex": "Unknown"},
    ]))
    assert report["child_applicability"]["status"] == "unknown"
    assert all(row["available"] and not row["eligible_for_public_headline"] for row in report["rows"])


def test_income_quartile_preserves_benefit_point_and_null_crossing(bundle):
    report = view(bundle, ScenarioInput(10, child_income_quartile=3,
        income_rank_definition="source distribution; illustrative transport"))
    for row in report["rows"]:
        assert row["value"]["point"] < 0
        assert row["value"]["low"] < 0 < row["value"]["high"]
        assert "oreopoulos2008" in row["steps"][0]["citation"]
    assert report["rows"][0]["earnings_multiplier"]["point"] == pytest.approx(math.exp(.007))
    assert report["rows"][0]["dollar_conversion"]["point"] < 0


def test_null_is_preserved_at_every_generation(bundle):
    params = replace(bundle["params"], parameters=tuple(
        replace(p, point=1., low=1., high=1.) if p.link == CHILD_DIRECT else p
        for p in bundle["params"].parameters
    ))
    report = child_gap_view(params, bundle["baselines"], ScenarioInput(10))
    assert all(row["value"] == {"point": 0., "low": 0., "high": 0.} for row in report["rows"])


@pytest.mark.parametrize("application", ["initial_only", "legacy_repeated"])
def test_place_context_matches_existing_ledger_and_is_exploratory(bundle, application):
    places = load_places(default_dir() / "places.csv")
    modifier = modifier_parameter(bundle["params"], places, "42101")["parameter"]
    line = child_line(bundle["params"], modifier, application)
    report = view(bundle, ScenarioInput(10, place_application=application), places=places, place_key="42101")
    assert report["place"]["modifier_applied"]
    assert report["place_application"] == application
    for row in report["rows"]:
        assert row["earnings_multiplier"]["point"] == line[row["generation"]].point
        assert "exploratory_place" in row["evidence_status"]
        assert not row["eligible_for_public_headline"]
    with pytest.raises(KeyError):
        view(bundle, places=places, place_key="unknown")


def target(**changes):
    return {"sex": "Male", "age": "45-54 years", "worker_tenure": "high-tenure",
            "geography": "Canada", "calendar_window": "1980-1982",
            "exposure_type": "firm closure", "children_sex": "Male", **changes}


def test_reviewed_child_transport_never_promotes_descendants(bundle):
    scenario = ScenarioInput(10, n_children=1,
        child_profiles=[{"age_at_displacement": 12, "sex": "Male"}],
        income_rank_definition="source-compatible mapping", target_population=target(),
        applicability_decisions={CHILD_DOLLARS: {"status": "reviewed", "reviewer": "test",
            "rationale": "test reviewed transport", "citations": "oreopoulos2008"}})
    report = view(bundle, scenario)
    assert report["rows"][0]["eligible_for_public_headline"]
    assert not any(row["eligible_for_public_headline"] for row in report["rows"][1:])


def test_incompatible_target_stays_blocked_even_without_dollar_baseline(bundle):
    baselines = {key: value for key, value in bundle["baselines"].items() if key != "median_male_lifetime_earnings"}
    report = child_gap_view(bundle["params"], baselines, ScenarioInput(10,
        target_population=target(children_sex="Female")))
    assert not any(row["available"] for row in report["rows"])


def test_zero_exposure_never_invents_descendant_population(bundle):
    report = view(bundle, ScenarioInput(0, n_children=0))
    assert report["rows"][0]["dollar_conversion"]["point"] == 0
    assert report["rows"][0]["value"]["point"] > 0  # per-person reference, not aggregate
    assert all(row["dollar_conversion"] is None for row in report["rows"][1:])


def test_housing_is_unavailable_even_with_boundary_coefficient(bundle):
    housing = view(bundle)["housing_chain"]
    assert not housing["available"]
    assert housing["total"] is None
    assert housing["source_row"]["citation"] == "campbell2011"
    assert housing["source_row"]["evidence_role"] == "boundary"
    assert len(housing["requirements"]) == 4
    params = replace(bundle["params"], parameters=tuple(
        p for p in bundle["params"].parameters if p.link != "foreclosure_order->house_price_gap"
    ))
    assert housing_chain_requirements(params)["source_row"] is None


def test_custom_missing_subgroup_library_never_falls_back(bundle, tmp_path):
    with pytest.raises(FileNotFoundError):
        view(bundle, ScenarioInput(10, child_income_quartile=3,
            income_rank_definition="source-compatible mapping"), params_dir=tmp_path)
