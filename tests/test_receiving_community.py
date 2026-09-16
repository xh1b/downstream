"""v1.48: the receiving-community crime stream, admitted through the
independence gate (Light-Miller 2018 Criminology; Bell-Fasani-Machin
2013 REStat; Bianchi-Buonanno-Pinotti 2012 JEEA). Both rows are
log-log elasticities of a local crime rate w.r.t. the local immigrant
population, composed on the work-access margin only."""

import pytest

from downstream.ledger import CHAIN_CAUSAL_ROLES, CHAIN_KINDS, DIRECT, GAP_LOG, chain
from downstream.params import load_all


def _parts():
    parts = load_all()
    return parts


def test_receiving_community_rows_are_admitted_chain_links():
    parts = _parts()
    assert CHAIN_KINDS["immigrant_influx->receiving_violent_crime_rate"] == GAP_LOG
    assert CHAIN_KINDS["immigrant_influx->receiving_total_crime_rate"] == GAP_LOG
    # Both are separately identified receiving-community estimates —
    # never relabeled as displacement effects or structural assumptions.
    for link in ("immigrant_influx->receiving_violent_crime_rate",
                 "immigrant_influx->receiving_total_crime_rate"):
        assert CHAIN_CAUSAL_ROLES[link] == "direct_receiving_community_estimate"
        row = parts["params"].by_link(link)
        assert row.evidence_role == "conditional"


def test_violent_crime_elasticity_composes_like_the_source():
    parts = _parts()
    led = chain(parts["params"], ["immigrant_influx->receiving_violent_crime_rate"],
                "influx", "gap_multiplier", [GAP_LOG], parts["nodes"], base=1.10)
    # Light-Miller elasticity -0.12: a +10% influx composes to
    # 1.10 ** -0.12 ~= 0.9885, i.e. violent crime falls about 1.2%.
    assert led.point == pytest.approx(1.10 ** -0.12, abs=1e-4)
    assert led.low <= led.point <= led.high
    # The band stays on the negative side (the preferred-spec SE
    # excludes zero) but the effect is an order of magnitude under the
    # displacement-side earnings effects.
    assert led.high < 1.0
    assert 1 - led.point < 0.02


def test_aggregate_crime_null_band_includes_no_change():
    parts = _parts()
    led = chain(parts["params"], ["immigrant_influx->receiving_total_crime_rate"],
                "influx", "gap_multiplier", [GAP_LOG], parts["nodes"], base=1.10)
    # BBP supply-push IV +0.105 with a band that INCLUDES zero: this row
    # is the aggregate null by design, not a positive.
    assert led.point == pytest.approx(1.10 ** 0.105, abs=1e-4)
    assert led.low < 1.0 < led.high


def test_negative_influx_is_refused_not_inverted():
    parts = _parts()
    # A fractional power of a negative multiplier is undefined: the
    # GAP_LOG guard must refuse rather than silently invert.
    with pytest.raises(ValueError, match="strictly positive"):
        chain(parts["params"], ["immigrant_influx->receiving_total_crime_rate"],
              "outflow", "gap_multiplier", [GAP_LOG], parts["nodes"], base=-1.0)


def test_receiving_community_links_never_start_from_displacement():
    parts = _parts()
    # The displacement graph and the receiving-community graph are
    # separate streams: no shipped chain may walk displacement into an
    # immigrant_influx node. A link outside CHAIN_KINDS is refused (and
    # a link that is not a shipped row at all fails the registry lookup).
    from downstream.ledger import validate_chain
    with pytest.raises(KeyError):
        validate_chain(parts["params"], ["displacement->immigrant_influx"],
                       [DIRECT], parts["nodes"])
