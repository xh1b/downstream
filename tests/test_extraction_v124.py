"""v1.24 pins: recessions -> IPV (queue #22, owner-downloaded PDF read in
full; Schneider, Harknett & McLanahan, Demography 53(2):471-505).

What this file hunts:
- the UR LEVEL becoming a wired row: the paper's Table 8 level is NULL
  on all three outcomes - only the 12-month CHANGE moves abuse; a
  surface wiring the level would publish a null as a finding
- the violent-only outcome getting its own row: it is null for BOTH
  unemployment measures; only hardship moves violent-only and the
  authors flag reverse causality (violent behavior dis-orders the
  household finances) - landing it would publish the flagged number
- the shock row losing its spec-range band or its headline-spec point:
  the logit/LDV/FE triple (.454/.401/.406) is the band evidence, and
  Model 1 (the paper's headline) is the point - edge-hugging is
  declared, not hidden
- the two Table 1 rows borrowing coefficients from a scrambled
  extraction: their bands are the declared +/-25% rounding band; the
  table coefficients stay recorded beside, never as band edges
- the boundary discipline breaking: all three rows are per-unit
  responses to an external shock - they must never compose into the
  earnings/IGE chains
"""
import pytest

from downstream.audit import audit
from downstream.params import default_dir, load, load_nodes

PARAMS_DIR = default_dir()
PARAMS = load(PARAMS_DIR / "parameters.csv")
SHOCK = "local_unemp_shock->household_ipv"
HARD = "household_hardship->household_ipv"
COUP = "couple_unemployment->household_ipv"


def test_version_is_v124():
    assert (PARAMS_DIR / "VERSION").read_text().strip() == "v1.37"


def test_shock_row():
    p = PARAMS.by_link(SHOCK)
    assert p.point == pytest.approx(1.58, abs=1e-6)
    assert p.low == pytest.approx(1.49) and p.high == pytest.approx(1.58)
    assert p.tier == "EXACT-results" and p.citation == "schneider2016"


def test_shock_row_carries_the_spec_triple():
    p = PARAMS.by_link(SHOCK)
    assert ".454*" in p.notes and ".401*" in p.notes and ".406*" in p.notes
    # the authors' own prevalence predictions stay on record beside the OR
    assert "10%->12%" in p.notes and "14%" in p.notes


def test_level_null_on_record():
    # Table 8: the UR level is null on all three outcomes - the row must
    # carry the discipline so no surface wires the level as a producer
    p = PARAMS.by_link(SHOCK)
    assert "LEVEL-NULL" in p.notes and "null" in p.notes
    assert "12-month CHANGE" in p.notes


def test_hardship_row_uses_prose_point_and_rounding_band():
    p = PARAMS.by_link(HARD)
    assert p.point == pytest.approx(2.14, abs=1e-6)
    assert p.low == pytest.approx(1.61) and p.high == pytest.approx(2.68)
    # the scrambled table coefficients are recorded beside, NOT band edges
    assert "scrambled" in p.notes
    assert "NOT used for the band" in p.notes
    assert "15% vs 7%" in p.notes


def test_violent_only_not_a_row():
    # violent-only is null for both unemployment measures; hardship ->
    # violent carries the authors' own reverse-causality flag
    links = {q.link for q in PARAMS.parameters}
    assert "household_hardship->ipv_violent_only" not in links
    assert "reverse-causality" in PARAMS.by_link(HARD).notes


def test_couple_unemployment_row():
    p = PARAMS.by_link(COUP)
    assert p.point == pytest.approx(1.30, abs=1e-6)
    assert p.low == pytest.approx(1.04) and p.high == pytest.approx(1.63)
    assert ".404**" in p.notes
    assert "unchanged" in p.notes  # FE magnitude survival, declared


def test_boundary_discipline():
    for link in (SHOCK, HARD, COUP):
        p = PARAMS.by_link(link)
        assert "NEVER" in p.notes and "PARALLEL" in p.notes
    outs = {q.link for q in PARAMS.parameters
            if q.from_node in ("local_unemp_shock", "household_hardship",
                               "couple_unemployment")} - {SHOCK, HARD, COUP}
    assert outs == set()
    from downstream import units
    assert units.composition_for("rate_ratio", "rate_ratio") == "rate"
    nodes = load_nodes(PARAMS_DIR / "nodes.csv")
    for n in ("local_unemp_shock", "household_hardship", "couple_unemployment"):
        assert nodes[n].unit == "rate_ratio"


def test_shock_node_semantics():
    # 1.0 = flat, 2.0 = doubling - the multiplier scale must be declared
    # on the node or a surface will feed it a percentage point
    nodes = load_nodes(PARAMS_DIR / "nodes.csv")
    assert "1.0 = flat, 2.0 = doubling" in nodes["local_unemp_shock"].description


def test_bib_and_doi():
    from downstream.citations import parse_bib
    e = parse_bib(PARAMS_DIR / "references.bib")["schneider2016"]
    assert e.evidence == "fulltext-table"
    assert e.fields["journal"] == "Demography"
    assert e.fields["volume"] == "53" and e.fields["number"] == "2"
    assert e.fields["pages"] == "471--505"
    assert e.fields["doi"] == "10.1007/s13524-016-0462-1"


def test_audit_clean():
    findings = audit()
    errors = [f for f in findings if f.severity == "ERROR"]
    assert errors == []
