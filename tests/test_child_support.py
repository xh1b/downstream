# @ref:test-child-support
# Method: @link:doc-child-support-0-4.
# Implementation: @link:code-child-support; @link:code-params; @link:code-scenario.
# @tag:children @tag:testing
"""Inspectable source support retains uncertainty and refuses false transport."""

import csv
import json
import math
from pathlib import Path
import subprocess
import sys

import pytest

from downstream.child_support import child_support_report
from downstream.params import default_dir
from downstream.scenario import ScenarioInput


def scenario(**changes):
    inputs = {
        'displaced_workers': 100, 'n_children': 1,
        'child_profiles': [{'age_at_displacement': 12, 'sex': 'Male'}],
        'income_rank_definition': "father average income 1978-1979 source rank",
        'target_population': {'sex': 'Male', 'children_sex': 'Male', 'age': '45-54 years',
            'worker_tenure': 'high-tenure', 'geography': 'Canada',
            'calendar_window': '1980-1982', 'exposure_type': 'firm closure'},
        **changes,
    }
    return ScenarioInput(**inputs)


def test_default_unknown_scope_and_all_five_source_contrasts_are_inspectable():
    report = child_support_report()
    assert report['support_state'] == 'unknown'
    assert not report['eligible_for_public_headline']
    assert report['unknown_conditions']
    assert len(report['contrasts']) == 5
    assert report['contrasts'][0]['selected']
    assert report['source_scope']['child_age_at_displacement'] == [10, 14]
    assert report['source_scope']['country'] == 'Canada'
    assert report['source_scope']['parent_minimum_tenure_years'] == 2
    for row in report['contrasts']:
        assert row['source']['source_sha256']
        assert row['source']['source_locator']
        assert row['source']['citation'] == 'oreopoulos2008'
    json.dumps(report, allow_nan=False)


@pytest.mark.parametrize('quartile,beta,se', [(1,-.143,.088),(2,-.117,.070),(3,.007,.065),(4,-.095,.068)])
def test_signed_source_contrasts_keep_beta_se_and_null_intervals(quartile, beta, se):
    report = child_support_report(scenario(child_income_quartile=quartile), parent_tenure_years=2)
    row = next(row for row in report['contrasts'] if row['selected'])
    assert row['income_quartile'] == quartile
    assert row['log_earnings_ratio'] == {'point': beta, 'standard_error': se}
    assert row['earnings_multiplier']['point'] == pytest.approx(math.exp(beta))
    assert row['relative_earnings_gap_pct']['point'] == pytest.approx(100*(1-math.exp(beta)))
    assert row['relative_earnings_gap_pct']['low'] < 0 < row['relative_earnings_gap_pct']['high']
    assert row['null_in_interval']
    if quartile == 3:
        assert row['relative_earnings_gap_pct']['point'] < 0


def test_complete_source_dimensions_are_conditional_not_automatically_reviewed():
    report = child_support_report(scenario(), parent_tenure_years=2)
    assert report['support_state'] == 'conditional_transport'
    assert not report['unknown_conditions']
    assert not report['refused_reasons']
    assert report['remaining_transport_conditions']


def test_numeric_tenure_unknown_even_with_high_tenure_label():
    assert child_support_report(scenario())['support_state'] == 'unknown'


def test_reviewed_transport_remains_conditional_source_inspection():
    decision = {'status': 'reviewed', 'reviewer': 'test reviewer',
                'rationale': 'test transport decision', 'citations': 'oreopoulos2008'}
    report = child_support_report(scenario(applicability_decisions={
        'child_lifetime_earnings_lost_usd': decision}), parent_tenure_years=6)
    assert report['support_state'] == 'reviewed_conditional_transport'
    assert report['transport_decision'] == decision
    assert not report['eligible_for_public_headline']


@pytest.mark.parametrize('profile', [
    {'age_at_displacement': 9, 'sex': 'Male'},
    {'age_at_displacement': 15, 'sex': 'Male'},
    {'age_at_displacement': 12, 'sex': 'Female'},
])
def test_incompatible_child_is_refused_and_source_rows_are_still_visible(profile):
    report = child_support_report(scenario(child_profiles=[profile]), parent_tenure_years=2)
    assert report['support_state'] == 'refused'
    assert report['refused_reasons']
    assert len(report['contrasts']) == 5


