---
title: Attach input sensitivity reports to scenario results
area: uncertainty
priority: P1
assignee: codex
due:
blocked-by: []
related-to: [2026-10-14-consumer-contract-fixtures]
expected-paths: [src/downstream/scenario.py, src/downstream/result_sensitivity.py, tests/test_result_sensitivity.py]
---

# Attach input sensitivity reports to scenario results

Owner requested a task and implementation of a complete sensitivity report,
rather than a special comparison for only sustained mortality. Start with
scenario count results and their entity, policy and valuation consumers.
Retain engine 0.4.0. Companion website changes remain a separate handoff.

## Acceptance

- [x] Attach per-outcome effect-removal and supported-endpoint experiments with values, sources and signed changes. [evidence](../../../validation/result_sensitivity_reference_20261015.json)
- [x] Preserve nonlinear interactions, subgroup selection, place inputs, fixed baselines and blocked outcomes. [evidence](../../../tests/test_result_sensitivity.py)
- [x] Identify fixed inputs and unavailable ranges without inventing uncertainty distributions. [evidence](../../../docs/INTEGRATION.md#per-result-sensitivity)
- [x] Offer correlation-aware parameter variance attribution separately from deterministic sensitivity. [evidence](../../../src/downstream/result_sensitivity.py)
- [x] Exercise CLI, scenario, entity and valuation delivery; document exclusions and consumer scaling requirements. [evidence](../../../docs/INTEGRATION.md#per-result-sensitivity)
- [x] Run numerical, regression and quality checks and retain a reproducible example. [evidence](../../../docs/INTEGRATION.md#per-result-sensitivity)
