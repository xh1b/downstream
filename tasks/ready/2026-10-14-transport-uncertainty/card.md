---
title: Extend uncertainty to transport and unknown dependence
area: uncertainty
priority: P2
assignee:
due:
blocked-by: []
expected-paths: []
---

# Extend uncertainty to transport and unknown dependence

## Context

Migrated from TODO entry 09, section "Next version — review follow-through (2026-10-14)", original line 103.

- **[PARTIAL / transport model pending] Uncertainty coverage:** extend beyond existing parameter Monte Carlo and
declared correlations to exposure, baseline, transport, structural and process uncertainty where a defensible joint
model exists. Keep unknown components named; do not call parameter intervals full prediction intervals. `uncertainty`
adds a metadata-matched Poisson baseline-count model, declared integer exposure distribution and independent-cohort
binomial variation; parameter-only results remain separate. Transport, structural probabilities, cross-component
dependence and earnings-profile uncertainty remain excluded.

## Acceptance

- [x] Documented baseline-count, declared exposure and independent-cohort process uncertainty are implemented.
- [ ] Specify defensible transport, structural and cross-component dependence models where evidence permits.
- [x] Keep excluded components and parameter-only intervals explicit. [uncertainty scope](../../../docs/MODEL_CARD.md) [result sensitivity contract](../../../docs/RESULT_SENSITIVITY.md)

## Release disposition — 2026-10-17

Existing conditional parameter intervals, structural comparisons and the
qualified extended budget can ship with their stated exclusions. New transport
probabilities and dependence models need evidence or reviewed declarations;
zero-filled errors or invented weights do not close this task. Scope review:
@task:2026-10-17-release-task-review.
