---
title: Adversarial lifecycle and V2 branch tests
area: quality
priority: P2
assignee:
due:
blocked-by: []
expected-paths: []
---

# Adversarial lifecycle and V2 branch tests

## Context

Migrated from TODO entry 27, section "Engine", original line 205.

- **[DONE 2026-09-09] Adversarial lifecycle and V2 branch tests** — Hypothesis state machines cover immutable forecast
registration and transactional bundle export/verification/tampering. Synthetic V2 fixtures cover valid scorecard
creation and malformed bridge/outcome refusals; count endpoints accept both signed-loss and positive-count conventions.

## Acceptance

- [x] Preserve forecast-registry, bundle-lifecycle and V2 fixture receipts. [forecast state machine](../../../tests/test_forecast_fsm.py) [bundle state machine](../../../tests/test_bundle_fsm.py) [V2 fixtures](../../../tests/test_v2_backtest.py)
