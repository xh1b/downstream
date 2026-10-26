---
title: Math corrections for engine 0.2.0 / parameters v1.34
area: engine
priority: P1
assignee:
due:
blocked-by: []
expected-paths: []
---

# Math corrections for engine 0.2.0 / parameters v1.34

## Context

Migrated from TODO entry 22, section "Engine", original line 200.

- **[DONE 2026-09-09] Math corrections, engine 0.2.0 / parameters v1.34** — odds-to-risk mortality and survival, one
initial place adjustment, signed interval corners, clamped normal/lognormal moments, and refusal of reused uncertain
parameters under independent-step inference. Legacy scenario methods remain selectable.

## Acceptance

- [x] Preserve the documented odds-to-risk, survival, ledger and interval corrections. [mathematical regressions](../../../tests/test_mathematics_v02.py)
