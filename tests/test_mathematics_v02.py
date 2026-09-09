from dataclasses import replace

import pytest

from downstream.children import child_line
from downstream.distributions import sample_unit_interval
from downstream.inference import analytic_chain, param_moments
from downstream.ledger import start, GAP
from downstream.mortality import excess_deaths, mortality_phase_years, odds_risk
from downstream.params import load_all
from downstream.place import load_places, modifier_parameter
from downstream.scenario import ScenarioInput, compute_counts


@pytest.mark.parametrize('dist', ['normal', 'lognormal'])
def test_analytic_matches_clamped_sampler(dist):
    parts = load_all()
    p = replace(parts['params'].parameters[0], low=.4, point=.8, high=1.3, dist=dist)
    values = [sample_unit_interval(dist, (i+.5)/20000, p.low, p.high, point=p.point) for i in range(20000)]
    for k, moment in enumerate(param_moments(p, None), 1):
        assert moment == pytest.approx(sum(v**k for v in values)/len(values), abs=1e-7)


def test_reusing_uncertain_parameter_is_not_independence():
    parts = load_all()
    p = parts['params'].parameters[0]
    with pytest.raises(ValueError, match='reused parameter'):
        analytic_chain(parts['params'], [p.link, p.link], ['level', 'level'], parts['nodes'])


def test_gap_envelope_covers_above_counterfactual():
    p = replace(load_all()['params'].parameters[0], low=.4, point=.5, high=.6)
    initial = replace(start('test', 'gap_multiplier'), low=1.1, point=1.2, high=1.3)
    out = initial.apply(GAP, p)
    assert out.low == pytest.approx(1.04)
    assert out.high == pytest.approx(1.18)


def test_mortality_probability_and_timing():
    assert odds_risk(.5, 2) == pytest.approx(2/3)
    assert excess_deaths(100, .1, 2, 1.5, 0) == 0
    assert excess_deaths(100, .1, 2, 1.5, 1) == pytest.approx(100*(odds_risk(.1, 2)-.1))
    assert excess_deaths(100, .1, 1, 1, 20) == pytest.approx(0)
    assert abs(excess_deaths(100, .4, 20, 20, 50)) <= 100


def test_year_six_estimate_is_not_backfilled_into_unidentified_years():
    phases = mortality_phase_years(20)
    assert phases == {"peak": 1.0, "unidentified": 4.0, "sustained": 15.0}
    aligned = excess_deaths(1000, .004944, 2.672, 1.135, 20)
    immediate = excess_deaths(1000, .004944, 2.672, 1.135, 20,
                               timing="immediate_sustained")
    assert aligned < immediate
    assert aligned == pytest.approx(16.37, abs=.01)


@pytest.mark.parametrize("baseline", [-0.01, float("nan"), float("inf"), True])
def test_mortality_rejects_invalid_baseline_probabilities(baseline):
    with pytest.raises(ValueError, match="baseline"):
        odds_risk(baseline, 1.1)


@pytest.mark.parametrize("odds", [0, -1, float("nan"), float("inf"), True])
def test_mortality_rejects_invalid_odds_ratios(odds):
    with pytest.raises(ValueError, match="odds ratio"):
        odds_risk(0.1, odds)


def test_mortality_accepts_probability_one_and_pins_legacy_calculation():
    assert odds_risk(1.0, 3.0) == 1.0
    assert excess_deaths(100, 0.1, 2.0, 1.5, 3, method="legacy_additive") == pytest.approx(25.0)


def test_neutral_mortality_odds_have_exactly_zero_excess_deaths():
    # Regression: split survival powers once yielded a tiny negative residual.
    assert excess_deaths(1, 0.16906335371770378, 1, 1, 61.72698833575127) == 0.0


def test_mortality_protective_and_mixed_effects_keep_their_signs():
    protective = excess_deaths(100, 0.1, 0.8, 0.8, 3)
    mixed = excess_deaths(100, 0.1, 2.0, 0.8, 3)
    assert -100 <= protective < 0
    assert -100 <= mixed <= 100
    with pytest.raises(ValueError, match="workers"):
        excess_deaths(True, 0.1, 1.2, 1.2, 1)
    with pytest.raises(ValueError, match="unknown mortality method"):
        excess_deaths(1, 0.1, 1.2, 1.2, 1, method="invented")


def test_place_adjustment_flows_once_through_generations():
    parts = load_all(); places = load_places()
    key = next(k for k,p in places.items() if p.mobility_percentile and p.mobility_percentile != places['national'].mobility_percentile)
    modifier = modifier_parameter(parts['params'], places, key)['parameter']
    line = child_line(parts['params'], modifier)
    t = parts['params'].by_link('child_earnings->grandchild_earnings').point
    assert line['grandchild'].point == pytest.approx(1-t*(1-line['child'].point))
    assert sum(s.link.startswith('place:') for s in line['greatgrandchild'].steps) == 1


def test_count_envelopes_and_missing_place_provenance():
    parts = load_all()
    out = compute_counts(parts['params'], parts['baselines'], ScenarioInput(100), places={}, place_key='missing')
    for row in out['modeled'].values():
        assert row['low'] <= row['point'] <= row['high']
    assert out['place']['baselines_applied'] is False


@pytest.mark.parametrize('kwargs', [dict(displaced_workers=-1), dict(displaced_workers=float('nan')),
                                   dict(displaced_workers=1, n_children=-1), dict(displaced_workers=1, tradable_share=2)])
def test_all_scenarios_validate_inputs(kwargs):
    with pytest.raises(ValueError):
        ScenarioInput(**kwargs)
