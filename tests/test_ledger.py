"""Compute checks for composition semantics — the core math."""

from pathlib import Path

import pytest

from downstream.ledger import DIRECT, GAP, LEVEL, RATE, chain, combine_parallel, start
from downstream.params import load

PARAMS = Path(__file__).resolve().parent.parent / "params" / "parameters.csv"


def test_loads_versioned_and_acyclic():
    params = load(PARAMS)
    assert params.parameters
    assert params.version == "v1.12"
    assert any(p.tier == "EXACT" for p in params.parameters)


def test_level_step_multiplies_band():
    led = start("x", "gap_multiplier").apply(LEVEL, load(PARAMS).by_link("displacement->worker_earnings"))
    assert (led.point, led.low, led.high) == (0.80, 0.75, 0.85)


def test_gap_step_propagates_in_gap_space_not_level_space():
    """THE regression trap: an IGE step must transform the gap, not
    multiply levels. Child gap 0.9076 through IGE 0.55 gives
    1 - 0.55*0.0924 = 0.94918 — NOT 0.91*0.55 = 0.5005."""
    params = load(PARAMS)
    child = start("child", "gap_multiplier").apply(DIRECT, params.by_link("displacement->child_earnings"))
    gc = child.apply(GAP, params.by_link("child_earnings->grandchild_earnings"))
    assert gc.point == pytest.approx(0.94918, abs=1e-6)
    assert gc.point > 0.9  # level composition would have given ~0.50
    # worst case = biggest IGE x biggest child gap
    assert gc.low == pytest.approx(1 - 0.60 * (1 - 0.844), abs=1e-6)
    assert gc.high == pytest.approx(1 - 0.40 * (1 - 0.976), abs=1e-6)


def test_band_always_brackets_point_and_never_inverts():
    params = load(PARAMS)
    led = chain(
        params,
        links=[
            "displacement->child_earnings",
            "child_earnings->grandchild_earnings",
            "grandchild_earnings->greatgrandchild_earnings",
        ],
        label="line",
        unit="gap_multiplier",
        kinds=[DIRECT, GAP, GAP],
    )
    assert led.low <= led.point <= led.high
    for s in led.steps:
        assert s.value[1] <= s.value[0] <= s.value[2]


def test_direct_step_replaces_value_and_carries_citation():
    params = load(PARAMS)
    led = start("x", "gap_multiplier").apply(DIRECT, params.by_link("displacement->child_earnings"))
    assert led.point == 0.9076
    assert led.steps[0].citation == "oreopoulos2008"
    assert led.steps[0].tier == "EXACT"


def test_rate_step_records_without_chaining():
    params = load(PARAMS)
    led = start("m", "rate_ratio").apply(RATE, params.by_link("earnings_shock->mortality_sustained"))
    assert led.point == 1.135  # recorded, not multiplied onto 1.0*1.17*...
    assert led.steps[0].kind == RATE


def test_every_step_of_the_full_line_is_cited():
    params = load(PARAMS)
    led = chain(
        params,
        links=["displacement->child_earnings", "child_earnings->grandchild_earnings"],
        label="line",
        unit="gap_multiplier",
        kinds=[DIRECT, GAP],
    )
    assert all(s.citation for s in led.steps)


def test_combine_parallel_adds_gaps_with_floor():
    """Two independent causes: gap 0.9076 and gap 0.95 -> 1 - (0.0924+0.05) = 0.8576."""
    params = load(PARAMS)
    a = start("a", "gap_multiplier").apply(DIRECT, params.by_link("displacement->child_earnings"))
    b = start("b", "gap_multiplier").apply(DIRECT, params.by_link("divorce->child_earnings"))
    combined = combine_parallel([a, b], "combined")
    assert combined.point == pytest.approx(1 - (0.0924 + 0.05), abs=1e-6)
    assert combined.low <= combined.point <= combined.high


def test_chain_rejects_mismatched_links_and_kinds():
    params = load(PARAMS)
    with pytest.raises(ValueError):
        chain(params, ["displacement->child_earnings"], "x", "gap_multiplier", kinds=[])


def test_unknown_link_fails_loudly():
    params = load(PARAMS)
    with pytest.raises(KeyError):
        params.by_link("nope->nothing")
