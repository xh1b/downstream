---
title: Expose reconciled annual household comparison summaries
area: households
priority: P2
assignee: mira
blocked-by: []
parent: 2026-10-14-full-comparison
related-to: [2026-10-14-household-dynamics]
expected-paths: [src/downstream/household.py, tests/test_household_summary.py, docs/HOUSEHOLD_COMPARISON_0_4.md]
---

# Inspect annual household comparison totals

User authorized this bounded improvement through the root agent. The current
paired annual SIPP scenario supplies each member's gross earnings/state
probabilities, but only exposes a cumulative household earnings difference.

Add member and household arm totals, signed differences and expected E/U/N
person-years, with explicit follow-up/calendar windows and reconciliation.
Preserve supplied scenario assumptions; add no joint distribution, causal
recovery claims, monthly dynamics or taxes/transfers.

## Acceptance

- [x] Return cumulative reference/displacement gross earnings and differences by member and household. [summary implementation](../../../src/downstream/household.py)
- [x] Return expected E/U/N person-years and explicit follow-up/calendar windows without an independence assumption. [contract and interpretation](../../../docs/HOUSEHOLD_COMPARISON_0_4.md)
- [x] Test reconciliation, null/benefit cases and meaningful validation failures. [summary contract tests](../../../tests/test_household_summary.py)
- [x] Document supported interpretation and keep broader household/comparison parents open. [scope and remaining limits](../../../docs/HOUSEHOLD_COMPARISON_0_4.md)
