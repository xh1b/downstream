---
title: Obtain matched external data and independently evaluate new paths
area: validation
priority: P1
assignee:
due:
blocked-by: []
expected-paths: []
---

# Obtain matched external data and independently evaluate new paths

## Context

Migrated from TODO entry 06, section "Next version — review follow-through (2026-10-14)", original line 75.

- **[BLOCKED external data] Matched independent evaluation:** freeze event bridges and scored endpoints; compare
direct-effect and stratified baselines with the expanded model; report every preregistered result, subgroup miss and
interval scope. Existing China-shock diagnostics and SIPP baseline checks remain visible; they do not establish
H-1B-specific causal validation. Executed all available diagnostics in
`validation/followthrough_evaluation_expanded_20261014.json` (the original `followthrough_evaluation.json` is retained).
No new source provides a matched event exposure bridge plus independently estimated outcomes. The new paths have not
passed causal event validation; no score or prospective timestamp is fabricated.

## Acceptance

- [ ] Obtain an aligned displacement bridge and independently estimated outcomes for an external event.
- [ ] Freeze endpoints and scoring before inspecting scored outcomes; publish every result and miss.

External blocker: no matched independent exposure bridge and outcome source has qualified. No causal score is claimed.
