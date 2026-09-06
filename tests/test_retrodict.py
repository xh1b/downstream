"""Traps for the V1 unit-level retrodiction scorecard.

Each trap names the defect it hunts:
- the bridge drifting from the transcribed ADH numbers
- a non-monotone or inverted band (low > point > high must hold)
- the miss being quietly flipped to a pass (the current honest state
  is: measured point OUTSIDE the modeled band, model point INSIDE
  the measured CI — if that ever changes it must be because the
  EVIDENCE changed, not the code)
- refusals swallowing the one scored outcome
"""

from __future__ import annotations

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
    # the miss publishes: measured point outside the modeled band,
    # model point inside the measured CI. If a change flips this, the
    # change must come with new evidence (a pinned parameter or a new
    # transcribed table), never from touching the verdict logic.
    all_adults = R["scored"][0]
    assert all_adults["measured_inside_modeled_band"] is False
    assert all_adults["modeled_point_inside_measured_ci"] is True


def test_refusals_exclude_only_the_scored_outcome():
    names = {r["outcome"] for r in R["refusals"]}
    assert "male_female_mort_diff_total" not in names
    assert len(names) == 10


def test_retrodict_deterministic():
    assert v1_retrodict(load_all()["params"]) == R
