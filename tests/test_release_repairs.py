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


def test_validation_and_scenario_use_same_mortality_profile():
    from downstream.mortality import parameter_profile_counts, source_profile_contract
    from downstream.scenario import ScenarioInput, compute_counts
    from downstream.snapshot import build
    parts = load_all()
    for years in (5, 10, 20):
        out = compute_counts(parts['params'], parts['baselines'], ScenarioInput(1000, exposure_years=years))
        expected = parameter_profile_counts(parts['params'], 1000, parts['baselines']['all_cause_mortality_annual'].value, years)
        assert out['modeled']['excess_deaths']['point'] == round(expected, 2)
    assert build()['modeling_assumptions']['mortality_contract'] == source_profile_contract()


def test_repeated_relationship_shares_exact_draw_and_sensitivity_block():
    from downstream.distributions import plan, materialize_parameter_set
    from downstream.sensitivity import sobol_indices, correlated_block_sobol
    from downstream.inference import analytic_chain
    from downstream.children import child_line
    parts = load_all()
    params, nodes = parts['params'], parts['nodes']
    links = ['child_earnings->grandchild_earnings', 'grandchild_earnings->greatgrandchild_earnings']
    draw = plan(params, nodes, 10, 19)
    for row in draw.u:
        sampled = materialize_parameter_set(params, nodes, row, draw.dists)
        assert sampled.by_link(links[0]).point == sampled.by_link(links[1]).point
    with pytest.raises(ValueError, match='reused parameter'):
        analytic_chain(params, ['displacement->child_earnings', *links], ['direct', 'gap', 'gap'], nodes)
    def compute(ps):
        return child_line(ps)['greatgrandchild'].point
    sob = sobol_indices(params, compute, nodes, base=16)
    assert any(row['links'] == links for row in sob['indices'])
    blocks = correlated_block_sobol(params, compute, nodes, [], base=16)
    assert any(row['links'] == links for row in blocks['blocks'])


def test_custom_link_sampling_uses_custom_correlations(tmp_path):
    from downstream.mc import simulate_chain
    parts = load_all()
    (tmp_path / 'correlations.csv').write_text('from_param,to_param,spearman,justification\n')
    result = simulate_chain(parts['params'], ['displacement->worker_earnings'], kinds=['level'],
                            nodes=parts['nodes'], draws=10, params_dir=tmp_path)
    assert result['correlations_applied'] == 0
