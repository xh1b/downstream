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


# Frozen screening vocabularies. ``composition_status`` states why a finding
# is or is not safe to compose; an unknown or blank value must be refused at
# load rather than silently read as one of the composable states.
COMPOSITION_STATUSES = frozenset({
    "already_parameterized",
    "composable_after_baseline_and_time_alignment",
    "composable_only_with_matching_age_and_country_scope",
    "composable_with_move_definition_and_place_scope",
    "context_only_not_a_causal_edge",
    "context_only_pending_causal_decomposition",
    "context_only_pending_design_review",
    "cross_study_anchor_not_current_parameter",
    "discovery_only_not_a_parameter_source",
    "do_not_double_count",
    "model_context_not_empirical_edge",
    "not_composable_without_probability_translation",
    "not_directly_composable_until_index_is_unpacked",
    "requires_design_and_table_review",
    "requires_outcome_specific_extraction",
    "requires_table_extraction",
    "requires_table_uncertainty_extraction",
    "requires_unit_and_uncertainty_extraction",
})

EXTRACTION_STATUSES = frozenset({
    "abstract_screened",
    "fulltext_results",
    "fulltext_table",
})

# Fields that make a finding legible at all; a blank one is missing
# applicability metadata, not a sparser but valid record.
_REQUIRED_FINDING_FIELDS = (
    "corpus_id", "exposure", "outcome", "estimand", "unit",
    "time_horizon", "population_scope", "design",
)


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
        rows = []
        for row in csv.DictReader(handle):
            finding = EvidenceFinding(
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
            if not finding.finding_id:
                raise ValueError("blank finding_id in evidence findings")
            blank = [name for name in _REQUIRED_FINDING_FIELDS
                     if not getattr(finding, name).strip()]
            if blank:
                raise ValueError(
                    f"finding {finding.finding_id!r} has blank applicability metadata: "
                    f"{', '.join(blank)}"
                )
            if finding.composition_status not in COMPOSITION_STATUSES:
                raise ValueError(
                    f"finding {finding.finding_id!r} has unknown composition_status "
                    f"{finding.composition_status!r}; expected one of {sorted(COMPOSITION_STATUSES)}"
                )
            if finding.extraction_status not in EXTRACTION_STATUSES:
                raise ValueError(
                    f"finding {finding.finding_id!r} has unknown extraction_status "
                    f"{finding.extraction_status!r}; expected one of {sorted(EXTRACTION_STATUSES)}"
                )
            rows.append(finding)
    ids = [row.finding_id for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate finding_id in evidence findings")
    return tuple(rows)
