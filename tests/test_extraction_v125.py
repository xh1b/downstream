"""v1.25 pins: unemployment -> mental health (queue #20, owner-downloaded
ScienceDirect PDF read in full; Paul & Moser, JVB 74(3):264-282).

What this file hunts:
- the unstable tail findings landing as rows: the post-29-month distress
  renewal is k=5 with a cubic term that is only marginal in the
  controlled analysis, and the age U-shape vanishes when marital status
  is controlled - the authors flag both; publishing either as a row
  would hand a surface an artifact
- the three causality anchors (factory-closure, longitudinal,
  cross-sectional) being averaged into one number: CITING section 5 -
  the factory-closure natural-experiment subset is the causal-clean
  number and stays beside, not folded in
- the band being stretched past the reported CI: the meta class pins
  the band to the reported random-effects CI verbatim
- the selection effect being buried: distress predicts job loss AND
  worse reemployment (d=.23/.15) - small but real, it must be declared
  so no surface presents the d=.51 as entirely causal
- the moderator scope disappearing: men and blue-collar workers are
  stronger; a surface quoting .51 at women or white-collar readers
  without that declaration is misquoting
- the status contrast being confused with the area unemployment rate:
  schneider2016's v1.24 level-null discipline says the UR LEVEL is
  null - this row is the person-level status contrast
"""
import pytest

from downstream.audit import audit
from downstream.params import default_dir, load, load_nodes

PARAMS_DIR = default_dir()
PARAMS = load(PARAMS_DIR / "parameters.csv")
LINK = "unemployment_status->mental_health_sd"


def test_version_is_v125():
    assert (PARAMS_DIR / "VERSION").read_text().strip() == "v1.45"


def test_row_exact_meta():
    p = PARAMS.by_link(LINK)
    assert p.point == pytest.approx(0.51, abs=1e-6)
    assert p.low == pytest.approx(0.47) and p.high == pytest.approx(0.54)
    assert p.tier == "EXACT" and p.citation == "paul2009"


def test_band_is_reported_ci():
    p = PARAMS.by_link(LINK)
    assert "CI" in p.notes
    # all-studies variant recorded beside, not averaged into the point
    assert "0.54" in p.notes and "k=323" in p.notes


def test_unstable_findings_not_landed():
    # post-29-month renewal: k=5, marginal cubic in the controlled
    # analysis; age U-shape: vanished under marital-status controls
    links = {q.link for q in PARAMS.parameters}
    tail = [l for l in links if "duration" in l or "long_term" in l]
    assert tail == []
    p = PARAMS.by_link(LINK)
    assert "UNSTABLE" in p.notes
    assert "not landed" in p.notes or "NOT landed" in p.notes
    assert "U-shape" in p.notes and "vanished" in p.notes


def test_causality_anchors_beside_not_averaged():
    p = PARAMS.by_link(LINK)
    assert "factory-closure" in p.notes and ".38" in p.notes
    assert "(CI .25-.51" in p.notes
    assert "never averaged" in p.notes
    assert "0.25" in p.notes and "0.29" in p.notes  # retest-corrected pair
    # the point stays the cross-sectional overall
    assert PARAMS.by_link(LINK).point == pytest.approx(0.51, abs=1e-6)


def test_case_rate_anchor():
    # the practical-importance translation: 34% vs 16% case rates
    p = PARAMS.by_link(LINK)
    assert "34%" in p.notes and "16%" in p.notes


def test_selection_declared():
    p = PARAMS.by_link(LINK)
    assert "SELECTION" in p.notes and ".23" in p.notes and ".15" in p.notes
    assert "OTHER way" in p.notes


def test_moderator_scope_declared():
    p = PARAMS.by_link(LINK)
    assert "men stronger" in p.notes and "blue-collar" in p.notes
    assert "9 months" in p.notes and ".73" in p.notes


def test_boundary_discipline():
    p = PARAMS.by_link(LINK)
    assert "NEVER" in p.notes and "PARALLEL" in p.notes
    outs = {q.link for q in PARAMS.parameters
            if q.from_node == "unemployment_status"} - {LINK}
    assert outs == set()
    from downstream import units
    assert units.composition_for("rate_ratio", "sd_delta") == "rate"
    nodes = load_nodes(PARAMS_DIR / "nodes.csv")
    assert nodes["unemployment_status"].unit == "rate_ratio"
    assert nodes["mental_health_sd"].unit == "sd_delta"
    # the person-level status contrast is NOT the area UR (level-null
    # discipline from v1.24)
    assert "NOT the area unemployment rate" in nodes["unemployment_status"].description


def test_bib_upgraded_to_fulltext():
    from downstream.citations import parse_bib
    e = parse_bib(PARAMS_DIR / "references.bib")["paul2009"]
    assert e.evidence == "fulltext-table"
    assert e.fields["journal"] == "Journal of Vocational Behavior"
    assert e.fields["volume"] == "74" and e.fields["number"] == "3"
    assert e.fields["pages"] == "264--282"
    assert e.fields["doi"] == "10.1016/j.jvb.2009.01.001"


def test_audit_clean():
    findings = audit()
    errors = [f for f in findings if f.severity == "ERROR"]
    assert errors == []
