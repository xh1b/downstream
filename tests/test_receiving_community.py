# @ref:test-receiving-community
# Method: @link:doc-receiving-community-0-4.
# Implementation: @link:code-receiving-community; @link:code-units.
# @tag:receiving @tag:testing
"""Receiving coefficients require distinct source-share inputs after v1.52 repair."""
import pytest

from downstream.ledger import CHAIN_CAUSAL_ROLES, CHAIN_KINDS, GAP_LOG, chain, validate_chain
from downstream.params import load_all
from downstream.units import LOG_DELTA, PERCENTAGE_POINT_DELTA

VIOLENT = "undocumented_share_change_pp->receiving_violent_crime_log_rate"
TOTAL = "regular_immigrant_share_ratio->receiving_total_crime_rate"


def test_receiving_sources_are_typed_and_preserve_coefficients():
    parts = load_all()
    assert parts["nodes"]["undocumented_share_change_pp"].unit == PERCENTAGE_POINT_DELTA
    assert parts["nodes"]["receiving_violent_crime_log_rate"].unit == LOG_DELTA
    assert VIOLENT not in CHAIN_KINDS  # no misleading generic multiplier composition
    assert CHAIN_KINDS[TOTAL] == GAP_LOG
    assert parts["params"].by_link(VIOLENT).point == -.12
    assert parts["params"].by_link(TOTAL).point == .105
    for link in (VIOLENT, TOTAL):
        assert CHAIN_CAUSAL_ROLES[link] == "direct_receiving_community_estimate"
        assert parts["params"].by_link(link).evidence_role == "conditional"
    assert parts["params"].by_link(TOTAL).tier == "canonical"


def test_total_crime_elasticity_uses_share_ratio_and_retains_null_support():
    parts = load_all()
    led = chain(parts["params"], [TOTAL], "regular immigrant share", "gap_multiplier",
                [GAP_LOG], parts["nodes"], base=1.10)
    assert led.point == pytest.approx(1.10**.105)
    assert led.low < 1 < led.high


def test_semi_log_source_requires_named_adapter():
    parts = load_all()
    with pytest.raises(ValueError, match="boundary-applied"):
        validate_chain(parts["params"], [VIOLENT], [GAP_LOG], parts["nodes"])


@pytest.mark.parametrize("link", ["immigrant_influx->receiving_violent_crime_rate",
                                  "immigrant_influx->receiving_total_crime_rate"])
def test_retired_stock_links_fail_with_migration_message(link):
    parts = load_all()
    with pytest.raises(ValueError, match="retired.*source-specific population shares"):
        validate_chain(parts["params"], [link], [GAP_LOG], parts["nodes"])
    with pytest.raises(KeyError):
        parts["params"].by_link(link)


def test_displacement_cannot_be_chained_into_receiving_population():
    parts = load_all()
    with pytest.raises(KeyError):
        validate_chain(parts["params"], ["displacement->regular_immigrant_share_ratio"],
                       [GAP_LOG], parts["nodes"])
