"""Admission and provenance contracts for support metadata.

The applicability audit requires every admitted estimate to travel with
its studied population. These tests pin the two halves of that contract:
``load`` refuses rows with blank support metadata, and public ledger
steps publish the studied population beside the citation.
"""

import csv
from pathlib import Path

import pytest

from downstream.community import service_jobs_lost
from downstream.params import load, load_all, load_baselines
from downstream.scenario import ScenarioInput, compute_counts

PARAMS_DIR = Path(__file__).resolve().parent.parent / "params"

_FIELDS = ["link", "from_node", "to_node", "point", "low", "high",
           "tier", "citation", "population_scope", "notes", "dist"]


def _row(**overrides):
    row = {"link": "a->b", "from_node": "a", "to_node": "b", "point": "1.0",
           "low": "1.0", "high": "1.0", "tier": "canonical", "citation": "x",
           "population_scope": "y", "notes": "", "dist": ""}
    row.update(overrides)
    return row


def _write(tmp_path, row):
    path = tmp_path / "parameters.csv"
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=_FIELDS)
        writer.writeheader()
        writer.writerow(row)
    return path


@pytest.mark.parametrize("blank_field", ["tier", "citation", "population_scope"])
def test_load_refuses_blank_support_metadata(tmp_path, blank_field):
    path = _write(tmp_path, _row(**{blank_field: "  "}))
    with pytest.raises(ValueError, match="blank support metadata"):
        load(path, version="t")


def test_every_shipped_step_publishes_studied_population():
    parts = load_all()
    params = parts["params"]
    for link in ("displacement->worker_earnings",
                 "displacement->child_earnings",
                 "child_earnings->grandchild_earnings",
                 "grandchild_earnings->greatgrandchild_earnings"):
        p = params.by_link(link)
        assert p.population_scope.strip()
    # A public chain built through the vignette path must publish the
    # studied population on every step, so a citation alone never reads
    # as unconditional support.
    from downstream.children import child_line
    from downstream.worker import worker_outcomes
    ledgers = [worker_outcomes(params)[name] for name in
               ("worker_earnings", "mortality_peak", "mortality_sustained")]
    ledgers += list(child_line(params)[k] for k in
                    ("child", "grandchild", "greatgrandchild"))
    for ledger in ledgers:
        for step in ledger.steps:
            published = step.as_dict()["population_scope"]
            assert published == params.by_link(step.link).population_scope
            assert published.strip(), f"{step.link} published without its population"


def test_mortality_profile_steps_carry_population_and_tier():
    parts = load_all()
    result = compute_counts(parts["params"], parts["baselines"],
                            ScenarioInput(10, exposure_years=8), _raw=True)
    steps = result["modeled"]["excess_deaths"]["steps"]
    assert {s["phase"] for s in steps} == {
        "displacement", "offset_1", "offsets_2_3", "offsets_4_5", "offset_6_plus"}
    for step in steps:
        assert step["population_scope"] == "US high-seniority displaced men"
        assert step["tier"] == "EXACT"


def test_community_steps_publish_population_and_declared_class():
    parts = load_all()
    params = parts["params"]
    jobs = service_jobs_lost(params, net_tradable_jobs_lost=2, job_mix="manufacturing")
    assert jobs["population_scope"] == params.by_link(
        "displacement->local_service_jobs").population_scope
    result = compute_counts(params, parts["baselines"],
                            ScenarioInput(10, net_tradable_jobs_lost=2,
                                          local_job_mix="manufacturing"), _raw=True)
    assert result["modeled"]["local_service_jobs_lost"]["population_scope"] == \
        jobs["population_scope"]


def test_local_jobs_class_selection_uses_class_specific_estimands():
    parts = load_all()
    params = parts["params"]
    row = params.by_link("displacement->local_service_jobs")
    assert (row.low, row.high) == (1.6, 5.0)
    manufacturing = service_jobs_lost(params, 10, "manufacturing")
    high_tech = service_jobs_lost(params, 10, "high_tech")
    # Each declared class returns its own published constant with a
    # degenerate band: the row span crosses job classes, not uncertainty.
    assert manufacturing["point"] == 16.0
    assert high_tech["point"] == 50.0
    for jobs in (manufacturing, high_tech):
        assert jobs["low"] == jobs["high"] == jobs["point"]
        assert "not an uncertainty band" in jobs["support_note"]
    with pytest.raises(ValueError, match="declared job class"):
        service_jobs_lost(params, 10, "any")


def test_local_jobs_blocked_without_declared_class():
    parts = load_all()
    result = compute_counts(parts["params"], parts["baselines"],
                            ScenarioInput(10, net_tradable_jobs_lost=2), _raw=True)
    blocked = {b["outcome"]: b["reason"] for b in result["blocked"]}
    assert "local_service_jobs_lost" in blocked
    assert "declared job class" in blocked["local_service_jobs_lost"]
    assert "local_service_jobs_lost" not in result["modeled"]


_BASELINE_FIELDS = ["outcome", "unit", "population", "value", "citation",
                    "source", "status", "notes"]


def _baseline_row(**overrides):
    row = {"outcome": "all_cause_mortality_annual", "unit": "deaths_per_person_year",
           "population": "US men 45-54", "value": "0.004944",
           "citation": "cdc_wonder", "source": "cdc_wonder", "status": "verified",
           "notes": ""}
    row.update(overrides)
    return row


def _write_baselines(tmp_path, row):
    path = tmp_path / "baselines.csv"
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=_BASELINE_FIELDS)
        writer.writeheader()
        writer.writerow(row)
    return path


def test_load_baselines_refuses_unknown_status(tmp_path):
    path = _write_baselines(tmp_path, _baseline_row(status="verifed"))
    with pytest.raises(ValueError, match="unknown status"):
        load_baselines(path)


@pytest.mark.parametrize("blank", ["citation", "population"])
@pytest.mark.parametrize("drop_value", [False, True])
def test_load_baselines_refuses_unpinned_verified_rows(tmp_path, blank, drop_value):
    row = _baseline_row(**{blank: ""})
    if drop_value:
        row["value"] = ""
    path = _write_baselines(tmp_path, row)
    with pytest.raises(ValueError, match="missing"):
        load_baselines(path)


def test_load_baselines_admits_pending_row_without_value(tmp_path):
    path = _write_baselines(tmp_path, _baseline_row(status="pending", value="",
                                                    citation="", population=""))
    loaded = load_baselines(path)
    assert loaded["all_cause_mortality_annual"].value is None
    assert loaded["all_cause_mortality_annual"].status == "pending"
