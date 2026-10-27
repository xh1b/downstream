# @ref:test-source-repairs
# Contract: @link:source-repair-contract. Implementation: @link:code-source-contrasts.
# @tag:evidence @tag:testing
"""Source arithmetic, noninterchangeable exposures and all sixteen dispositions."""
from copy import deepcopy
import json
import math
import subprocess
import sys

import pytest

from downstream.params import load_all
from downstream.source_contrasts import source_contrast
from downstream.source_support import SourceUnavailable, policy

RESTORED = {
    'displacement->college_enrollment': (1-.432/40.66, 1-(.432+1.96*.094)/40.66, 1-(.432-1.96*.094)/40.66),
    'displacement->parental_income_shortrun': (1-8138.09/59832, 1-(8138.09+1.96*219.53)/59832, 1-(8138.09-1.96*219.53)/59832),
    'eitc_exposure->adult_earnings_early': (564, 564-1.96*244.9, 564+1.96*244.9),
    'household_ipv->child_internalizing_sd': (.48, .39, .57),
    'household_ipv->child_externalizing_sd': (.47, .38, .56),
    'unemployment_status->mental_health_sd': (.51, .47, .54),
}
CORRECTED = {
    'unemployment_rate->property_crime': ('unemployment_rate_change_pp->property_crime_log_change', (5.018/100, (5.018-1.96*1.134)/100, (5.018+1.96*1.134)/100)),
    'wage_ratio->household_ipv': ('female_male_wage_ratio_change->female_assault_log_change', (-.813, -.813-1.96*.317, -.813+1.96*.317)),
    'import_shock->gop_win_probability': ('import_penetration_change_pp->gop_win_probability_change_pp', (24.08, 24.08-1.96*12.07, 24.08+1.96*12.07)),
    'import_shock->radical_right_vote_share': ('import_exposure_eur1000_per_worker_2y->radical_right_vote_share_change_pp', (13.2, (.132-1.96*.051)*100, (.132+1.96*.051)*100)),
    'eviction_order->eviction_earnings_response': ('eviction_order->quarterly_earnings_gap_q5_8', (1-613/4254, 1-(613+1.96*248)/4254, 1-(613-1.96*248)/4254)),
    'displacement_event->exam_noncompletion_hazard': ('displacement_event->exam_noncompletion_change_pp', (.54, (.0054-1.96*.0027)*100, (.0054+1.96*.0027)*100)),
    'ipv_exposure->daughter_violence_odds': ('childhood_parental_violence_exposure->adult_partner_victimization_odds', (2.68, 1.49, 4.82)),
}
UNSUPPORTED = {'divorce->child_earnings', 'family_size->child_earnings', 'grandchild_earnings->greatgrandchild_earnings'}


def data(link, dose=1):
    p = load_all()['params'].by_link(link)
    return {'link': link, 'input_node': p.from_node,
            'input_unit': load_all()['nodes'][p.from_node].unit, 'dose': dose}


def evaluate(payload):
    parts = load_all()
    return source_contrast(parts['params'], parts['nodes'], payload)


@pytest.mark.parametrize('link,values', RESTORED.items())
def test_original_estimates_are_restored_from_primary_tables(link, values):
    p = load_all()['params'].by_link(link)
    assert (p.point, p.low, p.high) == pytest.approx(values, abs=5.1e-5)
    assert policy()['individual_review'][link]['disposition'] == 'verified_original'


@pytest.mark.parametrize('old,replacement', CORRECTED.items())
def test_corrected_parameters_preserve_arithmetic_and_retire_unsafe_aliases(old, replacement):
    link, expected = replacement
    p = load_all()['params'].by_link(link)
    assert (p.point, p.low, p.high) == pytest.approx(expected, abs=1e-10)
    with pytest.raises(SourceUnavailable):
        load_all()['params'].by_link(old)
    assert policy()['withdrawn_parameters'][old]['superseded_by'] == link
    assert not evaluate(data(link))['eligible_for_public_headline']


def test_all_sixteen_have_individual_source_dispositions_and_history():
    reviews = policy()['individual_review']
    assert set(reviews) == set(RESTORED) | set(CORRECTED) | UNSUPPORTED
    assert set(policy()['historical_withdrawn_parameters_v1_53']) == set(reviews)
    assert {k for k,r in reviews.items() if r['disposition']=='unsupported_relationship'} == UNSUPPORTED
    assert len({r['available_link'] for r in reviews.values() if 'available_link' in r}) == 13
    for review in reviews.values():
        source = policy()['reviewed_sources'][review['source_key']]
        assert source['source_url'].startswith('https://') and source['locator']
        assert 'artifact_sha256' in source or source['access_limit']
    for link in UNSUPPORTED:
        with pytest.raises(SourceUnavailable):
            load_all()['params'].by_link(link)


