"""Vignette, scenario, and Monte Carlo checks."""

from pathlib import Path

import pytest

from downstream.mc import simulate, simulate_chain, simulate_many
from downstream.params import Baseline, load, load_all
from downstream.scenario import BaselineMissing, ScenarioInput, compute_counts, sample_counts
from downstream.vignette import standard_family

PARAMS_DIR = Path(__file__).resolve().parent.parent / "params"


def test_vignette_structure_and_honesty_markers():
    parts = load_all(PARAMS_DIR)
    out = standard_family(parts["params"])
    assert out["parameter_set_version"] == "v1.39"
    assert "never a deterministic claim" in out["vignette"]["framing"]
    assert out["children_stream"]["weakest_identified"] == "greatgrandchild"
    assert out["family_stream"]["daughter_violence_odds"]["blocked"]
    assert any("never composed" in note for note in out["composition_notes"])


def test_vignette_grandchild_matches_gap_math():
    parts = load_all(PARAMS_DIR)
    out = standard_family(parts["params"])
    gc = out["children_stream"]["grandchild"]
    assert gc["point"] == pytest.approx(0.94918, abs=1e-4)


def _fake_verified_baselines():
    return {
        "all_cause_mortality_annual": Baseline(
            outcome="all_cause_mortality_annual",
            unit="deaths_per_person_year",
            population="test",
            value=0.004,
            citation="test1999",
            source="test",
            status="verified",
        ),
        "median_male_lifetime_earnings": Baseline(
            outcome="median_male_lifetime_earnings",
            unit="usd_2024",
            population="test",
            value=1_000_000.0,
            citation="test1999",
            source="test",
            status="verified",
        ),
    }


def test_legacy_scenario_both_conversions_computed_from_real_baselines():
    # v1.3 verified mortality; v1.4 verified lifetime earnings — both
    # count conversions now run on the REAL pinned values, nothing blocked.
    parts = load_all(PARAMS_DIR)
    out = compute_counts(
        parts["params"], parts["baselines"], ScenarioInput(displaced_workers=100, mortality_method="legacy_additive", net_tradable_jobs_lost=100, local_job_mix="high_tech")
    )
    deaths = out["modeled"]["excess_deaths"]
    # v1.10 table-pinned S&vW (sustained 1.135, peak 2.672):
    # 100 x 0.004944 x (0.135*20 + 1.672) = 2.163
    assert deaths["point"] == pytest.approx(2.16, abs=0.005)  # engine rounds to 2dp
    assert deaths["baseline"]["value"] == 0.004944
    child = out["modeled"]["child_lifetime_earnings_lost_usd"]
    child_point = parts["params"].by_link("displacement->child_earnings").point
    expected = 100 * 2 * (1 - child_point) * 2591418
    assert child["point"] == pytest.approx(expected, abs=1.0)
    assert child["baseline"]["value"] == 2591418
    assert out["blocked"] == []
    # service jobs need no baseline: computed
    assert out["modeled"]["local_service_jobs_lost"]["point"] == 500


def test_scenario_strict_raises_on_missing_baseline():
    # all shipped baselines are verified now, so strict SUCCEEDS on the
    # shipped set and only trips when a consumed baseline is absent
    parts = load_all(PARAMS_DIR)
    out = compute_counts(
        parts["params"], parts["baselines"], ScenarioInput(displaced_workers=100, net_tradable_jobs_lost=100, local_job_mix="high_tech"), strict=True
    )
    assert out["blocked"] == []
    baselines = dict(parts["baselines"])
    baselines.pop("median_male_lifetime_earnings")
    with pytest.raises(BaselineMissing):
        compute_counts(
            parts["params"], baselines, ScenarioInput(displaced_workers=100, net_tradable_jobs_lost=100, local_job_mix="high_tech"), strict=True
        )
    out = compute_counts(
        parts["params"], baselines, ScenarioInput(displaced_workers=100, net_tradable_jobs_lost=100, local_job_mix="high_tech")
    )
    assert "child_lifetime_earnings_lost_usd" in {b["outcome"] for b in out["blocked"]}


