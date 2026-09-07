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
    assert out["parameter_set_version"] == "v1.12"
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


def test_scenario_both_conversions_computed_from_real_baselines():
    # v1.3 verified mortality; v1.4 verified lifetime earnings — both
    # count conversions now run on the REAL pinned values, nothing blocked.
    parts = load_all(PARAMS_DIR)
    out = compute_counts(
        parts["params"], parts["baselines"], ScenarioInput(displaced_workers=100)
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
        parts["params"], parts["baselines"], ScenarioInput(displaced_workers=100), strict=True
    )
    assert out["blocked"] == []
    baselines = dict(parts["baselines"])
    baselines.pop("median_male_lifetime_earnings")
    with pytest.raises(BaselineMissing):
        compute_counts(
            parts["params"], baselines, ScenarioInput(displaced_workers=100), strict=True
        )
    out = compute_counts(
        parts["params"], baselines, ScenarioInput(displaced_workers=100)
    )
    assert "child_lifetime_earnings_lost_usd" in {b["outcome"] for b in out["blocked"]}


def test_scenario_counts_with_verified_baselines():
    parts = load_all(PARAMS_DIR)
    out = compute_counts(
        parts["params"], _fake_verified_baselines(), ScenarioInput(displaced_workers=100)
    )
    deaths = out["modeled"]["excess_deaths"]
    # v1.10 table-pinned S&vW: sustained 1.135, peak 2.672
    # 100 * 0.004 * (0.135*20 + 1.672) = 1.7488
    assert deaths["point"] == pytest.approx(1.7488, abs=0.005)  # output rounded to 2dp
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
