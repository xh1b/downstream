"""Regression traps for the 2026-09-09 deep mathematics/code audit."""
import csv

import pytest

from downstream.community import SchoolExposure, school_spending_child_earnings
from downstream.distributions import plan
from downstream.inference import _draw_samples
from downstream.ledger import validate_chain
from downstream.mc import simulate
from downstream.mortality import excess_deaths
from downstream.params import load_all, load_correlations, spearman_matrix
from downstream.validate import v1_retrodict


PARTS = load_all()


def test_public_chain_policy_rejects_boundary_and_wrong_kind():
    params, nodes = PARTS["params"], PARTS["nodes"]
    with pytest.raises(ValueError, match="boundary-applied"):
        validate_chain(params, ["earnings_shock->mortality_peak"], ["level"], nodes)
    with pytest.raises(ValueError, match="requires 'direct'"):
        validate_chain(params, ["displacement->child_earnings"], ["level"], nodes)


def test_v1_mortality_score_uses_the_shipped_survival_kernel():
    params = PARTS["params"]
    row = v1_retrodict(params)["scored"][0]
    bridge = {}
    with open("validation/adh2019_exposure_bridge.csv", newline="", encoding="utf-8") as f:
        bridge = {r["quantity"]: r for r in csv.DictReader(line for line in f if not line.startswith("#"))}
    n = abs(float(bridge["mfg_employment_share_change_per_pp"]["point"])) * 1000
    baseline = (float(bridge["male_death_rate_1990_per100k"]["point"])
                + float(bridge["female_death_rate_1990_per100k"]["point"])) / 2 / 100_000
    expected = excess_deaths(n, baseline,
                             params.by_link("earnings_shock->mortality_peak").point,
                             params.by_link("earnings_shock->mortality_sustained").point,
                             10)
    assert row["modeled_excess_deaths_per100k"]["point"] == round(expected, 2)


def test_inference_draws_use_the_same_asymmetric_normal_center_as_mc():
    params, nodes = PARTS["params"], PARTS["nodes"]
    link = "unemployment_status->mental_health_sd"  # point .510, midpoint .505
    compute = lambda ps: ps.by_link(link).point
    mc = simulate(params, compute, draws=1200, seed=17, nodes=nodes,
                  use_declared_correlations=False)
    raw = _draw_samples(params, compute, nodes, 1200, seed=17)
    assert sum(raw) / len(raw) == pytest.approx(mc["mean"], abs=0.001)


def test_declared_spearman_is_achieved_as_rank_correlation():
    params, nodes = PARTS["params"], PARTS["nodes"]
    matrix = spearman_matrix(params, load_correlations("params/correlations.csv"))
    draws = plan(params, nodes, 4000, 11, spearman=matrix).u
    links = [p.link for p in params.parameters]
    a, b = links.index("displacement->worker_earnings"), links.index("earnings_shock->mortality_peak")
    x, y = [r[a] for r in draws], [r[b] for r in draws]
    mx, my = sum(x) / len(x), sum(y) / len(y)
    observed = sum((u-mx)*(v-my) for u, v in zip(x, y)) / (
        sum((u-mx)**2 for u in x) * sum((v-my)**2 for v in y)
    ) ** .5
    assert observed == pytest.approx(-.5, abs=.035)


def test_school_cut_step_range_is_ordered():
    out = school_spending_child_earnings(PARTS["params"], SchoolExposure(-10, 12))
    assert out.low <= out.high
    assert out.steps[-1].value[1] <= out.steps[-1].value[2]
