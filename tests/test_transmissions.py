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
    find_transmission,
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
    assert [w["outcome"] for w in d["walkable"]] == ["earnings", "achievement"]
    assert d["walkable"][0]["depth"] == 3
    assert len(d["blocked"]) == 3


def test_describe_maps_walkable_and_blocked_outcomes():
    d = describe(PARAMS)
    outcomes = {w["outcome"]: w for w in d["walkable"]}
    assert outcomes["earnings"]["depth"] == 3
    assert outcomes["earnings"]["generations"] == [
        "child", "grandchild", "greatgrandchild"]
    assert outcomes["achievement"]["depth"] == 2
    assert outcomes["achievement"]["steps"][0]["kind"] == "linear_shift"
    assert {b["outcome"] for b in d["blocked"]} == {
        "education_years", "adult_depression", "divorce"}
    blocked = {b["outcome"]: b for b in d["blocked"]}
    assert blocked["divorce"]["entry"] == "displacement->divorce_hazard"
    assert "conditional" in blocked["divorce"]["note"]


def test_achievement_walk_composes_the_standardized_slope():
    out = walk(PARAMS, find_transmission("achievement"))
    child, grandchild = out["child"], out["grandchild"]
    entry = PARAMS.by_link("displacement_event->child_achievement_sd")
    slope = PARAMS.by_link("child_achievement_sd->grandchild_achievement_sd")
    assert child.unit == "sd_delta"
    assert (child.point, child.low, child.high) == (entry.point, entry.low, entry.high)
    # linear_shift: the shift is multiplied by the standardized slope
    assert grandchild.point == pytest.approx(slope.point * child.point)
    corners = [t * x for x in (child.low, child.high) for t in (slope.low, slope.high)]
    assert grandchild.low == pytest.approx(min(corners))
    assert grandchild.high == pytest.approx(max(corners))
    assert grandchild.steps[-1].causal_role == "structural_transmission_assumption"
    assert grandchild.steps[-1].evidence_role == "structural"


def test_linear_shift_kind_orders_bands_sign_safely():
    from downstream.ledger import LINEAR_SHIFT, start

    def param(link, point, low, high):
        return Parameter(link=link, from_node="f", to_node="t", point=point,
                         low=low, high=high, tier="canonical", citation="c",
                         population_scope="s", notes="", dist="", evidence_role="structural")

    # negative parent shift, positive slope: band stays negative, ordered
    led = start("a", "sd_delta", 0.0).apply(
        DIRECT, param("e", -0.021, -0.04, 0.0))
    out = led.apply(LINEAR_SHIFT, param("t", 0.38, 0.38, 0.42))
    assert out.point == pytest.approx(0.38 * -0.021)
    assert out.low == pytest.approx(0.42 * -0.04)
    assert out.high == pytest.approx(0.38 * 0.0)
    assert out.low <= out.point <= out.high
    # positive shift: mirrored ordering
    led_p = start("a", "sd_delta", 0.0).apply(DIRECT, param("e", 0.02, 0.01, 0.03))
    out_p = led_p.apply(LINEAR_SHIFT, param("t", 0.38, 0.38, 0.42))
    assert out_p.low == pytest.approx(0.38 * 0.01)
    assert out_p.high == pytest.approx(0.42 * 0.03)
    # a non-positive slope band would flip signs unpredictably; the
    # corner min/max keeps the band ordered regardless
    out_n = led_p.apply(LINEAR_SHIFT, param("t", 0.38, -0.42, 0.42))
    assert out_n.low <= out_n.point <= out_n.high


def test_find_transmission_names_the_gap():
    from downstream.transmissions import find_transmission

    assert find_transmission("achievement").outcome == "achievement"
    with pytest.raises(KeyError, match="no admitted transmission walk"):
        find_transmission("divorce")


def test_cli_transmissions_walk_achievement(capsys):
    from downstream.cli import main

    assert main(["transmissions", "--walk", "achievement"]) == 0
    d = json.loads(capsys.readouterr().out)
    assert d["outcome"] == "achievement"
    assert list(d["generations"]) == ["child", "grandchild"]
    assert d["generations"]["grandchild"]["point"] == pytest.approx(-0.00783, abs=1e-4)


def test_education_transmission_row_pinned_and_dangling_by_design():
    """Row 33 landed; the walk cannot exist until the gen-2 entry lands."""
    row = PARAMS.by_link("child_education_years->grandchild_education_years")
    assert (row.point, row.low, row.high) == (0.296, 0.255, 0.337)
    assert row.dist == "normal"  # SE-derived band: point sits at the midpoint
    assert row.tier == "EXACT-results"
    assert row.evidence_role == "structural"
    assert "lindahl2015" in BIB
    assert BIB["lindahl2015"].evidence == "fulltext"  # upgraded at extraction
    # the walk is blocked only on the entry: CHAIN_KINDS admits the step
    from downstream.ledger import CHAIN_KINDS, LINEAR_SHIFT
    assert CHAIN_KINDS["child_education_years->grandchild_education_years"] == LINEAR_SHIFT
    blocked = {b["outcome"]: b for b in describe(PARAMS)["blocked"]}
    assert "LANDED" in blocked["education_years"]["missing"]
