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
    result = simulate_chain(parts['params'], ['displacement->worker_earnings'], kinds=['direct'],
                            nodes=parts['nodes'], draws=10, params_dir=tmp_path)
    assert result['correlations_applied'] == 0


def test_public_results_require_reviewed_target_applicability():
    from downstream.scenario import ScenarioInput, compute_counts
    parts = load_all()
    out = compute_counts(parts['params'], parts['baselines'], ScenarioInput(1000))
    for name in ('excess_deaths', 'child_lifetime_earnings_lost_usd'):
        assert not out['modeled'][name]['applicability']['eligible_for_public_headline']
        assert out['modeled'][name]['baseline']['notes']
    target = dict(sex='Female', age='45-54 years', worker_tenure='high-tenure', geography='US',
                  calendar_window='2026', exposure_type='mass layoff', children_sex='Female')
    out = compute_counts(parts['params'], parts['baselines'], ScenarioInput(1000, target_population=target))
    assert 'excess_deaths' not in out['modeled']
    with pytest.raises(ValueError):
        ScenarioInput(1000, applicability_decisions={'excess_deaths': {'status': 'reviewed'}})


def test_policy_and_knobs_preserve_county_context():
    from downstream.scenario import ScenarioInput, compute_counts
    from downstream.policy import PolicyCase, compare_policies
    from downstream.knobs import sweep
    from downstream.place import load_places
    parts = load_all()
    places = load_places(default_dir() / 'places.csv')
    county = load_county_mortality_posteriors(default_dir() / 'county_mortality.csv')
    scenario = ScenarioInput(1000)
    expected = compute_counts(parts['params'], parts['baselines'], scenario, places=places,
                              place_key='06037', county_mortality=county)['modeled']['excess_deaths']['point']
    case = PolicyCase('reference', 'document', 'supplied', scenario, place_key='06037')
    compared = compare_policies(parts['params'], parts['baselines'], case, case, places=places, county_mortality=county)
    assert compared['baseline']['parameter_envelope']['modeled']['excess_deaths']['point'] == expected
    parameter = parts['params'].by_link('displacement->worker_earnings')
    swept = sweep(parts['params'], parts['baselines'], scenario, parameter.link, [parameter.point],
                  places=places, place_key='06037', county_mortality=county)
    assert swept['rows'][0]['modeled']['excess_deaths'] == expected


def test_invalid_public_inputs_fail_cleanly(capsys):
    from downstream.scenario import ScenarioInput, compute_counts
    from downstream.vignette import standard_family
    from downstream.cli import main
    parts = load_all()
    for children in (-1, True, 1.5):
        with pytest.raises(ValueError):
            standard_family(parts['params'], n_children=children)
    assert '0 children' in standard_family(parts['params'], n_children=0)['vignette']['definition']
    with pytest.raises(ValueError, match='non-finite'):
        compute_counts(parts['params'], parts['baselines'], ScenarioInput(1e308))
    assert main(['simulate', '--outcome', 'grandchild', '--draws', '0']) == 2
    captured = capsys.readouterr()
    assert 'draws' in captured.err and 'Traceback' not in captured.err and not captured.out


def test_explanation_gap_direction_and_roles():
    from downstream.explanation import explain_child_line
    parts = load_all()
    exp = explain_child_line(parts['params'], draws=10, nodes=parts['nodes'])
    assert len(exp.steps) == 2
    assert 'narrows' in exp.steps[1].sentence and 'further' not in exp.steps[1].sentence
    assert all(s.evidence_role and s.causal_role for s in exp.steps)
    assert not exp.projection_eligibility['grandchild']['eligible_for_validated_direct_contrast']


def test_credits_distinguish_people_and_stay_fresh(tmp_path):
    from downstream.credits import collect, write_credits_md, attribution_sentences, parse_authors
    parts = load_all()
    data = collect(parts['bib'])
    names = {r['name'] for r in data['researchers']}
    assert {'Black, Dan A.', 'Black, Sandra E.', 'Sullivan, Teresa A.', 'Sullivan, Daniel G.'} <= names
    assert parse_authors('{Research and Policy Institute} and Smith, Jane') == ['Research and Policy Institute', 'Smith, Jane']
    generated = write_credits_md(data, tmp_path / 'credits.md')
    assert (default_dir().parent / 'CREDITS.md').read_text() == generated
    readme = (default_dir().parent / 'README.md').read_text()
    assert all(sentence in readme for sentence in attribution_sentences(data))
