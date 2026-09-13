"""v1.12 extraction pins: spillover (adh2013), achievement (dahl2012),
income-longevity slope (chetty2016).

Each row was read from the study's own tables (sources named in the
notes field). These traps pin the EXACT numbers so a re-extraction
cannot silently drift them, and pin the boundary-application rule:
per-$1k coefficients apply at a baseline boundary, never in a chain.
"""

import pytest

from downstream import units
from downstream.audit import ERROR, audit
from downstream.ledger import RATE, start
from downstream.params import default_dir, load, load_nodes

PARAMS_DIR = default_dir()
PARAMS = load(PARAMS_DIR / "parameters.csv")
NODES = load_nodes(PARAMS_DIR / "nodes.csv")


def test_spillover_row_matches_adh_table7pb_col6():
    p = PARAMS.by_link("import_shock->non_displaced_wage_spillover")
    assert (p.point, p.low, p.high) == (-0.822, pytest.approx(-1.3042, abs=1e-9),
                                        pytest.approx(-0.3398, abs=1e-9))
    assert p.tier == "EXACT"
    assert p.citation == "adh2013"
    # the band must be the quoted SE's 95% CI: -0.822 +/- 1.96*0.246
    assert p.point - 1.96 * 0.246 == pytest.approx(p.low, abs=5e-4)
    assert p.point + 1.96 * 0.246 == pytest.approx(p.high, abs=5e-4)


def test_spillover_is_negative_and_names_non_displaced_population():
    p = PARAMS.by_link("import_shock->non_displaced_wage_spillover")
    # a wage LOSS per positive exposure shock: sign trap
    assert p.point < 0 and p.high < 0
    assert "OUTSIDE manufacturing" in p.population_scope  # non-displaced workers


def test_achievement_row_matches_dahl_table3_col_i():
    p = PARAMS.by_link("family_income_shock->child_achievement_sd")
    assert (p.point, p.low, p.high) == (0.0610, pytest.approx(0.0157, abs=1e-9),
                                        pytest.approx(0.1063, abs=1e-9))
    assert p.tier == "EXACT"
    assert p.point - 1.96 * 0.0231 == pytest.approx(p.low, abs=5e-4)
    assert p.point + 1.96 * 0.0231 == pytest.approx(p.high, abs=5e-4)


def test_longevity_row_band_is_the_papers_own_range_divided():
    p = PARAMS.by_link("family_income_shock->life_expectancy_years")
    assert p.point == pytest.approx(0.8 / 6, abs=5e-4)
    assert p.low == pytest.approx(0.7 / 6, abs=5e-4)
    assert p.high == pytest.approx(0.9 / 6, abs=5e-4)
    # associational study: the honesty caveat must be carried on the row
    assert "causal" in p.notes


def test_boundary_coefficient_pairs_declared_as_rate_not_chain():
    # USD -> percent_delta / sd_delta / life_years are boundary-applied
    # coefficients. They must map to "rate" (record + boundary apply),
    # never to a multiplicative chain kind.
    assert units.composition_for(units.USD, units.PERCENT_DELTA) == "rate"
    assert units.composition_for(units.USD, units.SD_DELTA) == "rate"
    assert units.composition_for(units.USD, units.LIFE_YEARS) == "rate"


def test_boundary_coefficient_is_recorded_never_chained():
    # trap: composing a linear per-$1k coefficient as a multiplier would
    # silently scale the response by chain position; the ledger must
    # record it (RATE semantics) and not compound it.
    base = start("wage", "percent_delta", value=1.0)
    p = PARAMS.by_link("import_shock->non_displaced_wage_spillover")
    led = base.apply(RATE, p)
    assert led.point == p.point
    # applying it twice records the same boundary value, it does NOT
    # compound into (1-0.00822)^2
    led2 = led.apply(RATE, p)
    assert led2.point == p.point


def test_new_nodes_exist_with_declared_units():
    assert NODES["import_shock_per_worker"].unit == "usd"
    assert NODES["local_wage_response"].unit == "percent_delta"
    assert NODES["family_income_shock"].unit == "usd"
    assert NODES["child_achievement_sd"].unit == "sd_delta"
    assert NODES["life_expectancy_years"].unit == "life_years"


def test_version_bumped_and_audit_clean():
    version = (PARAMS_DIR / "VERSION").read_text().strip()
    assert version == "v1.42"
    out = audit(PARAMS_DIR)
    errors = [f for f in out if f.severity == ERROR]
    assert errors == []
