"""Parameter-set, node, baseline, and citation-database checks."""

from pathlib import Path

import pytest

from downstream.citations import parse_bib
from downstream.params import load, load_all, load_baselines, load_nodes

PARAMS_DIR = Path(__file__).resolve().parent.parent / "params"


def test_version_stamp():
    assert load(PARAMS_DIR / "parameters.csv").version == "v1.0"


def test_nodes_registry_loads_with_known_units():
    nodes = load_nodes(PARAMS_DIR / "nodes.csv")
    assert nodes["local_service_jobs"].unit == "level_ratio"
    assert nodes["child_earnings"].unit == "gap_multiplier"


def test_baselines_pending_until_pinned():
    baselines = load_baselines(PARAMS_DIR / "baselines.csv")
    assert baselines["all_cause_mortality_annual"].status == "pending"
    assert baselines["all_cause_mortality_annual"].value is None


def test_bib_parses_and_carries_evidence_classes():
    bib = parse_bib(PARAMS_DIR / "references.bib")
    assert len(bib) > 40
    assert bib["oreopoulos2008"].evidence == "fulltext-table"
    assert bib["oreopoulos2008"].year == "2008"
    assert "Oreopoulos" in bib["oreopoulos2008"].fields["author"]
    assert bib["rege2007"].title == "Plant Closure and Marital Dissolution"


def test_every_parameter_cites_resolvable_keys():
    parts = load_all(PARAMS_DIR)
    bib = parts["bib"]
    for p in parts["params"].parameters:
        keys = p.citation_keys
        assert keys, f"uncited parameter {p.link}"
        for k in keys:
            assert k in bib, f"{p.link} cites missing key {k}"


def test_with_param_overrides_and_marks_sampled():
    params = load(PARAMS_DIR / "parameters.csv")
    p0 = params.by_link("displacement->child_earnings")
    sampled = params.with_param(p0.link, 0.93)
    assert sampled.by_link(p0.link).point == 0.93
    assert sampled.version.endswith("-sampled")
    # original untouched (frozen dataclass semantics)
    assert params.by_link(p0.link).point == 0.91


def test_cycle_rejection():
    import csv as _csv
    import tempfile

    rows = [
        {"link": "a->b", "from_node": "a", "to_node": "b", "point": "1.0", "low": "1.0", "high": "1.0",
         "tier": "canonical", "citation": "x", "population_scope": "y", "notes": ""},
        {"link": "b->a", "from_node": "b", "to_node": "a", "point": "1.0", "low": "1.0", "high": "1.0",
         "tier": "canonical", "citation": "x", "population_scope": "y", "notes": ""},
    ]
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "bad.csv"
        with open(f, "w", newline="") as fh:
            w = _csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        with pytest.raises(ValueError, match="cycle"):
            load(f, version="t")
