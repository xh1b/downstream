"""Exposure labels cannot create unique people, dates or target-population evidence."""
from copy import deepcopy
from dataclasses import replace
import json
import math

import pytest

from downstream.cli import main
from downstream.employer import DocumentedExposure, compute_entity_counts
from downstream.params import load_all
from downstream.scenario import ScenarioInput


def exposure(workers=100.125, semantics=None):
    return DocumentedExposure("fixture", "employer", workers, "synthetic", "supplied method",
                              exposure_semantics=semantics)


@pytest.fixture(scope="module")
def parts():
    return load_all()


def compute(parts, item, scenario=None):
    return compute_entity_counts(parts["params"], parts["baselines"], item, scenario)


def test_legacy_call_preserves_outputs_and_leaves_metadata_unknown(parts):
    legacy = exposure()
    explicit = exposure(semantics={"kind": "reference_worker_equivalents"})
    before = compute(parts, legacy)
    after = compute(parts, explicit)
    assert before["modeled"] == after["modeled"]
    assert before["input_content_sha256"] == after["input_content_sha256"]
    assert before["exposure_input_sha256"] != after["exposure_input_sha256"]
    p = before["exposure_provenance"]
    assert p["kind"] == "unspecified_reference_exposure"
    assert p["method_version"] is p["record_window"] is p["components"] is None
    assert p["event_time"]["basis"] == p["overlap"]["status"] == "unknown"
    assert before["exposure_contract"]["target_demographics"] is None
    assert "unknown" in before["exposure_contract"]["family_composition"]
    assert not before["exposure_contract"]["integer_cohort_count_basis_eligible"]


def test_historical_window_is_not_an_event_date_or_calendar_forecast(parts):
    supplied = {"kind": "reference_worker_equivalents", "method_version": "upstream/2",
                "record_window": {"start": "2010-01-01", "end": "2025-12-31"},
                "overlap": {"status": "not_deduplicated", "note": "Repeated filings may overlap."},
                "conversion_assumptions": ["A filing contributes a declared reference equivalent."],
                "event_time": {"basis": "historical_aggregate"},
                "components": {"filings": {"value": 75, "unit": "filings"},
                               "wages": {"value": 200000, "unit": "usd_2024"}}}
    item = exposure(semantics=supplied)
    result = compute(parts, item)
    assert item.displaced_workers == result["exposure_contract"]["quantity"] == 100.125
    assert result["exposure_provenance"]["components"] == supplied["components"]
    assert result["exposure_provenance"]["event_time"]["date"] is None
    assert not result["exposure_contract"]["calendar_forecast_available"]
    assert not result["exposure_contract"]["integer_cohort_count_basis_eligible"]
    assert supplied["event_time"] == {"basis": "historical_aggregate"}
    supplied["components"]["filings"]["value"] = 999
    assert item.exposure_semantics["components"]["filings"]["value"] == 75


def test_integer_equivalents_are_not_an_integer_cohort(parts):
    result = compute(parts, exposure(100, {"kind": "reference_worker_equivalents"}))
    assert not result["exposure_contract"]["integer_cohort_count_basis_eligible"]
    known = {"kind": "unique_displaced_people", "overlap": {"status": "deduplicated",
             "note": "Synthetic fixture person IDs deduplicated."},
             "event_time": {"basis": "single_event", "date": "2026-01-15"}}
    unique = compute(parts, exposure(100, known))
    assert unique["exposure_contract"]["integer_cohort_count_basis_eligible"]
    assert not unique["exposure_contract"]["calendar_forecast_available"]
    assert all(not r["applicability"]["eligible_for_public_headline"]
               for r in unique["modeled"].values())
    missing_time = deepcopy(known)
    missing_time.pop("event_time")
    assert not compute(parts, exposure(100, missing_time))["exposure_contract"]["integer_cohort_count_basis_eligible"]
    missing_overlap = deepcopy(known)
    missing_overlap.pop("overlap")
    assert not compute(parts, exposure(100, missing_overlap))["exposure_contract"]["integer_cohort_count_basis_eligible"]


