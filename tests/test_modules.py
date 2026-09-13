"""Module-level checks: worker, children, family, community streams."""

from pathlib import Path

import pytest

from downstream.children import child_line
from downstream.community import SchoolExposure, service_jobs_lost, school_spending_child_earnings, youth_crime_delta
from downstream.family import daughter_violence_odds, divorce_hazard, family_size_penalty
from downstream.params import load
from downstream.worker import worker_outcomes

PARAMS = Path(__file__).resolve().parent.parent / "params" / "parameters.csv"


def test_worker_stream_jls_band_and_split_mortality():
    w = worker_outcomes(load(PARAMS))
    e = w["worker_earnings"]
    assert (e.point, e.low, e.high) == (0.80, 0.75, 0.85)
    # sustained vs peak are SEPARATE outcomes, never conflated into one row
    assert w["mortality_sustained"].point == 1.135
    assert w["mortality_peak"].point == 2.6696


def test_worker_pinned_multiplier_scales_band_not_point():
    w = worker_outcomes(load(PARAMS), wage_multiplier=0.70)
    e = w["worker_earnings"]
    assert e.point == 0.70
    assert e.low < 0.70 < e.high  # band keeps relative spread


def test_child_line_gap_space_and_weakest_layer_flagged():
    line = child_line(load(PARAMS))
    assert line["child"].point == 0.9076
    assert line["grandchild"].point == pytest.approx(0.94918, abs=1e-6)
    assert line["greatgrandchild"].point == pytest.approx(0.972049, abs=1e-6)
    assert line["weakest_identified"] == "greatgrandchild"
    assert "weakest" in line["honesty"]
    assert line["evidence_status"]["child"]["eligible_for_validated_direct_contrast"]
    assert not line["evidence_status"]["grandchild"]["eligible_for_validated_direct_contrast"]


def test_divorce_parameter_is_the_corrected_dp514_value():
    led = divorce_hazard(load(PARAMS))
    assert led.point == 1.11  # +11% — verified against DP514 abstract
    assert 1.05 <= led.point <= 1.25


def test_family_size_penalty_compounds_per_additional_child():
    led = family_size_penalty(load(PARAMS), n_children=3)
    assert led.point == pytest.approx(0.98**2, abs=1e-9)
    assert led.low == pytest.approx(0.95**2, abs=1e-9)
    with pytest.raises(ValueError):
        family_size_penalty(load(PARAMS), n_children=0)


def test_daughter_odds_reports_structurally_blocked_upstream():
    led = daughter_violence_odds(load(PARAMS))
    assert led.point == 2.5
    # upstream household_ipv has NO producer — scenario treats it blocked


def test_moretti_jobs_are_a_level_ratio_not_a_multiplier():
    # One declared class at a time: the row's 1.6-5.0 span crosses job
    # classes (manufacturing vs high-tech), it is not a band around one
    # estimand, so each class returns its own published constant.
    jobs = service_jobs_lost(load(PARAMS), net_tradable_jobs_lost=100, job_mix="high_tech")
    assert jobs["point"] == 500
    assert jobs["job_class"] == "high_tech"
    assert jobs["unit"] == "jobs"
    manufacturing = service_jobs_lost(load(PARAMS), net_tradable_jobs_lost=100, job_mix="manufacturing")
    assert manufacturing["point"] == 160  # 1.6 jobs/job for manufacturing


def test_school_spending_normalizes_intensity_and_duration():
    led = school_spending_child_earnings(load(PARAMS), SchoolExposure(spend_pct=10, exposure_years=12))
    assert led.point == pytest.approx(1.07, abs=1e-9)  # the literature case
    half = school_spending_child_earnings(load(PARAMS), SchoolExposure(spend_pct=10, exposure_years=6))
    assert half.point == pytest.approx(1.035, abs=1e-9)
    cut = school_spending_child_earnings(load(PARAMS), SchoolExposure(spend_pct=-10, exposure_years=12))
    assert cut.point == pytest.approx(0.93, abs=1e-9)


def test_youth_crime_elasticity_applies_in_sign():
    led = youth_crime_delta(load(PARAMS), wage_pct_delta=-10.0)
    assert led.point == pytest.approx(10.0)  # -1.0 * -10% = +10% crime
    assert led.low == pytest.approx(5.0)     # -0.5 x -10
    assert led.high == pytest.approx(15.0)   # -1.5 x -10
