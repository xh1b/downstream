"""Reconciled marginal household expectations, without invented joint outcomes."""

from copy import deepcopy
import csv
import json
import math

import pytest

from downstream.household import household_comparison
from downstream.params import default_dir


def example():
    return json.loads((default_dir().parent / 'validation/household_five_year_input.json').read_text())


def deterministic_cells(tmp_path, *, n=100, include_unemployed=True):
    path = tmp_path / 'baseline_employment_transitions.csv'
    with path.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=['sex','age_band','origin','n_persons','to_E','to_U','to_N'])
        writer.writeheader()
        for sex in ('male','female'):
            for band in ('25-34','35-44','45-54'):
                origins = ('E','U','N') if include_unemployed else ('E','N')
                for origin in origins:
                    writer.writerow(dict(sex=sex,age_band=band,origin=origin,n_persons=n,
                                         to_E=1,to_U=0,to_N=0))
    return tmp_path


def test_summaries_reconcile_with_annual_rows_and_member_totals():
    result = household_comparison(example())
    summary = result['summary']
    for index, member in enumerate(summary['members']):
        for arm in ('reference','displacement'):
            annual = [row[arm]['adults'][index] for row in result['annual']]
            assert member[arm]['gross_earnings_usd_2024'] == math.fsum(a['expected_earnings_usd_2024'] for a in annual)
            for state in ('E','U','N'):
                assert member[arm]['expected_state_person_years'][state] == math.fsum(a['state_probabilities'][state] for a in annual)
            assert sum(member[arm]['expected_state_person_years'].values()) == pytest.approx(5)
        difference = member['displacement_minus_reference']
        assert difference['gross_earnings_usd_2024'] == pytest.approx(
            member['displacement']['gross_earnings_usd_2024']-member['reference']['gross_earnings_usd_2024'])
        assert sum(difference['expected_state_person_years'].values()) == pytest.approx(0,abs=1e-12)
    for arm in ('reference','displacement','displacement_minus_reference'):
        household = summary['household'][arm]
        assert household['gross_earnings_usd_2024'] == math.fsum(m[arm]['gross_earnings_usd_2024'] for m in summary['members'])
        for state in ('E','U','N'):
            assert household['expected_state_person_years'][state] == math.fsum(m[arm]['expected_state_person_years'][state] for m in summary['members'])
    assert result['cumulative_earnings_difference_usd_2024'] == summary['household']['displacement_minus_reference']['gross_earnings_usd_2024']
    assert result['cumulative_earnings_difference_usd_2024'] == pytest.approx(math.fsum(r['displacement_minus_reference'] for r in result['annual']))
    assert 'no member independence' in summary['aggregation']
    assert result['uncertainty']['intervals'] is None
    assert not result['eligible_for_public_headline']
    json.dumps(result, allow_nan=False)


def test_deterministic_window_has_exact_earnings_and_person_year_reconciliation(tmp_path):
    payload = example()
    payload['event']['unemployed_years'] = 2
    payload['event']['calendar_year'] = 2026
    result = household_comparison(payload, deterministic_cells(tmp_path))
    worker, partner = result['summary']['members']
    assert worker['reference']['gross_earnings_usd_2024'] == 5*65000
    assert worker['displacement']['gross_earnings_usd_2024'] == 3*65000
    assert worker['displacement_minus_reference']['gross_earnings_usd_2024'] == -2*65000
    assert worker['reference']['expected_state_person_years'] == {'E':5,'U':0,'N':0}
    assert worker['displacement']['expected_state_person_years'] == {'E':3,'U':2,'N':0}
    assert worker['displacement_minus_reference']['expected_state_person_years'] == {'E':-2,'U':2,'N':0}
    assert partner['displacement_minus_reference']['gross_earnings_usd_2024'] == 0
    assert result['summary']['household']['reference']['gross_earnings_usd_2024'] == 550000
    assert result['summary']['household']['displacement']['gross_earnings_usd_2024'] == 420000
    assert sum(result['summary']['household']['reference']['expected_state_person_years'].values()) == 10
    assert result['window']['calendar_start_year'] == 2026
    assert result['window']['calendar_end_year_exclusive'] == 2031
    assert [r['calendar_year'] for r in result['annual']] == list(range(2026,2031))
    assert [r['follow_up_year_number'] for r in result['annual']] == [1,2,3,4,5]
    assert result['annual'][-1]['follow_up_interval_years'] == {'start':4,'end_exclusive':5}


def test_unknown_calendar_is_never_inferred_from_source_wave():
    result = household_comparison(example())
    assert result['window']['calendar_start_year'] is None
    assert result['window']['calendar_end_year_exclusive'] is None
    assert all(r['calendar_year'] is None for r in result['annual'])


def test_nonparticipating_partner_contributes_explicit_n_person_years(tmp_path):
    payload = example()
    payload['members'][1]['employment_state'] = 'N'
    result = household_comparison(payload, str(deterministic_cells(tmp_path)))
    partner = result['summary']['members'][1]
    assert partner['reference']['expected_state_person_years'] == {'E':4,'U':0,'N':1}
    assert partner['displacement']['expected_state_person_years'] == {'E':4,'U':0,'N':1}
    assert partner['reference']['gross_earnings_usd_2024'] == 4*45000


