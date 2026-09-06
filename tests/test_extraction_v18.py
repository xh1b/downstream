"""Traps for the v1.8 extraction round (ADH validation + Aizer IPV producer).

Each trap names the defect it hunts:
- a transcribed coefficient that cites a key the bibliography lacks
- a bib entry upgraded to fulltext without the full text actually read
- the aizer row losing its sign (an elasticity is signed, not a ratio)
- the log_elasticity unit silently sampling in log space (negative
  band would explode)
- validation targets drifting from the published table values
"""

from __future__ import annotations

import pytest

from downstream.distributions import dist_for
from downstream.params import load_all
from downstream.validate import v1_targets

PARTS = load_all()
PARAMS = PARTS["params"]
BIB = PARTS["bib"]
NODES = PARTS["nodes"]


def test_validation_targets_resolve_to_bib():
    for row in v1_targets()["targets"]:
        for key in row["citation"].split(";"):
            assert key.strip() in BIB, f"validation row cites unknown key {key!r}"


def test_autor2019_evidence_supports_fulltext_claims():
    assert BIB["autor2019"].evidence == "fulltext"
    assert "Insights" in BIB["autor2019"].fields["journal"]  # the P&P miscitation is fixed


def test_key_adh_transcription_values():
    rows = {r["outcome"]: r for r in v1_targets()["targets"]}
    assert float(rows["marriage_rate_pp"]["coefficient_per_pp_shock"]) == -0.72
    assert float(rows["fertility_rate_per_k"]["coefficient_per_pp_shock"]) == -3.30
    assert float(rows["child_poverty_pp"]["coefficient_per_pp_shock"]) == 2.2
    # every row with an SE must carry one (except the deliberately
    # not-transcribed component row)
    for r in rows.values():
        if r["outcome"] != "two_parent_household_pp":
            assert r["se"].strip(), f"missing SE on {r['outcome']}"


def test_aizer_row_pinned_with_sign_and_ci():
    p = PARAMS.by_link("wage_ratio->household_ipv")
    assert p.point == -0.813
    assert (p.low, p.high) == (-1.45, -0.18)
    assert p.tier == "EXACT-results"
    assert BIB["aizer2010"].evidence in {"fulltext", "results", "fulltext-table"}


def test_log_elasticity_samples_linear_not_log():
    node = NODES["household_ipv_elasticity"]
    p = PARAMS.by_link("wage_ratio->household_ipv")
    assert dist_for(p, node.unit) == "uniform", (
        "a signed elasticity must NOT sample in log space — the negative "
        "band would make the sampler explode"
    )


def test_wage_ratio_node_exists_and_is_gap():
    assert NODES["wage_ratio"].unit == "gap_multiplier"
