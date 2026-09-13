"""The generational transmission registry.

Traps the core design invariant: the child line is ONE admitted
parent->child relationship applied recursively — never separately
extracted per-generation parameters. The walker must reproduce the
explicit per-generation composition byte-for-byte, and the unrolled
copies of one relationship must never drift apart.
"""

import dataclasses
import json
import pathlib
import shutil

import pytest

from downstream.audit import ERROR, audit
from downstream.children import CHILD_DIRECT, GREATGRANDCHILD, GRANDCHILD, child_line
from downstream.ledger import DIRECT, GAP, GAP_SCALE, start
from downstream.params import Parameter, ParameterSet, load_all
from downstream import transmissions as mod
from downstream.transmissions import (
    EARNINGS,
    describe,
    drift_relationships,
    generation_label,
    load_transmissions,
    transmission_findings,
    walk,
)

PARAMS_DIR = pathlib.Path(__file__).resolve().parent.parent / "params"
PARTS = load_all(PARAMS_DIR)
PARAMS = PARTS["params"]
BIB = PARTS["bib"]
KEYS = ("child", "grandchild", "greatgrandchild")


def _modifier(point=0.5, low=0.3, high=0.7) -> Parameter:
    return Parameter(
        link="test->child_outcomes_modifier", from_node="test",
        to_node="child_outcomes_modifier", point=point, low=low, high=high,
        tier="structural", citation="chettyhendren2018",
        population_scope="test", notes="", dist="", evidence_role="structural",
    )


def _explicit(place_modifier=None, legacy_repeated=False) -> dict:
    """The pre-registry explicit per-generation composition."""
    child = start("child_earnings", "gap_multiplier").apply(
        DIRECT, PARAMS.by_link(CHILD_DIRECT),
        causal_role="direct_displacement_estimate")
    if place_modifier is not None:
        child = child.apply(GAP_SCALE, place_modifier,
                            causal_role="exploratory_place_effect_modifier")
    grandchild = child.apply(GAP, PARAMS.by_link(GRANDCHILD),
                             causal_role="structural_transmission_assumption")
    greatgrandchild = grandchild.apply(GAP, PARAMS.by_link(GREATGRANDCHILD),
                                       causal_role="structural_transmission_assumption")
    if place_modifier is not None and legacy_repeated:
        grandchild = grandchild.apply(GAP_SCALE, place_modifier,
                                      causal_role="exploratory_place_effect_modifier")
        greatgrandchild = greatgrandchild.apply(GAP_SCALE, place_modifier,
                                                causal_role="exploratory_place_effect_modifier")
    return {"child": child, "grandchild": grandchild, "greatgrandchild": greatgrandchild}


def test_child_line_is_the_recursive_walk_of_one_relationship():
    for kwargs in ({}, {"place_modifier": _modifier()},
                   {"place_modifier": _modifier(), "place_application": "legacy_repeated"}):
        walked = child_line(PARAMS, **kwargs)
        explicit = _explicit(
            place_modifier=kwargs.get("place_modifier"),
            legacy_repeated=kwargs.get("place_application") == "legacy_repeated")
        for k in KEYS:
            assert walked[k] == explicit[k], f"walker diverged at {k}"


def test_walk_names_generations_and_carries_per_step_support():
    out = walk(PARAMS, EARNINGS)
    assert list(out) == ["child", "grandchild", "greatgrandchild"]
    assert [s.link for s in out["greatgrandchild"].steps] == \
        [EARNINGS.entry] + [s.link for s in EARNINGS.steps]
    # the repetition is ONE relationship: same band at every step
    assert PARAMS.by_link(GRANDCHILD).point == PARAMS.by_link(GREATGRANDCHILD).point
    # per-step provenance: US IGE literature for step 2, Swedish
    # multi-generation registers for step 3
    assert "solon1992" in EARNINGS.steps[0].support
    assert "lindahl2015" in EARNINGS.steps[1].support


def test_generation_labels():
    assert generation_label(1) == "child"
    assert generation_label(2) == "grandchild"
    assert generation_label(3) == "greatgrandchild"
    assert generation_label(4) == "greatgreatgrandchild"
    with pytest.raises(ValueError):
        generation_label(0)


