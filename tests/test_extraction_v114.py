"""v1.14 extraction pins: long-run EITC earnings row (bastian2018,
published JOLE copy) and the Behrman & Taubman IGE cross-check notes.

The Bastian row is a reduced-form policy response (per $1k exposure),
not the IV-scaled income response — the IV number is 10%-significant and
its 95% CI crosses zero; landing it as a composed row would imply
precision the study does not claim. The timing result (exposure 0-12
null, 13-18 operative) is pinned on the row: it bounds which childhood
window the model's income stream may harm.
"""
import pytest

from downstream import units
from downstream.audit import ERROR, audit
from downstream.params import default_dir, load

PARAMS_DIR = default_dir()
PARAMS = load(PARAMS_DIR / "parameters.csv")


def test_eitc_row_matches_bastian_table2_col6():
    p = PARAMS.by_link("eitc_exposure->adult_earnings_early")
    assert p.point == pytest.approx(564.0, abs=1e-6)
    assert p.low == pytest.approx(564.0 - 1.96 * 244.9, abs=5e-4)
    assert p.high == pytest.approx(564.0 + 1.96 * 244.9, abs=5e-4)
    assert p.tier == "EXACT" and p.citation == "bastian2018"


def test_iv_scaled_number_recorded_not_landed():
    # honesty pin: the noisier IV-scaled response stays in the notes
    p = PARAMS.by_link("eitc_exposure->adult_earnings_early")
    assert "57.2" in p.notes
    assert "NOT landed" in p.notes


def test_timing_window_pinned_on_row():
    p = PARAMS.by_link("eitc_exposure->adult_earnings_early")
    assert "0-12" in p.notes and "13-18" in p.notes


def test_ige_rows_carry_behrman_cross_check():
    for link in ("child_earnings->grandchild_earnings",
                 "grandchild_earnings->greatgrandchild_earnings"):
        p = PARAMS.by_link(link)
        assert "BEHRMAN-TAUBMAN" in p.notes
        assert "0.20" in p.notes  # the one-year attenuation number
    # the IGE band values themselves must be untouched by the note append
    g = PARAMS.by_link("child_earnings->grandchild_earnings")
    assert (g.point, g.low, g.high) == (0.55, 0.40, 0.60)


def test_usd_usd_pair_is_boundary_applied():
    assert units.composition_for(units.USD, units.USD) == "rate"


def test_version_bumped_and_audit_clean():
    assert (PARAMS_DIR / "VERSION").read_text().strip() == "v1.15"
    errors = [f for f in audit(PARAMS_DIR) if f.severity == ERROR]
    assert errors == []
