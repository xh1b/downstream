"""v1.27 pins: V2 out-of-sample back-test framework (pre-registered).

What this file hunts:
- the pre-registration drifting AFTER data lands: the event ids, the
  scored streams, and the scoring rule are frozen in code at v1.27;
  a change to outcome definitions after a bridge arrives is the
  multiple-comparisons failure the clinical-trials rule exists to
  prevent
- a scorer fabricating exposure or a measured side: before both data
  files exist, the back-test must report `blocked` naming the missing
  sources — never invented numbers
- an unknown event id scoring silently instead of failing loudly
- the blocked dict omitting what the data plugs need, so no one can
  act on it
- the registry claiming a real scoring run while still blocked
"""
import pytest

from downstream.params import default_dir, load
from downstream.validate import (
    V2_EVENT_IDS,
    V2_SCORED_STREAMS,
    run,
    v2_backtest,
    v2_events,
)

PARAMS_DIR = default_dir()
PARAMS = load(PARAMS_DIR / "parameters.csv")


def test_version_is_v127():
    assert (PARAMS_DIR / "VERSION").read_text().strip() == "v1.32"


def test_registry_has_exactly_the_three_events():
    assert V2_EVENT_IDS == ("nafta", "auto_crisis", "brac")


def test_scored_streams_pre_registered():
    assert [s["outcome"] for s in V2_SCORED_STREAMS] == [
        "excess_deaths_per100k",
        "additional_divorces_per100k_women",
        "local_service_jobs_per_displaced",
    ]
    # every stream names its links: the definitions are in code, not prose
    mort = next(s for s in V2_SCORED_STREAMS if s["outcome"] == "excess_deaths_per100k")
    assert mort["links"] == [
        "earnings_shock->mortality_sustained",
        "earnings_shock->mortality_peak",
    ]


def test_scoring_rule_is_coverage_with_no_tuning():
    reg = v2_events(PARAMS)
    assert "no parameter tuning" in reg["scoring_rule"].lower()
    assert "Misses publish" in reg["scoring_rule"]
    assert "SAME frozen parameter set" in reg["scoring_rule"]


def test_pre_registration_declares_the_freeze_version():
    reg = v2_events(PARAMS)
    assert PARAMS.version in reg["pre_registered"]
    assert "BEFORE any event data lands" in reg["pre_registered"]


def test_every_event_records_its_blocker_and_sources():
    for e in v2_events(PARAMS)["events"]:
        assert e["status"].startswith("blocked:"), e["id"]
        assert e["exposure_bridge"]["file"].startswith("validation/")
        assert e["measured_outcomes"]["file"].startswith("validation/")
        # the block must name WHAT is missing and WHERE it would come from
        assert e["exposure_bridge"]["needs"]
        assert "sources" in e["exposure_bridge"]


def test_brac_records_the_scanned_wp_and_the_open_cross_checks():
    brac = next(e for e in v2_events(PARAMS)["events"] if e["id"] == "brac")
    srcs = " ".join(brac["measured_outcomes"]["sources"])
    assert "w6941" in srcs and "OCR" in srcs
    assert "MR-667" in srcs


def test_unknown_event_raises():
    with pytest.raises(KeyError):
        v2_backtest("chernobyl", PARAMS)


def test_blocked_scoring_names_the_missing_plugs():
    b = v2_backtest("brac", PARAMS)
    assert b["status"] == "blocked"
    assert b["reason"] == "data plugs pending; scoring is registered but NOT run"
    assert len(b["missing"]) == 2
    assert all(m.endswith(")") for m in b["missing"])
    assert "No fabricated exposure" in b["honesty"]


def test_blocked_scoring_does_not_fabricate_a_scorecard():
    b = v2_backtest("nafta", PARAMS)
    assert b["status"] == "blocked"
    assert "scored" not in b


def test_run_includes_v2_with_all_events_blocked():
    out = run(PARAMS)
    v2 = out["v2_backtest"]
    assert set(v2["events"]) == {"nafta", "auto_crisis", "brac"}
    assert all(r["status"] == "blocked" for r in v2["events"].values())
    assert v2["registry"]["pre_registered"]
