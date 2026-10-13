from dataclasses import replace
import math

import pytest

from downstream.child_applicability import select_child_contrast
from downstream.params import load_all
from downstream.scenario import ScenarioInput, compute_counts, sample_counts
from downstream.study_library import load_library
from downstream.synthesis import load_study_estimates, synthesize
from downstream.params import default_dir


def test_source_library_keeps_subgroups_and_phases_separate():
    rows = load_library()
    assert len(rows) == 14
    assert rows['sullivan2007_offsets_4_5']['standard_error'] == .138
    assert rows['oreopoulos2008_q3']['point'] == .007
    result = synthesize(load_study_estimates(default_dir() / 'study_estimates.csv'))
    assert not result['reports']
    assert len(result['blocked']) == 14


@pytest.mark.parametrize('age,sex', [(0,'Male'), (20,'Male'), (12,'Female')])
def test_known_unsupported_children_block_the_count(age,sex):
    p=load_all()
    result=compute_counts(p['params'],p['baselines'],ScenarioInput(10,n_children=1,
        child_profiles=[{'age_at_displacement':age,'sex':sex}]))
    assert 'child_lifetime_earnings_lost_usd' not in result['modeled']
    assert result['child_applicability']['incompatible_children'] == [0]


def test_unknown_age_is_labeled_and_cannot_gain_headline_eligibility():
    p=load_all()
    result=compute_counts(p['params'],p['baselines'],ScenarioInput(10,n_children=1,
        child_profiles=[{'age_at_displacement':None,'sex':'Unknown'}]))
    assert result['child_applicability']['status']=='unknown'
    assert not result['modeled']['child_lifetime_earnings_lost_usd']['applicability']['eligible_for_public_headline']


@pytest.mark.parametrize('quartile,beta,se',[(1,-.143,.088),(2,-.117,.070),(3,.007,.065),(4,-.095,.068)])
def test_quartile_estimates_preserve_benefits_and_nulls(quartile,beta,se):
    p=load_all()
    selected=select_child_contrast(p['params'],quartile).by_link('displacement->child_earnings')
    assert selected.point==pytest.approx(math.exp(beta))
    assert selected.low==pytest.approx(math.exp(beta-1.96*se))
    assert selected.high==pytest.approx(math.exp(beta+1.96*se))
    assert selected.low < 1 < selected.high
    assert p['params'].by_link('displacement->child_earnings').point==.9076
    result=sample_counts(p['params'],p['baselines'],ScenarioInput(100,child_income_quartile=quartile,
        income_rank_definition='source distribution; illustrative target transport'),draws=64,nodes=p['nodes'])
    row=result['modeled']['child_lifetime_earnings_lost_usd']
    assert row['low']<0<row['high']
    assert row['parameter_interval_90']['p05']<row['parameter_interval_90']['p95']
    if quartile==3:assert row['point']<0
    # A sampled subgroup must not be reset to its point estimate.
    s=select_child_contrast(p['params'],quartile)
    r=s.by_link('displacement->child_earnings')
    s=replace(s,parameters=tuple(replace(x,point=r.low) if x.link==r.link else x for x in s.parameters))
    assert select_child_contrast(s,quartile) is s


@pytest.mark.parametrize('options',[{'child_income_quartile':True},{'child_income_quartile':1.0},
    {'child_income_quartile':1},{'child_profiles':[]},
    {'child_profiles':[{'age_at_displacement':True,'sex':'Male'}],'n_children':1},
    {'child_profiles':[{'age_at_displacement':10,'sex':'other'}],'n_children':1}])
def test_invalid_child_metadata_fails(options):
    with pytest.raises(ValueError):ScenarioInput(100,**options)
