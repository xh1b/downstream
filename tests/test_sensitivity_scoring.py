"""Sobol sensitivity + scoring-rule checks."""

import random

import pytest

from downstream.params import Correlation, Parameter, ParameterSet, load, default_dir, load_nodes
from downstream.scoring import calibration_table, coverage, crps_sample, pit
from downstream.sensitivity import correlated_block_sobol, sobol_indices

NODES = load_nodes(default_dir() / "nodes.csv")


def _fake_params(bands: list[tuple[float, float]]) -> ParameterSet:
    rows = []
    for i, (lo, hi) in enumerate(bands):
        rows.append(
            Parameter(
                link=f"x{i}->y",
                from_node="displacement_event",
                to_node="worker_earnings",
                point=(lo + hi) / 2,
                low=lo,
                high=hi,
                tier="canonical",
                citation="test1999",
                population_scope="test",
            )
        )
    return ParameterSet(version="t", parameters=tuple(rows))


def test_sobol_identifies_the_dominant_parameter():
    """Output = p0 + p1; p0 has a 10x wider band -> p0 must dominate
    the output variance. A method that cannot rank these is broken."""
    params = _fake_params([(0.0, 10.0), (4.9, 5.1)])

    def compute(ps):
        return sum(p.point for p in ps.parameters)

    out = sobol_indices(params, compute, NODES, base=128, seed=5)
    by_link = {r["link"]: r["S_total"] for r in out["indices"]}
    assert by_link["x0->y"] > 5 * by_link["x1->y"]


def test_sobol_is_seeded_and_deterministic():
    params = _fake_params([(0.5, 1.5), (1.0, 3.0)])

    def compute(ps):
        return ps.parameters[0].point * ps.parameters[1].point

    a = sobol_indices(params, compute, NODES, base=64, seed=2)
    b = sobol_indices(params, compute, NODES, base=64, seed=2)
    assert a == b


def test_sobol_noise_stays_bounded():
    params = _fake_params([(0.5, 1.5), (1.0, 3.0), (0.0, 2.0), (2.0, 2.5)])

    def compute(ps):
        return sum(p.point for p in ps.parameters)

    out = sobol_indices(params, compute, NODES, base=64, seed=1)
    for r in out["indices"]:
        assert -0.25 <= r["S_first"] <= 1.25
        assert -0.25 <= r["S_total"] <= 1.25


def test_sobol_runs_on_the_real_child_line():
    params = load(default_dir() / "parameters.csv")

    from downstream.children import child_line

    out = sobol_indices(
        params, lambda ps: child_line(ps)["grandchild"].point, NODES, base=64, seed=3
    )
    assert len(out["indices"]) == len(params.parameters)
    assert out["model_evals"] == 64 * (len(params.parameters) + 2)
    # the IGE transmission step must be among the leading drivers
    top3 = {r["link"] for r in out["indices"][:3]}
    assert "child_earnings->grandchild_earnings" in top3


def test_correlated_inputs_are_attributed_as_one_block():
    params = _fake_params([(0.0, 1.0), (0.0, 1.0), (0.0, 1.0)])
    correlations = [Correlation("x0->y", "x1->y", .5, "declared test coupling")]
    out = correlated_block_sobol(
        params, lambda ps: sum(p.point for p in ps.parameters), NODES,
        correlations, base=64, seed=7,
    )
    assert out["correlations_applied"] == 1
    assert {tuple(r["links"]) for r in out["blocks"]} == {("x0->y", "x1->y"), ("x2->y",)}


def test_crps_of_point_forecast_is_absolute_error():
    assert crps_sample([3.0], 1.0) == pytest.approx(2.0)
    assert crps_sample([1.0], 1.0) == pytest.approx(0.0)


def test_crps_rewards_honest_uncertainty():
    """A tight sample around the truth must beat a wide one."""
    rng = random.Random(4)
    tight = [2.0 + rng.gauss(0, 0.1) for _ in range(500)]
    wide = [2.0 + rng.gauss(0, 5.0) for _ in range(500)]
    assert crps_sample(tight, 2.0) < crps_sample(wide, 2.0)


def test_crps_sample_matches_bruteforce_on_small_input():
    s = [1.0, 2.0, 4.0]
    y = 3.0
    brute = sum(abs(x - y) for x in s) / 3 - 0.5 * sum(
        abs(a - b) for a in s for b in s
    ) / 9
    assert crps_sample(s, y) == pytest.approx(brute, abs=1e-12)


def test_coverage_counts_hits():
    bands = [(0, 1), (0, 1), (5, 6), (0, 1)]
    obs = [0.5, 2.0, 5.5, 0.9]
    assert coverage(bands, obs) == pytest.approx(0.75)
    with pytest.raises(ValueError):
        coverage(bands[:-1], obs)


def test_pit_and_calibration():
    samples = [float(i) for i in range(10)]  # 0..9
    assert pit(samples, 4.5) == pytest.approx(0.5)
    table = calibration_table([pit(samples, v) for v in range(10)], bins=10)
    assert sum(b["count"] for b in table) == 10
    with pytest.raises(ValueError):
        calibration_table([0.5], bins=1)
