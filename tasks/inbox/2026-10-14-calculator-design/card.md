---
title: W0-W3 - Design and comprehension-test the calculator
area: calculator
priority: P3
assignee:
due:
blocked-by: []
expected-paths: []
---

# W0-W3 - Design and comprehension-test the calculator

## Context

Migrated from TODO entry 14, section "Forward milestones", original line 150.

- **[W0-W3] Calculator design:** research useful questions, write the explanation first, compare two visual directions,
and test comprehension with fictional or explicitly limited examples before scientific release readiness.

## Current scope — 2026-10-17

The [prototype comparison](@task:2026-10-15-calculator-prototype),
[minimal calculator](@task:2026-10-15-calculator-rebuild) and
[responsive layout](@task:2026-10-15-calculator-mobile) are implemented.
The local HTTP browser checks cover 320/390/600/1440 px; they do not establish
physical-device, zoom, assistive-technology or participant results.
Keep the [existing 6–8-user protocol](../../../docs/calculator.md) and test the
current chosen surface instead of commissioning another visual redesign.
Scope review: @task:2026-10-17-release-task-review.

## Acceptance

- [x] Compare two inspectable directions and implement the chosen compact calculation surface. [prototype](@task:2026-10-15-calculator-prototype) [chosen surface](@task:2026-10-15-calculator-rebuild)
- [ ] Test intended users' questions and comprehension with fictional or explicitly limited examples; record unaided errors and revisions.
- [x] Verify keyboard navigation, accessible names, validation and zoom-equivalent reflow on the current surface. [2026-10-17 browser audit](../../../docs/audits/calculator_accessibility_2026-10-17.md)
- [ ] Complete actual native-browser zoom, screen-reader and physical-device checks before claiming those forms of accessibility or public readiness.

Keyboard and reflow follow-up: @task:2026-10-17-calculator-accessibility.
The 640 CSS-pixel check is equivalent reflow from a 1280 px viewport at 200%;
it does not claim an actual native zoom or screen-reader test.
