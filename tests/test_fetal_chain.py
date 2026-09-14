"""Fetal dose-response chain (v1.45): birth weight walks to adult outcomes.

The in-utero cohort is a DIFFERENT population from the childhood-exposure
cohort of displacement->child_earnings; these tests pin the composition
arithmetic and the scoping that keeps the two channels from being stacked.
"""
from dataclasses import replace

import pytest

from downstream.ledger import CHAIN_KINDS, DIRECT, GAP_LOG, chain, start, validate_chain
from downstream.mc import simulate_chain
from downstream.params import ParameterSet, load_all


def parts():
    return load_all()


def test_fetal_links_are_chain_admitted():
    assert CHAIN_KINDS["displacement->infant_birth_weight"] == DIRECT
    for link in ("infant_birth_weight->child_earnings",
                 "infant_birth_weight->adult_type2_diabetes_hazard",
                 "infant_birth_weight->adult_cardiovascular_disease_hazard"):
        assert CHAIN_KINDS[link] == GAP_LOG


def test_birth_weight_composes_to_child_earnings():
    p = parts()
    links = ["displacement->infant_birth_weight", "infant_birth_weight->child_earnings"]
    kinds = [DIRECT, GAP_LOG]
    validate_chain(p["params"], links, kinds, p["nodes"])
    led = chain(p["params"], links, "in_utero_earnings", "gap_multiplier", kinds)
    bw = p["params"].by_link("displacement->infant_birth_weight")
    e = p["params"].by_link("infant_birth_weight->child_earnings")
    assert led.point == bw.point ** e.point  # exact same arithmetic as the ledger
    assert led.point == pytest.approx(0.9541 ** 0.10, abs=1e-6)
    assert led.low <= led.point <= led.high
    # ~-0.5% adult earnings: an order of magnitude under the childhood channel.
    assert 1 - led.point < 0.01


def test_birth_weight_composes_to_disease_hazards():
    p = parts()
    for link, or_per_kg in (("infant_birth_weight->adult_type2_diabetes_hazard", 0.78),
                            ("infant_birth_weight->adult_cardiovascular_disease_hazard", 0.835)):
        led = chain(p["params"], ["displacement->infant_birth_weight", link],
                    "in_utero_hazard", "odds_ratio", [DIRECT, GAP_LOG])
        # Cross-check against the source scale: the composed odds ratio must
        # reproduce the published per-kg OR at the equivalent BW change
        # (one kg on the declared 3.4 kg anchor).
        e = p["params"].by_link(link)
        # A 1 kg change is a multiplier of (mu+1)/mu on the declared anchor;
        # raising it to the row's elasticity must reproduce the published OR.
        per_kg = (4.4 / 3.4) ** e.point
        assert per_kg == pytest.approx(or_per_kg, abs=2e-3)
        # A BW loss must RAISE the hazard, and the band must stay ordered.
        assert led.point > 1
        assert led.low <= led.point <= led.high


def test_simulate_chain_honors_fetal_links_with_pinned_bands():
    p = parts()
    links = ["displacement->infant_birth_weight", "infant_birth_weight->child_earnings"]
    pinned = []
    for link in links:
        row = p["params"].by_link(link)
        pinned.append(replace(row, low=row.point, high=row.point))
    params = ParameterSet("pinned_fetal", tuple(pinned))
    result = simulate_chain(params, links, base=1.0,
                            kinds=[DIRECT, GAP_LOG], draws=8,
                            nodes=p["nodes"], use_declared_correlations=False)
    assert result["mean"] == pytest.approx(0.9541 ** 0.10, abs=1e-3)
    assert result["p05"] == pytest.approx(result["mean"], abs=1e-3)
    assert result["p95"] == pytest.approx(result["mean"], abs=1e-3)


def test_gap_log_allows_negative_exponent_band_but_never_a_nonpositive_base():
    p = parts()
    bw = p["params"].by_link("displacement->infant_birth_weight")
    t2d = p["params"].by_link("infant_birth_weight->adult_type2_diabetes_hazard")
    led = start("bw", "gap_multiplier").apply(DIRECT, bw).apply(GAP_LOG, t2d)
    # Negative exponents flip the monotonicity: the lower BW edge of the
    # entry band produces the HIGH hazard edge.
    assert led.low < led.point < led.high
    with pytest.raises(ValueError, match="strictly positive"):
        start("bw", "gap_multiplier", value=0.0).apply(GAP_LOG, t2d)
    with pytest.raises(ValueError, match="strictly positive"):
        start("bw", "gap_multiplier", value=-0.5).apply(GAP_LOG, t2d)
