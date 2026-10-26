---
title: Retain the declared county-mortality prior strength
area: mortality
priority: P2
assignee:
due:
blocked-by: []
expected-paths: []
---

# Retain the declared county-mortality prior strength

## Context

Migrated from TODO entry 17, section "Forward milestones", original line 157.

- **[DECIDED 2026-09-14] County-mortality prior strength:** the DECLARED k = 2000 prior person-years stays the shipped
pooling strength. The method-of-moments empirical-Bayes yardstick (k ≈ 822 on the male 45-54 export; Poisson noise ≈ 11%
of the county spread; Gamma shape ≈ 4.1) is recorded and reproducible (`build_county_mortality.py --estimate-prior-k`,
`tests/test_county_eb_prior.py`) but is NOT adopted: it is the less conservative direction, it assumes iid Gamma county
effects (no spatial correlation), and it rests on one export over one window. Revisit: rerun the flag as more
cause/sex/window exports land; adopting would rewrite all 2,748 posteriors and the v1.41 build-places places.csv columns
that key off k = 2000, so it needs an explicit fresh decision. (`docs/audits/data_sources.md` county row.)

## Acceptance

- [x] Record the k=2000 decision and the conditions for reconsidering the empirical-Bayes yardstick. [decision and limitations](../../../docs/audits/data_sources.md) [prior diagnostic](../../../tests/test_county_eb_prior.py)