def test_zero_duration_null_and_positive_supplied_earnings_path_remain_signed(tmp_path):
    payload = example()
    payload['event']['unemployed_years'] = 0
    directory = deterministic_cells(tmp_path)
    null = household_comparison(payload, directory)
    for member in null['summary']['members']:
        assert member['reference'] == member['displacement']
        assert member['displacement_minus_reference']['gross_earnings_usd_2024'] == 0
    payload['event']['reemployment_earnings_multipliers'] = [1.1]*5
    payload['event']['earnings_path_assumption'] = 'supplied beneficial scenario'
    benefit = household_comparison(payload, directory)
    assert benefit['summary']['household']['displacement_minus_reference']['gross_earnings_usd_2024'] == pytest.approx(32500)


def test_forced_years_do_not_claim_or_require_overwritten_transition_cells(tmp_path):
    payload = example()
    payload['event']['unemployed_years'] = 5
    payload['allow_sparse_cells'] = False
    result = household_comparison(payload, deterministic_cells(tmp_path, include_unemployed=False))
    assert not any(key.endswith('|U') for key in result['used_transition_cells_n'])
    assert result['summary']['members'][0]['displacement']['expected_state_person_years']['U'] == 5


def test_small_member_loss_is_not_swamped_by_large_unaffected_partner():
    payload = example()
    payload['follow_up_years'] = 1
    payload['members'][0]['annual_earnings_if_employed_usd_2024'] = 1
    payload['members'][1]['annual_earnings_if_employed_usd_2024'] = 1e16
    result = household_comparison(payload)
    assert result['annual'][0]['displacement_minus_reference'] == -1
    assert result['summary']['household']['displacement_minus_reference']['gross_earnings_usd_2024'] == -1


@pytest.mark.parametrize('changes,message', [
    ({'members':[None]},'member must be an object'),
    ({'event':[]},'event must be an object'),
])
def test_malformed_objects_fail_with_contract_error(changes, message):
    with pytest.raises(ValueError, match=message):
        household_comparison({**example(), **changes})
    with pytest.raises(ValueError, match='payload must be an object'):
        household_comparison([])


@pytest.mark.parametrize('year', [True, 1899, 2201, '2026'])
def test_invalid_calendar_year_fails(year):
    payload = example()
    payload['event']['calendar_year'] = year
    with pytest.raises(ValueError, match='calendar_year'):
        household_comparison(payload)


@pytest.mark.parametrize('assumption', [True, 1, [], '   '])
def test_earnings_assumption_must_be_explanatory_text(assumption):
    payload = example()
    payload['event']['reemployment_earnings_multipliers'] = [1]*5
    payload['event']['earnings_path_assumption'] = assumption
    with pytest.raises(ValueError, match='earnings_path_assumption'):
        household_comparison(payload)


def test_nonpositive_baseline_cell_sample_size_is_not_accepted(tmp_path):
    with pytest.raises(ValueError, match='n_persons must be positive'):
        household_comparison(example(), deterministic_cells(tmp_path,n=0))


@pytest.mark.parametrize('change,message', [
    ({'id':'   '},'unique household member IDs'),
    ({'sex':'unknown'},'sex, supported ages'),
    ({'annual_earnings_if_employed_usd_2024':math.nan},'annual earnings'),
])
def test_invalid_member_metadata_is_rejected(change, message):
    payload = example()
    payload['members'][0].update(change)
    with pytest.raises(ValueError, match=message):
        household_comparison(payload)


@pytest.mark.parametrize('scars', [[],[True]*5,[math.inf]*5])
def test_invalid_earnings_paths_are_rejected(scars):
    payload = example()
    payload['event']['reemployment_earnings_multipliers'] = scars
    payload['event']['earnings_path_assumption'] = 'invalid values'
    with pytest.raises(ValueError, match='reemployment multipliers'):
        household_comparison(payload)


@pytest.mark.parametrize('defect,message', [
    ('invalid_probability','invalid baseline transition'),
    ('duplicate','duplicate baseline transition'),
    ('missing','missing baseline transition'),
])
def test_transition_contract_and_actual_required_cells_remain_gated(tmp_path, defect, message):
    directory = deterministic_cells(tmp_path)
    path = directory / 'baseline_employment_transitions.csv'
    with path.open(newline='') as handle:
        reader = csv.DictReader(handle)
        fields, rows = reader.fieldnames, list(reader)
    if defect == 'invalid_probability':
        rows[0]['to_E'] = '2'
    elif defect == 'duplicate':
        rows.append(rows[0])
    else:
        rows = [row for row in rows if not (row['sex']=='male' and row['age_band']=='35-44' and row['origin']=='U')]
    with path.open('w',newline='') as handle:
        writer = csv.DictWriter(handle,fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError, match=message):
        household_comparison(example(), directory)


@pytest.mark.parametrize('earnings,scars', [(1e308,[1]*5), (1e308,[1e308]*5)])
def test_overflow_is_a_value_error_not_nonfinite_json_or_raw_overflow(earnings, scars, tmp_path):
    payload = example()
    payload['event']['unemployed_years'] = 0
    payload['members'] = [payload['members'][0]]
    payload['members'][0]['annual_earnings_if_employed_usd_2024'] = earnings
    payload['event']['reemployment_earnings_multipliers'] = scars
    payload['event']['earnings_path_assumption'] = 'overflow fixture'
    with pytest.raises(ValueError, match='overflow'):
        household_comparison(payload, deterministic_cells(tmp_path))


def test_output_does_not_retain_mutable_input_alias():
    payload = example()
    original = deepcopy(payload)
    result = household_comparison(payload)
    payload['members'][0]['age'] = 0
    assert result['input'] == original
