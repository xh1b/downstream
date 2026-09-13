"""v1.42 pins: Brand & Simon Thomas 2014 landing + EB prior yardstick.

What this file pins:
- four EXACT conditional rows from Brand & Simon Thomas 2014 (AJS
  119(4):955-1001, read via PMC4372265) on new nodes: hs_completion,
  college_attendance, college_completion, adult_depression_cesd
- PSM identification-class honesty: bands keep the study's own SEs
  (one row honestly crosses zero); timing gradients travel in notes
- the scale01 unit exists for the CESD index and is distinct from
  probability
- the EB prior-strength yardstick is pinned in test_county_eb_prior.py;
  here we pin only that the declared k=2000 table is untouched
"""
from downstream.audit import audit, summary
from downstream.params import default_dir, load, load_nodes

PARAMS_DIR = default_dir()
PARAMS = load(PARAMS_DIR / "parameters.csv")
NODES = load_nodes(PARAMS_DIR / "nodes.csv")


def test_hs_completion_row_pinned():
    row = PARAMS.by_link("displacement_event->hs_completion")
    assert (row.point, row.low, row.high) == (-0.037, -0.0801, 0.0061)
    assert row.tier == "EXACT" and row.evidence_role == "conditional"
    assert row.citation == "brand2014"
    assert "-0.115**" in row.notes  # adolescence timing travels in notes
    assert "weakest identification class" in row.notes


def test_college_rows_pinned_and_stock_flow_distinct():
    att = PARAMS.by_link("displacement_event->college_attendance")
    assert (att.point, att.low, att.high) == (-0.063, -0.1081, -0.0179)
    comp = PARAMS.by_link("displacement_event->college_completion")
    assert (comp.point, comp.low, comp.high) == (-0.036, -0.0674, -0.0046)
    assert "never be merged" in att.notes  # stock vs the hilger2016 flow
    assert "adolescence" in att.notes or "12-17" in att.notes
    assert NODES["college_attendance"].description.count("DISTINCT") >= 1


def test_cesd_row_on_scale01_unit():
    row = PARAMS.by_link("displacement_event->adult_depression_cesd")
    assert (row.point, row.low, row.high) == (0.025, 0.0034, 0.0466)
    assert NODES["adult_depression_cesd"].unit == "scale01"
    assert NODES["adult_depression_cesd"].unit != "probability"
    assert "NOT a probability" in NODES["adult_depression_cesd"].description
    assert "+0.047**" in row.notes  # middle-childhood timing beside


def test_maternal_scope_and_bib_venue():
    bib = (PARAMS_DIR / "references.bib").read_text()
    entry = bib.split("@article{brand2014")[1][:700]
    assert "American Journal of Sociology" in entry
    assert "fulltext-table" in entry
    head = PARAMS.by_link("displacement_event->hs_completion")
    assert "single mothers" in head.population_scope
    assert "MATERNAL job displacement" in head.population_scope
    for link in ("college_attendance", "college_completion",
                 "adult_depression_cesd"):
        row = PARAMS.by_link(f"displacement_event->{link}")
        assert "same scope as the hs_completion row" in row.population_scope
        assert "hs_completion row" in row.notes or "same read" in row.notes
        assert row.dist == "normal"


def test_declared_prior_k_untouched_by_eb_yardstick():
    # the EB report informs; the shipped table keeps the declared k
    import csv
    with open(PARAMS_DIR / "county_mortality.csv", newline="") as fh:
        first = next(csv.DictReader(fh))
    assert float(first["prior_person_years"]) == 2000.0


def test_audit_clean_and_version_current():
    s = summary(audit(PARAMS_DIR))
    assert s["pass"], [f.as_dict() for f in audit(PARAMS_DIR) if f.severity.value == "error"]
    assert PARAMS.version == "v1.44"
