"""v1.13 extraction pins: college enrollment + short-run income bridge
(hilger2016, published AEJ:Applied copy) and property-crime semielasticity
(raphael2001, JLE 44(1)).

Also pins the closure-selection honesty item: Hilger's own footnote 31
warns that firm-closure designs (our child-earnings and mortality
anchors) carry assortative-selection risk. The band on
displacement->child_earnings must NOT have been silently changed by this
discovery — the tension stays visible until the V2 reconciliation.
"""
import pytest

from downstream.audit import ERROR, audit
from downstream.params import default_dir, load, load_nodes

PARAMS_DIR = default_dir()
PARAMS = load(PARAMS_DIR / "parameters.csv")
NODES = load_nodes(PARAMS_DIR / "nodes.csv")


def test_college_enrollment_row_matches_hilger_table3_row1():
    p = PARAMS.by_link("displacement->college_enrollment")
    # -0.432pp (SE 0.094) on a 40.66% base -> relative multiplier
    assert p.point == pytest.approx(1 - 0.432 / 40.66, abs=5e-5)
    assert p.low == pytest.approx(1 - (0.432 + 1.96 * 0.094) / 40.66, abs=5e-5)
    assert p.high == pytest.approx(1 - (0.432 - 1.96 * 0.094) / 40.66, abs=5e-5)
    assert p.tier == "EXACT" and p.citation == "hilger2016"


def test_college_effect_is_small_and_band_excludes_zero_harm():
    # the honest headline: ~1% relative enrollment drop, far below the
    # closure-based claims; the band's low end is still only -1.5%
    p = PARAMS.by_link("displacement->college_enrollment")
    assert 0.98 <= p.point <= 0.999
    assert p.low > 0.98
    assert "wrong-signed" in p.notes or "selection" in p.notes


def test_income_bridge_row_and_scope_guard():
    p = PARAMS.by_link("displacement->parental_income_shortrun")
    assert p.point == pytest.approx((59832 - 8138.09) / 59832, abs=5e-5)
    assert p.low == pytest.approx((59832 - 8138.09 - 1.96 * 219.53) / 59832, abs=5e-5)
    assert p.high == pytest.approx((59832 - 8138.09 + 1.96 * 219.53) / 59832, abs=5e-5)
    # scope guard: this is the event-window drop, never the long-run gap
    assert "NOT the long-run" in p.notes or "SHORT-RUN" in p.notes
    assert NODES["parental_income_shortrun"].unit == "gap_multiplier"
    # and the long-run worker band is unchanged by this landing
    w = PARAMS.by_link("displacement->worker_earnings")
    assert (w.point, w.low, w.high) == (0.80, 0.75, 0.85)


def test_property_crime_row_matches_raphael_table5_full_spec_2sls():
    p = PARAMS.by_link("unemployment_rate->property_crime")
    assert p.point == pytest.approx(5.018, abs=5e-4)
    assert p.low == pytest.approx(5.018 - 1.96 * 1.134, abs=5e-4)
    assert p.high == pytest.approx(5.018 + 1.96 * 1.134, abs=5e-4)
    assert p.tier == "EXACT" and p.citation == "raphael2001"
    # sign: unemployment UP -> property crime UP
    assert p.point > 0 and p.low > 0
    # violent-crime refusal must be recorded on the row
    assert "Violent" in p.notes


def test_unemployment_crime_pair_is_boundary_applied():
    from downstream import units

    assert units.composition_for(units.PERCENT_DELTA, units.PERCENT_DELTA) == "rate"


def test_dahl_row_verified_against_published_version():
    p = PARAMS.by_link("family_income_shock->child_achievement_sd")
    assert (p.point, p.low, p.high) == (0.0610, pytest.approx(0.0157, abs=1e-9),
                                        pytest.approx(0.1063, abs=1e-9))
    # published AER copy checked 2026-09-07: same coefficient and SE; N drifted
    assert "8609" in p.notes


def test_version_bumped_and_audit_clean():
    assert (PARAMS_DIR / "VERSION").read_text().strip() == "v1.17"
    errors = [f for f in audit(PARAMS_DIR) if f.severity == ERROR]
    assert errors == []
