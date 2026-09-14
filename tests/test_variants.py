"""Traps for the structural-variant ensemble.

Each trap names the defect it hunts:
- a variant silently replacing the baseline in any shipped output
- the gap-additive variant claiming MORE child earnings than the
  direct estimate alone (adding causes can only add harm)
- decay variants landing on the wrong side of the baseline
- the spread not actually spanning the rows it reports
- the log-elasticity alternate publishing a number without its
  composition step, its structural causal role, or its citation
"""

from __future__ import annotations

import pytest

from downstream.children import child_line
from downstream.params import load_all
from downstream.variants import VARIANT_IDS, _log_elasticity_child, run_ensemble

PARAMS = load_all()["params"]


def test_baseline_row_equals_shipped_model():
    out = run_ensemble(PARAMS)
    base = [r for r in out["variants"] if r["variant"] == "baseline"][0]
    shipped = child_line(PARAMS)
    assert base["child_gap"]["point"] == round(shipped["child"].point, 4)
    assert base["grandchild_gap"]["point"] == round(shipped["grandchild"].point, 4)


def test_registry_ids_stable_and_all_present():
    out = run_ensemble(PARAMS)
    assert tuple(r["variant"] for r in out["variants"]) == VARIANT_IDS


def test_gap_additive_adds_harm_never_removes():
    out = run_ensemble(PARAMS)
    by = {r["variant"]: r for r in out["variants"]}
    assert by["parallel_gap_additive"]["child_gap"]["point"] < by["baseline"]["child_gap"]["point"], (
        "composing additional disadvantage streams must not RAISE child earnings"
    )


def test_decay_ordering_brackets_baseline():
    out = run_ensemble(PARAMS)
    by = {r["variant"]: r for r in out["variants"]}
    half = by["ige_decay_half"]["grandchild_gap"]["point"]
    power = by["ige_decay_power"]["grandchild_gap"]["point"]
    baseline = by["baseline"]["grandchild_gap"]["point"]
    assert half < baseline < power


def test_spread_spans_the_rows():
    out = run_ensemble(PARAMS)
    pts = [r["grandchild_gap"]["point"] for r in out["variants"]]
    assert out["spread"]["grandchild_point_min"] == min(pts)
    assert out["spread"]["grandchild_point_max"] == max(pts)


def test_ensemble_deterministic():
    assert run_ensemble(PARAMS) == run_ensemble(PARAMS)


def test_variant_envelopes_contain_points():
    for row in run_ensemble(PARAMS)["variants"]:
        for key in ("child_gap", "grandchild_gap"):
            assert row[key]["low"] <= row[key]["point"] <= row[key]["high"]


def test_log_elasticity_variant_is_a_role_tagged_ledger_step():
    out = _log_elasticity_child(PARAMS)
    steps = out["grandchild"].steps
    assert len(steps) == 2, "direct step plus the transmission composition step"
    step = steps[-1]
    row = PARAMS.by_link("child_earnings->grandchild_earnings")
    assert step.kind == "gap_log_elastic"
    assert step.link == row.link
    assert step.causal_role == "structural_transmission_assumption"
    assert step.evidence_role == row.evidence_role == "structural"
    assert step.population_scope == row.population_scope and step.population_scope
    assert step.citation == row.citation


def test_log_elasticity_corners_match_the_finite_change_map():
    from downstream.children import CHILD_DIRECT, GRANDCHILD
    out = _log_elasticity_child(PARAMS)
    d = PARAMS.by_link(CHILD_DIRECT)
    t = PARAMS.by_link(GRANDCHILD)
    g = out["grandchild"]
    assert g.point == pytest.approx(d.point ** t.point)
    corners = [v ** tt for v in (d.low, d.high) for tt in (t.low, t.high)]
    assert g.low == pytest.approx(min(corners))
    assert g.high == pytest.approx(max(corners))


def test_log_elastic_rule_retains_no_more_than_the_linear_rule():
    shipped = child_line(PARAMS)["grandchild"].point
    finite = _log_elasticity_child(PARAMS)["grandchild"].point
    direct = PARAMS.by_link("displacement->child_earnings").point
    t = PARAMS.by_link("child_earnings->grandchild_earnings").point
    assert 0 < direct < 1 and 0 < t < 1
    assert finite <= shipped, "for 0<v<1 the finite-change map sits below its Taylor expansion"
    assert finite == pytest.approx(direct ** t)


def test_gap_log_takes_negative_exponents_but_never_a_nonpositive_base():
    from dataclasses import replace

    from downstream.ledger import GAP_LOG, start
    from downstream.params import Parameter

    p = Parameter(link="x->y", from_node="x", to_node="y", point=0.4, low=0.2, high=0.6,
                  tier="canonical", citation="t:2000", population_scope="test",
                  evidence_role="structural")
    # Negative exponents are legal since v1.45 (protective gradients:
    # more birth weight, less disease risk flip the monotonicity).
    negative_band = replace(p, point=-0.4, low=-0.6, high=-0.2)
    led = start("y", "gap_multiplier", value=0.5).apply(GAP_LOG, negative_band)
    assert led.low <= led.point <= led.high
    assert led.point == pytest.approx(0.5 ** -0.4)
    # A non-positive base stays undefined for fractional powers.
    with pytest.raises(ValueError, match="strictly positive"):
        start("y", "gap_multiplier", value=-0.5).apply(GAP_LOG, p)
    with pytest.raises(ValueError, match="strictly positive"):
        start("y", "gap_multiplier", value=0.0).apply(GAP_LOG, p)


def test_chain_refuses_the_log_elastic_rule():
    from downstream.ledger import chain
    parts = load_all()
    with pytest.raises(ValueError, match="requires 'gap' composition"):
        chain(PARAMS, ["child_earnings->grandchild_earnings"], "g", "gap_multiplier",
              ["gap_log_elastic"], parts["nodes"])
