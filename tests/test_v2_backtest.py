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

import downstream.validate as validate_module
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


def _write_v2_inputs(directory, *, workers="100", low="50", high="150",
                     baseline="0.01", window="5", measured="0", se="1"):
    (directory / "nafta_exposure_bridge.csv").write_text(
        "quantity,point,low,high\n"
        f"displaced_workers,{workers},{low},{high}\n"
        f"window_years,{window},{window},{window}\n"
        f"baseline_mortality_per_person_year,{baseline},{baseline},{baseline}\n"
    )
    (directory / "nafta_measured_coefficients.csv").write_text(
        "outcome,point,se\n"
        f"excess_deaths_per100k,{measured},{se}\n"
    )


def test_version_is_v127():
    assert (PARAMS_DIR / "VERSION").read_text().strip() == "v1.34"


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


def test_v2_scores_synthetic_positive_count_bridge_with_ordered_corners(tmp_path, monkeypatch):
    """Positive count endpoints are valid; they must not invert after abs()."""
    monkeypatch.setattr(validate_module, "VALIDATION_DIR", tmp_path)
    _write_v2_inputs(tmp_path, measured="0", se="0")
    result = v2_backtest("nafta", PARAMS)
    assert result["status"] == "scored"
    row = result["scored"][0]
    assert row["modeled"]["low"] <= row["modeled"]["point"] <= row["modeled"]["high"]
    assert row["measured"]["ci95"] == [0.0, 0.0]


@pytest.mark.parametrize(
    ("bridge_kwargs", "expected"),
    [
        ({"baseline": ""}, "baseline_mortality_per_person_year"),
        ({"baseline": "1.1"}, "invalid baseline_mortality_per_person_year"),
        ({"window": "-1"}, "negative window_years"),
    ],
)
def test_v2_refuses_malformed_bridge_inputs(tmp_path, monkeypatch, bridge_kwargs, expected):
    monkeypatch.setattr(validate_module, "VALIDATION_DIR", tmp_path)
    _write_v2_inputs(tmp_path, **bridge_kwargs)
    result = v2_backtest("nafta", PARAMS)
    assert result["status"].startswith("blocked:")
    assert expected in result["status"]
    assert result["scored"] == []


@pytest.mark.parametrize("measured,se", [("not-a-number", "1"), ("1", "-0.1"), ("nan", "1")])
def test_v2_refuses_malformed_measured_outcomes(tmp_path, monkeypatch, measured, se):
    monkeypatch.setattr(validate_module, "VALIDATION_DIR", tmp_path)
    _write_v2_inputs(tmp_path, measured=measured, se=se)
    result = v2_backtest("nafta", PARAMS)
    assert result["status"] == "blocked: malformed measured outcome"
    assert result["scored"] == []
