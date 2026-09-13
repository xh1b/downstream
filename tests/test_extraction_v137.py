"""v1.37 pins: the 2026-09-13 research-sweep extractions.

What this file pins:
- huttunen2019 (IZA DP 12788, full text read) landed as CROSS-CHECK NOTES
  beside the oreopoulos2008 anchor on displacement->child_earnings — a
  working paper is never a composed row, and the reported-CI band never
  shrinks (CITING 4).
- brand2014 (AJS 119(4), full text read) exists in the bib with the exact
  table numbers pinned in QUEUED_EXTRACTIONS — not yet a composed row
  (PSM identification class + new-node design are open decisions).
- the sweep's queue corrections: no composed huttunen or brand row may
  exist by accident.
"""
from pathlib import Path

from downstream.audit import audit, summary
from downstream.params import default_dir, load

PARAMS_DIR = default_dir()


def test_huttunen_cross_check_recorded_not_composed():
    params = load(PARAMS_DIR / "parameters.csv")
    row = params.by_link("displacement->child_earnings")
    assert "huttunen2019" in row.notes
    assert "-575.476" in row.notes and "-2.2%" in row.notes
    # the composed point/band stay the oreopoulos anchor
    assert row.point == 0.9076
    bib = PARAMS_DIR / "references.bib"
    assert "huttunen2019" in bib.read_text()
    assert "fulltext-table" in bib.read_text().split("@article{huttunen2019")[1][:600]


def test_brand2014_bib_present_not_composed():
    bib = (PARAMS_DIR / "references.bib").read_text()
    assert "brand2014" in bib
    params = load(PARAMS_DIR / "parameters.csv")
    rows = [p.link for p in params.parameters if "brand2014" in p.citation_keys]
    assert rows == []  # pinned in the queue; no composed row until admitted


def test_audit_still_clean():
    s = summary(audit(PARAMS_DIR))
    assert s["pass"], [f.as_dict() for f in audit(PARAMS_DIR) if f.severity.value == "error"]


def test_version_stamp():
    assert load(PARAMS_DIR / "parameters.csv").version == "v1.37"
