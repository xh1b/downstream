"""Traps for the structural-variant ensemble.

Each trap names the defect it hunts:
- a variant silently replacing the baseline in any shipped output
- the gap-additive variant claiming MORE child earnings than the
  direct estimate alone (adding causes can only add harm)
- decay variants landing on the wrong side of the baseline
- the spread not actually spanning the rows it reports
"""

from __future__ import annotations

import pytest

from downstream.children import child_line
from downstream.params import load_all
from downstream.variants import VARIANT_IDS, run_ensemble

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
