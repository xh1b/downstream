---
title: Expose reconciled annual household comparison summaries
area: households
priority: P2
assignee:
blocked-by: []
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

- [ ] Return cumulative reference/displacement gross earnings and differences by member and household.
- [ ] Return expected E/U/N person-years and explicit follow-up/calendar windows without an independence assumption.
- [ ] Test reconciliation, null/benefit cases and meaningful validation failures.
- [ ] Document supported interpretation and keep broader household/comparison parents open.
