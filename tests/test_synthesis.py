import pytest

from downstream.admission import compare_synthesis_to_parameter
from downstream.params import load_all
from downstream.synthesis import StudyEstimate, random_effects, synthesize


def _rows():
    return [
        StudyEstimate("a->b", "s1", .10, .02, "log_odds_ratio", "US", "IV", "year 6+"),
        StudyEstimate("a->b", "s2", .20, .03, "log_odds_ratio", "US", "DiD", "year 6+"),
    ]


def test_random_effects_reports_heterogeneity_and_prediction_not_transport():
    out = random_effects(_rows())
    assert out["studies"] == 2
    assert out["random_effects"]["ci95"][0] < out["random_effects"]["mean"]
    assert "not a transported" in out["transport_note"]
    hk = out["random_effects"]["hartung_knapp_sensitivity"]
    assert hk["degrees_of_freedom"] == 1
    assert hk["critical_value"] == pytest.approx(12.706)


def test_synthesis_blocks_singletons_and_mixed_scales():
    singleton = StudyEstimate("c->d", "s3", .1, .02, "risk_difference", "US", "DiD", "one year")
    out = synthesize(tuple(_rows() + [singleton]))
    assert len(out["reports"]) == 1
    assert out["blocked"][0]["link"] == "c->d"
    with pytest.raises(ValueError, match="identical estimand scale"):
        random_effects(_rows() + [singleton])


def test_ratio_synthesis_comparison_is_read_only_manual_review():
    parts = load_all()
    report = random_effects([
        StudyEstimate("earnings_shock->mortality_sustained", "a", .10, .03,
                      "log_odds_ratio", "US", "design", "year 6+", "sourcea"),
        StudyEstimate("earnings_shock->mortality_sustained", "b", .14, .03,
                      "log_odds_ratio", "US", "design", "year 6+", "sourceb"),
    ])
    out = compare_synthesis_to_parameter(parts["params"], report, parts["nodes"])
    assert out["automatic_admission"] is False
    assert out["compatible_scale"] is True
    assert out["review_status"].startswith("manual")
    assert not out["metadata_complete"]
    assert out["admission_blockers"]


def test_complete_synthesis_metadata_removes_metadata_blocker_not_manual_review():
    parts = load_all()
    report = random_effects([
        StudyEstimate("earnings_shock->mortality_sustained", "a", .10, .03, "log_odds_ratio", "US", "design", "year 6+", "sourcea",
                      treatment="mass layoff", comparison="unexposed", outcome_definition="all-cause mortality", overlap_group="a"),
        StudyEstimate("earnings_shock->mortality_sustained", "b", .14, .03, "log_odds_ratio", "US", "design", "year 6+", "sourceb",
                      treatment="mass layoff", comparison="unexposed", outcome_definition="all-cause mortality", overlap_group="b"),
    ])
    out = compare_synthesis_to_parameter(parts["params"], report, parts["nodes"])
    assert out["metadata_complete"]
    assert out["admission_blockers"] == []
    assert out["automatic_admission"] is False