def test_scenario_counts_with_verified_baselines():
    parts = load_all(PARAMS_DIR)
    out = compute_counts(
        parts["params"], _fake_verified_baselines(), ScenarioInput(displaced_workers=100, mortality_method="legacy_additive")
    )
    deaths = out["modeled"]["excess_deaths"]
    # v1.10 table-pinned S&vW: sustained 1.135, peak 2.672
    # 100 * 0.004 * (0.135*20 + 1.672) = 1.7488
    assert deaths["point"] == pytest.approx(1.7488, abs=0.005)  # output rounded to 2dp
    assert not out["projection_eligibility"]["grandchild"]["eligible_for_validated_direct_contrast"]
    child = out["modeled"]["child_lifetime_earnings_lost_usd"]
    # 100 workers x 2 children x 9% x $1M
    assert child["point"] == pytest.approx(18_480_000.0, abs=1.0)  # v1.11: 1-0.9076=0.0924 gap


def test_mc_reproducible_and_bracketed():
    params = load(PARAMS_DIR / "parameters.csv")
    a = simulate_chain(
        params,
        ["displacement->child_earnings", "child_earnings->grandchild_earnings"],
        kinds=["direct", "gap"],
        draws=2000,
        seed=7,
    )
    b = simulate_chain(
        params,
        ["displacement->child_earnings", "child_earnings->grandchild_earnings"],
        kinds=["direct", "gap"],
        draws=2000,
        seed=7,
    )
    assert a == b  # same seed -> identical published range
    assert a["p05"] <= a["p50"] <= a["p95"]
    # p50 of gap-space composition sits near the deterministic point
    assert abs(a["p50"] - 0.94918) < 0.05
    assert a["p05"] > 0.80  # gap-space keeps the line near 1.0


def test_mc_generic_entry_rebuilds_full_module_per_draw():
    params = load(PARAMS_DIR / "parameters.csv")

    from downstream.children import child_line

    def compute(ps):
        return child_line(ps)["grandchild"].point

    out = simulate(params, compute, draws=500, seed=3)
    assert out["parameter_set_version"].endswith("-sampled")
    assert out["p05"] <= out["p50"] <= out["p95"]


def test_scenario_count_intervals_are_parameter_only_and_reproducible():
    parts = load_all(PARAMS_DIR)
    scenario = ScenarioInput(displaced_workers=100, mortality_method="odds_survival")
    a = sample_counts(parts["params"], parts["baselines"], scenario, draws=80, seed=8,
                      nodes=parts["nodes"], params_dir=PARAMS_DIR)
    b = sample_counts(parts["params"], parts["baselines"], scenario, draws=80, seed=8,
                      nodes=parts["nodes"], params_dir=PARAMS_DIR)
    assert a == b
    assert a["parameter_uncertainty"]["scope"] == "parameter uncertainty only"
    assert "baseline estimation error" in a["parameter_uncertainty"]["excluded"]
    for row in a["modeled"].values():
        interval = row["parameter_interval_90"]
        assert interval["p05"] <= interval["p50"] <= interval["p95"]
    # The old low/high fields remain an explicitly different object: a
    # support envelope, not an interval whose coverage is being claimed.
    assert a["uncertainty"]["band_kind"].startswith("parameter-support")
    predictive = a["predictive_uncertainty"]
    assert predictive["available"] is True
    assert predictive["exposed_deaths"]["p05"] <= predictive["exposed_deaths"]["p95"]
    assert "not an observable paired" in predictive["counterfactual_design"]


def test_predictive_counts_refuse_fractional_worker_aggregates():
    parts = load_all(PARAMS_DIR)
    out = sample_counts(parts["params"], parts["baselines"], ScenarioInput(2.5), draws=8,
                        nodes=parts["nodes"], params_dir=PARAMS_DIR)
    assert out["predictive_uncertainty"]["available"] is False


def test_simulate_many_preserves_joint_draw_metadata():
    params = load(PARAMS_DIR / "parameters.csv")
    out = simulate_many(params, lambda ps: {"a": ps.parameters[0].point,
                                             "b": 2 * ps.parameters[0].point},
                        draws=40, seed=9, params_dir=PARAMS_DIR)
    assert set(out["outcomes"]) == {"a", "b"}
    # Published summaries round independently to four decimal places.
    assert out["outcomes"]["b"]["mean"] == pytest.approx(2 * out["outcomes"]["a"]["mean"], abs=2e-4)
