"""Adversarial traps for the knob-experiment harness and Sobol CIs.

Each trap names the defect it hunts:
- a typo'd knob silently becoming a no-op
- an out-of-band value entering through the experiment door
- a knobbed run masquerading as a published parameter set
- a sweep row lying about direction (monotonicity of the mortality knob)
- a zero-influence link claiming width reduction
- estimator noise being sold as a confidence interval
"""

from __future__ import annotations

import pytest

from downstream.children import child_line
from downstream.knobs import pin, sweep, value_of_information, with_band
from downstream.params import load_all
from downstream.scenario import ScenarioInput
from downstream.sensitivity import sobol_ci

PARTS = load_all()
PARAMS = PARTS["params"]
BASELINES = PARTS["baselines"]
NODES = PARTS["nodes"]


# --- trap: typo'd knob becomes a silent no-op ------------------------------

def test_with_band_unknown_link_fails_loudly():
    with pytest.raises(KeyError, match="no_such_link"):
        with_band(PARAMS, "no_such_link", 1.0, 2.0)


def test_pin_unknown_link_fails_loudly():
    with pytest.raises(KeyError):
        pin(PARAMS, "earnings_shock->mortality", 1.17)


# --- trap: experiment door widens the evidence band ------------------------

def test_pin_outside_band_is_refused():
    # S&vW sustained band is [1.15, 1.20]; 1.40 is not licensed
    with pytest.raises(ValueError, match=r"outside its cited band"):
        pin(PARAMS, "earnings_shock->mortality_sustained", 1.40)


def test_pin_at_band_edges_is_allowed():
    for edge in (1.15, 1.20):
        ps = pin(PARAMS, "earnings_shock->mortality_sustained", edge)
        p = ps.by_link("earnings_shock->mortality_sustained")
        assert (p.low, p.point, p.high) == (edge, edge, edge)


# --- trap: knobbed run published as a pinned parameter set ------------------

def test_knob_version_marker_never_claims_published():
    ps = with_band(PARAMS, "earnings_shock->mortality_sustained", 1.16, 1.19)
    assert ps.version.endswith("-knob")
    # the marker never accumulates across repeated overrides
    ps2 = with_band(ps, "displacement->child_earnings", 0.88, 0.94)
    assert ps2.version.count("-knob") == 1


def test_original_set_untouched_by_override():
    lo = PARAMS.by_link("earnings_shock->mortality_sustained").low
    with_band(PARAMS, "earnings_shock->mortality_sustained", 1.16, 1.19)
    assert PARAMS.by_link("earnings_shock->mortality_sustained").low == lo


# --- trap: sweep row lies about direction ------------------------------------

def test_sweep_mortality_knob_monotonic_in_excess_deaths():
    link = "earnings_shock->mortality_sustained"
    out = sweep(
        PARAMS,
        BASELINES,
        ScenarioInput(displaced_workers=1000, label="t"),
        link,
        [1.15, 1.17, 1.20],
    )
    deaths = [r["modeled"]["excess_deaths"] for r in out["rows"]]
    assert deaths == sorted(deaths), f"excess deaths must rise with the knob, got {deaths}"
    # and nothing else moved except the knob's own multiplier
    for r in out["rows"]:
        assert r["modeled"]["child_lifetime_earnings_lost_usd"] == pytest.approx(
            out["rows"][0]["modeled"]["child_lifetime_earnings_lost_usd"]
        )


def test_sweep_values_outside_band_abort_whole_table():
    with pytest.raises(ValueError, match="outside its cited band"):
        sweep(
            PARAMS,
            BASELINES,
            ScenarioInput(displaced_workers=100),
            "earnings_shock->mortality_sustained",
            [1.15, 1.30],
        )


def test_sweep_empty_values_fail():
    with pytest.raises(ValueError):
        sweep(PARAMS, BASELINES, ScenarioInput(displaced_workers=1), "x", [])


def test_sweep_blocked_outcomes_still_surface():
    # a scenario blocked list is flattened into every row — hiding it
    # would let a sweep imply completeness it does not have
    out = sweep(
        PARAMS,
        BASELINES,
        ScenarioInput(displaced_workers=10, label="t"),
        "earnings_shock->mortality_sustained",
        [1.17],
    )
    assert "blocked_count" in out["rows"][0]["modeled"]


# --- trap: zero-influence link claims width reduction ------------------------

def test_voi_zero_influence_link_buys_nothing():
    voi = value_of_information(
        PARAMS,
        lambda ps: child_line(ps)["grandchild"].point,
        NODES,
        draws=400,
        seed=7,
    )
    by_link = {r["link"]: r for r in voi["rows"]}
    # the youth-crime elasticity cannot reach the grandchild line
    yc = by_link["youth_wages->youth_crime"]
    assert yc["width_reduction"] < 0.05, f"unlinked knob bought {yc['width_reduction']}"
    # while the direct child link must be the top purchase
    top = voi["rows"][0]
    assert top["link"] == "displacement->child_earnings"
    assert top["width_reduction"] > 0.2


def test_voi_deterministic_under_same_seed():
    fn = lambda ps: child_line(ps)["grandchild"].point  # noqa: E731
    a = value_of_information(PARAMS, fn, NODES, draws=200, seed=3)
    b = value_of_information(PARAMS, fn, NODES, draws=200, seed=3)
    assert a["rows"] == b["rows"]


@pytest.mark.parametrize("bad", [0.0, -0.5, 1.5])
def test_voi_shrink_validated(bad):
    with pytest.raises(ValueError, match="shrink"):
        value_of_information(
            PARAMS,
            lambda ps: child_line(ps)["grandchild"].point,
            NODES,
            draws=50,
            shrink=bad,
        )


def test_voi_zero_width_band_reported_not_crashed():
    ps = pin(PARAMS, "earnings_shock->mortality_sustained", 1.17)
    voi = value_of_information(
        ps,
        lambda p: child_line(p)["grandchild"].point,
        NODES,
        draws=100,
        seed=5,
    )
    row = [r for r in voi["rows"] if r["link"] == "earnings_shock->mortality_sustained"][0]
    assert row["note"] == "already pinned (zero-width band)"
    assert row["width_reduction"] == 0.0


# --- trap: estimator noise sold as a confidence interval ---------------------

def test_sobol_ci_rejects_single_replicate():
    with pytest.raises(ValueError, match="replicates"):
        sobol_ci(PARAMS, lambda ps: 1.0, NODES, replicates=1)


def test_sobol_ci_output_is_labeled_as_design_noise():
    out = sobol_ci(
        PARAMS,
        lambda ps: child_line(ps)["grandchild"].point,
        NODES,
        base=32,
        replicates=2,
    )
    assert "not a confidence interval" in out["note"]
    assert len(out["indices"]) == len(PARAMS.parameters)
    assert out["model_evals"] == out["base"] * (len(PARAMS.parameters) + 2) * 2


def test_sobol_ci_top_link_separates_from_its_noise():
    out = sobol_ci(
        PARAMS,
        lambda ps: child_line(ps)["grandchild"].point,
        NODES,
        base=128,
        replicates=5,
    )
    top = out["indices"][0]
    assert top["link"] == "displacement->child_earnings"
    assert top["S_total_mean"] - 2 * top["S_total_sd"] > 0.5, (
        "the dominant driver must separate from design noise; "
        f"got mean {top['S_total_mean']} sd {top['S_total_sd']}"
    )
