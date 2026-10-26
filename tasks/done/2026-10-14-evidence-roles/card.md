---
title: Evidence-role and estimand contracts
area: evidence
priority: P1
assignee:
due:
blocked-by: []
expected-paths: []
---

# Evidence-role and estimand contracts

## Context

Migrated from TODO entry 47, section "Review priorities — 2026-09-10", original line 269.

- **[DONE 2026-09-13] Evidence-role and estimand contracts:** screening vocabularies frozen (unknown/blank composition
or extraction status refused), Moretti conversion requires a declared job class (manufacturing or high_tech) instead of
answering with the cross-class 1.6–5.0 span, and every parameter row now carries a machine-readable `evidence_role` (18
conditional / 3 structural / 28 boundary; `admitted` reserved) that load refuses when missing, chains refuse when
boundary, and vignette streams visibly block with role-named reasons. Landing v1.39; applicability conditions themselves
remain explicit assumptions.

## Acceptance

- [x] Preserve role-tagged evidence, screening vocabularies, job-class restrictions and boundary refusals. [role and boundary tests](../../../tests/test_evidence.py)
