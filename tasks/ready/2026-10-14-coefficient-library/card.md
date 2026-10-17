---
title: Populate compatible independent coefficient pools
area: evidence
priority: P1
assignee:
due:
blocked-by: []
expected-paths: []
---

# Populate compatible independent coefficient pools

## Context

Migrated from TODO entry 05, section "Next version — review follow-through (2026-10-14)", original line 65.

- **[PARTIAL / compatible independent pools pending] Coefficient synthesis library:** predeclare search and inclusion
rules; retain nulls, protective effects and conflicts. Extract compatible treatment/comparison, population, scale,
horizon, uncertainty, and sample-overlap records. Existing synthesis code is not a pooled evidence library; study-level
heterogeneity is not a target transport model. Twenty-three hash-pinned Table 5/7, Table 2/8 and Danish
cumulative-hazard contrasts now ship in `params/study_estimates.csv`. These are three study samples, not twenty-three
independent studies. Current groups are singleton/overlapping and are deliberately not pooled. Search/inclusion and
overlap rules are frozen in `docs/research/scenario_evidence_protocol.md`; independent full-text extraction remains open.

## Acceptance

- [x] Twenty-three hash-pinned contrasts ship; current incompatible/overlapping groups are not pooled.
- [ ] Extract independent estimates with population, design, scale, horizon, uncertainty and overlap metadata.
- [ ] Pool only compatible estimates and preserve null, protective and conflicting findings.
