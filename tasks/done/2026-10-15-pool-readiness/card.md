---
title: Report coefficient compatibility and independent pool readiness
area: evidence
priority: P2
assignee: eli
parent: 2026-10-14-coefficient-library
expected-paths: [scripts/build_pool_readiness.py, tests/test_pool_readiness.py, docs/audits/POOL_READINESS_0_4.md]
blocked-by: []
---

# Report compatibility and independent pool readiness

The owner authorized a reproducible report from current source contrasts.
This child diagnoses readiness without inventing new source extractions,
precision or pooled estimates. Independent extraction remains the parent task.

## Acceptance

- [x] Preserve every current contrast, coefficient sign and null-compatible interval. [report](../../../docs/audits/POOL_READINESS_0_4.md) [tests](../../../tests/test_pool_readiness.py)
- [x] Show scale, horizon, treatment/comparison, outcome, population and subgroup compatibility/refusal reasons. [report](../../../docs/audits/POOL_READINESS_0_4.md) [tests](../../../tests/test_pool_readiness.py)
- [x] Separate same-sample overlap from declared distinct groups; do not count contrast rows as independent studies. [report](../../../docs/audits/POOL_READINESS_0_4.md) [tests](../../../tests/test_pool_readiness.py)
- [x] Produce deterministic inspectable output with source identity and a freshness check; do not pool or change model parameters. [report](../../../docs/audits/POOL_READINESS_0_4.md) [tests](../../../tests/test_pool_readiness.py)
- [x] Test admission distinctions using independent, overlapping and mismatched synthetic contrasts. [report](../../../docs/audits/POOL_READINESS_0_4.md) [tests](../../../tests/test_pool_readiness.py)
