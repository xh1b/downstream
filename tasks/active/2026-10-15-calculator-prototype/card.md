---
title: Build two inspectable calculator prototype directions
area: calculator
priority: P2
assignee: fenix
blocked-by: []
---

Build an inspectable local calculator prototype using current engine results.
This is the implementable part of task:2026-10-14-calculator-design.
Human comprehension research stays on that parent task.

## Acceptance

- [x] Provide two selectable visual directions with editable exposure and clear comparison, units and horizons. [prototype](../../../examples/calculator/index.html)
- [x] Use generated engine data; preserve sensitivity, source versions, applicability and unavailable paths. [generator](../../../scripts/build_calculator_prototype.py)
- [x] Provide keyboard/mobile-friendly controls and a reproducible build/check command. [implementation and remaining manual review](../../../docs/CALCULATOR_PROTOTYPE.md)
- [x] Record automated or browser checks and a concrete human comprehension-test protocol without fabricating participants. [automated checks](../../../tests/test_calculator_prototype.py) [protocol and browser limitation](../../../docs/CALCULATOR_PROTOTYPE.md)
