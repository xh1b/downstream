---
title: Age-timed child-dollar present values
area: children
priority: P2
assignee:
due:
blocked-by: []
expected-paths: []
---

# Age-timed child-dollar present values

## Context

Migrated from TODO entry 08, section "Next version — review follow-through (2026-10-14)", original line 95.

- **[DONE conditional valuation] Child-dollar valuation:** retain undiscounted lifetime totals and add separately
labeled present values with explicit real discount rate, valuation date, child age and annual earnings profile. Test
zero-rate equivalence and supported timing; do not relabel an adult annual effect as an identified constant effect
across the whole career. Known child ages + real discount rate + valuation/event year produce annual schedules, separate
observed-age and career projections, undiscounted totals and parameter intervals. Zero-rate equivalence and signed
subgroup gains pass.

## Acceptance

- [x] Retain undiscounted totals and separate observed-age-window and career projections with explicit discounting. [valuation tests](../../../tests/test_valuation.py)
