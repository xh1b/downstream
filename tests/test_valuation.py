import pytest

from downstream.params import load_all
from downstream.scenario import ScenarioInput, compute_counts, sample_counts


def evaluate(rate, age=11, quartile=None, sampled=False):
    parts=load_all()
    scenario=ScenarioInput(1000,n_children=1,child_profiles=[{'age_at_displacement':age,'sex':'Male'}],
        child_income_quartile=quartile,income_rank_definition='source income distribution' if quartile else None,
        real_discount_rate=rate,valuation_year=2026)
    method=sample_counts if sampled else compute_counts
    return method(parts['params'],parts['baselines'],scenario,**({'draws':64,'nodes':parts['nodes']} if sampled else {}))


def test_zero_discount_career_value_equals_existing_undiscounted_count():
    result=evaluate(0)
    career=result['child_valuation']['projections']['constant_career_gap']
    assert career['point']==pytest.approx(result['modeled']['child_lifetime_earnings_lost_usd']['point'])
    assert career['undiscounted_point']==career['point']
    schedule=career['annual_schedules_per_worker_family'][0]
    assert schedule[0]['calendar_year']==2035
    assert schedule[-1]['age']==64
    assert all(row['discount_factor']==1 for row in schedule)


def test_positive_discount_and_later_receipts_reduce_present_loss():
    def point(rate,age):return evaluate(rate,age)['child_valuation']['projections']['constant_career_gap']['point']
    assert point(.05,11)<point(.03,11)<point(0,11)<point(-.01,11)
    assert point(.03,10)<point(.03,14)


def test_observed_age_window_is_separate_from_lifetime_projection():
    result=evaluate(.03)['child_valuation']
    observed=result['projections']['observed_adult_age_window']
    assert [r['age'] for r in observed['annual_schedules_per_worker_family'][0]]==list(range(25,34))
    assert observed['point']<result['projections']['constant_career_gap']['point']
    assert not result['eligible_for_public_headline']


def test_beneficial_subgroup_stays_signed_in_valuation_and_sampling():
    result=evaluate(.03,quartile=3,sampled=True)
    row=result['child_valuation']['projections']['constant_career_gap']
    assert row['point']<0 and row['low']<0<row['high']
    assert row['parameter_interval_90']['p05']<row['parameter_interval_90']['p95']
    assert set(result['parameter_uncertainty']['outcomes'])==set(result['modeled'])


@pytest.mark.parametrize('kw',[{'real_discount_rate':.03},{'valuation_year':2026},
    {'real_discount_rate':-1,'valuation_year':2026},
    {'real_discount_rate':float('nan'),'valuation_year':2026},
    {'real_discount_rate':.03,'valuation_year':True}])
def test_incomplete_or_invalid_valuation_input_fails(kw):
    with pytest.raises(ValueError):ScenarioInput(10,**kw)


@pytest.mark.parametrize('change',[{'unit':'usd_2023'},{'unit':'EUR'},{'value':-1}])
def test_incompatible_earnings_baseline_cannot_be_relabeled_as_2024_dollars(change):
    from dataclasses import replace
    from downstream.scenario import BaselineMissing
    parts=load_all()
    baselines={**parts['baselines'],'median_male_lifetime_earnings':replace(parts['baselines']['median_male_lifetime_earnings'],**change)}
    scenario=ScenarioInput(10,n_children=1,child_profiles=[{'age_at_displacement':11,'sex':'Male'}],
                           real_discount_rate=.03,valuation_year=2026)
    result=compute_counts(parts['params'],baselines,scenario)
    assert 'child_lifetime_earnings_lost_usd' not in result['modeled']
    assert result['child_valuation']['available'] is False
    with pytest.raises(BaselineMissing,match='usd_2024'):
        compute_counts(parts['params'],baselines,scenario,strict=True)


def test_custom_lifetime_total_retains_fixed_annual_profile_attribution():
    result=evaluate(.03)['child_valuation']
    assert '2023' in result['annual_profile_source']
    assert 'custom lifetime total' in result['normalization']
