"""Distribution, LHS, and correlation-induction checks."""

import math
import random

import pytest

from downstream.distributions import (
    LOGNORMAL,
    LOGUNIFORM,
    UNIFORM,
    apply_rank_correlation,
    dist_for,
    lhs_matrix,
    sample_unit_interval,
    _probit,
)
from downstream.params import load_nodes, default_dir

NODES = load_nodes(default_dir() / "nodes.csv")


def _unit(node_name):
    return NODES[node_name].unit if node_name in NODES else None


def test_rate_ratios_default_to_log_space():
    from downstream.params import Parameter, load, default_dir

    # the unit DEFAULT for ratio rows is loguniform (v1.27: a row may
    # override it with a declared dist when its band is a reported CI)
    fake = Parameter(
        link="t", from_node="a", to_node="b", point=2.0, low=1.5, high=2.5,
        tier="EXACT", citation="x", population_scope="t",
    )
    assert dist_for(fake, "rate_ratio") == LOGUNIFORM
    params = load(default_dir() / "parameters.csv")
    mort = params.by_link("earnings_shock->mortality_peak")
    # v1.27: the band IS exp(beta +/- 1.96 SE), so the row declares the
    # CI shape — lognormal (still log space, same honesty property)
    assert dist_for(mort, "rate_ratio") == LOGNORMAL
    gap = params.by_link("displacement->child_earnings")
    assert dist_for(gap, "child_earnings") == UNIFORM


def test_log_space_sampling_is_the_geometric_midpoint():
    # u=0.5 in log space gives the GEOMETRIC mean, not the arithmetic one
    v = sample_unit_interval(LOGUNIFORM, 0.5, 1.5, 2.0)
    assert v == pytest.approx(math.sqrt(1.5 * 2.0), abs=1e-9)


def test_log_space_with_nonpositive_bound_fails_loudly():
    with pytest.raises(ValueError):
        sample_unit_interval(LOGUNIFORM, 0.5, -0.5, 2.0)


def test_all_samples_stay_inside_the_declared_band():
    rng = random.Random(3)
    for dist in (UNIFORM, LOGUNIFORM, "normal"):
        for _ in range(500):
            v = sample_unit_interval(dist, rng.random(), 1.15, 2.0)
            assert 1.15 <= v <= 2.0


def test_probit_sanity():
    assert _probit(0.5) == pytest.approx(0.0, abs=1e-9)
    assert _probit(0.975) == pytest.approx(1.96, abs=0.01)
    with pytest.raises(ValueError):
        _probit(0.0)


def test_lhs_covers_every_stratum_exactly_once():
    """THE LHS property: one point per stratum per column — this is
    what makes it converge faster than IID."""
    rng = random.Random(11)
    m = lhs_matrix(4, 50, rng)
    for j in range(4):
        col = sorted(row[j] for row in m)
        for k in range(50):
            in_stratum = sum(1 for v in col if k / 50 <= v < (k + 1) / 50)
            assert in_stratum == 1, f"stratum {k} of column {j}"


def test_rank_correlation_preserves_marginals_exactly():
    """Iman-Conover must NEVER change the values, only their order."""
    rng = random.Random(7)
    u = lhs_matrix(2, 200, rng)
    rho = [[1.0, 0.9], [0.9, 1.0]]
    out = apply_rank_correlation(u, rho)
    for j in range(2):
        assert sorted(row[j] for row in out) == sorted(row[j] for row in u)


def test_rank_correlation_induces_positive_dependence():
    rng = random.Random(9)
    u = lhs_matrix(2, 400, rng)
    rho = [[1.0, 0.9], [0.9, 1.0]]
    out = apply_rank_correlation(u, rho)

    def rank(xs):
        order = sorted(range(len(xs)), key=lambda i: xs[i])
        r = [0] * len(xs)
        for rank_, i in enumerate(order):
            r[i] = rank_
        return r

    ra, rb = rank([row[0] for row in out]), rank([row[1] for row in out])
    n = len(ra)
    ma, mb = sum(ra) / n, sum(rb) / n
    cov = sum((a - ma) * (b - mb) for a, b in zip(ra, rb))
    var = math.sqrt(sum((a - ma) ** 2 for a in ra) * sum((b - mb) ** 2 for b in rb))
    assert cov / var > 0.7  # target Spearman 0.9 with finite-sample slack


def test_non_psd_matrix_is_rejected():
    with pytest.raises(ValueError):
        apply_rank_correlation([[0.0] * 2 for _ in range(3)], [[1.0, 1.5], [1.5, 1.0]])


def test_correlation_matrix_size_must_match():
    with pytest.raises(ValueError):
        apply_rank_correlation([[0.1, 0.2], [0.3, 0.4]], [[1.0]])
