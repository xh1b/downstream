"""Traps for the V1 unit-level retrodiction scorecard.

Each trap names the defect it hunts:
- the bridge drifting from the transcribed ADH numbers
- a non-monotone or inverted band (low > point > high must hold)
- the miss being quietly flipped to a pass (the corrected five-phase
  method misses both comparisons; evidence and documented method
  corrections may change a verdict, never coefficient tuning for a pass)
- refusals swallowing the one scored outcome
"""

from __future__ import annotations

import pytest

from downstream.params import load_all
from downstream.validate import v1_retrodict

R = v1_retrodict(load_all()["params"])


def test_bridge_pinned_to_transcribed_table():
    b = R["bridge"]["displaced_per_100k"]
    assert (b["point"], b["low"], b["high"]) == (2520.0, 1740.0, 3300.0)


def test_bands_monotone():
    for s in R["scored"]:
        m = s["modeled_excess_deaths_per100k"]
        assert m["low"] <= m["point"] <= m["high"], f"inverted band in {s['variant']}"
        ci = s["measured_differential_per100k"]["ci95"]
        assert ci[0] < 4.27 < ci[1]


def test_male_variant_exceeds_all_adults():
    by = {s["variant"]: s for s in R["scored"]}
    assert by["all_male"]["modeled_excess_deaths_per100k"]["point"] > by["all_adults"]["modeled_excess_deaths_per100k"]["point"]


def test_current_honest_verdict_state():
    # Engine 0.3.0 aligns validation with the production five-phase
    # timing. Fixed evidence now misses both comparisons; retain that
    # result rather than tuning coefficients to restore the old verdict.
    all_adults = R["scored"][0]
    assert all_adults["mortality_contract"]["timing"] == "source_profile"
    assert all_adults["measured_inside_modeled_band"] is False
    assert all_adults["modeled_point_inside_measured_ci"] is False
    # the overshoot itself persists at the point level
    assert all_adults["modeled_excess_deaths_per100k"]["point"] > all_adults["measured_differential_per100k"]["point"]


def test_refusals_exclude_only_the_scored_outcomes():
    names = {r["outcome"] for r in R["refusals"]}
    assert "male_female_mort_diff_total" not in names
    assert "widowed_divorced_separated_pp" not in names
    assert len(names) == 10


def test_divorce_verdict_state():
    # non-circular stream (rege2007, not ADH): model undershoots the
    # measured stock change (~11-22% explained), measured CI covers the
    # model point. Pinned: flippable only by evidence.
    for w in R["scored_divorce"]["windows"]:
        assert w["measured_inside_modeled_band"] is False
        assert w["modeled_point_inside_measured_ci"] is True
    w10 = [w for w in R["scored_divorce"]["windows"] if w["window_years"] == 10.0][0]
    w5 = [w for w in R["scored_divorce"]["windows"] if w["window_years"] == 5.0][0]
    assert w10["modeled_pp_women"]["point"] == pytest.approx(2 * w5["modeled_pp_women"]["point"], abs=1e-3)
    for w in (w5, w10):
        m = w["modeled_pp_women"]
        assert m["low"] <= m["point"] <= m["high"]


def test_divorce_stream_cites_non_adh_sources():
    s = R["scored_divorce"]["stream"]
    assert "rege2007" in s and "census" in s


def test_retrodict_deterministic():
    assert v1_retrodict(load_all()["params"]) == R
