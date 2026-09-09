import json
import math

import pytest

from downstream.cli import main
from downstream.employer import DocumentedExposure, compute_entity_counts
from downstream.params import load_all, default_dir
from downstream.scenario import ScenarioInput, compute_counts


def exposure(workers=100):
    return DocumentedExposure('fixture', 'employer', workers, 'fixture source', 'precomputed exposure')


@pytest.mark.parametrize('workers', [-1, math.inf, math.nan, True, '100'])
def test_invalid_exposure_refused(workers):
    with pytest.raises(ValueError):
        exposure(workers)


def test_adapter_preserves_engine_and_scenario():
    parts = load_all(default_dir())
    sc = ScenarioInput(999, n_children=3)
    result = compute_entity_counts(parts['params'], parts['baselines'], exposure(), sc)
    direct = compute_counts(parts['params'], parts['baselines'], ScenarioInput(100, n_children=3))
    assert result['modeled'] == direct['modeled']
    assert sc.displaced_workers == 999
    assert result['exposure_provenance']['source'] == 'fixture source'


def test_person_cli_uses_impact_framing(tmp_path, capsys):
    path = tmp_path / 'exposure.json'
    path.write_text(json.dumps(dict(subject_id='fixture', subject_type='person',
                                  displaced_workers=0, source='fixture', method='fixture')))
    assert main(['entity', '--input', str(path)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result['subject']['type'] == 'person'
    assert result['modeled']['excess_deaths']['point'] == 0
    assert 'not a prediction' in result['interpretation']
