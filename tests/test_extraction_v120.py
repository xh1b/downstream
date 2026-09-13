"""v1.21 pins: the Stevens & Schaller 2011 grade-retention row (queue
#12, read via NBER w15480; Economics of Education Review 30(2) is the
version of record).

What this file hunts:
- the queue's original "math/reading effect sizes" target creeping
  back: the paper has NO test scores, and the row must say so — a
  future re-reader who 'upgrades' the row to SD units would be
  inventing an outcome the study never measured
- the base escaping the pin: the multiplier is 1 + coef/BASE with
  BASE = 0.055 named on the row; a silent base swap changes the point
- the current-year null (the paper's own identification) going
  undeclared, letting a cross-sectional reader miss the pre-trend
  argument
- the new node composing with child_achievement_sd (dahl2012) or the
  earnings-gap multiplier — PARALLEL stream, boundary-applied
- the venue correction regressing to the phantom Sociology of
  Education citation, or the bib evidence tier regressing below
  fulltext-table
"""
import pytest

from downstream.audit import ERROR, audit
from downstream.citations import parse_bib
from downstream.params import default_dir, load, load_all, load_nodes

PARAMS_DIR = default_dir()
PARAMS = load(PARAMS_DIR / "parameters.csv")
LINK = "displacement->grade_retention_hazard"


def test_row_matches_table4_col1_child_fe():
    p = PARAMS.by_link(LINK)
    # Table 4 col 1: +0.0081 (SE 0.0038) on the 0.055 sample average
    coef, se, base = 0.0081, 0.0038, 0.055
    assert p.point == pytest.approx(1 + coef / base, abs=1e-4)
    assert p.low == pytest.approx(1 + (coef - 1.96 * se) / base, abs=1e-4)
    assert p.high == pytest.approx(1 + (coef + 1.96 * se) / base, abs=1e-4)
    assert p.tier == "EXACT" and p.citation == "stevens2011"


def test_multiplier_band_state_pinned():
    # exact corners so a base or SE swap cannot pass unnoticed
    p = PARAMS.by_link(LINK)
    assert p.point == pytest.approx(1.1473, abs=1e-3)
    assert p.low == pytest.approx(1.0119, abs=1e-3)
    assert p.high == pytest.approx(1.2827, abs=1e-3)


def test_queue_target_correction_recorded_no_test_scores():
    p = PARAMS.by_link(LINK)
    assert "NO math/reading test scores" in p.notes
    assert "grade retention" in p.notes
    # the correction must be dated so it reads as a decision, not drift
    assert "v1.20" in p.notes


def test_timing_identification_declared():
    p = PARAMS.by_link(LINK)
    # current-year null 0.0032 (SE 0.0040) is the no-pre-trend argument
    assert "0.0032" in p.notes
    assert "current-year" in p.notes and "null" in p.notes


def test_heterogeneity_scope_declared():
    p = PARAMS.by_link(LINK)
    assert "HS education or less" in p.notes
    assert "conservative" in p.notes


def test_parallel_stream_never_composed_with_achievement_sd():
    p = PARAMS.by_link(LINK)
    assert "PARALLEL" in p.notes
    assert "child_achievement_sd" in p.notes
    assert "NEVER chained" in p.notes
    # and the node itself refuses the SD interpretation
    nodes = load_nodes(PARAMS_DIR / "nodes.csv")
    assert nodes["grade_retention_hazard"].unit == "rate_ratio"
    assert "NOT test-score SDs" in nodes["grade_retention_hazard"].description


def test_venue_corrected_and_not_the_phantom_citation():
    bib = parse_bib(PARAMS_DIR / "references.bib")
    e = bib["stevens2011"]
    assert e.fields["journal"] == "Economics of Education Review"
    assert e.fields["volume"] == "30" and e.fields["number"] == "2"
    assert e.fields["pages"] == "289--299"
    assert e.fields["doi"] == "10.1016/j.econedurev.2010.10.002"
    assert "Sociology of Education" not in e.fields.get("note", "") or "miscited" in e.fields.get("note", "")
    assert e.evidence == "fulltext-table"


def test_bib_has_no_duplicate_keys():
    # last-write-wins parsing made stale pre-upgrade copies a silent
    # downgrade trap (dahl2012/hilger2016/raphael2001 were shadowed)
    import re
    text = (PARAMS_DIR / "references.bib").read_text(encoding="utf-8")
    keys = [m.group(2).strip() for m in re.finditer(r"@(\w+)\{([^,]+),", text)]
    assert len(keys) == len(set(keys))


def test_hilger_cross_check_noted_values_unchanged():
    p = PARAMS.by_link("displacement->parental_income_shortrun")
    assert "STEVENS-SCHALLER 2011 CROSS-CHECK" in p.notes
    assert "-10.9%" in p.notes
    # the note appends; the anchor values must not move
    assert p.point == pytest.approx(0.8640, abs=1e-6)
    assert p.citation == "hilger2016"


def test_dag_wiring_valid():
    allp = load_all()
    assert "grade_retention_hazard" in allp["nodes"]
    # the link's endpoints resolve to real nodes
    p = PARAMS.by_link(LINK)
    assert p.from_node == "displacement_event"
    assert p.to_node == "grade_retention_hazard"


def test_version_bumped_and_audit_clean():
    assert (PARAMS_DIR / "VERSION").read_text().strip() == "v1.42"
    errors = [f for f in audit(PARAMS_DIR) if f.severity == ERROR]
    assert errors == []
