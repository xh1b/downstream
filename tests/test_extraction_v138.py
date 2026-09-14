"""v1.39 pins: Browning & Heinesen 2012 + Marcus 2013 full-text extractions.

What this file pins:
- three EXACT boundary-applied cause-specific mortality rows from
  Browning & Heinesen 2012 (JHE 31(4):599-616, read from the published
  version of record): circulatory, alcohol-related, external-cause
  cumulative hazard ratios, years 1-4 after base year
- the all-cause replication cross-checks on the SvW peak/sustained rows
- marcus2013 spouse mental-health spillover (new node spouse_mental_health_sd)
  and the own-effect cross-check recorded on paul2009
- cancer NULL discipline: no cancer row may exist
"""
from pathlib import Path

import pytest

from downstream.audit import audit, summary
from downstream.params import default_dir, load

PARAMS_DIR = default_dir()
PARAMS = load(PARAMS_DIR / "parameters.csv")


def test_circulatory_row_pinned():
    row = PARAMS.by_link("displacement->circulatory_mortality_hazard")
    assert (row.point, row.low, row.high) == (1.54, 1.29, 1.83)
    assert row.tier == "EXACT"
    assert "MI-or-stroke 1-4y 1.58" in row.notes
    assert "NEVER chained" in row.notes


def test_alcohol_row_pinned():
    row = PARAMS.by_link("displacement->alcohol_mortality_hazard")
    assert (row.point, row.low, row.high) == (1.62, 1.09, 2.41)
    assert "deaths-of-despair" in row.notes
    assert "1-20y 1.15 [0.96, 1.38] n.s." in row.notes


def test_external_cause_row_pinned_with_cancer_null_discipline():
    row = PARAMS.by_link("displacement->external_cause_mortality_hazard")
    assert (row.point, row.low, row.high) == (1.53, 1.15, 2.04)
    assert "4.31 [1.64, 11.37]" in row.notes
    assert "Cancer NULL" in row.notes
    rows = [p.link for p in PARAMS.parameters if "cancer" in p.link]
    assert rows == []  # the null never becomes a row


def test_svW_replication_cross_checks_recorded():
    peak = PARAMS.by_link("earnings_shock->mortality_peak")
    assert "1.84 [1.44, 2.34]" in peak.notes
    sustained = PARAMS.by_link("earnings_shock->mortality_sustained")
    assert "1.10 [1.05, 1.16]" in sustained.notes
    assert "near-exact long-run replication" in sustained.notes
    # the SvW anchors themselves are untouched
    assert peak.point == 2.6696 and sustained.point == 1.135


def test_marcus_spouse_row_pinned():
    row = PARAMS.by_link("displacement_event->spouse_mental_health_sd")
    assert (row.point, row.low, row.high) == (-0.194, -0.327, -0.061)
    assert row.tier == "EXACT"
    assert "-1.94" in row.notes and "placebo" in row.notes.lower()
    paul = PARAMS.by_link("unemployment_status->mental_health_sd")
    assert "marcus2013 CROSS-CHECK" in paul.notes
    assert paul.point == 0.51  # the meta anchor is untouched


def test_audit_clean_and_version_current():
    s = summary(audit(PARAMS_DIR))
    assert s["pass"], [f.as_dict() for f in audit(PARAMS_DIR) if f.severity.value == "error"]
    assert PARAMS.version == "v1.46"
