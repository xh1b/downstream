"""Generative invariants for the numerical kernel (Hypothesis)."""
from dataclasses import replace

import pytest
from hypothesis import given, settings, strategies as st

from downstream.ledger import GAP, LEVEL, start
from downstream.mortality import excess_deaths, odds_risk
from downstream.params import load_all
from downstream.place import shrink


FINITE = st.floats(min_value=1e-6, max_value=10.0, allow_nan=False, allow_infinity=False)
PARAM = load_all()["params"].parameters[0]


@settings(max_examples=100, deadline=None)
@given(x=FINITE, a=FINITE, b=FINITE)
def test_level_envelope_is_exact_over_all_corners(x, a, b):
    lo, hi = sorted((a, b))
    p = replace(PARAM, low=lo, point=(lo + hi) / 2, high=hi)
    out = start("x", "gap_multiplier", x).apply(LEVEL, p)
    assert out.low == pytest.approx(min(x * lo, x * hi))
    assert out.high == pytest.approx(max(x * lo, x * hi))
    assert out.low <= out.point <= out.high


@settings(max_examples=100, deadline=None)
@given(x0=st.floats(min_value=-2, max_value=3, allow_nan=False, allow_infinity=False),
       a=FINITE, b=FINITE)
def test_gap_envelope_matches_all_corners(x0, a, b):
    lo, hi = sorted((a, b))
    p = replace(PARAM, low=lo, point=(lo + hi) / 2, high=hi)
    out = start("x", "gap_multiplier", x0).apply(GAP, p)
    corners = [1 - t * (1 - x0) for t in (lo, hi)]
    assert out.low == pytest.approx(min(corners))
    assert out.high == pytest.approx(max(corners))
    assert out.low <= out.point <= out.high


@settings(max_examples=100, deadline=None)
@given(baseline=st.floats(min_value=0, max_value=0.95, allow_nan=False, allow_infinity=False),
       peak=st.floats(min_value=1, max_value=30, allow_nan=False, allow_infinity=False),
       sustained=st.floats(min_value=1, max_value=30, allow_nan=False, allow_infinity=False),
       years=st.floats(min_value=0, max_value=80, allow_nan=False, allow_infinity=False),
       workers=st.floats(min_value=0, max_value=1e6, allow_nan=False, allow_infinity=False))
def test_survival_excess_deaths_is_bounded_and_monotone(baseline, peak, sustained, years, workers):
    value = excess_deaths(workers, baseline, peak, sustained, years)
    assert 0 <= value <= workers
    assert odds_risk(baseline, peak) >= baseline
    assert odds_risk(baseline, sustained) >= baseline
    assert excess_deaths(workers, baseline, peak + 0.01, sustained, years) >= value
    assert excess_deaths(workers, baseline, peak, sustained + 0.01, years) >= value


@settings(max_examples=100, deadline=None)
@given(n=st.floats(min_value=0, max_value=1e8, allow_nan=False, allow_infinity=False),
       k=st.floats(min_value=0, max_value=1e8, allow_nan=False, allow_infinity=False),
       local=st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False),
       national=st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False))
def test_partial_pooling_is_a_convex_combination(n, k, local, national):
    value, weight = shrink(local, n, national, k)
    assert 0 <= weight <= 1
    assert min(local, national) <= value <= max(local, national)
    assert value == pytest.approx((1 - weight) * national + weight * local)
