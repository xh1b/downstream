"""v1.18 pins: Thornton 1980 landed as CROSS-CHECK NOTES on the
fertility row — and deliberately NOT as a parameter row.

The trap this file hunts: an observational OLS correlation result
slipping into parameters.csv as a point. CITING §1 allows only
quasi-experimental designs to set points; Thornton's PSID two-
generation OLS is correlation-grade. The row values must be
untouched by the note append, the near-null actual-fertility
transmission and the strong preference transmission must both be
on the row, and the no-parameter-row rationale must be recorded.
"""
import pytest

from downstream.audit import ERROR, audit
from downstream.params import default_dir, load

PARAMS_DIR = default_dir()
PARAMS = load(PARAMS_DIR / "parameters.csv")


def test_fertility_row_values_untouched_by_note_append():
    p = PARAMS.by_link("male_earnings->marital_fertility")
    assert (p.point, p.low, p.high) == pytest.approx((1.24, 0.397, 2.083), abs=1e-6)
    assert p.tier == "EXACT" and p.citation == "kearney2018fracking"


def test_thornton_cross_check_notes_pinned():
    p = PARAMS.by_link("male_earnings->marital_fertility")
    assert "THORNTON 1980 CROSS-CHECK" in p.notes
    # the near-null ACTUAL transmission numbers (Table 3)
    assert ".070" in p.notes and ".058" in p.notes
    # the strong IDEAL (preference) transmission
    assert ".282" in p.notes and ".237" in p.notes


def test_no_parameter_row_licensable_rationale_recorded():
    p = PARAMS.by_link("male_earnings->marital_fertility")
    assert "OBSERVATIONAL" in p.notes
    assert "no parameter row licensable" in p.notes
    assert "NO cross-generation fertility multiplier" in p.notes


def test_no_thornton_parameter_row_exists():
    # the correlation result must never appear as its own parameter row
    thorton_rows = [r for r in PARAMS.parameters if "thornton" in r.citation.lower()]
    assert thorton_rows == []


def test_version_bumped_and_audit_clean():
    assert (PARAMS_DIR / "VERSION").read_text().strip() == "v1.22"
    errors = [f for f in audit(PARAMS_DIR) if f.severity == ERROR]
    assert errors == []
