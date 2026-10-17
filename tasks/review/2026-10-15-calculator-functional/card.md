---
title: Refactor calculator into pure calculation and focused rendering functions
area: calculator
priority: P2
assignee: codex
blocked-by: []
---

Make the calculator JavaScript easier to read and audit without changing its equations, receipt schema or user controls.

## Acceptance

- [x] Express phase timing, odds replacement, sensitivity and curve calculations as pure functions. [math](../../../calculator/math.js)
- [x] Keep DOM effects in focused UI functions; remove redundant mutable preset/result state and duplicate input validation. [UI](../../../calculator/app.js)
- [x] Verify native-engine parity, mathematical invariants, input immutability and existing interactions. [tests](../../../tests/test_calculator.py) [receipt](task:2026-10-15-calculator-functional#c-0896c66eca98)
- [x] Document the calculation flow and numerical-stability choices; rebuild the app and check it in the browser. [explanation](../../../docs/calculator.md#code-structure) [browser receipt](task:2026-10-15-calculator-functional#c-0896c66eca98)
