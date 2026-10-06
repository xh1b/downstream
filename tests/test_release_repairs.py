"""Regression checks for the website readiness review."""
import csv
import subprocess
import sys
from dataclasses import replace

import pytest

from downstream.params import load_all, default_dir
from downstream.county_rates import load_county_mortality_posteriors
from downstream.place import place_baselines
from downstream.mortality_profiles import resolve_mix, validate_sullivan_von_wachter_applicability


def test_county_prior_demographics_and_arithmetic(tmp_path):
    parts = load_all()
    county = load_county_mortality_posteriors(default_dir() / 'county_mortality.csv')
    from downstream.place import load_places
    places = load_places(default_dir() / 'places.csv')
    key = '06037'
    bad = {**county, key: replace(county[key], population_scope='county residents, female, ages 45-54 years; cause: All causes')}
    result = place_baselines(places, parts['baselines'], key, county_mortality=bad)
    assert result['baselines']['all_cause_mortality_annual'].value == parts['baselines']['all_cause_mortality_annual'].value
    path = tmp_path / 'bad.csv'
    with open(default_dir() / 'county_mortality.csv') as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        row = next(reader)
    row['posterior_mean_rate'] = '0.99'
    with path.open('w') as f:
        writer = csv.DictWriter(f, fields)
        writer.writeheader()
        writer.writerow(row)
    with pytest.raises(ValueError, match='disagrees'):
        load_county_mortality_posteriors(path)


def test_county_builder_refuses_female_prior(tmp_path):
    result = subprocess.run([sys.executable, 'scripts/build_county_mortality.py', '--export',
                            'validation/cdc_wonder_county_female_45_54_2015_2019.csv',
                            '--out', str(tmp_path / 'county.csv')], capture_output=True, text=True)
    assert result.returncode != 0
    assert 'does not match' in result.stderr
    assert not (tmp_path / 'county.csv').exists()


def test_explicit_empty_mortality_mix_is_rejected():
    with pytest.raises(ValueError, match='nonempty'):
        resolve_mix({}, None, {})
    with pytest.raises(ValueError, match='at least one'):
        validate_sullivan_von_wachter_applicability([])
