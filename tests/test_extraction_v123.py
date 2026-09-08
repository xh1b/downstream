"""v1.23 pins: IPV exposure -> child mental health (queue #21, read via
the Nebraska DigitalCommons accepted manuscript; Evans, Davies &
DiLillo, Aggression and Violent Behavior 13(2):131-140).

What this file hunts:
- the trauma d = 1.54 sneaking in as a row: k = 6, heterogeneous, and
  the authors themselves say interpret with caution - landing it would
  publish the meta's least reliable number as its headline
- the three metas (evans2008/kitzmann2003/wolfe2003) being averaged
  into one number: CITING section 5 - contested/duplicate findings
  never average; the cross-checks stay recorded beside
- the pooled externalizing .47 losing its gender split: boys .46 vs
  girls .23 is a SIGNIFICANT moderator (QB = 4.11) - the pooled row
  must carry the split or a surface will quote .47 at girls
- the boundary discipline breaking: these are exposure-contrast d's
  (exposed vs not) - they must never compose into the child_earnings
  IGE chain or the achievement SD row; the new composition rule is
  boundary-only by design
- the bib tier regressing to canonical after the full-text read
- a fabricated CI: the bands are the reported random-effects CIs,
  verbatim
"""
import pytest

from downstream.audit import audit
from downstream.params import default_dir, load, load_nodes
from downstream.citations import parse_bib

PARAMS_DIR = default_dir()
PARAMS = load(PARAMS_DIR / "parameters.csv")
BIB = parse_bib(PARAMS_DIR / "references.bib")
INT = "household_ipv->child_internalizing_sd"
EXT = "household_ipv->child_externalizing_sd"


def test_version_is_v123():
    assert (PARAMS_DIR / "VERSION").read_text().strip() == "v1.25"


def test_internalizing_row_exact():
    p = PARAMS.by_link(INT)
    assert p.point == pytest.approx(0.48, abs=1e-6)
    assert p.low == pytest.approx(0.39) and p.high == pytest.approx(0.57)
    assert p.tier == "EXACT" and p.citation == "evans2008"


def test_externalizing_row_exact():
    p = PARAMS.by_link(EXT)
    assert p.point == pytest.approx(0.47, abs=1e-6)
    assert p.low == pytest.approx(0.38) and p.high == pytest.approx(0.56)
    assert p.tier == "EXACT" and p.citation == "evans2008"


def test_bands_are_reported_cis():
    # random-effects CIs verbatim from the results text - not derived,
    # not rounded, not stretched
    pi = PARAMS.by_link(INT)
    pe = PARAMS.by_link(EXT)
    assert "CI .39-.57" in pi.notes
    assert "z = 11.25" in pi.notes
    assert "CI .38-.56" in pe.notes
    assert "z = 10.11" in pe.notes


def test_trauma_refused():
    # d = 1.54 must NOT be a row: k=6, Q(5) = 18.35 heterogeneous, and
    # the authors' own caution is on record
    links = {q.link for q in PARAMS.parameters}
    assert "household_ipv->child_trauma_sd" not in links
    assert "child_trauma" not in " ".join(links)
    assert "1.54" in PARAMS.by_link(INT).notes
    assert "NOT landed" in PARAMS.by_link(INT).notes


def test_cross_checks_not_averaged():
    # kitzmann2003 (-.50/-.43) and wolfe2003 (.38/.42) stay recorded
    # beside, never folded into the point
    p = PARAMS.by_link(INT)
    assert "Kitzmann" in p.notes and "Wolfe" in p.notes
    assert "never averaged" in p.notes
    assert p.point == pytest.approx(0.48, abs=1e-6)


def test_gender_moderator_declared():
    p = PARAMS.by_link(EXT)
    assert ".46" in p.notes and ".23" in p.notes
    assert "QB = 4.11" in p.notes
    assert "boys .46 / girls .23" in p.population_scope


def test_homogeneity_declared():
    # internalizing homogeneous (no split landed), externalizing
    # heterogeneous (moderators examined) - the design asymmetry is
    # load-bearing for how the rows may be quoted
    assert "Q(56) = 70.61" in PARAMS.by_link(INT).notes
    assert "Q(52) = 80.35" in PARAMS.by_link(EXT).notes


def test_boundary_discipline():
    # exposure-contrast d's: PARALLEL stream, no downstream edges, and
    # the composition rule is the boundary "rate" like dahl2012
    for link in (INT, EXT):
        p = PARAMS.by_link(link)
        assert "NEVER" in p.notes and "PARALLEL" in p.notes
    outs = {q.link for q in PARAMS.parameters
            if q.from_node in ("child_internalizing_sd", "child_externalizing_sd")}
    assert outs == set()
    from downstream import units
    assert units.composition_for("rate_ratio", "sd_delta") == "rate"
    nodes = load_nodes(PARAMS_DIR / "nodes.csv")
    assert nodes["child_internalizing_sd"].unit == "sd_delta"
    assert nodes["child_externalizing_sd"].unit == "sd_delta"


def test_bib_upgraded_to_fulltext():
    e = BIB["evans2008"]
    assert e.evidence == "fulltext-table"
    assert e.fields["journal"] == "Aggression and Violent Behavior"
    assert e.fields["volume"] == "13" and e.fields["number"] == "2"
    assert e.fields["pages"] == "131--140"
    assert e.fields["doi"] == "10.1016/j.avb.2008.02.005"
    # the read path is declared: accepted manuscript via the permission
    # copy, recovered through the Wayback mirror of the WAF-blocked PDF
    assert "DigitalCommons" in e.fields.get("note", "")


def test_audit_clean():
    findings = audit()
    errors = [f for f in findings if f.severity == "ERROR"]
    assert errors == []
