"""v1.26 pins: import competition -> radical vote (queue #15, owner-downloaded
PDF read in full; Colantone & Stanig, AJPS 62(4):936-953).

What this file hunts:
- the NO-LEFT-WING discipline collapsing: protectionist left AND liberal
  right are NULL in this design - a surface claiming import competition
  feeds "polarization" in Europe (the autor2020 US pattern) or a
  left-protectionist surge would be inventing a result the paper
  explicitly does not find
- the sociotropic scope disappearing: the individual-level interactions
  are ALL n.s. - the effect is NOT confined to displaced manufacturing
  workers or the unemployed, so quoting this row as a
  displaced-workers-only mechanism misstates it
- the window discipline getting lost: the regression's shock is the
  2-year window change ($1k/worker per window); the row stores the
  same coefficient per $1k/worker of cumulative exposure - a surface
  that re-multiplies by the window count would double-count
- the IV/OLS gap being hidden: IV (.132) is 3x OLS (.041) - the
  authors attribute the attenuation to demand shocks; a surface quoting
  the OLS number would be quoting the attenuated one
- the band being fabricated: the CI is 1.96 SE on the reported IV SE,
  not a stretched or rounded band
"""
import pytest

from downstream.audit import audit
from downstream.params import default_dir, load, load_nodes

PARAMS_DIR = default_dir()
PARAMS = load(PARAMS_DIR / "parameters.csv")
LINK = "import_shock->radical_right_vote_share"


def test_version_is_v126():
    assert (PARAMS_DIR / "VERSION").read_text().strip() == "v1.47"


def test_row_exact():
    p = PARAMS.by_link(LINK)
    assert p.point == pytest.approx(13.2, abs=1e-6)
    assert p.low == pytest.approx(3.2) and p.high == pytest.approx(23.2)
    assert p.tier == "EXACT" and p.citation == "colantone2018"


def test_band_is_196_se():
    # 13.2 +/- 1.96 * 5.1 = [3.2, 23.2] - the reported IV SE, not stretched
    p = PARAMS.by_link(LINK)
    assert "CI = 1.96 SE" in p.notes
    assert "SE .051" in p.notes


def test_authors_scaling_recorded():
    p = PARAMS.by_link(LINK)
    assert "+1.7pp" in p.notes
    assert "5%" in p.notes and "SD 7%" in p.notes


def test_ols_gap_declared():
    # IV (.132) > OLS (.041): demand-shock attenuation, on record
    p = PARAMS.by_link(LINK)
    assert ".041" in p.notes and "attenuate" in p.notes


def test_no_left_wing_discipline():
    p = PARAMS.by_link(LINK)
    assert "protectionist left NULL" in p.notes
    assert "NO polarization" in p.notes
    assert "Contrasts" in p.notes or "CONTRASTS" in p.notes
    # the companion numbers stay beside, not landed as rows
    links = {q.link for q in PARAMS.parameters}
    assert "import_shock->protectionist_right_vote_share" not in links
    assert "import_shock->pro_trade_left_vote_share" not in links


def test_sociotropic_scope_declared():
    p = PARAMS.by_link(LINK)
    assert "SOCIOTROPIC" in p.notes
    assert "displaced-manufacturers-only" in p.notes
    assert "paul2009" in p.notes  # cross-referenced, not chained


def test_window_discipline():
    p = PARAMS.by_link(LINK)
    assert "2-year window" in p.notes
    assert "cumulative exposure" in p.notes
    nodes = load_nodes(PARAMS_DIR / "nodes.csv")
    assert nodes["radical_right_vote_share"].unit == "percent_delta"
    assert "gop_win_probability" in nodes["radical_right_vote_share"].description


def test_boundary_discipline():
    p = PARAMS.by_link(LINK)
    assert "NEVER" in p.notes
    outs = {q.link for q in PARAMS.parameters
            if q.from_node == "import_shock_per_worker"}
    assert LINK in outs  # the row itself is landed
    from downstream import units
    assert units.composition_for("usd", "percent_delta") == "rate"


def test_bib_upgraded_and_doi_fixed():
    from downstream.citations import parse_bib
    e = parse_bib(PARAMS_DIR / "references.bib")["colantone2018"]
    assert e.evidence == "fulltext-table"
    assert e.fields["journal"] == "American Journal of Political Science"
    assert e.fields["volume"] == "62" and e.fields["number"] == "4"
    assert e.fields["pages"] == "936--953"
    # the staging doi pointed at the SSRN preprint - replaced
    assert e.fields["doi"] == "10.1111/ajps.12358"
    assert "10.2139/ssrn.2904105" not in e.fields["doi"]
    assert "SSRN preprint" in e.fields.get("note", "")


def test_audit_clean():
    findings = audit()
    errors = [f for f in findings if f.severity == "ERROR"]
    assert errors == []
