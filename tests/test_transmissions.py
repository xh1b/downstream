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
    ACHIEVEMENT,
    EARNINGS,
    Transmission,
    TransmissionStep,
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


# --- adversarial: attacks on the registry, the walker, and the CLI ---


def test_walk_enforces_the_hook_contract():
    """The hook is trusted to preserve unit and band ordering only in the
    docstring's dreams: a hook that breaks either is refused, and a
    well-behaved hook walks through untouched."""
    for bad, fragment in (
        (lambda led, i: dataclasses.replace(led, unit="gap_multiplier"), "unit"),
        (lambda led, i: dataclasses.replace(led, low=1.0, high=-1.0), "band"),
    ):
        with pytest.raises(ValueError, match=fragment):
            walk(PARAMS, find_transmission("achievement"), hook=bad)
    identity = walk(PARAMS, find_transmission("achievement"),
                    hook=lambda led, i: led)
    assert identity == walk(PARAMS, find_transmission("achievement"))


def test_relationship_drift_is_caught_across_transmissions():
    """One relationship id must agree with itself across the WHOLE
    registry: an impostor transmission reusing ige_earnings with a
    different band is drift, even though each transmission is internally
    consistent."""
    impostor = Transmission(
        outcome="earnings_mirror", unit="gap_multiplier",
        entry="displacement->child_earnings", entry_label="child_earnings",
        steps=(TransmissionStep(
            link="child_achievement_sd->grandchild_achievement_sd",
            kind="gap", relationship="ige_earnings", support=()),),
    )
    original = mod.TRANSMISSIONS
    mod.TRANSMISSIONS = (EARNINGS, impostor)
    try:
        assert "ige_earnings" in drift_relationships(PARAMS)
    finally:
        mod.TRANSMISSIONS = original
    assert drift_relationships(PARAMS) == []  # shipped registry stays clean


def test_duplicate_outcome_claims_are_refused_at_load():
    rogue = dataclasses.replace(EARNINGS, outcome="achievement")
    original = mod.TRANSMISSIONS
    mod.TRANSMISSIONS = (ACHIEVEMENT, rogue)
    try:
        with pytest.raises(ValueError, match="'achievement'"):
            load_transmissions(PARAMS)
    finally:
        mod.TRANSMISSIONS = original


def test_transmission_without_steps_is_refused():
    empty = dataclasses.replace(EARNINGS, steps=())
    original = mod.TRANSMISSIONS
    mod.TRANSMISSIONS = (empty,)
    try:
        with pytest.raises(ValueError, match="no steps"):
            load_transmissions(PARAMS)
    finally:
        mod.TRANSMISSIONS = original


def test_boundary_role_is_refused_on_steps_too():
    boundary_step = tuple(
        dataclasses.replace(r, evidence_role="boundary")
        if r.link == GREATGRANDCHILD else r for r in PARAMS.parameters)
    with pytest.raises(ValueError, match="step.*boundary"):
        load_transmissions(ParameterSet(version="t", parameters=boundary_step))


def test_registry_units_are_pinned_to_the_node_table():
    """A fabricated Transmission mislabeling its unit would mislabel every
    generation it walks; the registry's units are the node table's."""
    from downstream.params import load_nodes

    nodes = load_nodes(PARAMS_DIR / "nodes.csv")
    for t in (EARNINGS, ACHIEVEMENT):
        entry = PARAMS.by_link(t.entry)
        assert t.entry_label == entry.to_node
        assert t.unit == nodes[entry.to_node].unit
        for s in t.steps:
            row = PARAMS.by_link(s.link)
            assert nodes[row.from_node].unit == nodes[row.to_node].unit


def test_walk_recurses_to_arbitrary_depth_on_admitted_edges():
    """The recursion is unrolled copies of ONE relationship: repeating an
    admitted step walks further generations with composed labels, no
    new machinery, no drift."""
    deep = dataclasses.replace(EARNINGS, steps=EARNINGS.steps + (
        EARNINGS.steps[1], EARNINGS.steps[1], EARNINGS.steps[1]))
    out = walk(PARAMS, deep)
    assert list(out) == [
        "child", "grandchild", "greatgrandchild", "greatgreatgrandchild",
        "greatgreatgreatgrandchild", "greatgreatgreatgreatgrandchild"]
    exp = out["greatgrandchild"].apply(
        GAP, PARAMS.by_link(GREATGRANDCHILD),
        causal_role="structural_transmission_assumption")
    assert out["greatgreatgrandchild"] == exp
    assert all(led.unit == "gap_multiplier" for led in out.values())
    assert drift_relationships(PARAMS) == []  # same band everywhere: no drift


def test_linear_shift_survives_degenerate_bands():
    from downstream.ledger import LINEAR_SHIFT, start

    def param(link, point, low, high):
        return Parameter(link=link, from_node="f", to_node="t", point=point,
                         low=low, high=high, tier="canonical", citation="c",
                         population_scope="s", notes="", dist="", evidence_role="structural")

    # zero-width bands on both sides: everything collapses to the point
    led = start("a", "sd_delta", 0.0).apply(DIRECT, param("e", -0.02, -0.02, -0.02))
    out = led.apply(LINEAR_SHIFT, param("t", 0.4, 0.4, 0.4))
    assert (out.point, out.low, out.high) == pytest.approx((-0.008, -0.008, -0.008))
    # a null parent shift transmits null regardless of the slope
    out0 = start("a", "sd_delta", 0.0).apply(
        DIRECT, param("e", 0.0, -0.01, 0.01)).apply(
        LINEAR_SHIFT, param("t", 0.4, 0.38, 0.42))
    assert out0.point == 0.0 and out0.low <= 0.0 <= out0.high
    # a slope band above 1 (extrapolation) never inverts the ordering
    out_big = led.apply(LINEAR_SHIFT, param("t", 1.3, 1.2, 1.4))
    assert out_big.low == pytest.approx(1.4 * -0.02)
    assert out_big.high == pytest.approx(1.2 * -0.02)
    assert out_big.low <= out_big.point <= out_big.high


def test_cli_walk_refuses_unknown_and_blocked_outcomes_cleanly(capsys):
    """A typo or a blocked candidate is a usage error naming what DOES
    walk — never a raw KeyError traceback."""
    from downstream.cli import main

    for name in ("nosuchoutcome", "divorce", "education_years",
                 "adult_depression"):
        with pytest.raises(SystemExit) as ei:
            main(["transmissions", "--walk", name])
        assert ei.value.code == 2
    err = capsys.readouterr().err
    assert "earnings" in err and "achievement" in err


def test_cli_transmissions_refuses_a_broken_registry_cleanly(tmp_path, capsys):
    """A params dir missing an admitted row degrades to a clean CLI
    error (and an audit ERROR finding), not a traceback."""
    work = tmp_path / "params"
    shutil.copytree(PARAMS_DIR, work,
                    ignore=shutil.ignore_patterns("__pycache__"))
    kept = [ln for ln in (work / "parameters.csv").read_text().splitlines()
            if not ln.startswith("displacement_event->child_achievement_sd,")]
    (work / "parameters.csv").write_text("\n".join(kept) + "\n", encoding="utf-8")
    from downstream.cli import main

    with pytest.raises(SystemExit) as ei:
        main(["transmissions", "--params", str(work)])
    assert ei.value.code == 2
    assert "failed to load" in capsys.readouterr().err
    hits = [f for f in audit(work) if f.check == "transmission"]
    assert hits and hits[0].severity == ERROR
    assert "failed to load" in hits[0].message
