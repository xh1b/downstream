---
title: Combined child-gap view, housing chain and explanation design
area: presentation
priority: P3
assignee: mira
due:
blocked-by: []
expected-paths: [src/downstream/child_gap_view.py, tests/test_child_gap_view.py, docs/CHILD_GAP_VIEW.md]
---

# Combined child-gap view, housing chain and explanation design

## Context

Migrated from TODO entry 36, section "Engine", original line 215.

- **[P3] Combined child-gap view; housing contagion chain; explanation surface design.**

## Acceptance

- [x] Specify the combined child-gap view and housing-contagion evidence/estimand requirements. [API and missing bridges](../../../docs/CHILD_GAP_VIEW.md)
- [x] Design explanations that retain provenance and scope for each supported path. [structured report](../../../src/downstream/child_gap_view.py)
- [x] Verify signed/null-compatible values, child/target refusals, source income contrasts, dollar-baseline absence, both place modes and unavailable housing totals. [14 contract tests](../../../tests/test_child_gap_view.py)

## Implementation scope

The combined view is a side-by-side report rather than an additive child-gap
total. Structural descendant gaps do not acquire invented populations or dollar
totals. The housing contract explicitly lists the missing exposure, spatial,
valuation and school-finance bridges; no unsupported end-to-end housing total
is supplied. Engine remains 0.4.0 and parameter defaults are unchanged.
