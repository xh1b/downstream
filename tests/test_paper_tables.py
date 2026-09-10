"""The paper's scorecard must come from live engine results."""
import importlib.util
import json
from pathlib import Path

from downstream.params import load_all, load_correlations
from downstream.validate import run

ROOT = Path(__file__).resolve().parents[1]


def test_paper_generation_matches_engine_and_is_deterministic(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location('paper_tables', ROOT / 'paper/build_tables.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, 'OUT', tmp_path)
    module.main()
    output = json.loads((tmp_path / 'results.json').read_text())
    parts = load_all()
    assert output['validation'] == json.loads(json.dumps(run(parts['params'])))
    assert output['parameter_set_version'] == parts['params'].version
    assert output['declared_correlation_pairs'] == len(load_correlations(ROOT / 'params/correlations.csv'))
    rows = (tmp_path / 'parameters.tex').read_text()
    assert rows.count('\\nolinkurl{') == len(parts['params'].parameters)
    for p in parts['params'].parameters:
        assert p.link in rows
    # Charts must preserve the scorecard's units, order, and full precision.
    validation = run(parts['params'])
    unit = validation['v1_retrodict']
    panel = validation['v1_panel']['tercile_tests']
    expected_plots = {
        'mortality_plot.dat': [(r['modeled_excess_deaths_per100k'],
                                r['measured_differential_per100k']['point'])
                               for r in unit['scored']],
        'divorce_plot.dat': [(r['modeled_pp_women'], r['measured_pp_women']['point'])
                            for r in unit['scored_divorce']['windows']],
        'panel_divorce_plot.dat': [(r['modeled_gap_pp'], r['measured_gap_pp'])
                                  for r in panel[:2]],
        'panel_earnings_plot.dat': [(r['modeled_gap_usd'], r['measured_gap_usd'])
                                   for r in panel[2:]],
    }
    for filename, expected in expected_plots.items():
        lines = (tmp_path / filename).read_text().splitlines()
        assert lines[0].split() == ['row', 'point', 'low', 'high', 'measured']
        actual = [[float(value) for value in line.split()] for line in lines[1:]]
        assert actual == [[i, model['point'], model['low'], model['high'], measured]
                          for i, (model, measured) in enumerate(expected)]
    before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in tmp_path.iterdir()}
    module.main()
    after = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in tmp_path.iterdir()}
    assert before == after
