"""Snapshot export traps (the P1 'export verb' item).

What this file hunts:
- the export drifting from the params tree: a row added to the CSV but
  missing from the snapshot (or vice versa) silently ships a stale
  pinned artifact that production then caches under a fresh version
  stamp — the worst failure class for a version-pinned pipeline
- a timestamp sneaking into the export: breaks byte-determinism, and
  ENTITY_ANALYSIS.md pins "same version = same bytes" end to end
- a snapshot building while the audit is RED: a broken parameter set
  must never ship as a pinned artifact (the ERROR class, not the
  standing staging WARNs)
- citations regressing below the engine's evidence rules: a canonical-
  tier-only export would let production render citations the engine
  never read in full
- nodes/baselines dropped: the consumer recomputes exposure from the
  entity breakdown, but composition rules + baselines are load-bearing
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from downstream.snapshot import SCHEMA, build, dumps

ROOT = Path(__file__).resolve().parent.parent
PARAMS_DIR = ROOT / "params"


def test_version_and_schema_stamped():
    doc = build(PARAMS_DIR)
    assert doc["schema"] == SCHEMA
    assert doc["version"] == (PARAMS_DIR / "VERSION").read_text().strip()


def test_every_row_round_trips():
    # count + field-level equality against the CSV loader — no silent drop
    from downstream.params import load

    csv_params = load(PARAMS_DIR / "parameters.csv")
    doc = build(PARAMS_DIR)
    assert len(doc["parameters"]) == len(csv_params.parameters)
    by_link = {p["link"]: p for p in doc["parameters"]}
    for p in csv_params.parameters:
        row = by_link[p.link]
        assert row["point"] == p.point and row["low"] == p.low and row["high"] == p.high
        assert row["tier"] == p.tier and row["citation"] == p.citation
        assert row["notes"] == p.notes and row["population_scope"] == p.population_scope


def test_deterministic_bytes():
    # same version = same bytes: no timestamps, no hash-of-machine noise
    assert dumps(PARAMS_DIR) == dumps(PARAMS_DIR)
    assert "exported_at" not in dumps(PARAMS_DIR)


def test_citations_block_meets_evidence_floor():
    doc = build(PARAMS_DIR)
    bib_keys = {k for p in doc["parameters"] for k in p["citation"].split(";") if k}
    assert set(doc["citations"]) == bib_keys
    # version-of-record correction landed as a full-text read (v1.21)
    assert doc["citations"]["collinson2024"]["doi"] == "10.1093/qje/qjad042"
    assert doc["citations"]["collinson2024"]["evidence"] == "fulltext-table"


def test_nodes_and_baselines_present():
    doc = build(PARAMS_DIR)
    names = {n["name"] for n in doc["nodes"]}
    for p in doc["parameters"]:
        assert p["from_node"] in names and p["to_node"] in names
    outcomes = {b["outcome"] for b in doc["baselines"]}
    assert "all_cause_mortality_annual" in outcomes
    for b in doc["baselines"]:
        assert b["value"] is not None or b["status"] != "verified"


def test_refuses_when_audit_red(tmp_path):
    # corrupt a copy: point a row at a bib key that does not exist ->
    # the audit must ERROR and the export must refuse
    import shutil

    bad = tmp_path / "bad-params"
    shutil.copytree(PARAMS_DIR, bad)
    rows = (bad / "parameters.csv").read_text(encoding="utf-8")
    corrupted = rows.replace(
        "jacobson1993;oreopoulos2008", "jacobson1993;ghost2011", 1
    )
    assert corrupted != rows, "corruption target not found - trap would not fire"
    (bad / "parameters.csv").write_text(corrupted, encoding="utf-8")
    with pytest.raises(ValueError, match="ghost2011"):
        build(bad)


def test_cli_export_matches_build():
    doc = json.loads(
        subprocess.run(
            [str(ROOT / ".venv" / "bin" / "downstream"), "export"],
            capture_output=True,
            text=True,
            check=True,
            cwd=ROOT,
        ).stdout
    )
    assert doc == build(PARAMS_DIR)
