---
title: Refactor calculator into pure calculation and focused rendering functions
area: calculator
priority: P2
assignee:
blocked-by: []
---

Make the calculator JavaScript easier to read and audit without changing its equations, receipt schema or user controls.

## Acceptance

- [ ] Express phase timing, odds replacement, sensitivity and curve calculations as pure functions.
- [ ] Keep DOM effects in focused UI functions; remove redundant mutable preset/result state and duplicate input validation.
- [ ] Verify native-engine parity, mathematical invariants, input immutability and existing interactions.
- [ ] Document the calculation flow and numerical-stability choices; rebuild the app and check it in the browser.
