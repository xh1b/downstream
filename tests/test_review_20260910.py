"""Independent numerical oracles for the September 10 review repairs."""
from dataclasses import replace

import pytest

from downstream.distributions import plan
from downstream.ledger import validate_chain
from downstream.mc import simulate_chain
from downstream.mortality import odds_risk, rate_to_risk
from downstream.params import Correlation, Parameter, ParameterSet, load_all
from downstream.place import Place, PRIOR_N
from downstream.scenario import ScenarioInput, sample_counts
from downstream.sensitivity import correlated_block_sobol


def synthetic_parameters():
    return ParameterSet("synthetic", tuple(
        Parameter(f"x{i}->y", f"x{i}", "y", .5, 0, 1,
                  "canonical", "synthetic", "synthetic") for i in range(3)
    ))


def test_copula_seed_changes_ranks_and_same_seed_reproduces_them():
    params = synthetic_parameters()
    correlation = [[1, .5, 0], [.5, 1, 0], [0, 0, 1]]
    a = plan(params, {}, 256, 7, spearman=correlation)
    b = plan(params, {}, 256, 8, spearman=correlation)
    assert a == plan(params, {}, 256, 7, spearman=correlation)
    # Independent replicate ranks must not be the same template with only
    # within-stratum jitter changed. The fixed-seed bug gave correlation ~1.
    distance = sum((x[0] - y[0])**2 for x, y in zip(a.u, b.u)) / len(a.u)
    assert .10 < distance < .23  # E[(U-V)^2] = 1/6 for independent uniforms.


def test_correlated_block_sobol_matches_additive_variance_oracle():
    params = synthetic_parameters()
    result = correlated_block_sobol(
        params, lambda ps: sum(p.point for p in ps.parameters), {},
        [Correlation("x0->y", "x1->y", .5, "declared synthetic")],
        base=4096, seed=7,
    )
    # Uniform margins: Spearman = Pearson, so Var(X0+X1)=3/12,
    # Var(X2)=1/12. Additivity gives first = total = .75 and .25.
    expected = {("x0->y", "x1->y"): .75, ("x2->y",): .25}
    for block in result["blocks"]:
        for key in ("S_first", "S_total"):
            assert block[key] == pytest.approx(expected[tuple(block["links"])], abs=.06)


@pytest.mark.parametrize("links,kinds", [
    (["displacement->worker_earnings", "child_earnings->grandchild_earnings"], ["direct", "gap"]),
    (["displacement->child_earnings", "grandchild_earnings->greatgrandchild_earnings"], ["direct", "gap"]),
    (["child_earnings->grandchild_earnings"] * 2, ["gap", "gap"]),
])
def test_public_chains_reject_disconnected_transitions(links, kinds):
    parts = load_all()
    with pytest.raises(ValueError, match="disconnected chain"):
        validate_chain(parts["params"], links, kinds, parts["nodes"])


def test_mc_chain_honors_nonunit_start():
    parts = load_all()
    link = "child_earnings->grandchild_earnings"
    params = ParameterSet("pinned", (replace(parts["params"].by_link(link),
                                             point=.5, low=.5, high=.5),))
    result = simulate_chain(params, [link], base=.8, kinds=["gap"], draws=8,
                            nodes=parts["nodes"], use_declared_correlations=False)
    assert result["mean"] == .9
    assert result["p05"] == result["p95"] == .9


def test_predictive_cohorts_refuse_generic_county_mortality_pooling(monkeypatch):
    parts = load_all()
    national = parts["baselines"]["all_cause_mortality_annual"].value
    local = .04
    places = {"county": Place("county", "Synthetic", "county", None, None,
                               local, PRIOR_N["all_cause_mortality_annual"],
                               None, None, "synthetic")}
    # The modifier needs a national reference, but no mobility measurements.
    places["national"] = replace(places["county"], key="national", level="national")
    calls = []

    def record_probability(self, n, p):
        calls.append(p)
        return 0

    monkeypatch.setattr("random.Random.binomialvariate", record_probability)
    params = ParameterSet("pinned", tuple(replace(p, low=p.point, high=p.point)
                                         for p in parts["params"].parameters))
    result = sample_counts(params, parts["baselines"], ScenarioInput(100, exposure_years=1),
                           places=places, place_key="county", nodes=parts["nodes"], draws=8)
    pooled = rate_to_risk(national)
    exposed = odds_risk(pooled, params.by_link("earnings_shock->mortality_peak").point)
    assert calls[::2] == pytest.approx([exposed] * 8)
    assert calls[1::2] == pytest.approx([pooled] * 8)
    assert result["predictive_uncertainty"]["baseline_annual_probability"] == pooled


def test_legacy_additive_does_not_claim_a_predictive_probability_model():
    parts = load_all()
    result = sample_counts(parts["params"], parts["baselines"],
                           ScenarioInput(100, mortality_method="legacy_additive"),
                           nodes=parts["nodes"], draws=8)
    assert not result["predictive_uncertainty"]["available"]
    assert "legacy additive" in result["predictive_uncertainty"]["reason"]
