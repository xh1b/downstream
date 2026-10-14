---
title: Bound published additive mortality phase uncertainty without invented covariance
area: mortality
priority: P2
assignee:
blocked-by: []
---

Child of task:2026-10-14-published-mortality-profile. Implement a diagnostic for linear phase totals and unknown coefficient covariance, keeping published additive coefficients separate from working-paper odds phases. No model admission or core/default/CLI changes.

## Acceptance

- [ ] Validate component contracts and compute sharp PSD-compatible phase-total standard-error bounds.
- [ ] Record available source coefficients/SEs or label illustrative inputs and unresolved extraction gap; never invent covariance.
- [ ] Test analytic extrema, invalid inputs and missing-SE behavior.
- [ ] Document interpretation, reproducible diagnostic command and remaining parent blocker.
