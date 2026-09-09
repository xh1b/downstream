"""Synthetic warehouse contract fixtures; no database or production records."""
from copy import deepcopy
from decimal import Decimal
import json

import pytest

from downstream.cli import main
from downstream.employer import DocumentedExposure
from downstream.params import load_all
from downstream.scenario import ScenarioInput, compute_counts


@pytest.fixture
def employer_row():
    return dict(subject_id='fixture-employer', subject_type='employer',
                source='synthetic aggregate fixture', americans_displaced=137.125,
                displacement_breakdown=dict(base=100, wage_depression=12.125,
                    warn_layoffs=25, total=137.125, certified_filings=4,
                    total_workers=100, warn_notices=2, avg_wage_gap_pct=12.1,
                    formula='upstream exposure method'))


def test_warehouse_to_cli_to_engine(employer_row, tmp_path, capsys):
    before = deepcopy(employer_row)
    path = tmp_path / 'warehouse.json'
    path.write_text(json.dumps(employer_row))
    assert main(['entity', '--input', str(path), '--input-format', 'warehouse',
                 '--children', '3', '--place', 'national']) == 0
    result = json.loads(capsys.readouterr().out)
    parts = load_all()
    expected = compute_counts(parts['params'], parts['baselines'], ScenarioInput(137.125, n_children=3))
    for key, row in expected['modeled'].items():
        for field in ('point', 'low', 'high'):
            assert result['modeled'][key][field] == row[field]
    assert result['exposure']['displaced_workers'] == 137.125
    assert result['exposure_provenance']['method'] == 'upstream exposure method'
    assert result['place']['key'] == 'national'
    assert employer_row == before


def test_person_does_not_require_warn(employer_row):
    employer_row.update(subject_type='person', americans_displaced=112.125)
    b = employer_row['displacement_breakdown']
    del b['warn_layoffs']
    b['total'] = 112.125
    assert DocumentedExposure.from_warehouse(**employer_row).displaced_workers == 112.125


def test_rounding_preserves_authoritative_total(employer_row):
    employer_row['americans_displaced'] = Decimal('137.126')
    employer_row['displacement_breakdown']['total'] = Decimal('137.126')
    assert DocumentedExposure.from_warehouse(**employer_row).displaced_workers == 137.126


@pytest.mark.parametrize('key,value', [('base', None), ('wage_depression', '12.125'),
    ('warn_layoffs', -1), ('warn_layoffs', True), ('base', float('nan')),
    ('base', float('inf')), ('formula', ''), ('total', 999), ('base', 999)])
def test_malformed_or_inconsistent_breakdown_refused(employer_row, key, value):
    employer_row['displacement_breakdown'][key] = value
    with pytest.raises(ValueError):
        DocumentedExposure.from_warehouse(**employer_row)


def test_missing_warn_is_not_silently_zero(employer_row):
    del employer_row['displacement_breakdown']['warn_layoffs']
    with pytest.raises(ValueError, match='warn_layoffs'):
        DocumentedExposure.from_warehouse(**employer_row)


def test_zero_requires_explicit_components(employer_row):
    employer_row['americans_displaced'] = 0
    b = employer_row['displacement_breakdown']
    b.update(base=0, wage_depression=0, warn_layoffs=0, total=0)
    assert DocumentedExposure.from_warehouse(**employer_row).displaced_workers == 0
    employer_row['displacement_breakdown'] = {}
    with pytest.raises(ValueError, match='missing'):
        DocumentedExposure.from_warehouse(**employer_row)


@pytest.mark.parametrize('flags', [('--children', '-1'), ('--tradable-share', '2'),
                                  ('--exposure-years', 'nan')])
def test_invalid_scenario_cli_refused(employer_row, tmp_path, capsys, flags):
    path = tmp_path / 'row.json'
    path.write_text(json.dumps(employer_row))
    with pytest.raises(SystemExit) as exc:
        main(['entity', '--input', str(path), '--input-format', 'warehouse', *flags])
    assert exc.value.code == 2
    assert capsys.readouterr().out == ''
