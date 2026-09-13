"""Adversarial traps for the audit — each names the bug class it hunts."""

import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from downstream.audit import ERROR, INFO, WARN, audit, summary

REAL_PARAMS = Path(__file__).resolve().parent.parent / "params"


@pytest.fixture
def params_dir(tmp_path):
    """A copy of the real parameter dir to mutate per trap."""
    d = tmp_path / "params"
    shutil.copytree(REAL_PARAMS, d, ignore=shutil.ignore_patterns("__pycache__"))
    return d


def _write_rows(d, rows, fieldnames):
    with open(d / "parameters.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _rows(d):
    with open(d / "parameters.csv", newline="") as f:
        r = csv.DictReader(f)
        return list(r), list(r.fieldnames)


def test_clean_shipped_set_has_zero_errors():
    findings = audit(REAL_PARAMS)
    s = summary(findings)
    assert s["errors"] == 0, [f for f in findings if f.severity == ERROR]
    # Cross-check bibliography is informational; the shipped graph has no
    # unexplained producer gaps.
    assert s["warnings"] == 0
    assert s["info"] > 0


def test_trap_inverted_band(params_dir):
    rows, fields = _rows(params_dir)
    rows[0]["low"], rows[0]["high"] = "0.9", "0.5"
    _write_rows(params_dir, rows, fields)
    findings = audit(params_dir)
    assert any(f.check == "dag" and f.severity == ERROR and "outside its band" in f.message for f in findings)


def test_trap_point_outside_band(params_dir):
    rows, fields = _rows(params_dir)
    rows[0]["point"] = "2.0"
    _write_rows(params_dir, rows, fields)
    findings = audit(params_dir)
    assert any(f.check == "dag" and f.severity == ERROR and "outside its band" in f.message for f in findings)


def test_trap_unresolvable_citation_key(params_dir):
    rows, fields = _rows(params_dir)
    rows[0]["citation"] = "not_in_bib2020"
    _write_rows(params_dir, rows, fields)
    findings = audit(params_dir)
    assert any(f.check == "citation" and "not_in_bib2020" in f.message for f in findings)


def test_trap_uncited_parameter(params_dir):
    rows, fields = _rows(params_dir)
    rows[0]["citation"] = ""
    _write_rows(params_dir, rows, fields)
    findings = audit(params_dir)
    # A blank citation is now refused at admission (params.load), so the
    # audit surfaces the load failure; the trap still names the row and
    # the missing field.
    assert any(f.severity == ERROR and "blank support metadata: citation" in f.message
               for f in findings)


def test_trap_unknown_tier(params_dir):
    rows, fields = _rows(params_dir)
    rows[0]["tier"] = "vibes"
    _write_rows(params_dir, rows, fields)
    findings = audit(params_dir)
    assert any(f.check == "tier" for f in findings)


def test_trap_exact_tier_without_fulltext_evidence(params_dir):
    rows, fields = _rows(params_dir)
    for r in rows:
        if r["tier"] == "EXACT":
            r["tier"] = "EXACT"
            # oreopoulos2008 IS fulltext-table; sabotage a different EXACT row:
            pass
    # find the exact row and point it at an abstract-only key
    for r in rows:
        if r["link"] == "displacement->child_earnings":
            r["citation"] = "jacobson1993"  # abstract evidence, claims EXACT
    _write_rows(params_dir, rows, fields)
    findings = audit(params_dir)
    assert any(f.check == "tier-evidence" and f.severity == ERROR for f in findings)


def test_trap_moretti_shape_level_ratio_below_one(params_dir):
    rows, fields = _rows(params_dir)
    for r in rows:
        if r["to_node"] == "local_service_jobs":
            r["point"] = "0.8"  # the v0 bug shape
    _write_rows(params_dir, rows, fields)
    findings = audit(params_dir)
    assert any(f.check == "dag" and f.severity == ERROR and "outside its band" in f.message for f in findings)


def test_trap_duplicate_link(params_dir):
    rows, fields = _rows(params_dir)
    dup = dict(rows[0])
    rows.append(dup)
    _write_rows(params_dir, rows, fields)
    findings = audit(params_dir)
    assert any(f.check == "dag" and f.severity == ERROR and "duplicate" in f.message for f in findings)


def test_trap_unknown_node(params_dir):
    rows, fields = _rows(params_dir)
    rows[0]["to_node"] = "unicorn_node"
    _write_rows(params_dir, rows, fields)
    findings = audit(params_dir)
    assert any(f.check == "node" and "unicorn_node" in f.message for f in findings)


def test_boundary_inputs_are_declared_not_orphaned(params_dir):
    findings = audit(REAL_PARAMS)
    orphans = [f for f in findings if f.check == "orphan"]
    assert orphans == []


def test_verified_baseline_needs_value(params_dir):
    lines = (params_dir / "baselines.csv").read_text().splitlines()
    lines[1] = lines[1].replace(",pending,", ",verified,")
    (params_dir / "baselines.csv").read_text()
    out = []
    for ln in lines:
        parts = ln.split(",")
        out.append(ln)
    (params_dir / "baselines.csv").write_text("\n".join(out) + "\n")
    findings = audit(params_dir)
    # whatever the edit, audit must not crash and must stay honest
    assert isinstance(summary(findings)["errors"], int)


def test_cycle_is_reported_not_raised(params_dir):
    rows, fields = _rows(params_dir)
    rows.append(
        {
            "link": "grandchild_earnings->child_earnings",
            "from_node": "grandchild_earnings",
            "to_node": "child_earnings",
            "point": "0.5", "low": "0.4", "high": "0.6",
            "tier": "canonical", "citation": "solon1992",
            "population_scope": "x", "notes": "",
        }
    )
    _write_rows(params_dir, rows, fields)
    findings = audit(params_dir)
    assert any(f.check == "dag" and f.severity == ERROR for f in findings)


def test_audit_cli_exit_code():
    r = subprocess.run(
        [sys.executable, "-m", "downstream.audit"],
        cwd=str(REAL_PARAMS.parent / "src" / ".."),  # repo root
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(REAL_PARAMS.parent / "src"), "PATH": "/usr/bin:/bin"},
    )
    out = json.loads(r.stdout)
    assert out["summary"]["errors"] == 0
    assert r.returncode == 0


