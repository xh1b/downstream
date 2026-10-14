---
title: Bound published additive mortality phase uncertainty without invented covariance
area: mortality
priority: P2
assignee: fenix
blocked-by: []
parent: 2026-10-14-published-mortality-profile
---

Child of task:2026-10-14-published-mortality-profile. Implement a diagnostic for linear phase totals and unknown coefficient covariance, keeping published additive coefficients separate from working-paper odds phases. No model admission or core/default/CLI changes.

## Acceptance

- [x] Validate component contracts and compute sharp PSD-compatible phase-total standard-error bounds. [implementation](../../../src/downstream/mortality_covariance.py)
- [x] Record available source coefficients/SEs or label illustrative inputs and unresolved extraction gap; never invent covariance. [manuscript locator and transcription](../../../docs/MORTALITY_COVARIANCE_0_4.md)
- [x] Test analytic extrema, invalid inputs and missing-SE behavior. [33 focused checks](../../../tests/test_mortality_covariance.py)
- [x] Document interpretation, reproducible diagnostic command and remaining parent blocker. [diagnostic scope](../../../docs/MORTALITY_COVARIANCE_0_4.md) [report command](../../../scripts/analyze_mortality_covariance.py)
