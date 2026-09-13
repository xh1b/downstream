"""v1.14b pins: fertility elasticity (kearney2018fracking) and the
bib-duplicate resolution.

Trap history: the queue cited "Kearney & Wilson 2020 REStat" and the
bib held BOTH a real Pill-study entry (kearney2020) and a broken stub
(kearney2020fracking) conflating the fracking title with a Pill
subtitle. These pins lock the resolution: two real papers, no stub,
the landed row cites the fracking paper only.
"""
import pytest

from downstream.audit import ERROR, audit
from downstream.citations import parse_bib
from downstream.params import default_dir, load

PARAMS_DIR = default_dir()
PARAMS = load(PARAMS_DIR / "parameters.csv")
BIB = parse_bib(PARAMS_DIR / "references.bib")


def test_fertility_row_matches_kearney_table8_panelB_col2():
    p = PARAMS.by_link("male_earnings->marital_fertility")
    assert p.point == pytest.approx(1.24, abs=1e-6)
    assert p.low == pytest.approx(1.24 - 1.96 * 0.43, abs=5e-4)
    assert p.high == pytest.approx(1.24 + 1.96 * 0.43, abs=5e-4)
    assert p.tier == "EXACT" and p.citation == "kearney2018fracking"


def test_weak_instrument_and_marriage_null_declared():
    p = PARAMS.by_link("male_earnings->marital_fertility")
    assert "F=11.8" in p.notes
    assert "NOT marriage" in p.notes
    assert "0.75" in p.notes  # coal-boom cross-context anchor


def test_fertility_row_is_positive_elasticity():
    # positive income shock raises births; a displacement loss applies
    # it negatively. Sign trap.
    p = PARAMS.by_link("male_earnings->marital_fertility")
    assert p.point > 0 and p.low > 0


def test_bib_duplicate_resolved_both_real_papers_kept():
    # the broken stub is gone
    assert "kearney2020fracking" not in BIB
    # the two real papers both exist
    assert "kearney2020" in BIB          # Pill study, REStat 102(2)
    assert "kearney2018fracking" in BIB  # fracking study, REStat 100(4)
    assert BIB["kearney2018fracking"].fields.get("doi") == "10.1162/rest_a_00739"


def test_version_bumped_and_audit_clean():
    assert (PARAMS_DIR / "VERSION").read_text().strip() == "v1.38"
    errors = [f for f in audit(PARAMS_DIR) if f.severity == ERROR]
    assert errors == []
