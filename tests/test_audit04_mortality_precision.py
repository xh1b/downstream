# @ref:test-audit04-mortality-precision
# Method: @link:doc-mortality-source-reconciliation-2026-09-10.
# Implementation: @link:code-mortality; @link:code-params.
# @tag:mortality @tag:testing
"""Independent high-precision checks for near-null survival contrasts."""
from decimal import Decimal, localcontext

import pytest

from downstream.mortality import excess_deaths_profile, rate_to_risk, SOURCE_PROFILE_PHASES


def profile(value):
    return dict.fromkeys((name for name,_ in SOURCE_PROFILE_PHASES),value)


def reference(workers,baseline,odds,years):
    with localcontext() as context:
        context.prec=70
        n,b,o=map(Decimal.from_float,(workers,baseline,odds))
        q=o*b/(1-b+o*b)
        return float(n*((1-b)**years-(1-q)**years))


@pytest.mark.parametrize('years',[.5,6.5,20,100])
def test_null_profile_cancels_exactly_for_fractional_and_long_horizons(years):
    assert excess_deaths_profile(1e9,.004944,profile(1.0),years)==0


@pytest.mark.parametrize('odds',[1.00000001,.99999999,2.0,.5])
def test_tiny_baseline_signed_contrast_matches_independent_decimal_arithmetic(odds):
    expected=reference(1e12,1e-8,odds,20)
    actual=excess_deaths_profile(1e12,1e-8,profile(odds),20)
    assert actual==pytest.approx(expected,rel=2e-8,abs=1e-12)


def test_rate_conversion_preserves_tiny_positive_hazards():
    assert rate_to_risk(1e-18)==pytest.approx(1e-18,rel=1e-14,abs=0)


@pytest.mark.parametrize('baseline',[0,1])
def test_boundary_baseline_has_no_contrast(baseline):
    assert excess_deaths_profile(1e9,baseline,profile(2.0),20)==0


def test_very_long_protective_profile_stays_finite_and_within_count_bounds():
    result=excess_deaths_profile(1000,.9,profile(1e-20),1e308)
    assert -1000<=result<=0
