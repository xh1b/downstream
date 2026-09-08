"""v1.19 pins: the closure-selection design contrast added to the
structural-variant ensemble (the V2 item queued at v1.13).

What this file hunts:
- the contrast quietly becoming the shipped model (it is a VARIANT;
  the baseline row must stay the direct-anchor composition)
- the contrast being described without its evidence (Hilger fn31,
  wrong-signed closure-DD, assortative selection)
- the composed path drifting outside the direct anchor's band (the
  two literatures overlap; a drift means one is misread — V0's check)
- the direction of the disagreement being left undocumented (dropping
  the closure anchor moves the modeled child loss UP under current
  evidence — a reader must not assume the critique implies smaller
  losses)
"""
import pytest

from downstream.params import load_all
from downstream.variants import VARIANT_IDS, run_ensemble

P = run_ensemble(load_all()["params"])
BY = {r["variant"]: r for r in P["variants"]}
CC = BY["closure_selection_contrast"]
BASE = BY["baseline"]


def test_variant_registered_and_baseline_unchanged():
    assert "closure_selection_contrast" in VARIANT_IDS
    assert tuple(r["variant"] for r in P["variants"]) == VARIANT_IDS
    # baseline still the shipped model (direct anchor 0.9076)
    assert BASE["child_gap"]["point"] == pytest.approx(0.9076, abs=1e-4)


def test_contrast_state_pinned_to_ige_composition():
    # father gap 0.80 [0.75, 0.85] through IGE 0.55 [0.40, 0.60]:
    # child = 1 - t*(1-g): point 1-0.55*0.20, band corners 1-0.60*0.25 / 1-0.40*0.15
    c = CC["child_gap"]
    assert c["point"] == pytest.approx(1 - 0.55 * 0.20, abs=1e-4)
    assert c["low"] == pytest.approx(1 - 0.60 * 0.25, abs=1e-4)
    assert c["high"] == pytest.approx(1 - 0.40 * 0.15, abs=1e-4)
    # grandchild composes the same cited band on the variant child gap
    g = CC["grandchild_gap"]
    assert g["point"] == pytest.approx(1 - 0.55 * (1 - c["point"]), abs=1e-4)


def test_contrast_band_inside_direct_anchor_band():
    # the two literatures overlap: the composed band must sit inside the
    # direct anchor's [0.844, 0.976] — a drift means one is misread
    assert CC["child_gap"]["low"] >= BASE["child_gap"]["low"]
    assert CC["child_gap"]["high"] <= BASE["child_gap"]["high"]


def test_contrast_direction_pinned_loss_moves_up():
    # dropping the closure-exposed anchor LOWERS the modeled child gap
    # (child keeps less) under current evidence — the selection critique
    # does not imply smaller losses; this documents which way it bites
    assert CC["child_gap"]["point"] < BASE["child_gap"]["point"]


def test_contrast_description_carries_the_evidence():
    d = CC["description"]
    assert "fn31" in d and "wrong-signed" in d and "assortative" in d
    assert "NOT changed" in d or "not changed" in d.lower()
