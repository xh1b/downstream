"""v1.41 pins: Bingley-Cappellari-Ovidi (JEEA 2026) + Schaller-Stevens 2015.

What this file pins:
- two EXACT conditional rows from Bingley, Cappellari & Ovidi (JEEA,
  advance article 2026, DOI 10.1093/jeea/jvag048; read via IZA DP 16367,
  the WP draft of the version of record): math achievement in SD units
  and the derived left-tail exam non-completion relative on the new node
  exam_noncompletion_hazard
- the timing structure (infancy concentration) travels in row notes, not
  as rows - the model has no age-at-exposure selector
- the income-channel mediation recorded as a dahl2012 cross-check
- schallerstevens2015 cross-check notes on paul2009 (probability units,
  not SD-convertible) and the queue correction: no mortality estimates
  exist in that paper
"""
from downstream.audit import audit, summary
from downstream.params import default_dir, load, load_nodes

PARAMS_DIR = default_dir()
PARAMS = load(PARAMS_DIR / "parameters.csv")
NODES = load_nodes(PARAMS_DIR / "nodes.csv")


def test_child_achievement_row_pinned():
    row = PARAMS.by_link("displacement_event->child_achievement_sd")
    assert (row.point, row.low, row.high) == (-0.0206, -0.0402, -0.001)
    assert row.tier == "EXACT" and row.evidence_role == "conditional"
    assert row.citation == "bingley2026"
    assert "-0.0521" in row.notes  # infancy, the paper's headline stage
    assert "-0.0117 n.s." in row.notes  # test scores beside, declared null
    assert "age-at-exposure selector" in row.notes


def test_exam_noncompletion_row_pinned():
    row = PARAMS.by_link("displacement_event->exam_noncompletion_hazard")
    assert (row.point, row.low, row.high) == (1.0688, 1.0014, 1.1362)
    assert row.tier == "EXACT" and row.evidence_role == "conditional"
    assert "stevens2011 derivation precedent" in row.notes
    assert "1.126" in row.notes  # infancy beside
    assert "p=0.986" in row.notes  # age >= 18 placebo, identifying assumption
    assert NODES["exam_noncompletion_hazard"].unit == "rate_ratio"


def test_income_channel_is_crosscheck_never_a_row():
    dahl = PARAMS.by_link("family_income_shock->child_achievement_sd")
    assert "bingley2026 CROSS-CHECK" in dahl.notes
    assert "+0.0008" in dahl.notes  # mediation slope, recorded not composed
    assert dahl.point == 0.0610  # the dahl2012 anchor is untouched
    rows = [p.link for p in PARAMS.parameters if "mediation" in p.link]
    assert rows == []


def test_schaller_stevens_crosscheck_probability_units():
    paul = PARAMS.by_link("unemployment_status->mental_health_sd")
    assert "schallerstevens2015 CROSS-CHECK" in paul.notes
    assert "+1.39pp" in paul.notes and "not SD-convertible" in paul.notes
    assert paul.point == 0.51  # the paul2009 meta anchor is untouched


def test_bib_entries_with_evidence_fields():
    bib = (PARAMS_DIR / "references.bib").read_text()
    assert "bingley2026" in bib
    entry = bib.split("@article{bingley2026")[1][:700]
    assert "fulltext-table" in entry and "jeea/jvag048" in entry
    assert "schallerstevens2015" in bib
    entry2 = bib.split("@article{schallerstevens2015")[1][:700]
    assert "fulltext" in entry2 and "43" in entry2


def test_audit_clean_and_version_current():
    s = summary(audit(PARAMS_DIR))
    assert s["pass"], [f.as_dict() for f in audit(PARAMS_DIR) if f.severity.value == "error"]
    assert PARAMS.version == "v1.49"
