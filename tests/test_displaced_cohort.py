# @ref:test-displaced-cohort
# Method: @link:doc-scenario-evidence-protocol.
# @tag:data @tag:testing
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("displaced_builder", ROOT / "scripts/build_displaced_cohort.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def test_fixed_width_scientific_notation_and_truncation():
    line = [" "] * 1222
    for name, (a, b) in builder.FIELDS.items():
        line[a-1:b] = str(1).rjust(b-a+1)
    line[1127:1133] = "1.13E6"
    assert builder.decode("".join(line))["PRSLWKLY"] == 1130000
    with pytest.raises(ValueError, match="truncated"):
        builder.decode("short")


def test_known_event_year_and_lost_job_tenure_are_required():
    row = {name: 1 for name in builder.FIELDS}
    row.update(PRTAGE=40, PESEX=1, PTSD18TN=300, PWSUPWGT=100000,
               PRSLWKLY=-9, PRNMCHLD=-1, PRCHLD=-1)
    result = builder.summarize([row, {**row, "PESD3": -2}, {**row, "PTSD18TN": 299}])
    assert result["raw_sample_n"] == 1
    assert result["weighted_workers"] == 10
    assert result["lost_job_weekly_earnings_median_nominal"] is None
    assert result["weighted_counts"]["own_children_under_18"] == {"not_in_universe_or_missing": 10}
    with pytest.raises(ValueError, match="no eligible"):
        builder.summarize([{**row, "PWSUPWGT": 0}])


def test_pinned_public_cohort_reproduces_independent_bls_total():
    result = json.loads((ROOT / "validation/cps2024_displaced_cohort.json").read_text())
    assert result["raw_sample_n"] == 650
    assert result["published_total_check"]["pass"]
    assert result["weighted_workers"] == pytest.approx(2578000, abs=1000)
    assert sum(result["sex_age_shares"].values()) == pytest.approx(1)
    assert "H-1B" in result["limitations"][0]
