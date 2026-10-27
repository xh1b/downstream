# @ref:test-source-withdrawals
# Contract: @link:source-withdrawal-contract.
# Implementation: @link:code-source-support; @link:code-params; @link:code-ledger.
# @tag:evidence @tag:testing
"""Unsupported archived inputs never become numeric model outputs again."""
from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys

import pytest

from downstream.ledger import DIRECT, start
from downstream.params import load_all
from downstream.source_support import SourceUnavailable, UnavailableLedger, policy

ORIGINAL_WITHDRAWALS = (
    'divorce->child_earnings',
    'family_size->child_earnings',
    'grandchild_earnings->greatgrandchild_earnings',
    'ipv_exposure->daughter_violence_odds',
    'wage_ratio->household_ipv',
    'displacement->college_enrollment',
    'displacement->parental_income_shortrun',
    'unemployment_rate->property_crime',
    'eitc_exposure->adult_earnings_early',
    'import_shock->gop_win_probability',
    'eviction_order->eviction_earnings_response',
    'household_ipv->child_internalizing_sd',
    'household_ipv->child_externalizing_sd',
    'unemployment_status->mental_health_sd',
    'import_shock->radical_right_vote_share',
    'displacement_event->exam_noncompletion_hazard',
)

RESTORED = {
    'displacement->college_enrollment', 'displacement->parental_income_shortrun',
    'eitc_exposure->adult_earnings_early', 'household_ipv->child_internalizing_sd',
    'household_ipv->child_externalizing_sd', 'unemployment_status->mental_health_sd',
}
WITHDRAWN = tuple(link for link in ORIGINAL_WITHDRAWALS if link not in RESTORED)



@pytest.mark.parametrize('link', WITHDRAWN)
def test_every_withdrawn_lookup_and_direct_archive_composition_is_refused(link):
    params = load_all()['params']
    original = params.retained_by_link(link)
    assert original.link == link
    with pytest.raises(SourceUnavailable, match=link):
        params.by_link(link)
    with pytest.raises(SourceUnavailable, match=link):
        start('test', 'gap_multiplier').apply(DIRECT, original)
    with pytest.raises(SourceUnavailable):
        params.with_param(link, 1).by_link(link)
    from downstream.inference import analytic_chain
    with pytest.raises(SourceUnavailable):
        analytic_chain(params, [link], ["direct"], load_all()["nodes"])


def test_unavailable_branch_preserves_direct_child_and_grandchild():
    from downstream.children import child_line
    from downstream.scenario import ScenarioInput, compute_counts
    parts = load_all()
    line = child_line(parts['params'])
    assert line['child'].point > 0 and line['grandchild'].point > 0
    assert isinstance(line['greatgrandchild'], UnavailableLedger)
    with pytest.raises(SourceUnavailable):
        _ = line['greatgrandchild'].point
    report = compute_counts(parts['params'], parts['baselines'], ScenarioInput(1000))
    assert report['modeled']['excess_deaths']['point'] == 28.76
    assert report['modeled']['child_lifetime_earnings_lost_usd']['point'] > 0
    assert report['multipliers']['greatgrandchild_earnings']['point'] is None


def test_snapshot_partitions_active_and_archived_parameters_and_references():
    from downstream.snapshot import build
    result = build()
    assert result['schema'] == 'downstream-parameter-set/3'
    assert len(result['parameters']) == 64
    assert {row['link'] for row in result['withdrawn_parameters']} == set(WITHDRAWN)
    assert not (set(WITHDRAWN) & {row['link'] for row in result['parameters']})
    assert not (set(result['unidentified_reference_archive']) & set(result['citations']))
    assert result['source_support_policy_sha256']


def test_sampling_and_custom_point_overrides_cannot_resurrect_withdrawals():
    from downstream.mc import simulate
    parts = load_all()
    with pytest.raises(SourceUnavailable):
        simulate(parts['params'], lambda ps: ps.by_link(WITHDRAWN[0]).point,
                 draws=2, nodes=parts['nodes'])
    # Even changing a retained record's point and version does not change the policy.
    params = replace(parts['params'], version='custom', parameters=tuple(
        replace(row, point=row.low) if row.link == WITHDRAWN[0] else row
        for row in parts['params'].parameters))
    with pytest.raises(SourceUnavailable):
        params.by_link(WITHDRAWN[0])


def test_grouped_cli_outputs_are_partial_and_never_emit_withdrawn_numbers():
    for arguments in (['family'], ['transmissions', '--walk', 'earnings'], ['ensemble']):
        completed = subprocess.run([sys.executable, '-m', 'downstream.cli', *arguments],
                                   capture_output=True, text=True)
        assert completed.returncode == 0, completed.stderr
        report = json.loads(completed.stdout)
        if arguments[0] == 'family':
            assert report['children_stream']['greatgrandchild']['point'] is None
            assert report['family_stream']['daughter_violence_odds']['point'] is None
        elif arguments[0] == 'transmissions':
            assert report['generations']['greatgrandchild']['available'] is False
        else:
            assert report['unavailable_variants'][0]['variant'] == 'parallel_gap_additive'
            assert all(row['variant'] != 'parallel_gap_additive' for row in report['variants'])


def test_original_parameter_csv_records_are_byte_preserved():
    import hashlib
    root = Path(__file__).resolve().parents[1]
    # SHA-256 at d7691dac652a81bddb16c9f91a9cf8ecd88b70db, before withdrawal policy.
    # A fixed receipt also works in shallow CI checkouts and source distributions.
    assert hashlib.sha256((root/'params/parameters.csv').read_bytes()[:82447]).hexdigest() == (
        'f6ce70a100042189691eb10291c9ead48655cbf37dc49d49c4ac2ce4a3a468d6'
    )


def test_policy_matches_the_public_withdrawal_inventory():
    from collections import Counter
    rows = policy()['historical_withdrawn_parameters_v1_53']
    assert set(rows) == set(ORIGINAL_WITHDRAWALS)
    assert set(policy()['withdrawn_parameters']) == set(WITHDRAWN)
    assert Counter(row['finding'] for row in rows.values()) == {'sourceMismatch': 7, 'notVerified': 9}
    assert set(policy()['unidentified_references']) == {'adermon2018', 'lindo2018'}
