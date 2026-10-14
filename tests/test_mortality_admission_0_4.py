"""Demographic baseline availability is never causal-response admission."""

import csv
import shutil

import pytest

from downstream.mortality_profiles import load_profiles, resolve_mix, validate_sullivan_von_wachter_applicability
from downstream.mortality_strata import project_mortality_cohort
from downstream.params import default_dir


def cohort(**stratum_changes):
    return {
        'source': 'documented test cohort', 'method': 'exact stratum counts',
        'transport_rationale': 'hypothetical source-window response transport',
        'projection_assumption': 'constant_source_window_log_odds', 'follow_up_years': 5,
        'strata': [{'age_at_event': 34, 'sex': 'Male', 'workers': 100,
                    'tenure_years': 6, 'exposure_type': 'mass layoff', **stratum_changes}],
    }


def custom_directory(tmp_path, study_change=None):
    shutil.copyfile(default_dir() / 'age_mortality.csv', tmp_path / 'age_mortality.csv')
    with (default_dir() / 'study_estimates.csv').open(newline='') as handle:
        reader = csv.DictReader(handle)
        fields, rows = reader.fieldnames, list(reader)
    if study_change:
        rows = [dict(row, **study_change) if row['study_id'] == 'sullivan2007_age_30_39' else row for row in rows]
    with (tmp_path / 'study_estimates.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return tmp_path


@pytest.mark.parametrize('change', [
    {'sex': 'Female'}, {'sex': 'Unknown'}, {'age_at_event': 29},
    {'age_at_event': 70}, {'tenure_years': 5.99}, {'exposure_type': 'individual dismissal'},
])
def test_unadmitted_response_stays_unknown_despite_available_baselines(change):
    result = project_mortality_cohort(cohort(**change))
    assert result['covered_workers'] == 0
    assert result['unmodeled_workers'] == 100
    assert result['whole_cohort_excess_deaths'] is None
    assert result['unsupported_strata'][0]['reason'] == 'no compatible source mortality response'


def test_supported_strata_keep_full_source_restrictions_and_conditional_status():
    result = project_mortality_cohort(cohort())
    admission = result['supported_strata'][0]['applicability']
    assert admission['status'] == 'conditional_source_stratum_projection'
    assert not admission['eligible_for_public_headline']
    assert admission['source_restrictions']['age_at_displacement'] == [30, 39]
    assert admission['source_restrictions']['employer_size'] == 'more than 50 employees'
    assert admission['source_restrictions']['geography'] == 'Pennsylvania'
    assert admission['remaining_transport_assumptions']


@pytest.mark.parametrize('field,value', [
    ('treatment', 'voluntary quit'), ('comparison', 'other displaced workers'),
    ('scale', 'log_hazard_ratio'), ('sex', 'Female'),
    ('age_max', '49'), ('tenure_min_years', '1'),
    ('outcome_definition', 'cancer mortality'), ('time_horizon', 'one year only'),
    ('projection_status', 'unrestricted_age_response'),
])
def test_custom_source_contract_cannot_silently_change_estimand(tmp_path, field, value):
    directory = custom_directory(tmp_path, {field: value})
    with pytest.raises(ValueError, match=field):
        project_mortality_cohort(cohort(), directory)


def test_missing_age_source_is_not_filled_from_another_age_or_default_profile(tmp_path):
    directory = custom_directory(tmp_path, {'study_id': 'removed_age_contrast'})
    with pytest.raises(KeyError, match='sullivan2007_age_30_39'):
        project_mortality_cohort(cohort(), directory)


def test_response_selection_tracks_event_age_while_baseline_ages():
    result = project_mortality_cohort({**cohort(age_at_event=39), 'follow_up_years': 12})
    row = result['supported_strata'][0]
    assert row['source_contrast']['study_id'] == 'sullivan2007_age_30_39'
    assert len(set(row['aging_bands']['annual_baseline_rates'])) > 1
    assert len(set(row['fixed_baseline']['annual_baseline_rates'])) == 1
    assert not result['eligible_for_public_headline']


@pytest.mark.parametrize('profile_id', ['female_45_54_2015_2019', 'male_35_44_2015_2019'])
def test_verified_baseline_profile_does_not_expand_default_phase_response(profile_id):
    profiles = load_profiles(default_dir() / 'mortality_profiles.csv')
    assert profiles[profile_id].status == 'verified'
    with pytest.raises(ValueError, match='separately admitted effect'):
        validate_sullivan_von_wachter_applicability(resolve_mix(profiles, profile_id, None))