def test_known_short_parent_tenure_refused():
    report = child_support_report(scenario(), parent_tenure_years=1.99)
    assert report['support_state'] == 'refused'
    assert 'two years' in report['refused_reasons'][0]


@pytest.mark.parametrize('changes', [
    {'sex': 'Female'}, {'children_sex': 'Female'}, {'exposure_type': 'individual layoff'},
])
def test_known_parent_child_event_mismatch_is_refused(changes):
    base = scenario()
    target = {**base.target_population, **changes}
    report = child_support_report(scenario(target_population=target), parent_tenure_years=2)
    assert report['support_state'] == 'refused'


def test_country_period_transport_is_explicit_not_new_country_evidence():
    target = {**scenario().target_population, 'geography': 'US', 'calendar_window': '2026'}
    report = child_support_report(scenario(target_population=target), parent_tenure_years=2)
    assert report['support_state'] == 'conditional_transport'
    assert len(report['remaining_transport_conditions']) == 3
    assert report['source_scope']['country'] == 'Canada'
    assert 'additional countries' in report['unavailable_extensions']


def test_unknown_child_profiles_and_income_mapping_cannot_become_reviewed():
    report = child_support_report(scenario(child_profiles=[{'age_at_displacement': None, 'sex': 'Unknown'}],
        income_rank_definition=None), parent_tenure_years=2)
    assert report['support_state'] == 'unknown'
    assert len(report['unknown_conditions']) == 2


@pytest.mark.parametrize('field', ['sex', 'children_sex', 'exposure_type', 'geography', 'calendar_window'])
def test_explicit_unknown_target_fields_are_unknown_not_known_mismatches(field):
    target = {**scenario().target_population, field: 'Unknown'}
    report = child_support_report(scenario(target_population=target), parent_tenure_years=2)
    assert report['support_state'] == 'unknown'
    assert report['unknown_conditions']
    assert not report['refused_reasons']


@pytest.mark.parametrize('tenure', [True, -1, math.nan, math.inf, '2'])
def test_invalid_parent_tenure_fails(tenure):
    with pytest.raises(ValueError, match='parent_tenure_years'):
        child_support_report(parent_tenure_years=tenure)


@pytest.mark.parametrize('field,value', [
    ('sex', 'Female'), ('age_min', '0'), ('tenure_min_years', '0'),
    ('treatment', 'maternal job loss'), ('comparison', 'other displaced fathers'),
    ('outcome_definition', 'school test scores'), ('scale', 'log_hazard_ratio'),
    ('income_quartile', '4'), ('projection_status', 'lifetime_path'),
])
def test_custom_source_metadata_cannot_silently_expand_admission(tmp_path, field, value):
    with (default_dir() / 'study_estimates.csv').open(newline='') as handle:
        reader = csv.DictReader(handle)
        fields, rows = reader.fieldnames, list(reader)
    for row in rows:
        if row['study_id'] == 'oreopoulos2008_q3':
            row[field] = value
    with (tmp_path / 'study_estimates.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError, match=field):
        child_support_report(params_dir=tmp_path)


def test_missing_custom_source_library_never_falls_back(tmp_path):
    with pytest.raises(FileNotFoundError):
        child_support_report(params_dir=tmp_path)


def test_standalone_report_accepts_scenario_and_rejects_invalid_tenure(tmp_path):
    script = Path(__file__).resolve().parents[1] / 'scripts' / 'inspect_child_support.py'
    from dataclasses import asdict
    payload = tmp_path / 'scenario.json'
    payload.write_text(json.dumps(asdict(scenario())))
    result = subprocess.run([sys.executable, str(script), '--input', str(payload),
                             '--parent-tenure-years', '2'], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['support_state'] == 'conditional_transport'
    invalid = subprocess.run([sys.executable, str(script), '--parent-tenure-years', '-1'],
                             text=True, capture_output=True)
    assert invalid.returncode == 2
    assert 'parent_tenure_years' in invalid.stderr
