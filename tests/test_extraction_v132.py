"""v1.32 pins: #25 Akee casino quasi-experiment + #9 Duncan refusal.

What this file hunts:
- the three landed akee2010 rows drifting: EXACT tier, reported-SE
  bands (1.96 SE), the per-treatment dose semantics (NOT per-dollar),
  and the dist shape (normal)
- the scope trap: the poverty split must be on the row (the
  full-sample null and the never-poor nulls), so no surface can quote
  the pooled number as if income helps everyone
- the age-window trap: the crime effect is MINORS-ONLY — the 18+
  nulls are declared on the row and must never be generalized
- the offense-type trap: minor-crime only; moderate/violent nulls
  recorded, never silently dropped
- the refusal row: duncan2010 must be REFUSED (observational, CITING
  SS1) with the zg2012 cross-check magnitudes recorded somewhere
  verifiable — not landed as a parameter
- the audit/units wiring: entry node registered, compositions
  (USD, EDU_YEARS) and (USD, PROB) are boundary 'rate' rules
"""
import pytest

from downstream.params import default_dir, load, load_all
from downstream.units import EDU_YEARS, PROB, USD, composition_for

PARAMS_DIR = default_dir()
PARAMS = load(PARAMS_DIR / "parameters.csv")


def test_version_is_v132():
    assert (PARAMS_DIR / "VERSION").read_text().strip() == "v1.32"


EDUCATION = "unconditional_income->child_education_years"
ANY_CRIME = "unconditional_income->youth_any_crime"
MINOR_CRIME = "unconditional_income->youth_minor_crime_ever"


def _row(link: str):
    return PARAMS.by_link(link)


# --- the education row ------------------------------------------------

def test_education_row_exact_values():
    p = _row(EDUCATION)
    assert p.tier == "EXACT"
    assert p.point == 1.127
    assert p.low == 0.247 and p.high == 2.007  # 1.96 x SE 0.449
    assert p.dist == "normal"


def test_education_row_carries_the_poverty_split():
    p = _row(EDUCATION)
    assert "0.379" in p.notes          # full-sample null recorded
    assert "never previously in poverty" in p.notes or "NEVER previously in poverty" in p.notes
    # never averaged: the row pins the previously-poor subsample
    assert "previously in poverty" in p.population_scope


def test_education_row_mother_receipt_and_mechanism():
    p = _row(EDUCATION)
    assert "1.48" in p.notes           # mother-receipt coefficient
    assert "labor force participation NULL" in p.notes  # income, not employment


def test_education_row_duncan_cross_check_refused_not_composed():
    p = _row(EDUCATION)
    # the observational magnitudes live on the row as a CROSS-CHECK,
    # explicitly barred from a point
    assert "0.63" in p.notes and "SE 0.21" in p.notes
    assert "CITING" in p.notes and "barred" in p.notes


# --- the crime rows ----------------------------------------------------

def test_any_crime_row_exact_values():
    p = _row(ANY_CRIME)
    assert p.point == -0.224
    assert p.low == -0.377 and p.high == -0.071  # 1.96 x SE 0.078
    assert p.tier == "EXACT" and p.dist == "normal"


def test_minor_crime_row_exact_values():
    p = _row(MINOR_CRIME)
    assert p.point == -0.179
    assert p.low == -0.353 and p.high == -0.005  # 1.96 x SE 0.089


def test_crime_rows_minor_only_and_age_windowed():
    # the 18+ nulls are declared on the any-crime row — no surface
    # generalizes the minors-only effect past 18
    p = _row(ANY_CRIME)
    assert "18" in p.notes and "NULL" in p.notes
    # moderate/violent nulls recorded on the any-crime row
    assert "0.002" in p.notes
    # the ever-minor row declares its offense list
    assert "minor crime (disorderly conduct, trespassing, shoplifting)" in _row(MINOR_CRIME).notes


def test_crime_band_directions_survive_band_math():
    # negative effect: the band must bracket with the point inside
    for link in (ANY_CRIME, MINOR_CRIME):
        p = _row(link)
        assert p.low < p.point < p.high < 0


# --- the refusal (duncan2010) ------------------------------------------

def test_duncan_refused_not_a_parameter():
    import pytest

    with pytest.raises(KeyError):
        PARAMS.by_link("early_poverty_income->adult_earnings")
    with pytest.raises(KeyError):
        PARAMS.by_link("unconditional_income->adult_earnings")


def test_duncan_bib_entry_marks_refusal():
    parts = load_all(PARAMS_DIR)
    bib = parts["bib"]
    d = bib["duncan2010"]
    assert "observational" in d.fields["note"]
    assert "0.63" in d.fields["note"]


def test_zg_companion_bib_entry_exists():
    parts = load_all(PARAMS_DIR)
    assert "zg2012" in parts["bib"]


# --- units wiring -------------------------------------------------------

def test_edu_years_token_and_composition():
    assert EDU_YEARS == "edu_years"
    assert composition_for(USD, EDU_YEARS) == "rate"


def test_usd_prob_is_boundary_rate():
    assert composition_for(USD, PROB) == "rate"


def test_all_three_rows_are_boundary_applicable():
    from downstream.audit import audit

    findings = audit(PARAMS_DIR)
    errors = [f for f in findings if f.severity == "ERROR"]
    assert errors == []
