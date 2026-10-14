"""Keep adjacent divorce findings from becoming a fabricated remarriage pathway."""
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def screen():
    return json.loads((ROOT / "validation/remarriage_margin_screen_20261015.json").read_text())


def test_missing_remarriage_effect_is_withheld_not_encoded_as_null_effect():
    report = screen()
    decision = report["admission"]
    assert report["screening_status"] == "complete_with_supported_refusal"
    assert decision["eligible"] is False
    assert decision["estimate"] is None
    assert decision["standard_error"] is None
    assert decision["interval"] is None
    assert decision["effect_is_zero"] is False
    assert report["production_changes"] is False
    assert "not a systematic review" in report["scope_limit"]


def test_positive_divorce_and_history_coefficients_do_not_pass_target_admission():
    report = screen()
    contract = report["admission_contract"]
    assert contract["estimand_match"] is False
    assert contract["causal_identification_for_remarriage"] is False
    for row in report["adjacent_estimates"]:
        assert row["estimate"] > 0  # Retain the actual signs; do not invent a reversal.
        assert row["standard_error"] > 0
        assert row["admit_as_remarriage"] is False
        assert row["outcome"] != "remarriage"
        assert row["refusal"]
    assert [r["scale"] for r in report["adjacent_estimates"]] == [
        "probability_difference", "probit_index_coefficient", "probit_index_coefficient"]


def test_source_transcription_preserves_units_uncertainty_and_specification():
    rows = screen()["adjacent_estimates"]
    assert [(r["estimate"], r["standard_error"]) for r in rows] == [
        (.00783, .00210), (.220, .083), (.252, .083)]
    assert "Model 3" in rows[0]["locator"]
    assert rows[0]["observations"] == 80962
    for row in rows[1:]:
        assert "first estimate/SE pair" in row["locator"]
        assert row["observations"] == 14083
        assert "clustered within couples" in row["uncertainty_kind"]
        assert "conditional" in row["contrast"]


def test_every_finding_has_immutable_primary_source_and_version_locator():
    report = screen()
    for row in report["adjacent_estimates"]:
        source = report["sources"][row["source"]]
        assert re.fullmatch(r"[0-9a-f]{64}", source["sha256"])
        assert source["url"].startswith(("https://www.ssb.no/", "https://sites.lsa.umich.edu/"))
        assert source["locators"] and source["population"] and source["method"]
    assert "author draft" in report["sources"]["charles2004"]["version"]
    assert "Discussion Paper" in report["sources"]["rege2007"]["version"]


def test_windows_and_future_admission_contract_do_not_relabel_dissolution_as_formation():
    report = screen()
    assert report["sources"]["rege2007"]["exposure_window"] == [1995, 2000]
    assert report["sources"]["rege2007"]["outcome_window"] == [1995, 2003]
    assert report["sources"]["charles2004"]["dissolution_follow_up_window"] == [1985, 1993]
    requirement = report["admission_contract"]["future_requirement"]
    for distinction in ("origin population", "time since event", "new partners",
                        "cohabitation", "censoring", "effect scale", "uncertainty"):
        assert distinction in requirement
