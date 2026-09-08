"""v1.22 pins: the foreclosure price-spillover row (queue #18, read via
NBER w14866; Campbell, Giglio & Pathak, AER 101(5):2108-31).

What this file hunts:
- the clustering-inflated hedonic number creeping back as the point:
  the 0.1mi zero-distance associations (-9.1% / -7.3%) are ~4x the
  lead-vs-lag DiD; landing them would overstate harm by the exact
  factor the paper says clustering inflates them
- the DiD's missing SE getting fabricated into a fake CI: the band
  must be the declared rounding band, with the SE-carrying hedonic
  associates recorded BESIDE (never averaged in)
- the queue's phantom venue (QJE 126) or the Immergluck & Smith crime
  paper being cited as the price-spillover source
- the row composing into the earnings/child chains: PARALLEL stream,
  boundary-applied - the housing-contagion chain is a queued P3 item,
  not a live edge
- the identification limit being lost: no instrument, estimates not
  structural (the authors' own statement) - a future editor must not
  upgrade this to EXACT or to a causal chain
- the WP-read caveat degrading into a published-version claim: the
  table-level numbers come from the April 2009 draft; the published
  AER abstract confirms the preferred estimate and the 27% discount
"""
import pytest

from downstream.audit import audit
from downstream.params import default_dir, load, load_nodes
from downstream.citations import parse_bib

PARAMS_DIR = default_dir()
PARAMS = load(PARAMS_DIR / "parameters.csv")
BIB = parse_bib(PARAMS_DIR / "references.bib")
LINK = "foreclosure_order->house_price_gap"


def test_version_is_v122():
    assert (PARAMS_DIR / "VERSION").read_text().strip() == "v1.22"


def test_row_matches_preferred_did():
    # "each foreclosure that takes place 0.05 miles away lowers the
    # price of a house by about 1%" - lead-vs-lag DiD preferred
    p = PARAMS.by_link(LINK)
    assert p.point == pytest.approx(0.99, abs=1e-6)
    assert p.tier == "EXACT-results" and p.citation == "campbell2011"
    assert p.low == pytest.approx(0.9875) and p.high == pytest.approx(0.9925)


def test_band_is_declared_rounding_not_fake_ci():
    # the DiD reports NO SE; the band must SAY it is the rounding band
    # (point +/-25%) - a fabricated 1.96-SE interval is the failure
    p = PARAMS.by_link(LINK)
    assert "NO standard error" in p.notes or "NO SE" in p.notes
    assert "rounding band" in p.notes
    assert p.low == pytest.approx(1 - 0.01 * 1.25, abs=1e-6)
    assert p.high == pytest.approx(1 - 0.01 * 0.75, abs=1e-6)


def test_inflated_hedonics_recorded_not_landed():
    # the SE-carrying associations stay in the notes as spread context
    p = PARAMS.by_link(LINK)
    assert "-1.8%" in p.notes and "-1.1%" in p.notes
    assert "-9.1%" in p.notes and "-7.3%" in p.notes
    assert "clustering-inflated" in p.notes
    # and the point is the DiD, not the hedonic
    assert p.point == pytest.approx(0.99, abs=1e-6)


def test_identification_limit_declared():
    p = PARAMS.by_link(LINK)
    assert "NOT structural" in p.notes or "not structural" in p.notes
    assert "no instrument" in p.notes
    assert "lead-vs-lag" in p.notes
    # the WP-read caveat must survive: tables are the April 2009 draft
    assert "w14866" in p.notes and "EXACT-results" in p.notes


def test_venue_correction_recorded():
    p = PARAMS.by_link(LINK)
    assert "AER 101(5):2108-31" in p.notes
    assert "Immergluck" in p.notes and "CRIME paper" in p.notes
    e = BIB["campbell2011"]
    assert e.fields["journal"] == "American Economic Review"
    assert e.fields["volume"] == "101" and e.fields["number"] == "5"
    assert e.fields["pages"] == "2108--2131"
    assert e.fields["doi"] == "10.1257/aer.101.5.2108"
    assert e.evidence == "fulltext-table"


def test_parallel_stream_never_composed():
    # the spillover is a housing-market level response: no edge from
    # house_price_gap into the earnings multiplier or the child chains
    p = PARAMS.by_link(LINK)
    assert "parallel" in p.notes.lower() and "never composed" in p.notes.lower()
    downstream_links = {
        q.link
        for q in PARAMS.parameters
        if q.from_node == "house_price_gap"
    }
    assert downstream_links == set()
    nodes = load_nodes(PARAMS_DIR / "nodes.csv")
    assert nodes["foreclosure_order"].unit == "persons"
    assert nodes["house_price_gap"].unit == "gap_multiplier"
    assert "no upstream producer" in nodes["foreclosure_order"].description


def test_zero_distance_tail_declared():
    # the same-location DiD (-2%) and the 99.9th-percentile dummies
    # (-21% to -26%) must stay findable for the housing-contagion item
    p = PARAMS.by_link(LINK)
    assert "zero distance -2%" in p.notes
    assert "99.9th" in p.notes


def test_persistence_and_aggregate_context():
    p = PARAMS.by_link(LINK)
    assert "Table 14" in p.notes
    assert "$406,000" in p.notes and "$110,000" in p.notes


def test_audit_clean():
    findings = audit()
    errors = [f for f in findings if f.severity == "ERROR"]
    assert errors == []
