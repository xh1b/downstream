from copy import deepcopy
import json

import pytest

from downstream.household import household_comparison
from downstream.params import default_dir


def example():
    return json.loads((default_dir().parent/'validation/household_five_year_input.json').read_text())


def test_zero_duration_identical_reference_cancels_exactly():
    p=example();p['event']['unemployed_years']=0
    result=household_comparison(p)
    assert result['cumulative_earnings_difference_usd_2024']==0
    assert all(r['displacement_minus_reference']==0 for r in result['annual'])


def test_one_year_displacement_uses_a_supplied_duration_not_a_permanent_shock():
    p=example();result=household_comparison(p)
    first=result['annual'][0]
    assert first['displacement_minus_reference']==-65000
    assert first['displacement']['adults'][0]['state_probabilities']['U']==1
    assert result['annual'][1]['displacement']['adults'][0]['state_probabilities']['E']>0
    assert result['annual'][4]['children_ages']==[15,17]
    for r in result['annual']:
        assert r['reference']['adults'][1]==r['displacement']['adults'][1]
        for arm in ('reference','displacement'):
            for adult in r[arm]['adults']:
                assert sum(adult['state_probabilities'].values())==pytest.approx(1)
    assert result['sparse_cells']
    assert result['uncertainty']['intervals'] is None
    assert not result['eligible_for_public_headline']


def test_forced_two_year_duration_and_declared_scars():
    p=example();p['event']['unemployed_years']=2
    p['event']['reemployment_earnings_multipliers']=[1,1,.8,.9,1]
    with pytest.raises(ValueError,match='assumption'):household_comparison(p)
    p['event']['earnings_path_assumption']='supplied recovery path, not a causal estimate'
    result=household_comparison(p)
    assert all(r['displacement']['adults'][0]['expected_earnings_usd_2024']==0 for r in result['annual'][:2])
    assert result['annual'][2]['displacement']['adults'][0]['expected_earnings_usd_2024']>0


def test_sparse_cells_require_explicit_acceptance():
    p=example();p['allow_sparse_cells']=False
    with pytest.raises(ValueError,match='sparse'):household_comparison(p)


@pytest.mark.parametrize('change',[{'transition_assumption':'estimated_causal'},{'follow_up_years':6},
                                  {'follow_up_years':True},{'members':[]},{'children':[True]}])
def test_invalid_household_contract_fails(change):
    with pytest.raises(ValueError):household_comparison({**example(),**change})


def test_event_reference_must_be_employed_and_ids_unique():
    p=example();p['members'][0]['employment_state']='U'
    with pytest.raises(ValueError,match='employed'):household_comparison(p)
    p=example();p['members'].append(deepcopy(p['members'][0]))
    with pytest.raises(ValueError,match='unique'):household_comparison(p)
