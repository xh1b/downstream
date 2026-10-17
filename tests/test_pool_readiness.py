# @ref:test-pool-readiness
# Method: @link:doc-pool-readiness-0-4.
# Implementation: @link:code-study-library.
# @tag:evidence @tag:testing
"""Readiness must never mistake phases, subgroups or scale mismatches for replications."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path

import pytest

from downstream.study_library import load_library

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("pool_readiness", ROOT / "scripts/build_pool_readiness.py")
REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORT)


@pytest.fixture(scope="module")
def report():
    return REPORT.build()


def synthetic_pair():
    left = deepcopy(load_library()["oreopoulos2008_overall"])
    right = {**left, "study_id": "synthetic_independent", "overlap_group": "synthetic_new_sample",
             "source_sha256": "b"*64}
    return left, right


def test_independent_matching_pair_is_only_a_manual_review_candidate():
    left, right = synthetic_pair()
    candidate = REPORT.compare(left, right)
    assert candidate["mechanical_screen_pass"]
    assert not candidate["automatic_pooling_allowed"]
    assert "not_verified" in candidate["independence"]
    assert "Manual" in candidate["next_step"]


def test_matching_phase_does_not_create_independence():
    left, right = synthetic_pair()
    right["overlap_group"] = left["overlap_group"]
    result = REPORT.compare(left, right)
    assert not result["mechanical_screen_pass"]
    assert result["independence"] == "shared_sample"
    assert "same_overlap_group:dependence_model_required" in result["refusal_reasons"]


@pytest.mark.parametrize("field,changed", [
    ("scale", "log_cumulative_hazard_ratio"), ("time_horizon", "20-year cumulative"),
    ("treatment", "a different intervention"), ("comparison", "a different control"),
    ("outcome_definition", "a different outcome"), ("population_scope", "a different population"),
    ("design", "observational cross-section"), ("income_quartile", "3"),
    ("age_min", "45"), ("age_max", "54"), ("sex", "Female"),
    ("tenure_min_years", "6"), ("projection_status", "different projection"),
])
def test_mismatched_estimands_require_harmonization_or_exclusion(field, changed):
    left, right = synthetic_pair()
    right[field] = changed
    result = REPORT.compare(left, right)
    assert not result["mechanical_screen_pass"]
    assert f"mismatch:{field}" in result["refusal_reasons"]


def test_missing_metadata_does_not_match_another_missing_field():
    left, right = synthetic_pair()
    for field in ("overlap_group", "treatment", "standard_error_method"):
        left[field] = right[field] = ""
    result = REPORT.compare(left, right)
    assert not result["mechanical_screen_pass"]
    assert result["independence"] == "unknown"
    assert all(f"missing:{f}" in result["refusal_reasons"]
               for f in ("overlap_group", "treatment", "standard_error_method"))


def test_same_document_warning_survives_claimed_distinct_groups():
    left, right = synthetic_pair()
    right["source_sha256"] = left["source_sha256"]
    result = REPORT.compare(left, right)
    assert result["warnings"]
    assert not result["automatic_pooling_allowed"]


def test_every_current_contrast_and_pair_preserved_without_sign_selection(report):
    library = load_library()
    rows = {r["study_id"]: r for r in report["contrasts"]}
    assert set(rows) == set(library)
    assert len(report["pairs"]) == len(library)*(len(library)-1)//2
    for key, original in library.items():
        assert all(rows[key][field] == original[field] for field in original)
    protective = rows["oreopoulos2008_q3"]
    assert protective["point"] > 0
    assert protective["interval_includes_zero"]
    assert rows["sullivan2007_age_60_69"]["point"] < 0
    assert rows["sullivan2007_age_60_69"]["interval_includes_zero"]
    assert rows["browning2011_cancer_4y"]["interval_includes_zero"]
    assert "approximate" in rows["browning2011_allcause_20y"]["standard_error_method"]
    assert report["summary"]["mechanical_screen_pass_pairs"] == 0
    assert report["summary"]["declared_overlap_groups"] == 3
    assert report["summary"]["automatically_admitted_pools"] == 0


def test_current_annual_odds_and_cumulative_hazards_explicitly_refused(report):
    key = {"sullivan2007_displacement", "browning2011_allcause_1y"}
    pair = next(p for p in report["pairs"] if {p["left"], p["right"]} == key)
    assert "mismatch:scale" in pair["refusal_reasons"]
    assert "mismatch:time_horizon" in pair["refusal_reasons"]
    assert not pair["mechanical_screen_pass"]


def test_committed_report_retains_navigation_and_current_source_identity(report):
    text = REPORT.render(report)
    assert text == (ROOT / 'docs/audits/POOL_READINESS_0_4.md').read_text()
    assert '<!-- @' + 'ref:doc-pool-readiness-0-4;' in text
    assert '@link:script-build-pool-readiness' in text


def test_json_export_is_inspectable_and_freshness_check_detects_change(tmp_path):
    output = tmp_path / "report.json"
    args = ["--format", "json", "--out", str(output)]
    assert REPORT.main(args) == 0
    exported = json.loads(output.read_text())
    assert exported["pairs"]
    assert REPORT.main([*args, "--check"]) == 0
    output.write_text("{}")
    assert REPORT.main([*args, "--check"]) == 1
    with pytest.raises(SystemExit):
        REPORT.main(["--format", "json"])
