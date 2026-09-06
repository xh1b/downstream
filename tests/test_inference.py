"""Adversarial traps for the analytic inference layer.

Each trap names the defect it hunts:
- moment algebra drifting from hand-computed values (silent wrong math)
- the exact mean disagreeing with the MC (sampler bug dressed as result)
- coverage drifting from nominal (a "90% band" that is not a 90% band)
- log-space shares applied to a non-multiplicative chain (the
  level-ratio bug in analytic disguise)
- negative variance passing silently (algebra violation)
"""

from __future__ import annotations

import math

import pytest

from downstream.children import CHILD_DIRECT, GRANDCHILD, child_line
from downstream.inference import (
    _loguniform_moments,
    _uniform_moments,
    analytic_chain,
    analytic_vs_mc,
    closure_coverage,
    logspace_variance_shares,
)
from downstream.params import load_all

PARTS = load_all()
PARAMS = PARTS["params"]
NODES = PARTS["nodes"]


def _grandchild(ps):
    return child_line(ps)["grandchild"].point


# --- trap: moment algebra silently wrong ------------------------------------

def test_uniform_moments_hand_computed():
    # U(0,1): E=0.5, E2=1/3
    assert _uniform_moments(0.0, 1.0) == pytest.approx((0.5, 1 / 3))
    # U(1,3): E=2, E2=(27-1)/(3*2)=13/3
    assert _uniform_moments(1.0, 3.0) == pytest.approx((2.0, 13 / 3))


def test_loguniform_moments_hand_computed():
    # log-uniform on [1, e]: E = (e-1)/1, E2 = (e^2-1)/2
    m, m2 = _loguniform_moments(1.0, math.e)
    assert m == pytest.approx(math.e - 1)
    assert m2 == pytest.approx((math.e**2 - 1) / 2)


def test_gap_moments_match_direct_simulation_of_bilinear():
    # gap step: V' = 1 - T + T*V with independent T, V. Verify the exact
    # identity against brute-force integration on a coarse grid.
    # Use synthetic bands: child U(0.86,0.96), IGE U(0.40,0.60).
    out = analytic_chain(
        PARAMS, [CHILD_DIRECT, GRANDCHILD], ["direct", "gap"], NODES
    )
    # brute force: uniform grid product (Simpson-grade for a test)
    n = 400
    s, s2 = 0.0, 0.0
    for i in range(n):
        g = 0.86 + (0.96 - 0.86) * (i + 0.5) / n
        for j in range(n):
            t = 0.40 + (0.60 - 0.40) * (j + 0.5) / n
            v = 1 - t * (1 - g)
            s += v
            s2 += v * v
    m, m2 = s / n**2, s2 / n**2
    assert out["mean"] == pytest.approx(m, abs=1e-6)
    assert out["var"] == pytest.approx(m2 - m * m, abs=1e-6)


def test_degenerate_pinned_chain_has_zero_variance():
    # pin every link: variance must be exactly 0, not negative noise
    from downstream.knobs import pin

    ps = pin(pin(PARAMS, CHILD_DIRECT, 0.91), GRANDCHILD, 0.55)
    out = analytic_chain(ps, [CHILD_DIRECT, GRANDCHILD], ["direct", "gap"], NODES)
    assert out["var"] == 0.0
    assert out["p05_normal"] == out["p95_normal"] == out["mean"]


# --- trap: sampler bug dressed as a result -----------------------------------

def test_exact_mean_agrees_with_mc_grandchild():
    analytic = analytic_chain(
        PARAMS, [CHILD_DIRECT, GRANDCHILD], ["direct", "gap"], NODES
    )
    rep = analytic_vs_mc(PARAMS, _grandchild, analytic, NODES, draws=10_000)
    assert rep["mean_diff_in_se"] < 3, (
        f"MC mean sits {rep['mean_diff_in_se']} SE from the exact mean — "
        "either the sampler or the algebra is wrong"
    )
    # sd agreement to ~1% (MC sd error at 10k draws is ~0.7%)
    assert rep["sd_mc"] == pytest.approx(rep["sd_analytic"], rel=0.02)


def test_normal_band_prices_skewness_not_hides_it():
    # the normal band and MC quantiles must be CLOSE but need not match;
    # a huge gap means the note lies about what the MC is for
    analytic = analytic_chain(
        PARAMS, [CHILD_DIRECT, GRANDCHILD], ["direct", "gap"], NODES
    )
    rep = analytic_vs_mc(PARAMS, _grandchild, analytic, NODES, draws=10_000)
    for side in ("p05", "p95"):
        gap = abs(rep[side]["normal"] - rep[side]["mc"])
        assert gap < 0.01, f"{side} normal-vs-MC gap {gap} too large to call skewness"


# --- trap: a "90% band" that is not a 90% band -------------------------------

def test_closure_coverage_hits_nominal_within_2se():
    out = closure_coverage(
        PARAMS, _grandchild, NODES, trials=600, draws=3000, seed=11
    )
    assert out["pass"], f"coverage drifted: {out['levels']}"
    row90 = [r for r in out["levels"] if r["nominal"] == 0.9][0]
    assert abs(row90["empirical"] - 0.9) < 2 * row90["binomial_se"]


def test_closure_coverage_catches_a_corrupted_band():
    # sabotage: a band built at the WRONG level must fail the test for
    # the level it claims (this is the trap proving the test has teeth)
    import downstream.inference as inf

    orig = inf._normal_quantile_band

    def corrupted(samples, level):
        lo, hi = orig(samples, level)
        return lo + 0.3 * (hi - lo), hi  # shifted band

    inf._normal_quantile_band = corrupted
    try:
        out = closure_coverage(
            PARAMS, _grandchild, NODES, trials=400, draws=2000, seed=5
        )
    finally:
        inf._normal_quantile_band = orig
    assert not out["pass"], "a corrupted band passed the closure test — it has no teeth"


# --- trap: log-space shares on a non-multiplicative chain ---------------------

def test_logspace_shares_refuse_gap_chains():
    with pytest.raises(ValueError, match="multiplicative"):
        logspace_variance_shares(
            PARAMS, [CHILD_DIRECT, GRANDCHILD], NODES, kinds=["direct", "gap"]
        )


def test_logspace_shares_exact_for_level_chain():
    # single level link: the share must be exactly 1.0 — no estimator noise
    out = logspace_variance_shares(
        PARAMS, ["displacement->worker_earnings"], NODES, kinds=["level"]
    )
    assert out["shares"][0]["share"] == 1.0


def test_logspace_shares_sum_to_one():
    links = ["displacement->worker_earnings", "displacement->child_earnings"]
    out = logspace_variance_shares(PARAMS, links, NODES, kinds=["level", "level"])
    total = sum(r["share"] for r in out["shares"])
    assert total == pytest.approx(1.0, abs=1e-6)


def test_analytic_chain_rejects_rate_kind():
    with pytest.raises(ValueError, match="never chained"):
        analytic_chain(
            PARAMS,
            ["earnings_shock->mortality_sustained"],
            ["rate"],
            NODES,
        )


def test_unknown_link_names_the_typo():
    with pytest.raises(KeyError, match="no_such_link"):
        analytic_chain(PARAMS, ["no_such_link"], ["level"], NODES)
