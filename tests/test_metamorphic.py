"""Metamorphic checks for scenario arithmetic and mortality timing.

These assert relations that must hold even where a fixed expected result would
be difficult to obtain independently.
"""
from __future__ import annotations

import pytest

from downstream.mortality import excess_deaths
from downstream.params import load_all
from downstream.scenario import ScenarioInput, compute_counts


def _counts(workers: float) -> dict:
    parts = load_all()
    return compute_counts(parts["params"], parts["baselines"], ScenarioInput(workers), _raw=True)


def test_count_outcomes_scale_linearly_with_documented_exposure():
    single = _counts(100)
    scaled = _counts(700)
    for name, outcome in single["modeled"].items():
        for bound in ("point", "low", "high"):
            assert scaled["modeled"][name][bound] == pytest.approx(7 * outcome[bound])


def test_scenario_results_are_additive_over_disjoint_exposure_cohorts():
    left, right, combined = _counts(125), _counts(375), _counts(500)
    assert set(left["modeled"]) == set(right["modeled"]) == set(combined["modeled"])
    for name in combined["modeled"]:
        for bound in ("point", "low", "high"):
            expected = left["modeled"][name][bound] + right["modeled"][name][bound]
            assert combined["modeled"][name][bound] == pytest.approx(expected)


def test_evidence_aligned_mortality_defers_the_year_six_effect():
    # With harmful effects, treating the year-6+ estimate as immediate can
    # only increase excess deaths before year six.  The production timing is
    # deliberately the smaller, evidence-aligned quantity.
    source_aligned = excess_deaths(1_000, 0.01, 2.0, 1.5, 5, timing="source_aligned")
    immediate = excess_deaths(1_000, 0.01, 2.0, 1.5, 5, timing="immediate_sustained")
    assert 0 <= source_aligned < immediate
    assert excess_deaths(1_000, 0.01, 2.0, 1.5, 1, timing="source_aligned") == pytest.approx(
        excess_deaths(1_000, 0.01, 2.0, 1.5, 1, timing="immediate_sustained")
    )
