---
title: Extend household dynamics beyond the annual prototype
area: households
priority: P2
assignee:
due:
blocked-by: []
expected-paths: []
---

# Extend household dynamics beyond the annual prototype

## Context

Migrated from TODO entry 07, section "Next version — review follow-through (2026-10-14)", original line 85.

- **[DONE annual prototype / monthly and joint model pending] Household dynamics and displacement duration:** build on
R2 SIPP transitions, linked households, recovery, partner resources and child ages. Distinguish baseline transitions
from causal event responses and prevent double counting. Joint outcomes need evidenced/declared dependence;
microsimulation alone does not identify it. `household` advances supported E/U/N probabilities, linked adult gross
earnings and child ages under a supplied unemployment duration. Sparse cells require explicit acceptance; observational
recovery is not a causal displacement response. Taxes/transfers, monthly timing, replicate-weight intervals, membership
changes and joint outcomes remain open.

## Acceptance

- [x] The annual SIPP employment/gross-earnings prototype is implemented.
- [ ] Add supported monthly timing, recovery and household-resource components with explicit dependence.
- [ ] Estimate survey-design uncertainty and membership changes; avoid double counting.