def test_walk_refuses_unknown_links_and_wrong_kinds():
    bad_link = dataclasses.replace(EARNINGS, steps=EARNINGS.steps + (
        dataclasses.replace(EARNINGS.steps[0], link="nope->nothing"),))
    with pytest.raises(KeyError):
        walk(PARAMS, bad_link)
    bad_kind = dataclasses.replace(EARNINGS, steps=(
        dataclasses.replace(EARNINGS.steps[0], kind="level"),))
    with pytest.raises(ValueError, match="requires 'gap' composition"):
        walk(PARAMS, bad_kind)
    bad_entry = dataclasses.replace(EARNINGS, entry="divorce->child_earnings")
    with pytest.raises(ValueError, match="chain-kind 'direct'"):
        walk(PARAMS, bad_entry)


def test_registry_admission_refuses_boundary_roles():
    boundary_entry = tuple(
        dataclasses.replace(r, evidence_role="boundary")
        if r.link == CHILD_DIRECT else r for r in PARAMS.parameters)
    with pytest.raises(ValueError, match="boundary"):
        load_transmissions(ParameterSet(version="t", parameters=boundary_entry))


def test_drift_between_unrolled_copies_is_a_finding():
    assert drift_relationships(PARAMS) == []
    assert transmission_findings(PARAMS, BIB) == []
    drifted = tuple(
        dataclasses.replace(r, point=0.61)
        if r.link == GREATGRANDCHILD else r for r in PARAMS.parameters)
    bad = ParameterSet(version="drift", parameters=drifted)
    assert drift_relationships(bad) == ["ige_earnings"]
    findings = transmission_findings(bad, BIB)
    assert any(c == "transmission-drift" and "ige_earnings" in m for c, m in findings)


def test_transmission_support_keys_must_exist_in_bib():
    assert transmission_findings(PARAMS, BIB) == []  # shipped registry cites real keys
    rogue = dataclasses.replace(
        EARNINGS, steps=(dataclasses.replace(
            EARNINGS.steps[0], support=("solon1992", "not_a_bib_key")),))
    original = mod.TRANSMISSIONS
    mod.TRANSMISSIONS = (rogue,)
    try:
        findings = transmission_findings(PARAMS, BIB)
        assert any(c == "transmission-support" and "not_a_bib_key" in m
                   for c, m in findings)
    finally:
        mod.TRANSMISSIONS = original


def test_audit_surfaces_transmission_drift(tmp_path):
    work = tmp_path / "params"
    shutil.copytree(PARAMS_DIR, work,
                    ignore=shutil.ignore_patterns("__pycache__"))
    lines = (work / "parameters.csv").read_text().splitlines()
    out = []
    for ln in lines:
        if ln.startswith(GREATGRANDCHILD + ","):
            parts = ln.split(",")
            # in-band drift: an out-of-band point would be refused at
            # admission before the audit's cross-row checks ever run
            parts[3] = "0.52"
            ln = ",".join(parts)
        out.append(ln)
    (work / "parameters.csv").write_text("\n".join(out) + "\n", encoding="utf-8")
    hits = [f for f in audit(work) if f.check == "transmission-drift"]
    assert hits and hits[0].severity == ERROR
    assert audit(PARAMS_DIR) is not None  # shipped set stays clean


def test_cli_transmissions_verb(capsys):
    from downstream.cli import main

    assert main(["transmissions"]) == 0
    d = json.loads(capsys.readouterr().out)
    assert [w["outcome"] for w in d["walkable"]] == ["earnings"]
    assert d["walkable"][0]["depth"] == 3
    assert len(d["blocked"]) >= 4


def test_describe_maps_walkable_and_blocked_outcomes():
    d = describe(PARAMS)
    outcomes = {w["outcome"]: w for w in d["walkable"]}
    assert outcomes["earnings"]["depth"] == 3
    assert outcomes["earnings"]["generations"] == [
        "child", "grandchild", "greatgrandchild"]
    assert {b["outcome"] for b in d["blocked"]} >= {
        "achievement", "education_years", "adult_depression", "divorce"}
    blocked = {b["outcome"]: b for b in d["blocked"]}
    assert blocked["divorce"]["entry"] == "displacement->divorce_hazard"
    assert "conditional" in blocked["divorce"]["note"]
