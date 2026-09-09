from dataclasses import replace
import pytest
from downstream.params import load_all
from downstream.policy import PolicyCase, compare_policies
from downstream.scenario import ScenarioInput


def case(n, **kwargs):
    return PolicyCase('synthetic fixture', 'fixture', 'hypothetical exposure, not an estimate', ScenarioInput(n), **kwargs)


def test_identical_policy_cancels_shared_uncertainty():
    p=load_all(); a=case(100, exposure_low=80, exposure_high=120)
    out=compare_policies(p['params'], p['baselines'], a, a)
    assert all(r['point']==r['low']==r['high']==0 for r in out['policy_minus_baseline'].values())


def test_policy_lower_exposure_reduces_losses_and_widens_exposure_envelope():
    p=load_all(); a=case(100); b=case(50, exposure_low=25, exposure_high=75)
    out=compare_policies(p['params'], p['baselines'], a,b)
    assert all(r['point'] < 0 for r in out['policy_minus_baseline'].values())
    for key,row in out['policy']['parameter_and_exposure_envelope'].items():
        fixed=out['policy']['parameter_envelope']['modeled'][key]
        assert row['low'] <= fixed['low'] <= fixed['high'] <= row['high']


def test_policy_requires_exposure_provenance_and_valid_bounds():
    with pytest.raises(ValueError): case(10, exposure_low=11)
    with pytest.raises(ValueError): replace(case(10), source='')
