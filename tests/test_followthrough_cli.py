import json
import shutil

import pytest

from downstream.cli import main
from downstream.params import default_dir


@pytest.mark.parametrize('command,filename,schema',[
    ('household','household_five_year_input.json','downstream-household-comparison/1'),
    ('mortality-cohort','cps2024_hypothetical_mortality_input.json','downstream-stratified-mortality/1'),
    ('uncertainty','uncertainty_budget_input.json','downstream-uncertainty-budget/1')])
def test_new_cli_verbs_use_saved_reproducible_inputs(command,filename,schema,tmp_path,capsys):
    source=default_dir().parent/'validation'/filename
    value=json.loads(source.read_text())
    if command=='uncertainty':value['draws']=8
    path=tmp_path/'input.json';path.write_text(json.dumps(value))
    assert main([command,'--input',str(path)])==0
    result=json.loads(capsys.readouterr().out)
    assert result['schema']==schema
    assert not result['eligible_for_public_headline']


def test_child_cli_keeps_signed_subgroup_present_value(tmp_path,capsys):
    path=tmp_path/'children.json'
    path.write_text('[{"age_at_displacement":11,"sex":"Male"}]')
    assert main(['scenario','--workers','100','--children','1','--draws','8',
                 '--child-profiles',str(path),'--child-income-quartile','3',
                 '--income-rank-definition','source income group; illustrative transport',
                 '--real-discount-rate','.03','--valuation-year','2026'])==0
    result=json.loads(capsys.readouterr().out)
    assert result['modeled']['child_lifetime_earnings_lost_usd']['point']<0
    assert result['child_valuation']['projections']['constant_career_gap']['point']<0


def test_custom_mortality_data_cannot_silently_fall_back_to_default(tmp_path,capsys):
    destination=tmp_path/'params'
    shutil.copytree(default_dir(),destination)
    path=destination/'age_mortality.csv'
    path.write_text(path.read_text().replace('2015-2019','2020-2024'))
    source=default_dir().parent/'validation/cps2024_hypothetical_mortality_input.json'
    assert main(['mortality-cohort','--params',str(destination),'--input',str(source)])==2
    assert 'incompatible' in capsys.readouterr().err
