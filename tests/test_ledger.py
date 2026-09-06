"""Compute checks for the v0 chain."""

from pathlib import Path

from downstream.ledger import standard_family_daughter
from downstream.params import load

PARAMS = Path(__file__).resolve().parent.parent / "params" / "parameters.csv"


def test_loads_and_dag_is_acyclic():
    params = load(PARAMS)
    assert params.parameters
    assert any(p.tier == "EXACT" for p in params.parameters)


def test_standard_family_daughter_monotone_and_cited():
    params = load(PARAMS)
    out = standard_family_daughter(params, wage_multiplier=0.80)
    mult = out["daughter_line_earnings_multiplier"]
    # The chain only ever multiplies; the band must bracket the point.
    assert mult["low"] <= mult["point"] <= mult["high"]
    # Three links: father earnings, child inheritance, grandchild inheritance.
    assert len(out["steps"]) == 3
    # Every step carries its citation.
    assert all(step["citation"] for step in out["steps"])


def test_worse_wage_shock_never_improves_the_daughter():
    params = load(PARAMS)
    mild = standard_family_daughter(params, wage_multiplier=0.90)
    harsh = standard_family_daughter(params, wage_multiplier=0.70)
    assert (
        harsh["daughter_line_earnings_multiplier"]["point"]
        < mild["daughter_line_earnings_multiplier"]["point"]
    )
