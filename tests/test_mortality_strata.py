# @ref:test-mortality-strata
# Method: @link:integration-mortality.
# Implementation: @link:code-mortality-strata.
# @tag:mortality @tag:testing
from copy import deepcopy
import math

import pytest

from downstream.mortality_strata import project_mortality_cohort


def example(age=34, sex='Male', workers=1000, years=2):
    return {'source':'fixture','method':'fixture','transport_rationale':'declared hypothetical projection',
            'projection_assumption':'constant_source_window_log_odds','follow_up_years':years,
            'strata':[dict(age_at_event=age,sex=sex,workers=workers,tenure_years=6,exposure_type='mass layoff')]}


def test_aging_crosses_baseline_band_but_keeps_event_age_response():
    result=project_mortality_cohort(example())
    row=result['supported_strata'][0]
    rates=row['aging_bands']['annual_baseline_rates']
    assert rates[1]>rates[0]
    assert row['fixed_baseline']['annual_baseline_rates']==[rates[0]]*2
    risks=[1-math.exp(-r) for r in rates]
    odds=math.exp(.313)
    expected=1000*(math.prod(1-b for b in risks)-math.prod(1-odds*b/(1-b+odds*b) for b in risks))
    assert row['aging_bands']['point']==pytest.approx(expected)
    assert row['source_contrast']['age_min']=='30'


def test_exact_weighted_aggregation_is_invariant_to_splitting_strata():
    a=example(workers=1000)
    b=deepcopy(a)
    b['strata']=[{**a['strata'][0],'workers':100} for _ in range(10)]
    left,right=project_mortality_cohort(a),project_mortality_cohort(b)
    for mode in ('fixed_baseline','aging_bands'):
        assert left['whole_cohort_excess_deaths'][mode]['point']==pytest.approx(right['whole_cohort_excess_deaths'][mode]['point'])


def test_unsupported_exposure_stays_unknown_not_zero():
    payload=example()
    payload['strata'].append({**payload['strata'][0],'sex':'Female','workers':500})
    result=project_mortality_cohort(payload)
    assert result['covered_workers']==1000
    assert result['unmodeled_workers']==500
    assert result['whole_cohort_excess_deaths'] is None
    assert not result['eligible_for_public_headline']


def test_older_source_group_keeps_protective_estimate():
    r=project_mortality_cohort(example(age=65,years=10))['covered_expected_excess_deaths']['aging_bands']
    assert r['point']<0 and r['low']<0<r['high']


@pytest.mark.parametrize('change',[{'projection_assumption':'inferred'}, {'follow_up_years':True},
                                  {'follow_up_years':23},{'source':''},{'strata':[]}])
def test_missing_or_unsupported_projection_contract_fails(change):
    with pytest.raises(ValueError):project_mortality_cohort({**example(),**change})


@pytest.mark.parametrize('change',[{'age_at_event':30.5},{'workers':float('nan')},
                                  {'tenure_years':True},{'sex':'invalid'}])
def test_invalid_strata_fail(change):
    p=example();p['strata'][0].update(change)
    with pytest.raises(ValueError):project_mortality_cohort(p)


def test_zero_horizon_has_zero_contrast():
    r=project_mortality_cohort(example(years=0))['covered_expected_excess_deaths']
    assert r['aging_bands']['point']==r['fixed_baseline']['point']==0
