"""v1.15 pins: GOP win-probability row (autor2020polarization) and the
Carneiro timing-corroboration notes.

Honesty pins: the AER paper's vote-share columns are null and the row
must say so; the win-probability CI is wide (t=2.0) and must be stored
at its full width. The Carneiro structural-model result is corroboration
on existing rows, never a composed parameter.
"""
import pytest

from downstream.audit import ERROR, audit
from downstream.params import default_dir, load

PARAMS_DIR = default_dir()
PARAMS = load(PARAMS_DIR / "parameters.csv")


def test_gop_win_probability_row_matches_autor_table4_col6():
    p = PARAMS.by_link("import_shock->gop_win_probability")
    assert p.point == pytest.approx(24.08, abs=1e-6)
    assert p.low == pytest.approx(24.08 - 1.96 * 12.07, abs=5e-3)
    assert p.high == pytest.approx(24.08 + 1.96 * 12.07, abs=5e-3)
    assert p.tier == "EXACT" and p.citation == "autor2020polarization"
    assert p.point > 0


def test_vote_share_nulls_declared_on_row():
    p = PARAMS.by_link("import_shock->gop_win_probability")
    assert "-1.08" in p.notes      # all-districts vote share, SE 5.98
    assert "re-sorting" in p.notes # the honest interpretation
    assert "2010" in p.notes       # timing: null before 2010


def test_carneiro_corroboration_sits_on_existing_rows_not_new_parameter():
    assert all(p.link != "carneiro2021" for p in PARAMS.parameters)
    for link in ("family_income_shock->child_achievement_sd",
                 "eitc_exposure->adult_earnings_early"):
        notes = PARAMS.by_link(link).notes
        assert "CARNEIRO" in notes
        assert "NOT a composed row" in notes
    # timing windows quoted
    assert "12-17" in PARAMS.by_link("eitc_exposure->adult_earnings_early").notes


def test_version_bumped_and_audit_clean():
    assert (PARAMS_DIR / "VERSION").read_text().strip() == "v1.44"
    errors = [f for f in audit(PARAMS_DIR) if f.severity == ERROR]
    assert errors == []
