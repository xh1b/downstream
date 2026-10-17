---
title: Expose current child source support and eligibility
area: children
priority: P2
assignee: mira
blocked-by: []
parent: 2026-10-14-child-heterogeneity
expected-paths: [src/downstream/child_support.py, tests/test_child_support.py, scripts/inspect_child_support.py, docs/INTEGRATION.md]
---

# Inspectable child source-support report

Parent: task:2026-10-14-child-heterogeneity. User authorized this bounded
implementation while wider evidence extraction remains open.

Expose the currently extracted child source restrictions and signed Table 8
income contrasts in a reusable report. Distinguish matched source dimensions,
unknown target inputs, known refusals and conditional transport. Do not invent
age-response curves or new country-specific evidence.

## Acceptance

- [x] Report source child age/sex, parent/event/income conditions, country and outcome window with source provenance. [structured report](../../../src/downstream/child_support.py)
- [x] Preserve signed overall/quartile estimates, source uncertainty and null-crossing intervals. [source contrast tests](../../../tests/test_child_support.py)
- [x] Test matched, unknown, refused and conditional transport states, including custom source contract refusal. [38 contract checks](../../../tests/test_child_support.py)
- [x] Document use and limits; keep the wider evidence-extraction parent open. [scope and usage](../../../docs/INTEGRATION.md#inspect-source-support)