def test_family_assumptions_are_not_observed_family_composition(parts):
    output = compute(parts, exposure(), ScenarioInput(1, n_children=3))
    assert "unknown" in output["exposure_contract"]["family_composition"]
    output = compute(parts, exposure(), ScenarioInput(1, child_profiles=[
        {"age_at_displacement": 12, "sex": "Male"},
        {"age_at_displacement": 13, "sex": "Male"}]))
    assert output["exposure_contract"]["family_composition"] == "caller-supplied child profiles"


@pytest.mark.parametrize("semantics", [
    [], {"schema": "future/2"}, {"unexpected": 1}, {"kind": []}, {"kind": "worker_years"},
    {"kind": "unique_displaced_people"}, {"method_version": ""},
    {"record_window": {"start": "2025-01-01", "end": "2024-01-01"}},
    {"record_window": {"start": "2025-1-1", "end": "2025-12-31"}},
    {"record_window": {"start": "2025-02-30", "end": "2025-12-31"}},
    {"record_window": {}}, {"overlap": {"status": "deduplicated"}},
    {"overlap": {"status": []}}, {"event_time": {"basis": []}},
    {"event_time": {"basis": "single_event"}},
    {"event_time": {"basis": "historical_aggregate", "date": "2025-01-01"}},
    {"conversion_assumptions": "inferred"}, {"conversion_assumptions": [""]},
    {"components": {}}, {"components": {"raw": {"value": True, "unit": "people"}}},
    {"components": {"raw": {"value": math.nan, "unit": "people"}}},
    {"components": {"raw": {"value": 10**400, "unit": "people"}}},
    {"components": {"raw": {"value": 1, "unit": ""}}},
])
def test_invalid_metadata_is_refused(semantics):
    with pytest.raises(ValueError):
        exposure(semantics=semantics)


def test_warehouse_retains_authoritative_components_and_total(parts):
    row = dict(subject_id="warehouse", subject_type="employer", source="synthetic",
               americans_displaced=12.501,
               displacement_breakdown={"base": 10, "wage_depression": 2.5, "warn_layoffs": 0,
                                       "total": 12.501, "formula": "upstream"})
    item = DocumentedExposure.from_warehouse(**row)
    result = compute(parts, item)
    assert result["exposure_contract"]["quantity"] == 12.501
    assert result["exposure_provenance"]["kind"] == "reference_worker_equivalents"
    assert result["exposure_provenance"]["components"]["wage_depression"] == {
        "value": 2.5, "unit": "worker_equivalents"}
    with pytest.raises(ValueError, match="not a unique cohort"):
        DocumentedExposure.from_warehouse(**row, exposure_semantics={"kind": "unique_displaced_people"})
    with pytest.raises(ValueError, match="reported breakdown"):
        DocumentedExposure.from_warehouse(**row, exposure_semantics={"components": {}})


def test_cli_round_trips_additive_metadata(tmp_path, capsys):
    path = tmp_path / "exposure.json"
    path.write_text(json.dumps(dict(subject_id="fixture", subject_type="employer",
                    displaced_workers=.125, source="synthetic", method="supplied",
                    exposure_semantics={"kind": "reference_worker_equivalents", "method_version": "v2"})))
    assert main(["entity", "--input", str(path)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["exposure_provenance"]["method_version"] == "v2"
    assert result["exposure_contract"]["quantity"] == .125


def test_changed_metadata_invalidates_exposure_identity_without_changing_effect(parts):
    first = exposure(semantics={"method_version": "v1"})
    second = replace(first, exposure_semantics={"method_version": "v2"})
    a, b = compute(parts, first), compute(parts, second)
    assert a["modeled"] == b["modeled"]
    assert a["exposure_input_sha256"] != b["exposure_input_sha256"]
