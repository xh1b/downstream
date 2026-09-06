"""Vignette, scenario, and Monte Carlo checks."""

from pathlib import Path

import pytest

from downstream.mc import simulate, simulate_chain
from downstream.params import Baseline, load, load_all
from downstream.scenario import BaselineMissing, ScenarioInput, compute_counts
from downstream.vignette import standard_family

PARAMS_DIR = Path(__file__).resolve().parent.parent / "params"


def test_vignette_structure_and_honesty_markers():
    parts = load_all(PARAMS_DIR)
    out = standard_family(parts["params"])
    assert out["parameter_set_version"] == "v1.1"
    assert "never a deterministic claim" in out["vignette"]["framing"]
    assert out["children_stream"]["weakest_identified"] == "greatgrandchild"
    assert out["family_stream"]["daughter_violence_odds"]["blocked"]
    assert any("never composed" in note for note in out["composition_notes"])


def test_vignette_grandchild_matches_gap_math():
    parts = load_all(PARAMS_DIR)
    out = standard_family(parts["params"])
    gc = out["children_stream"]["grandchild"]
    assert gc["point"] == pytest.approx(0.9505, abs=1e-4)


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


def test_scenario_blocked_loudly_on_pending_baselines():
    parts = load_all(PARAMS_DIR)
    out = compute_counts(
        parts["params"], parts["baselines"], ScenarioInput(displaced_workers=100)
    )
    blocked = {b["outcome"] for b in out["blocked"]}
    assert "excess_deaths" in blocked
    assert "child_lifetime_earnings_lost_usd" in blocked
    # service jobs need no baseline: computed
    assert out["modeled"]["local_service_jobs_lost"]["point"] == 500
    # every blocked reason names the fix
    assert all("baselines.csv" in b["reason"] for b in out["blocked"])


def test_scenario_strict_raises_on_missing_baseline():
    parts = load_all(PARAMS_DIR)
    with pytest.raises(BaselineMissing):
        compute_counts(
            parts["params"], parts["baselines"], ScenarioInput(displaced_workers=100), strict=True
        )


def test_scenario_counts_with_verified_baselines():
    parts = load_all(PARAMS_DIR)
    out = compute_counts(
        parts["params"], _fake_verified_baselines(), ScenarioInput(displaced_workers=100)
    )
    deaths = out["modeled"]["excess_deaths"]
    # sustained: 100 * 0.004 * 0.17 * 20y = 1.36 ; peak: 100 * 0.004 * 0.75 = 0.30
    assert deaths["point"] == pytest.approx(1.66, abs=1e-6)
    child = out["modeled"]["child_lifetime_earnings_lost_usd"]
    # 100 workers x 2 children x 9% x $1M
    assert child["point"] == pytest.approx(18_000_000.0, abs=1.0)


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
    assert abs(a["p50"] - 0.9505) < 0.05
    assert a["p05"] > 0.80  # gap-space keeps the line near 1.0


def test_mc_generic_entry_rebuilds_full_module_per_draw():
    params = load(PARAMS_DIR / "parameters.csv")

    from downstream.children import child_line

    def compute(ps):
        return child_line(ps)["grandchild"].point

    out = simulate(params, compute, draws=500, seed=3)
    assert out["parameter_set_version"].endswith("-sampled")
    assert out["p05"] <= out["p50"] <= out["p95"]
