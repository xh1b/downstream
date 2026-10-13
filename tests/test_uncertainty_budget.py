from copy import deepcopy
import json

import pytest

from downstream.params import default_dir, load_all
from downstream.uncertainty_budget import propagate_uncertainty


def example():
    p=json.loads((default_dir().parent/'validation/uncertainty_budget_input.json').read_text())
    p['draws']=64
    return p


def evaluate(payload):
    p=load_all()
    return propagate_uncertainty(p['params'],p['baselines'],payload,nodes=p['nodes'])


def test_joint_budget_is_reproducible_and_does_not_relabel_parameter_intervals():
    payload=example();before=deepcopy(payload)
    result=evaluate(payload)
    assert result==evaluate(payload)
    assert payload==before
    assert result['fixed_input_reference']['parameter_uncertainty']['scope']=='parameter uncertainty only'
    assert 'target-population transport error' in result['excluded']
    assert result['sampled_inputs']['sampled_workers']['p05']>=800
    assert result['sampled_inputs']['sampled_workers']['p95']<=1200
    rates=result['sampled_inputs']['sampled_baseline_rate_per_100k']
    assert rates['p05']<rates['p95'] and 490<rates['mean']<500
    assert result['process_intervals_90']['realized_exposed_deaths']['p05']>=0
    assert 'independent cohorts' in result['interpretation']


def test_equal_exposure_bounds_have_no_exposure_sampling_variation():
    p=example();p['exposure_model'].update(low=1000,high=1000)
    assert set(evaluate(p)['sampled_inputs']['sampled_workers'].values())=={1000}


def test_identical_mortality_structures_cancel_on_shared_joint_draw():
    from dataclasses import replace
    parts=load_all();params=parts['params']
    params=replace(params,parameters=tuple(replace(r,point=1,low=1,high=1)
        if r.link=='earnings_shock->mortality_sustained' else r for r in params.parameters))
    result=propagate_uncertainty(params,parts['baselines'],example(),nodes=parts['nodes'])
    assert set(result['expected_effect_intervals_90']['mortality_persistence_difference'].values())=={0}


@pytest.mark.parametrize('field,value',[('sex','Female'),('events',True),('person_years',float('inf')),('events',10)])
def test_baseline_scope_and_count_arithmetic_cannot_be_bypassed(field,value):
    p=example();p['baseline_counts'][field]=value
    with pytest.raises(ValueError):evaluate(p)


@pytest.mark.parametrize('field,value',[('distribution','empirical'),('low',True),('high',999),('source','')])
def test_unsupported_or_undocumented_exposure_model_fails(field,value):
    p=example();p['exposure_model'][field]=value
    with pytest.raises(ValueError):evaluate(p)


def test_demographic_profile_override_is_not_silently_ignored():
    p=example();p['scenario']['mortality_profile']='male_45_54_2015_2019'
    with pytest.raises(ValueError,match='national'):evaluate(p)
