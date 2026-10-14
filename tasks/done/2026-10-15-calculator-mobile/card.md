---
title: Align calculator controls and improve narrow-screen layout
area: calculator
priority: P1
assignee: codex
blocked-by: []
---

Align labels and numeric controls when text wraps. Review the calculator's narrow-screen layout and preserve its compact calculation surface.

## Acceptance

- [x] Keep numeric inputs aligned within each row, including the annual mortality rate label. [aligned labels](../../../calculator/style.css)
- [x] Keep controls and outputs usable on narrow screens; confine table overflow to its scroll container. [narrow layout](../../../calculator/style.css)
- [x] Preserve accessible names, focus and calculation behavior. [interaction checks](../../../tests/test_calculator.py)
- [x] Record code/interaction checks and actual visual checks or a concrete preview-access limit. [verification limits](../../../docs/CALCULATOR.md)
