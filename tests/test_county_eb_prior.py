"""Empirical-Bayes prior-strength check for the county-mortality pooling.

Pins the method-of-moments EB yardstick (county_rates.empirical_bayes_
prior_person_years) against the committed male 45-54 export: the estimate
is recorded as a sensitivity check on the DECLARED k = 2000 prior
person-years (docs/DATA_SOURCES.md), never auto-imposed by the build.
"""
import dataclasses

import pytest

from downstream.county_mortality import count_observations, parse_export
from downstream.county_rates import CountyRateObservation, NationalRatePrior, \
    empirical_bayes_prior_person_years

EXPORT = "validation/cdc_wonder_county_male_45_54_2015_2019.csv"
METADATA = EXPORT.replace(".csv", ".metadata.json")


def _observations():
    metadata = __import__("json").loads(open(METADATA).read())
    return count_observations(parse_export(EXPORT, metadata=metadata))


def test_eb_yardstick_pinned_on_committed_export():
    report = empirical_bayes_prior_person_years(_observations(), 0.004944)
    assert report["counties"] == 2748
    # deterministic MoM arithmetic, pinned to 3 significant figures
    assert report["estimate_prior_person_years"] == pytest.approx(822.25, rel=1e-3)
    assert report["implied_gamma_shape"] == pytest.approx(4.0688, rel=1e-3)
    assert report["noise_share_of_spread"] == pytest.approx(0.1064, rel=1e-2)
    # visible-county pooled rate sits just above the Total-row pin: the
    # Total counts suppressed counties' deaths while county rows cannot
    assert report["pooled_rate_per_person_year"] == pytest.approx(0.0049483, rel=1e-5)
    assert 0 < report["shrinkage_weight_deciles"]["p50"]["shrinkage_weight"] < 1


def test_eb_refuses_when_noise_absorbs_all_spread():
    # identical true rates: observed spread equals Poisson noise -> full pooling
    obs = [CountyRateObservation(
        key=f"{i:05d}", outcome="o", population_scope="p", time_window="t",
        events=5, person_years=10_000.0, citation="c",
    ) for i in range(40)]
    report = empirical_bayes_prior_person_years(obs, 0.0005)
    assert report["estimate"] is None
    assert "full pooling" in report["reason"]


def test_eb_refuses_degenerate_inputs():
    with pytest.raises(ValueError):
        empirical_bayes_prior_person_years([], 0.005)
    obs = [CountyRateObservation(
        key=f"{i:05d}", outcome="o", population_scope="p", time_window="t",
        events=5, person_years=10_000.0, citation="c",
    ) for i in range(10)]
    with pytest.raises(ValueError):
        empirical_bayes_prior_person_years(obs, 0.005)  # too few counties