@pytest.mark.parametrize('old', ('unemployment_rate->property_crime', 'wage_ratio->household_ipv'))
def test_semilog_conversion_is_exact_and_preserves_signed_dose(old):
    link, (b,lo,hi) = CORRECTED[old]
    for dose in (.01, -1, 0):
        result = evaluate(data(link, dose))
        assert result['effect']['point'] == pytest.approx(b*dose)
        assert result['percent_change']['point'] == pytest.approx(100*math.expm1(b*dose))
        assert result['rate_ratio']['point'] == pytest.approx(math.exp(b*dose))
        assert result['effect']['low'] == pytest.approx(min(lo*dose,hi*dose))
        assert result['effect']['high'] == pytest.approx(max(lo*dose,hi*dose))
    assert evaluate(data(link,0))['rate_ratio']['point'] == 1


@pytest.mark.parametrize('old', ('import_shock->gop_win_probability','import_shock->radical_right_vote_share','wage_ratio->household_ipv'))
def test_wrong_currency_or_old_multiplier_exposure_cannot_be_substituted(old):
    link = CORRECTED[old][0]
    for key,value in (('input_node','import_shock_per_worker'),('input_unit','usd'),('input_unit','gap_multiplier')):
        payload=data(link,.01);payload[key]=value
        with pytest.raises(ValueError,match='node/unit'):
            evaluate(payload)


@pytest.mark.parametrize('old', ('eviction_order->eviction_earnings_response','displacement_event->exam_noncompletion_hazard','ipv_exposure->daughter_violence_odds'))
def test_fixed_study_contrast_is_not_a_population_count(old):
    link=CORRECTED[old][0]
    for n in (0,2,1000,-1):
        with pytest.raises(ValueError,match='dose must be 1'):
            evaluate(data(link,n))
    result=evaluate(data(link))
    assert result['input']['dose']==1
    if 'daughter' in old:
        assert 'both sexes pooled' in result['population_scope']
        assert 'daughters-only' in result['method']


@pytest.mark.parametrize('value',[True,math.inf,math.nan,'1',None])
def test_nonfinite_and_boolean_doses_are_refused(value):
    with pytest.raises(ValueError,match='finite'):
        evaluate(data(CORRECTED['wage_ratio->household_ipv'][0],value))


def test_unrepresentable_and_physically_impossible_contrasts_are_refused():
    with pytest.raises(ValueError,match='finite ratio'):
        evaluate(data(CORRECTED['wage_ratio->household_ipv'][0],-1e4))
    with pytest.raises(ValueError,match='possible percentage'):
        evaluate(data(CORRECTED['import_shock->gop_win_probability'][0],100))
    with pytest.raises(ValueError):
        evaluate({'link': 'anything'})


def test_saved_source_example_and_cli(tmp_path):
    from downstream.params import default_dir
    directory=default_dir().parent/'validation'
    payload=json.loads((directory/'source_contrast_input.json').read_text())
    before=deepcopy(payload); result=evaluate(payload)
    assert payload==before
    assert result==json.loads((directory/'source_contrast_result.json').read_text())
    completed=subprocess.run([sys.executable,'-m','downstream.cli','source-contrast','--input',str(directory/'source_contrast_input.json')],capture_output=True,text=True)
    assert completed.returncode==0,completed.stderr
    assert json.loads(completed.stdout)==result


def test_custom_data_cannot_reinterpret_reviewed_source_units_or_coefficients():
    from dataclasses import replace
    parts=load_all();link=CORRECTED['wage_ratio->household_ipv'][0]
    params=parts['params'].with_param(link,-1)
    with pytest.raises(ValueError,match='reviewed source'):
        source_contrast(params,parts['nodes'],data(link))
    nodes=dict(parts['nodes']);node=nodes['female_male_wage_ratio_change']
    nodes[node.name]=replace(node,unit='usd')
    payload=data(link);payload['input_unit']='usd'
    with pytest.raises(ValueError,match='reviewed source'):
        source_contrast(parts['params'],nodes,payload)
