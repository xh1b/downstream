from pathlib import Path

from downstream.evidence import load_corpus, load_findings


ROOT = Path(__file__).resolve().parent.parent


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
