---
title: Attach input sensitivity reports to scenario results
area: uncertainty
priority: P1
assignee: codex
due:
blocked-by: []
expected-paths: [src/downstream/scenario.py, src/downstream/result_sensitivity.py, tests/test_result_sensitivity.py]
---

# Attach input sensitivity reports to scenario results

Owner requested a task and implementation of a complete sensitivity report,
rather than a special comparison for only sustained mortality. Start with
scenario count results and their entity, policy and valuation consumers.
Retain engine 0.4.0. Companion website changes remain a separate handoff.

## Acceptance

- [ ] Attach per-outcome effect-removal and supported-endpoint experiments with values, sources and signed changes.
- [ ] Preserve nonlinear interactions, subgroup selection, place inputs, fixed baselines and blocked outcomes.
- [ ] Identify fixed inputs and unavailable ranges without inventing uncertainty distributions.
- [ ] Offer correlation-aware parameter variance attribution separately from deterministic sensitivity.
- [ ] Exercise CLI, scenario, entity and valuation delivery; document exclusions and consumer scaling requirements.
- [ ] Run numerical, regression and quality checks and retain a reproducible example.
