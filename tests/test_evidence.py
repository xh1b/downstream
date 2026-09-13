from pathlib import Path

import pytest

from downstream.evidence import (
    COMPOSITION_STATUSES,
    EXTRACTION_STATUSES,
    load_corpus,
    load_findings,
)


ROOT = Path(__file__).resolve().parent.parent

_FINDINGS_HEADER = ("finding_id,corpus_id,exposure,outcome,estimand,point,"
                    "standard_error,unit,time_horizon,population_scope,design,"
                    "composition_status,extraction_status,notes\n")


def _finding_row(**overrides):
    row = {"finding_id": "f9", "corpus_id": "c9", "exposure": "ex", "outcome": "out",
           "estimand": "est", "point": "1.0", "standard_error": "0.1", "unit": "units",
           "time_horizon": "year 6+", "population_scope": "US adults", "design": "IV",
           "composition_status": "requires_table_extraction",
           "extraction_status": "abstract_screened", "notes": "note"}
    row.update(overrides)
    return ",".join(str(v) for v in row.values()) + "\n"


def _write_findings(tmp_path, row):
    path = tmp_path / "findings.csv"
    path.write_text(_FINDINGS_HEADER + row)
    return path


def test_acquired_corpus_is_hash_pinned_and_not_misrepresented_as_extracted():
    records = load_corpus(ROOT / "params" / "evidence_corpus.csv")
    assert len(records) == 100
    assert all(record.retrieval_status == "verified_pdf" for record in records)
    assert sum(record.text_extractable for record in records) == 96
    assert all(record.source_url for record in records)
    assert sum(record.screening_status == "screened" for record in records) == 67
    assert all(record.screening_status in {"screened", "unreviewed"} for record in records)
    assert all(len(record.sha256) == 64 for record in records)


def test_screened_findings_preserve_noncomposable_estimands():
    findings = load_findings(ROOT / "params" / "evidence_findings.csv")
    assert len(findings) >= 9
    assert any(f.composition_status == "not_composable_without_probability_translation" for f in findings)
    assert any(f.composition_status == "already_parameterized" for f in findings)
    assert all(f.extraction_status in {"fulltext_table", "fulltext_results", "abstract_screened"} for f in findings)
    # The shipped file exercises the vocabularies widely; every value must
    # be a declared one.
    assert {f.composition_status for f in findings} <= COMPOSITION_STATUSES
    assert {f.extraction_status for f in findings} <= EXTRACTION_STATUSES


def test_findings_refuse_unknown_composition_status(tmp_path):
    path = _write_findings(tmp_path, _finding_row(composition_status="fine_i_guess"))
    with pytest.raises(ValueError, match="unknown composition_status"):
        load_findings(path)


def test_findings_refuse_blank_composition_status(tmp_path):
    path = _write_findings(tmp_path, _finding_row(composition_status=""))
    with pytest.raises(ValueError, match="unknown composition_status"):
        load_findings(path)


def test_findings_refuse_unknown_extraction_status(tmp_path):
    path = _write_findings(tmp_path, _finding_row(extraction_status="skimmed"))
    with pytest.raises(ValueError, match="unknown extraction_status"):
        load_findings(path)


def test_findings_refuse_blank_applicability_metadata(tmp_path):
    path = _write_findings(tmp_path, _finding_row(population_scope=" "))
    with pytest.raises(ValueError, match="blank applicability metadata"):
        load_findings(path)
