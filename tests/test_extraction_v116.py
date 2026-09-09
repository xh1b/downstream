"""v1.16 pins: child-maltreatment row (lindo2018maltreatment, read via
NBER w18994; JPubE 163 is the version of record).

Scope pins matter here: the row models the MALE-shock channel only
(the female-layoff coefficient is opposite-signed in the same table),
and the raw unemployment association is negative/endogenous — both
must stay declared on the row so a future re-reader cannot silently
apply this coefficient to the wrong shock or mistake the sign.
"""
import pytest

from downstream.audit import ERROR, audit
from downstream.params import default_dir, load

PARAMS_DIR = default_dir()
PARAMS = load(PARAMS_DIR / "parameters.csv")


def test_maltreatment_row_matches_lsh_table3_panelA_col3():
    p = PARAMS.by_link("male_job_loss_rate->child_maltreatment")
    assert p.point == pytest.approx(6.0, abs=1e-6)
    assert p.low == pytest.approx(6.0 - 1.96 * 1.2, abs=5e-3)
    assert p.high == pytest.approx(6.0 + 1.96 * 1.2, abs=5e-3)
    assert p.tier == "EXACT" and p.citation == "lindo2018maltreatment"


def test_male_scope_declared_female_opposite_sign_recorded():
    p = PARAMS.by_link("male_job_loss_rate->child_maltreatment")
    assert "FEMALE" in p.notes and "opposite-signed" in p.notes
    assert "-6.5%" in p.notes
    assert "male-shock channel" in p.notes


def test_unemployment_endogeneity_warning_declared():
    p = PARAMS.by_link("male_job_loss_rate->child_maltreatment")
    assert "NEGATIVELY" in p.notes and "endogeneity" in p.notes
    # the identification statement must name the quasi-experiment
    assert "mass-layoff" in p.notes


def test_version_bumped_and_audit_clean():
    assert (PARAMS_DIR / "VERSION").read_text().strip() == "v1.32"
    errors = [f for f in audit(PARAMS_DIR) if f.severity == ERROR]
    assert errors == []
