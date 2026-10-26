# @ref:test-uncertainty-cases
# Contract: @link:uncertainty-assumption-cases.
# Implementation: @link:code-uncertainty-cases; @link:code-uncertainty-budget.
# @tag:uncertainty @tag:testing
"""Transport/dependence cases preserve draws and cannot imply target admission."""
from copy import deepcopy
import json
import math
import subprocess
import sys

import pytest

from downstream.params import default_dir, load_all
from downstream.uncertainty_budget import propagate_uncertainty
from downstream.uncertainty_cases import pair_by_rank


def payload(cases=None):
    value = json.loads((default_dir().parent/'validation/uncertainty_budget_input.json').read_text())
    value['draws'] = 32
    if cases is not None:
        value['assumption_cases'] = cases
    return value


def case(name='identity', scale=1, exposure='independent', baseline='independent'):
    return {'name': name, 'mortality_log_odds_scale': scale,
            'exposure_rank': exposure, 'baseline_rank': baseline,
            'source': 'synthetic contract experiment; no target evidence',
            'method': 'explicit test assumptions; no probabilities'}


def evaluate(value):
    parts = load_all()
    return propagate_uncertainty(parts['params'], parts['baselines'], value, nodes=parts['nodes'])


def test_identity_reuses_reference_and_optional_cases_do_not_change_the_budget():
    original = payload()
    expected = evaluate(original)
    value = payload([case()])
    before = deepcopy(value)
    result = evaluate(value)
    assert value == before
    reports = result.pop('assumption_sensitivity')
    result['input'] = original
    assert result == expected
    identity = reports['cases'][0]
    for key, summary in identity['expected_effect_intervals_90'].items():
        assert summary == expected['expected_effect_intervals_90'][key]
    assert set(identity['case_minus_independent_source_reference_90'].values()) == {0}
    assert identity['sampled_inputs'] == expected['sampled_inputs']
    assert not identity['eligible_for_public_headline']
    assert 'No probabilities' in reports['limitations'][0]


def test_null_and_protective_transport_remain_signed_and_structures_stay_separate():
    result = evaluate(payload([case('null', 0), case('reversed', -1)]))['assumption_sensitivity']
    null, protective = result['cases']
    for summary in null['expected_effect_intervals_90'].values():
        assert set(summary.values()) == {0}
    assert null['case_minus_independent_source_reference_90']['mean'] < 0
    assert protective['expected_effect_intervals_90']['excess_deaths']['p95'] < 0
    assert protective['expected_effect_intervals_90']['mortality_no_sustained_excess']['mean'] < 0
    assert 'process_intervals_90' not in protective


def test_dependence_cases_preserve_marginals_and_case_order_does_not_change_results():
    cases = [case('aligned', exposure='aligned', baseline='aligned'),
             case('opposed', exposure='opposed', baseline='opposed')]
    result = evaluate(payload(cases))
    reordered = evaluate(payload(list(reversed(cases))))
    assert result['assumption_sensitivity']['cases'] == list(reversed(reordered['assumption_sensitivity']['cases']))
    for row in result['assumption_sensitivity']['cases']:
        assert row['sampled_inputs'] == result['sampled_inputs']
        assert not row['eligible_for_public_headline']
    assert result['assumption_sensitivity']['cases'][0]['expected_effect_intervals_90'] != result['assumption_sensitivity']['cases'][1]['expected_effect_intervals_90']
    assert 'target-population transport error' in result['excluded']


@pytest.mark.parametrize('direction,expected', [
    ('independent', [40, 10, 30, 20]), ('aligned', [20, 10, 40, 30]),
    ('opposed', [30, 40, 10, 20]),
])
def test_rank_pairing_preserves_each_value_and_signed_anchor_order(direction, expected):
    values, anchors = [40, 10, 30, 20], [-1, -2, 2, 0]
    before = values[:], anchors[:]
    paired = pair_by_rank(values, anchors, direction)
    assert paired == expected
    assert sorted(paired) == sorted(values)
    assert (values, anchors) == before


def test_constant_anchor_cannot_be_misrepresented_as_rank_dependence():
    with pytest.raises(ValueError, match='nonconstant'):
        pair_by_rank([1, 2], [0, 0], 'aligned')
    value = payload([case()])
    value['scenario']['exposure_years'] = 0
    assert set(evaluate(value)['assumption_sensitivity']['cases'][0]['expected_effect_intervals_90']['excess_deaths'].values()) == {0}


@pytest.mark.parametrize('cases', [None, [], {}, [case()]*2,
    [case()]*17, [{**case(), 'weight': .5}], [{k:v for k,v in case().items() if k != 'method'}],
    [{**case(), 'source': ''}], [case(scale=True)], [case(scale=math.inf)],
    [case(scale=math.nan)], [case(exposure='gaussian')], [case(baseline='perfect')],
])
def test_unsupported_or_undocumented_cases_fail_before_sampling(cases):
    value = payload()
    value['assumption_cases'] = cases
    with pytest.raises(ValueError):
        evaluate(value)


def test_nonrepresentable_transport_scale_fails_cleanly():
    with pytest.raises(ValueError, match='finite and positive'):
        evaluate(payload([case(scale=1e10)]))


def test_existing_population_refusals_cannot_be_bypassed_by_assumption_cases():
    value = payload([case()])
    value['scenario']['target_population'] = {
        'sex': 'Female', 'age': '45-54 years', 'worker_tenure': 'high-tenure',
        'geography': 'United States', 'calendar_window': '2026',
        'exposure_type': 'firm closure', 'children_sex': 'Male'}
    with pytest.raises(ValueError, match='admitted mortality outcome'):
        evaluate(value)


def test_cli_routes_assumption_cases_without_changing_the_schema(tmp_path):
    path = tmp_path/'input.json'
    value = payload([case('null', 0)])
    value['draws'] = 4
    path.write_text(json.dumps(value))
    completed = subprocess.run([sys.executable, '-m', 'downstream.cli', 'uncertainty',
                                '--input', str(path)], capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr
    report = json.loads(completed.stdout)
    assert report['schema'] == 'downstream-uncertainty-budget/1'
    assert report['assumption_sensitivity']['cases'][0]['assumption']['name'] == 'null'


def test_saved_assumption_example_matches_current_engine():
    from scripts.artifact_checks import same_json
    directory = default_dir().parent/'validation'
    value = json.loads((directory/'uncertainty_assumptions_input.json').read_text())
    saved = json.loads((directory/'uncertainty_assumptions_result.json').read_text())
    assert same_json(evaluate(value), saved)


def test_zero_workers_and_identical_structures_cancel_exactly():
    value = payload([case()])
    value['scenario']['displaced_workers'] = 0
    value['exposure_model'].update(low=0, high=0)
    result = evaluate(value)['assumption_sensitivity']['cases'][0]
    for summary in result['expected_effect_intervals_90'].values():
        assert set(summary.values()) == {0}
    from dataclasses import replace
    parts = load_all()
    params = replace(parts['params'], parameters=tuple(
        replace(row, point=1, low=1, high=1) if row.link == 'earnings_shock->mortality_sustained'
        else row for row in parts['params'].parameters))
    result = propagate_uncertainty(params, parts['baselines'], payload([case(scale=.5)]), nodes=parts['nodes'])
    assert set(result['assumption_sensitivity']['cases'][0]['expected_effect_intervals_90']['mortality_persistence_difference'].values()) == {0}
