"""Traps for Sobol estimator stability at small output variance.

The 2026-09-10 review recorded a shipped grandchild block run whose
first-order index for the transmission coefficient came out -.384
against a total index of .0753: the uncentered covariance product
turned a large output mean into design noise. These traps pin the
centered estimators and the dependent-block design-noise report:
- a constant output shift must leave every index unchanged
- a mean-dominated single-input model must still recover S = T = 1
- the dependent-block CI reports seed-replicate spread like the
  independent one, deterministically
"""

from __future__ import annotations

import pytest

from downstream.params import Correlation, Parameter, ParameterSet
from downstream.sensitivity import (
    correlated_block_sobol,
    correlated_block_sobol_ci,
    sobol_indices,
)


def _params(n: int) -> ParameterSet:
    return ParameterSet("synthetic", tuple(
        Parameter(f"x{i}->y", f"x{i}", "y", .5, 0, 1,
                  "canonical", "synthetic1999", "synthetic")
        for i in range(n)
    ))


def test_indices_are_invariant_to_a_constant_output_shift():
    params = _params(2)

    def compute(ps):
        return sum(p.point for p in ps.parameters)

    base = sobol_indices(params, compute, {}, base=64, seed=11)
    shifted = sobol_indices(params, lambda ps: compute(ps) + 1e6, {}, base=64, seed=11)
    assert base["indices"] == shifted["indices"]
    assert base["output_variance"] == shifted["output_variance"]


def test_block_indices_are_invariant_to_a_constant_output_shift():
    params = _params(2)
    correlations = [Correlation("x0->y", "x1->y", .5, "declared synthetic")]

    def compute(ps):
        return sum(p.point for p in ps.parameters)

    base = correlated_block_sobol(params, compute, {}, correlations, base=64, seed=11)
    shifted = correlated_block_sobol(params, lambda ps: compute(ps) + 1e6, {},
                                     correlations, base=64, seed=11)
    assert base["blocks"] == shifted["blocks"]
    assert base["output_variance"] == shifted["output_variance"]


def test_mean_dominated_model_recovers_unit_indices():
    """f = 1000 + 0.01*x has one input, so S = T = 1 exactly; the output
    mean dwarfs its variation by ~8 orders of magnitude in variance
    terms. The uncentered product returned noise hundreds of times the
    index on this shape; the centered covariance must not."""
    params = _params(1)

    def compute(ps):
        return 1000 + 0.01 * ps.parameters[0].point

    out = sobol_indices(params, compute, {}, base=256, seed=7)
    only = out["indices"][0]
    assert only["S_first"] == pytest.approx(1.0, abs=.05)
    assert only["S_total"] == pytest.approx(1.0, abs=.05)


def test_block_sobol_stays_on_the_additive_oracle_with_a_large_mean():
    """Same additive oracle as the review suite, with the output mean
    lifted by 1e4: centering must keep the variance shares at .75/.25."""
    params = _params(3)
    correlations = [Correlation("x0->y", "x1->y", .5, "declared synthetic")]

    def compute(ps):
        return 1e4 + sum(p.point for p in ps.parameters)

    result = correlated_block_sobol(params, compute, {}, correlations, base=4096, seed=7)
    expected = {("x0->y", "x1->y"): .75, ("x2->y",): .25}
    for block in result["blocks"]:
        for key in ("S_first", "S_total"):
            assert block[key] == pytest.approx(expected[tuple(block["links"])], abs=.06)


def test_block_ci_reports_seed_replicate_spread_deterministically():
    params = _params(2)
    correlations = [Correlation("x0->y", "x1->y", .5, "declared synthetic")]

    def compute(ps):
        return sum(p.point for p in ps.parameters)

    kwargs = dict(params=params, compute=compute, nodes={}, correlations=correlations,
                  base=64, seed=3, replicates=3)
    out = correlated_block_sobol_ci(**kwargs)
    assert out == correlated_block_sobol_ci(**kwargs)
    assert out["replicates"] == 3
    assert out["model_evals"] == 64 * 3 * 3  # one joint block: base * (1 + 2) sections per replicate
    assert all(b["S_total_sd"] >= 0 for b in out["blocks"])
    assert all(len(b["values"]) == 3 for b in out["blocks"])
    with pytest.raises(ValueError, match="replicates.*integer"):
        correlated_block_sobol_ci(**{**kwargs, "replicates": 1})
