import pytest

from downstream.county_rates import CountyRateObservation, beta_binomial_posterior


def test_beta_binomial_posterior_shrinks_sparse_county_and_is_seeded():
    row = CountyRateObservation("01001", "mortality", 2, 1_000, "prime-age men", "2015-19", "source")
    a = beta_binomial_posterior(row, .005, 2_000, draws=200, seed=4)
    b = beta_binomial_posterior(row, .005, 2_000, draws=200, seed=4)
    assert a == b
    assert .002 < a["posterior"]["mean"] < .005
    assert a["posterior"]["p05"] <= a["posterior"]["p50"] <= a["posterior"]["p95"]


def test_beta_binomial_refuses_non_probability_or_nonpositive_prior():
    row = CountyRateObservation("01001", "mortality", 2, 1_000, "prime-age men", "2015-19", "source")
    with pytest.raises(ValueError):
        beta_binomial_posterior(row, 0, 2_000)
    with pytest.raises(ValueError):
        beta_binomial_posterior(row, .005, 0)
