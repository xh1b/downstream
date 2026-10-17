---
title: Rebuild calculator as a minimal calculation surface
area: calculator
priority: P1
assignee: codex
blocked-by: []
---

Build a minimal technical calculator with numeric inputs, equations and output tables.
Related design work: task:2026-10-14-calculator-design.

## Acceptance

- [x] Replace the prose-led layout with one compact calculation surface and source details on demand. [surface](../../../calculator/template.html)
- [x] Add real calculation controls for mortality timing/risks and child loss assumptions; preserve units and source/reference differences. [equations](../../../calculator/math.js)
- [x] Verify browser formulas against native engine calculations at varied inputs, including zero and fractional exposure. [native refit and interaction checks](../../../tests/test_calculator.py)
- [x] Use short, direct necessary text based on ASD-STE100; keep technical names and explicit interval meanings. [language and method](../../../docs/calculator.md)
- [x] Record checks and the remaining visual/human review limits. [verification limits](../../../docs/calculator.md)
