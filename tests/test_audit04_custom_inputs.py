"""Regression receipts for release-audit custom-source findings."""
import csv
from dataclasses import replace
import json
import math
import shutil

import pytest

from downstream.cli import main
from downstream.employer import DocumentedExposure, compute_entity_counts
from downstream.params import default_dir, load_all
from downstream.policy import PolicyCase, compare_policies
from downstream.scenario import ScenarioInput, compute_counts, sample_counts
from downstream.uncertainty_budget import propagate_uncertainty


@pytest.fixture
def custom(tmp_path):
    directory = tmp_path / 'params'
    shutil.copytree(default_dir(), directory)
    path = directory / 'study_estimates.csv'
    with path.open(newline='') as handle:
        reader = csv.DictReader(handle)
        fields, rows = reader.fieldnames, list(reader)
    for row in rows:
        if row['study_id'] == 'oreopoulos2008_q3':
            row.update(point='-.2', standard_error='.01')
    with path.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader();writer.writerows(rows)
    return directory, load_all(directory)


def scenario():
    return ScenarioInput(100, child_income_quartile=3, income_rank_definition='source quartile; illustrative fixture')


def assert_custom(result):
    assert result['multipliers']['child_earnings']['point'] == pytest.approx(math.exp(-.2), abs=5e-5)
    assert result['modeled']['child_lifetime_earnings_lost_usd']['point'] > 0


@pytest.mark.parametrize('sampled', [False, True])
def test_scenario_honors_custom_subgroups_and_keeps_sample_variation(custom, sampled):
    directory, parts = custom
    options = dict(params_dir=directory)
    if sampled:options.update(draws=32, nodes=parts['nodes'])
    result = (sample_counts if sampled else compute_counts)(parts['params'], parts['baselines'], scenario(), **options)
    assert_custom(result)
    if sampled:
        band = result['modeled']['child_lifetime_earnings_lost_usd']['parameter_interval_90']
        assert 0 < band['p05'] < band['p95']


def test_entity_and_policy_honor_custom_subgroups(custom):
    directory, parts = custom
    exposure = DocumentedExposure('fixture','employer',100,'fixture source','fixture method')
    assert_custom(compute_entity_counts(parts['params'],parts['baselines'],exposure,scenario(),params_dir=directory))
    before = PolicyCase('before','fixture','fixture',scenario())
    after = PolicyCase('after','fixture','fixture',replace(scenario(),displaced_workers=50))
    comparison = compare_policies(parts['params'],parts['baselines'],before,after,params_dir=directory)
    assert_custom(comparison['baseline']['parameter_envelope'])
    assert comparison['policy_minus_baseline']['child_lifetime_earnings_lost_usd']['point'] < 0


def test_extended_uncertainty_honors_custom_subgroups(custom):
    directory, parts = custom
    payload = json.loads((default_dir().parent/'validation/uncertainty_budget_input.json').read_text())
    payload['scenario'].update(child_income_quartile=3,income_rank_definition='source quartile; illustrative fixture')
    payload['draws']=16
    result=propagate_uncertainty(parts['params'],parts['baselines'],payload,nodes=parts['nodes'],params_dir=directory)
    assert_custom(result['fixed_input_reference'])
    assert result['expected_effect_intervals_90']['child_lifetime_earnings_lost_usd']['p05']>0


@pytest.mark.parametrize('verb', ['scenario','entity','policy'])
def test_cli_honors_the_selected_parameter_directory(custom,verb,tmp_path,capsys):
    directory,_=custom
    common=[verb,'--params',str(directory)]
    if verb=='policy':
        case={'name':'fixture','source':'fixture','method':'fixture','scenario':{'displaced_workers':100,
              'child_income_quartile':3,'income_rank_definition':'source quartile; illustrative fixture'}}
        payload={'baseline':case,'policy':case}
    elif verb=='entity':
        payload={'subject_id':'fixture','subject_type':'employer','displaced_workers':100,'source':'fixture','method':'fixture'}
    if verb!='scenario':
        path=tmp_path/'input.json';path.write_text(json.dumps(payload));common+=['--input',str(path)]
    else:common+=['--workers','100','--draws','16']
    if verb!='policy':common+=['--child-income-quartile','3','--income-rank-definition','source quartile; illustrative fixture']
    assert main(common)==0
    result=json.loads(capsys.readouterr().out)
    assert_custom(result['baseline']['parameter_envelope'] if verb=='policy' else result)


def test_missing_custom_library_never_falls_back_to_bundled_coefficients(custom):
    directory,parts=custom
    (directory/'study_estimates.csv').unlink()
    with pytest.raises(FileNotFoundError):
        sample_counts(parts['params'],parts['baselines'],scenario(),draws=8,params_dir=directory)
