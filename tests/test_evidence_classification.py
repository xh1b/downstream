"""Classification must retain admission and causal-use distinctions."""
from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

import pytest

from downstream.ledger import validate_chain
from downstream.params import default_dir, load, load_nodes

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "build_evidence_classification", ROOT / "scripts/build_evidence_classification.py"
)
REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORT)


@pytest.fixture(scope="module")
def data():
    return REPORT.inventory(default_dir())


def test_transport_condition_does_not_upgrade_structural_causal_use(data):
    rows = {row["link"]: row for row in data["parameters"]}
    direct = rows["displacement->child_earnings"]
    mediated = rows["infant_birth_weight->child_earnings"]
    assert direct["evidence_role"] == mediated["evidence_role"] == "conditional"
    assert direct["runtime_use"] == "direct_displacement_estimate"
    assert mediated["runtime_use"] == "structural_transmission_assumption"
    assert rows["child_earnings->grandchild_earnings"]["evidence_role"] == "structural"


def test_observed_share_is_distinct_from_a_displacement_response(data):
    rows = {row["link"]: row for row in data["parameters"]}
    share = rows["married_cohort->parental_dissolution_share"]
    assert share["runtime_use"] == "observed_counterfactual_share"
    assert share["chain_kind"] is None
    assert rows["displacement->divorce_hazard"]["runtime_use"] == "direct_displacement_estimate"


def test_boundary_evidence_has_no_generic_chain_permission(data):
    params = load(default_dir() / "parameters.csv")
    nodes = load_nodes(default_dir() / "nodes.csv")
    for row in data["parameters"]:
        if row["evidence_role"] == "boundary":
            assert row["chain_kind"] is None
            with pytest.raises(ValueError, match="boundary"):
                validate_chain(params, [row["link"]], ["direct"], nodes)


def test_receiving_estimate_is_not_labeled_a_displacement_effect(data):
    rows = {row["link"]: row for row in data["parameters"]}
    for link in ("immigrant_influx->receiving_violent_crime_rate",
                 "immigrant_influx->receiving_total_crime_rate"):
        assert rows[link]["runtime_use"] == "direct_receiving_community_estimate"
        assert rows[link]["evidence_role"] == "conditional"


def test_report_does_not_count_contrasts_as_independent_studies(data):
    groups = {row["overlap_group"] for row in data["contrasts"].values()}
    assert len(groups) < len(data["contrasts"])
    text = REPORT.render(data)
    assert "not independent studies" in text
    assert "not an admitted edge" in text
    assert "not\nan identified response to involuntary displacement" in text
    assert "female displacement mortality response" in text


def test_unclassified_parameter_cannot_be_exported_as_supported(tmp_path):
    source = default_dir() / "parameters.csv"
    with source.open(newline="") as handle:
        reader = csv.DictReader(handle)
        fields, rows = reader.fieldnames, list(reader)
    rows[0]["evidence_role"] = ""
    target = tmp_path / "parameters.csv"
    with target.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError, match="evidence_role"):
        load(target)


def test_check_rejects_missing_or_stale_output(tmp_path):
    output = tmp_path / "report.md"
    assert REPORT.main(["--check", "--output", str(output)]) == 1
    assert REPORT.main(["--output", str(output)]) == 0
    assert REPORT.main(["--check", "--output", str(output)]) == 0
    output.write_text(output.read_text().replace("conditional", "unrestricted", 1))
    assert REPORT.main(["--check", "--output", str(output)]) == 1
