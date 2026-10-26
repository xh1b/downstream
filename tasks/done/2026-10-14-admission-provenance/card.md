---
title: Admission and provenance contract
area: evidence
priority: P1
assignee:
due:
blocked-by: []
expected-paths: []
---

# Admission and provenance contract

## Context

Migrated from TODO entry 46, section "Review priorities — 2026-09-10", original line 255.

- **[DONE 2026-09-13] Admission and provenance contract:** blank tier, citation, or population_scope is refused at
parameter load, and every public ledger/scenario/community step publishes its studied population beside the citation
(`tests/test_admission_provenance.py`). Synthesis loading and pooling also refuse blank population/design/horizon
compatibility fields instead of pooling blank-to-blank as "identical" (`tests/test_synthesis.py`), and verified baseline
rows must pin value, citation, and population at load, with unknown statuses refused. Code safeguards only — they do not
discharge the transport assumptions in the applicability audit. Of the evidence blocks recorded this morning, county
integration was lifted the same day by v1.36 (validated county export + matching metadata, wired end to end); the
published-QJE mortality profile and V2/prospective validation remain unresolved.

## Acceptance

- [x] Preserve parameter/baseline admission safeguards and published population/tier provenance. [admission tests](../../../tests/test_admission_provenance.py) [synthesis admission](../../../tests/test_synthesis.py)
