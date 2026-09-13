import csv

import pytest

from downstream.admission import compare_synthesis_to_parameter
from downstream.params import load_all
from downstream.synthesis import StudyEstimate, load_study_estimates, random_effects, synthesize


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


_FIELDS = ["link", "study_id", "point", "standard_error", "scale",
           "population_scope", "design", "time_horizon", "citation"]


def _study_row(**overrides):
    row = {"link": "a->b", "study_id": "s1", "point": "0.10", "standard_error": "0.02",
           "scale": "log_odds_ratio", "population_scope": "US adults", "design": "IV",
           "time_horizon": "year 6+", "citation": "source2026"}
    row.update(overrides)
    return row


@pytest.mark.parametrize("blank_field",
                         ["population_scope", "design", "time_horizon"])
def test_loader_refuses_blank_compatibility_metadata(tmp_path, blank_field):
    path = tmp_path / "studies.csv"
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=_FIELDS)
        writer.writeheader()
        writer.writerow(_study_row(**{blank_field: "  "}))
    with pytest.raises(ValueError, match="blank compatibility metadata"):
        load_study_estimates(path)


@pytest.mark.parametrize("blank_field",
                         ["population_scope", "design", "time_horizon"])
def test_pooling_refuses_programmatic_rows_with_blank_compatibility(blank_field):
    # Two blank fields would satisfy the identical-population/horizon
    # equality check and pool silently; the pooling path must refuse them.
    first, second = _rows()
    blanked = StudyEstimate(
        first.link, first.study_id, first.point, first.standard_error, first.scale,
        **{**{n: getattr(first, n) for n in ("population_scope", "design", "time_horizon")},
           blank_field: ""},
    )
    kept = StudyEstimate(
        second.link, second.study_id, second.point, second.standard_error, second.scale,
        **{n: getattr(second, n) for n in ("population_scope", "design", "time_horizon")},
    )
    with pytest.raises(ValueError, match="blank compatibility metadata"):
        random_effects([blanked, kept])
