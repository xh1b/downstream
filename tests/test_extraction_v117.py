"""v1.17 pins: the adh2013 spillover link WIRED into the V1 panel
earnings row (the open wiring left by v1.12's landing of the row).

What must hold:
- the direct-only row keeps its v1.12 miss exactly — misses publish,
  they are not overwritten by a better-composed row
- the composed row (direct + spillover) must deepen the modeled fall,
  close part of the gap, and still undershoot — the residual is
  published, not tuned away
- the aggregate cross-check (implied total male wage response vs ADH
  2013 T6 col 2) covers in both directions
"""
import pytest

from downstream.params import load_all
from downstream.validate import v1_panel

P = v1_panel(load_all()["params"])
TESTS = P["tercile_tests"]
DIRECT = [t for t in TESTS if t["outcome"].endswith("direct stream only")][0]
COMPOSED = [t for t in TESTS if t["outcome"].endswith("direct + spillover composed")][0]
XC = P["wage_response_cross_check"]


def test_direct_only_miss_retained_unchanged():
    m = DIRECT["modeled_gap_usd"]
    # pinned v1.12-era state (deterministic panel data): ~5x undershoot
    assert m["point"] == pytest.approx(-73.59, abs=0.02)
    assert m["low"] == pytest.approx(-91.99, abs=0.02)
    assert m["high"] == pytest.approx(-55.19, abs=0.02)
    assert DIRECT["measured_gap_usd"] == pytest.approx(-352.73, abs=0.02)
    assert DIRECT["measured_inside_modeled_band"] is False


def test_composed_row_deepens_the_modeled_fall():
    # the spillover is a NEGATIVE wage response: wiring it must deepen
    # the modeled fall, never soften it (sign-direction trap)
    assert COMPOSED["modeled_gap_usd"]["point"] < DIRECT["modeled_gap_usd"]["point"] < 0
    assert COMPOSED["sign_agreement"] is True


def test_composed_row_band_monotone_and_state_pinned():
    m = COMPOSED["modeled_gap_usd"]
    assert m["low"] <= m["point"] <= m["high"]
    assert m["point"] == pytest.approx(-165.31, abs=0.02)
    assert m["low"] == pytest.approx(-237.03, abs=0.02)
    assert m["high"] == pytest.approx(-93.24, abs=0.02)


def test_composed_row_closes_part_of_the_gap_but_still_undershoots():
    # gap closure direction: composed must sit closer to the measured
    # fall than the direct-only row
    measured = COMPOSED["measured_gap_usd"]
    assert abs(measured - COMPOSED["modeled_gap_usd"]["point"]) < abs(
        measured - DIRECT["modeled_gap_usd"]["point"]
    )
    # pinned closure share: the link closes ~33% of the point-gap
    assert COMPOSED["gap_closure_share"] == pytest.approx(0.3286, abs=5e-4)
    # the residual undershoot PUBLISHES: measured stays outside the band
    assert COMPOSED["measured_inside_modeled_band"] is False


def test_composed_row_assumptions_declared():
    text = " ".join(COMPOSED["assumptions"]).lower()
    assert "additive" in text            # additivity declared, not silent
    assert "non-displaced share" in text  # who the spillover applies to
    assert "exp" in text                  # exact log-point conversion


def test_spillover_scope_caveat_declared():
    text = " ".join(COMPOSED["scope_caveats"])
    # the coefficient identifies nonmanufacturing noncollege workers;
    # applying it to the whole p25 population is the declared direction
    assert "NONmanufacturing" in text and "conservative" in text


def test_wage_response_cross_check_covers_both_ways():
    m = XC["model_logpts_per_1k"]
    meas = XC["measured_logpts_per_1k"]
    # measured CI arithmetic from the recorded T6 col 2 numbers
    assert meas["ci95"] == pytest.approx(
        [meas["point"] - 1.96 * meas["se"], meas["point"] + 1.96 * meas["se"]], abs=5e-4
    )
    # both coverage directions pinned: flippable only by evidence
    assert XC["model_point_inside_measured_ci"] is True
    assert XC["measured_point_inside_model_band"] is True
    # model point state pin
    assert m["point"] == pytest.approx(-1.408, abs=5e-3)
    # the model band must not be narrower than the measured CI (no
    # manufactured precision)
    assert m["low"] < meas["ci95"][0] and m["high"] > meas["point"]
