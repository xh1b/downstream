---
title: Count-level parameter uncertainty intervals
area: uncertainty
priority: P2
assignee:
due:
blocked-by: []
expected-paths: []
---

# Count-level parameter uncertainty intervals

## Context

Migrated from TODO entry 38, section "Engine", original line 217.

- **[DONE 2026-09-09] Count-level parameter intervals** — `scenario` jointly samples local-job, mortality, and
child-dollar counts on the same LHS/correlation draws and emits central 90% parameter-only intervals. Support envelopes
remain separately labeled; exposure, baseline, county/pooling, structural, and unmodeled uncertainty are named rather
than merged into a false total interval.

## Acceptance

- [x] Preserve joint LHS/correlation draws, central parameter-only intervals and separate support envelopes.
