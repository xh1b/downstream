"""v1.43 pins: the six second-sweep studies extracted and landed.

What this file pins:
- three EXACT rows: halla2020 spousal participation elasticity (band =
  subgroup range, dist empty), huttunenkellokumpi2016 annual birth
  response (male null declared), schallerzerpa2019 child depression/
  anxiety (paternal channel, spec sensitivity declared)
- the three-country mortality convergence and the declared ES no-long-
  run divergence travel as notes on the SvW peak/sustained rows
- the rege2007 divorce row carries the HSW order-smaller register
  cross-check without changing the anchor
- mork2019 is the honesty anchor: cited from the child row, never a row
"""
from downstream.audit import audit, summary
from downstream.params import default_dir, load, load_nodes

PARAMS_DIR = default_dir()
PARAMS = load(PARAMS_DIR / "parameters.csv")
NODES = load_nodes(PARAMS_DIR / "nodes.csv")


def test_spouse_elasticity_row_pinned():
    row = PARAMS.by_link("displacement_event->spouse_participation_elasticity")
    assert (row.point, row.low, row.high) == (-0.04, -0.07, -0.03)
    assert row.tier == "EXACT" and row.evidence_role == "conditional"
    assert NODES["spouse_participation_elasticity"].unit == "log_elasticity"
    assert row.dist == ""  # band is the paper's subgroup range, not a CI
    assert "-0.4" in row.notes  # an order below the AWE-literature average
    assert "extensive margin" in row.notes


def test_birth_response_row_pinned_with_male_null():
    row = PARAMS.by_link("displacement_event->annual_birth_response")
    assert (row.point, row.low, row.high) == (-0.005, -0.0089, -0.0011)
    assert row.tier == "EXACT"
    assert "MALE NULL" in row.notes
    assert "-4 births per 100" in row.notes  # cumulative by year 11
    assert "career-concern channel, NOT income" in row.notes.replace(
        "career-concern channel, not income", "career-concern channel, NOT income")
    assert "kearney2018fracking" in row.notes  # never merged with the local shock


def test_child_depression_row_pinned():
    row = PARAMS.by_link("displacement_event->child_depression_anxiety")
    assert (row.point, row.low, row.high) == (0.008, 0.0002, 0.0158)
    assert row.tier == "EXACT"
    assert "PATERNAL" in row.population_scope
    assert "MATERNAL depression/anxiety NULL" in row.notes
    assert "mork2019" in row.notes  # honesty anchor cited from the row
    assert NODES["child_depression_anxiety"].unit == "probability"


def test_mortality_convergence_and_divergence_recorded():
    peak = PARAMS.by_link("earnings_shock->mortality_peak")
    assert "eliasonstorrie2009" in peak.notes and "1.44 [1.19, 1.76]" in peak.notes
    assert "+0.2229pp" in peak.notes and "+85.8%" in peak.notes
    sustained = PARAMS.by_link("earnings_shock->mortality_sustained")
    assert "+0.5968pp" in sustained.notes and "+33.5%" in sustained.notes
    assert "DECLARED DIVERGENCE" in sustained.notes and "0.98" in sustained.notes
    # the SvW anchors themselves are untouched
    assert peak.point == 2.6696 and sustained.point == 1.135


def test_divorce_crosscheck_keeps_anchor():
    div = PARAMS.by_link("displacement->divorce_hazard")
    assert div.point == 1.11  # the rege2007 anchor is untouched
    assert "HALLA-SCHMIEDER-WEBER 2020 CROSS-CHECK" in div.notes
    assert "PRECISE ZERO" in div.notes
    assert "never averaged" in div.notes
    bh = PARAMS.by_link("displacement->external_cause_mortality_hazard")
    assert "REPLICATIONS + HETEROGENEITY" in bh.notes
    circ = PARAMS.by_link("displacement->circulatory_mortality_hazard")
    assert "+52.8%" in circ.notes


def test_audit_clean_and_version_current():
    s = summary(audit(PARAMS_DIR))
    assert s["pass"], [f.as_dict() for f in audit(PARAMS_DIR) if f.severity.value == "error"]
    assert PARAMS.version == "v1.43"
