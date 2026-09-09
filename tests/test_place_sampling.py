"""Place experiments must recompute gamma and preserve national behavior."""
import json

import pytest

from downstream.cli import main
from downstream.params import load_all, default_dir
from downstream.place import load_places, MOBILITY_MODIFIER_LINK
from downstream.knobs import sweep
from downstream.scenario import ScenarioInput


def run(capsys, *args):
    assert main(list(args)) == 0
    return json.loads(capsys.readouterr().out)


def test_national_mc_matches_and_county_moves(capsys):
    args = ('simulate', '--outcome', 'child', '--draws', '40')
    national = run(capsys, *args)
    explicit = run(capsys, *args, '--place', 'national')
    for key in ('p05', 'p50', 'p95', 'mean'):
        assert explicit[key] == national[key]
    places = load_places()
    key = next(k for k, p in places.items() if p.mobility_percentile is not None
               and p.mobility_percentile != places['national'].mobility_percentile)
    county = run(capsys, *args, '--place', key)
    assert county['mean'] != national['mean']
    assert county['place']['mobility_modifier']['applied']


def test_sweep_recomputes_mobility_at_each_pin():
    parts = load_all(default_dir())
    ps = parts['params']
    places = load_places()
    key = next(k for k, p in places.items() if p.mobility_percentile is not None
               and p.mobility_percentile != places['national'].mobility_percentile)
    p = ps.by_link(MOBILITY_MODIFIER_LINK)
    sc = ScenarioInput(1000)
    result = sweep(ps, parts['baselines'], sc, p.link, [p.low, p.high],
                   places=places, place_key=key)
    assert result['rows'][0]['modeled']['mult:child_earnings'] != result['rows'][1]['modeled']['mult:child_earnings']


@pytest.mark.parametrize('args', [
    ('sensitivity', '--base', '8'),
    ('sensitivity', '--base', '8', '--ci', '2'),
    ('knobs', '--action', 'voi', '--draws', '8'),
    ('knobs', '--action', 'voi', '--outcome', 'excess_deaths', '--draws', '8'),
])
def test_sampling_surfaces_carry_place(capsys, args):
    result = run(capsys, *args, '--place', 'national')
    assert result['place']['provenance']['key'] == 'national'
    assert 'fixed' in result['place_uncertainty']


def test_arbitrary_chain_refuses_place(capsys):
    with pytest.raises(SystemExit) as exc:
        main(['simulate', '--links', 'displacement->child_earnings', '--place', 'national'])
    assert exc.value.code == 2
    assert '--place requires --outcome' in capsys.readouterr().err


def test_mc_samples_gamma_instead_of_freezing_it(capsys, monkeypatch):
    from dataclasses import replace
    import downstream.cli as cli
    from downstream.params import ParameterSet

    parts = load_all(default_dir())
    params = parts['params']
    parts['params'] = ParameterSet(params.version, tuple(
        p if p.link == MOBILITY_MODIFIER_LINK else replace(p, low=p.point, high=p.point)
        for p in params.parameters
    ))
    monkeypatch.setattr(cli, 'load_all', lambda _: parts)
    places = load_places()
    key = max(places, key=lambda k: abs((places[k].mobility_percentile or
              places['national'].mobility_percentile) - places['national'].mobility_percentile))
    national = run(capsys, 'simulate', '--outcome', 'child', '--draws', '80')
    local = run(capsys, 'simulate', '--outcome', 'child', '--draws', '80', '--place', key)
    assert national['p05'] == national['p95']
    assert local['p05'] < local['p95']
