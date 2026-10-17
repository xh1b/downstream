---
title: Review mortality applicability before admitting other strata
area: mortality
priority: P1
assignee: mira
due:
blocked-by: []
expected-paths: [src/downstream/mortality_strata.py, tests/test_mortality_admission_0_4.py, docs/audits/mortality_applicability_0_4.md]
---

# Review mortality applicability before admitting other strata

## Context

Migrated from TODO entry 42, section "Review priorities — 2026-09-10", original line 233.

- **[P1] Mortality applicability:** demographic profile selection now refuses sex/age mismatch with the male 45--54
causal response. Adding other strata requires separately admitted effect estimates, not only new baseline rates.

## Acceptance

- [x] Require separately admitted compatible response estimates for demographic expansion. [source-contract and baseline-gate tests](../../../tests/test_mortality_admission_0_4.py)
- [x] Review the new conditional mortality-stratum path without treating baseline variation as effect modification. [review and scope](../../../docs/audits/mortality_applicability_0_4.md)

## Outcome

Existing age/sex/tenure/event gates and separate Table 7 age-contrast admission
are retained. The source treatment/comparator contract is now enforced, and
each supported stratum carries conditional scope and remaining transport
assumptions. No new effects, strata or numerical defaults are admitted.