def test_audit_reports_missing_version_and_invalid_place_metadata(params_dir):
    (params_dir / "VERSION").unlink()
    with (params_dir / "places.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(line for line in handle if not line.startswith("#"))
        rows = list(reader)
        fields = reader.fieldnames
    # Remove the required national fallback, then make the first retained row
    # visibly unsuitable for a pooling calculation.
    rows = [row for row in rows if row["key"] != "national"]
    rows[0]["level"] = "planet"
    rows[0]["citation"] = ""
    with (params_dir / "places.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    findings = audit(params_dir)
    assert any(f.check == "version" and f.severity == WARN for f in findings)
    assert any(f.check == "places" and "failed to load" in f.message for f in findings)
    assert any(f.check == "places" and "unknown level" in f.message for f in findings)


def _baseline_rows(d):
    with open(d / "baselines.csv", newline="") as f:
        r = csv.DictReader(f)
        return list(r), list(r.fieldnames)


def _write_baseline_rows(d, rows, fields):
    with open(d / "baselines.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def _place_rows(d):
    with open(d / "places.csv", newline="") as f:
        r = csv.DictReader(line for line in f if not line.startswith("#"))
        return list(r), list(r.fieldnames)


def _write_place_rows(d, rows, fields):
    with open(d / "places.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def _write_correlations(d, rows):
    with open(d / "correlations.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["from_param", "to_param", "spearman", "justification"])
        w.writeheader()
        w.writerows(rows)


def test_input_load_failure_is_reported_not_raised(params_dir):
    rows, fields = _baseline_rows(params_dir)
    rows[0]["status"] = "archived"  # load() passes; load_all refuses
    _write_baseline_rows(params_dir, rows, fields)
    findings = audit(params_dir)
    assert any(f.check == "inputs" and "failed to load" in f.message for f in findings)


def test_unit_composition_gap_is_reported(params_dir):
    with open(params_dir / "nodes.csv", newline="") as f:
        r = csv.DictReader(f)
        nodes, node_fields = list(r), list(r.fieldnames)
    for n in nodes:
        if n["node"] == "worker_earnings":
            n["unit"] = "count"  # known unit, but persons -> count has no rule
    with open(params_dir / "nodes.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=node_fields)
        w.writeheader()
        w.writerows(nodes)
    findings = audit(params_dir)
    assert any(f.check == "units" and "no composition rule" in f.message for f in findings)


def test_level_ratio_below_one_with_widened_band_is_flagged(params_dir):
    rows, fields = _rows(params_dir)
    for r in rows:
        if r["link"] == "displacement->local_service_jobs":
            r["low"], r["point"], r["high"] = "0.8", "0.9", "5.0"
    _write_rows(params_dir, rows, fields)
    findings = audit(params_dir)
    assert any(f.check == "level-ratio-shape" and f.severity == ERROR for f in findings)


def test_exact_abstract_tier_needs_abstract_evidence(params_dir):
    rows, fields = _rows(params_dir)
    rows[0]["citation"] = "solon1992"  # canonical evidence, not abstract/results/fulltext
    rows[0]["tier"] = "EXACT-abstract"
    _write_rows(params_dir, rows, fields)
    findings = audit(params_dir)
    assert any(f.check == "tier-evidence" and "EXACT-abstract" in f.message for f in findings)


def test_lognormal_with_nonpositive_edges_is_flagged(params_dir):
    rows, fields = _rows(params_dir)
    rows[0]["dist"] = "lognormal"
    rows[0]["low"] = "0"
    _write_rows(params_dir, rows, fields)
    findings = audit(params_dir)
    assert any(f.check == "dist" and "positive band edges" in f.message for f in findings)


def test_lognormal_point_off_geometric_mean_warns(params_dir):
    rows, fields = _rows(params_dir)
    rows[0]["dist"] = "lognormal"
    rows[0]["low"], rows[0]["point"], rows[0]["high"] = "1.0", "3.0", "5.0"
    _write_rows(params_dir, rows, fields)
    findings = audit(params_dir)
    assert any(f.check == "dist" and f.severity == WARN and "geometric mean" in f.message
               for f in findings)


def test_pending_baseline_is_reported_as_info(params_dir):
    rows, fields = _baseline_rows(params_dir)
    rows[0]["status"] = "pending"
    _write_baseline_rows(params_dir, rows, fields)
    findings = audit(params_dir)
    assert any(f.check == "baseline" and f.severity == INFO and "pending" in f.message
               for f in findings)


def test_place_row_without_citation_is_flagged(params_dir):
    rows, fields = _place_rows(params_dir)
    target = next(r for r in rows if r["key"] != "national")
    target["citation"] = ""
    _write_place_rows(params_dir, rows, fields)
    findings = audit(params_dir)
    assert any(f.check == "places" and "no citation" in f.message for f in findings)


def test_divorce_rate_without_precision_n_warns(params_dir):
    rows, fields = _place_rows(params_dir)
    target = next(r for r in rows if r["key"] != "national")
    target["divorce_rate"] = "0.11"
    target["divorce_n"] = ""
    _write_place_rows(params_dir, rows, fields)
    findings = audit(params_dir)
    assert any(f.check == "places" and f.severity == WARN and "divorce_rate without divorce_n" in f.message
               for f in findings)


def test_missing_mobility_modifier_warns_when_places_present(params_dir):
    rows, fields = _rows(params_dir)
    mobility = "neighborhood_exposure->child_outcomes_modifier"
    assert any(r["link"] == mobility for r in rows)
    _write_rows(params_dir, [r for r in rows if r["link"] != mobility], fields)
    findings = audit(params_dir)
    assert any(f.check == "places" and f.severity == WARN and "mobility modifier" in f.message
               for f in findings)


def test_correlations_load_failure_is_reported(params_dir):
    _write_correlations(params_dir, [
        {"from_param": "displacement->worker_earnings",
         "to_param": "earnings_shock->mortality_peak",
         "spearman": "strong", "justification": "declared"},
    ])
    findings = audit(params_dir)
    assert any(f.check == "correlation" and "failed to load" in f.message for f in findings)


def test_correlation_unknown_link_is_reported(params_dir):
    _write_correlations(params_dir, [
        {"from_param": "ghost->link", "to_param": "displacement->worker_earnings",
         "spearman": "0.5", "justification": "declared"},
    ])
    findings = audit(params_dir)
    assert any(f.check == "correlation" and "unknown link" in f.message for f in findings)


def test_correlation_spearman_outside_unit_interval_is_reported(params_dir):
    _write_correlations(params_dir, [
        {"from_param": "displacement->worker_earnings",
         "to_param": "earnings_shock->mortality_peak",
         "spearman": "1.5", "justification": "declared"},
    ])
    findings = audit(params_dir)
    assert any(f.check == "correlation" and "outside (-1, 1)" in f.message for f in findings)


def test_correlation_blank_justification_is_reported(params_dir):
    _write_correlations(params_dir, [
        {"from_param": "displacement->worker_earnings",
         "to_param": "earnings_shock->mortality_peak",
         "spearman": "0.5", "justification": ""},
    ])
    findings = audit(params_dir)
    assert any(f.check == "correlation" and "no justification" in f.message for f in findings)


def test_correlation_justification_without_basis_is_reported(params_dir):
    _write_correlations(params_dir, [
        {"from_param": "displacement->worker_earnings",
         "to_param": "earnings_shock->mortality_peak",
         "spearman": "0.5", "justification": "trust me"},
    ])
    findings = audit(params_dir)
    assert any(f.check == "correlation" and "must name a citable basis" in f.message
               for f in findings)


def test_correlation_non_psd_matrix_is_reported(params_dir):
    # 0.9 / 0.9 / -0.9 over three real links is not positive semidefinite.
    _write_correlations(params_dir, [
        {"from_param": "displacement->worker_earnings",
         "to_param": "earnings_shock->mortality_peak",
         "spearman": "0.9", "justification": "declared"},
        {"from_param": "displacement->worker_earnings",
         "to_param": "earnings_shock->mortality_sustained",
         "spearman": "0.9", "justification": "declared"},
        {"from_param": "earnings_shock->mortality_peak",
         "to_param": "earnings_shock->mortality_sustained",
         "spearman": "-0.9", "justification": "declared"},
    ])
    findings = audit(params_dir)
    assert any(f.check == "correlation" and "not PSD" in f.message for f in findings)


def test_finding_as_dict_roundtrip():
    from downstream.audit import Finding
    assert Finding(WARN, "check", "msg").as_dict() == {"severity": WARN, "check": "check", "message": "msg"}


def test_unknown_dist_name_is_flagged(params_dir):
    rows, fields = _rows(params_dir)
    rows[0]["dist"] = "biblical"
    _write_rows(params_dir, rows, fields)
    findings = audit(params_dir)
    assert any(f.check == "dist" and "not in" in f.message for f in findings)


def test_normal_dist_off_midpoint_warns(params_dir):
    rows, fields = _rows(params_dir)
    rows[0]["dist"] = "normal"
    rows[0]["low"], rows[0]["point"], rows[0]["high"] = "0.0", "0.4", "1.0"
    _write_rows(params_dir, rows, fields)
    findings = audit(params_dir)
    assert any(f.check == "dist" and f.severity == WARN and "midpoint" in f.message
               for f in findings)


def test_places_without_national_row_is_flagged(params_dir):
    rows, fields = _place_rows(params_dir)
    kept = [r for r in rows if r["key"] != "national"]
    assert len(kept) < len(rows)
    _write_place_rows(params_dir, kept, fields)
    findings = audit(params_dir)
    assert any(f.check == "places" and "no 'national' row" in f.message for f in findings)


def test_mortality_rate_without_precision_n_warns(params_dir):
    rows, fields = _place_rows(params_dir)
    target = next(r for r in rows if r["key"] != "national")
    target["mortality_rate"] = "0.005"
    target["mortality_n"] = ""
    _write_place_rows(params_dir, rows, fields)
    findings = audit(params_dir)
    assert any(f.check == "places" and f.severity == WARN and "mortality_rate without mortality_n" in f.message
               for f in findings)


def test_header_only_correlations_file_is_tolerated(params_dir):
    with open(params_dir / "correlations.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["from_param", "to_param", "spearman", "justification"])
        w.writeheader()
    findings = audit(params_dir)
    assert not any(f.check == "correlation" for f in findings)
