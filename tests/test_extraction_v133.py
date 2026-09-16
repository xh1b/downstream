"""v1.33 pins: #24 Damm & Dustmann 2014 neighborhood conviction-share exposure.

What this file hunts:
- the two landed damm2014 rows drifting: EXACT tier, 1.96-SE bands,
  the spec-5 (municipality FE) point choice with spec 4 recorded
  beside, the dist shape (normal)
- the queue-target trap: the queue said "exposure-duration
  elasticity" — the paper has NO clean duration elasticity (age at
  assignment is perfectly correlated with potential exposure years);
  the correction must stay declared on the row
- the operative-channel trap: the exposure is the SHARE of convicted
  youth, NOT the committed-crime rate (Table 6 null) — a surface that
  chains a crime-count delta into this row is wrong by the paper's own
  finding; the nulls must stay recorded
- the female null: panel B is all-n.s. and must never be generalized
- the units wiring: PERCENT level token, (PERCENT, PROB) boundary
  'rate' composition, both share nodes registered as entry nodes
"""
from downstream.params import default_dir, load, load_all
from downstream.units import PERCENT, PROB, composition_for

PARAMS_DIR = default_dir()
PARAMS = load(PARAMS_DIR / "parameters.csv")


def test_version_is_v133():
    assert (PARAMS_DIR / "VERSION").read_text().strip() == "v1.47"


OVERALL = "youth_crime_conviction_share->youth_crime_convicted"
VIOLENT = "youth_violent_crime_conviction_share->youth_crime_convicted"


def _row(link: str):
    return PARAMS.by_link(link)


# --- the overall-share row --------------------------------------------

def test_overall_row_exact_values():
    p = _row(OVERALL)
    assert p.tier == "EXACT"
    assert p.point == 0.061  # 0.043/0.70pp per 1pp (T3 spec 5, male 15-21)
    assert p.low == 0.000 and p.high == 0.123  # 1.96 x SE 0.022/0.70
    assert p.dist == "normal"


def test_overall_row_carries_the_queue_correction():
    p = _row(OVERALL)
    # the queue's "exposure-duration elasticity" target is corrected on
    # the row: no clean duration elasticity exists in this paper
    assert "exposure-duration" in p.notes
    assert "confound" in p.notes
    assert "CORRECTED" in p.notes


def test_overall_row_spec4_beside_and_relative_scaling():
    p = _row(OVERALL)
    assert "0.033" in p.notes          # conservative spec 4 recorded beside
    assert "7-13%" in p.notes          # paper's relative prose scaling
    assert "0.241" in p.notes          # count-of-convictions row beside


def test_overall_row_band_edge_declared():
    p = _row(OVERALL)
    # the band's lower edge touches the no-effect line — declared, not
    # massaged away
    assert "lower edge rounds to 0.000" in p.notes


# --- the violent-share row --------------------------------------------

def test_violent_row_exact_values():
    p = _row(VIOLENT)
    assert p.tier == "EXACT"
    assert p.point == 0.366  # 0.045/0.123pp per 1pp (T5 spec 5)
    assert p.low == 0.143 and p.high == 0.589  # 1.96 x SE 0.014/0.123
    assert p.dist == "normal"


def test_violent_row_spec4_beside():
    p = _row(VIOLENT)
    assert "0.276" in p.notes          # spec 4 recorded beside
    assert "1% level" in p.notes


def test_violent_row_thin_level_never_chained():
    p = _row(VIOLENT)
    # the violent share is a thin LEVEL (mean 0.286%) — chaining a
    # crime-count delta into it is forbidden by the row itself
    assert "never chained" in p.notes
    assert "0.286" in p.notes


# --- declared nulls -----------------------------------------------------

def test_committed_crime_rate_null_recorded():
    # Table 6: the committed-crime RATE does not move children — only
    # the conviction share does; this is the paper's operative-channel
    # discipline and must stay on the node + row
    p = _row(OVERALL)
    assert "COMMITTED-crime rate is a NULL" in p.notes
    parts = load_all(PARAMS_DIR)
    assert any("committed-crime RATE is a declared null" in n.description
               for n in parts["nodes"].values())


def test_female_null_recorded():
    p = _row(OVERALL)
    assert "FEMALE NULL" in p.notes
    assert "FEMALE NULL" in _row(VIOLENT).notes


def test_property_drug_nulls_recorded():
    p = _row(VIOLENT)
    assert "property" in p.notes and "null" in p.notes
    assert "drug" in p.notes


def test_co_national_channel_recorded():
    p = _row(OVERALL)
    # Table 7: the operative peer channel is co-nationals' conviction
    # share; immigrant-share measures null — social interaction
    assert "co-national" in p.notes
    assert "social interaction" in p.notes


def test_source_version_declared():
    p = _row(OVERALL)
    # the numbers come from the Aarhus WP 2013-17 draft of the AER
    # version of record — declared on every landed row
    assert "WP 2013-17" in p.notes
    assert "WP 2013-17" in _row(VIOLENT).notes


# --- the boundary rule --------------------------------------------------

def test_no_crime_count_chain_producer():
    # no parameter may produce youth_crime_convicted from a crime-count
    # delta: the only producers are the two share nodes
    producers = {p.from_node for p in PARAMS.parameters
                 if p.to_node == "youth_crime_convicted"}
    assert producers == {
        "youth_crime_conviction_share",
        "youth_violent_crime_conviction_share",
    }


# --- units wiring -------------------------------------------------------

def test_percent_token_and_composition():
    assert PERCENT == "percent"
    assert composition_for(PERCENT, PROB) == "rate"


def test_new_nodes_have_declared_units():
    parts = load_all(PARAMS_DIR)
    nodes = parts["nodes"]
    assert nodes["youth_crime_convicted"].unit == "probability"
    assert nodes["youth_crime_conviction_share"].unit == "percent"
    assert nodes["youth_violent_crime_conviction_share"].unit == "percent"


def test_share_nodes_are_entry_nodes():
    from downstream.audit import audit

    findings = audit(PARAMS_DIR)
    orphans = [f for f in findings
               if f.severity == "WARN" and f.check == "orphan"
               and ("conviction_share" in f.message)]
    assert orphans == []


def test_audit_passes_clean():
    from downstream.audit import audit

    findings = audit(PARAMS_DIR)
    errors = [f for f in findings if f.severity == "ERROR"]
    assert errors == []


def test_bib_entry_upgraded_to_fulltext_table():
    parts = load_all(PARAMS_DIR)
    d = parts["bib"]["damm2014"]
    assert d.fields["xh1b-evidence"] == "fulltext-table"
    assert "2013-17" in d.fields["note"]
