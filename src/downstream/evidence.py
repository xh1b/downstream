"""The acquired-paper registry.

The parameter table is deliberately small: it contains only estimates that
have been read, scoped, and checked for composability.  This module carries
the wider evidence corpus so a downloaded study is not invisible while that
work is pending.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EvidenceRecord:
    """A hash-pinned acquired paper, before or after scientific screening."""

    corpus_id: str
    source_url: str
    sha256: str
    pages: int
    text_extractable: bool
    retrieval_status: str
    screening_status: str
    import_status: str
    local_filename: str


@dataclass(frozen=True)
class EvidenceFinding:
    """A read result from one paper, before graph-parameter admission.

    A finding may be directional-only or may use an estimand that is unsafe to
    compose.  Those are valuable scientific results, so the registry preserves
    them rather than forcing every finding into ``parameters.csv``.
    """

    finding_id: str
    corpus_id: str
    exposure: str
    outcome: str
    estimand: str
    point: float | None
    standard_error: float | None
    unit: str
    time_horizon: str
    population_scope: str
    design: str
    composition_status: str
    extraction_status: str
    notes: str


def load_corpus(path: str | Path) -> tuple[EvidenceRecord, ...]:
    """Load the mechanically verified acquisition registry.

    This intentionally does not turn records into model parameters.  See
    ``docs/CITING.md`` for the separate scientific-extraction gate.
    """
    with open(path, newline="", encoding="utf-8") as handle:
        rows = [
            EvidenceRecord(
                corpus_id=row["corpus_id"],
                source_url=row["source_url"],
                sha256=row["sha256"],
                pages=int(row["pages"]),
                text_extractable=row["text_extractable"] == "true",
                retrieval_status=row["retrieval_status"],
                screening_status=row["screening_status"],
                import_status=row["import_status"],
                local_filename=row["local_filename"],
            )
            for row in csv.DictReader(handle)
        ]
    ids = [row.corpus_id for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate corpus_id in evidence registry")
    return tuple(rows)


def _optional_float(value: str) -> float | None:
    return float(value) if value.strip() else None


def load_findings(path: str | Path) -> tuple[EvidenceFinding, ...]:
    """Load full-text screening results; no admission to parameters is implied."""
    with open(path, newline="", encoding="utf-8") as handle:
        rows = [
            EvidenceFinding(
                finding_id=row["finding_id"],
                corpus_id=row["corpus_id"],
                exposure=row["exposure"],
                outcome=row["outcome"],
                estimand=row["estimand"],
                point=_optional_float(row["point"]),
                standard_error=_optional_float(row["standard_error"]),
                unit=row["unit"],
                time_horizon=row["time_horizon"],
                population_scope=row["population_scope"],
                design=row["design"],
                composition_status=row["composition_status"],
                extraction_status=row["extraction_status"],
                notes=row["notes"],
            )
            for row in csv.DictReader(handle)
        ]
    ids = [row.finding_id for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate finding_id in evidence findings")
    return tuple(rows)
