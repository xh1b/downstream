# comments

## c-e7b7ac4f15df

- At: 2026-10-17 21:39 HKT
- By: codex-release-finish

Created in inbox.

## c-2415a4b67734

- At: 2026-10-17 21:39 HKT
- By: codex-release-finish

triage: inbox -> ready.

Owner authorized the remaining simpler local 0.4 work; this is the executable portion of the calculator-design parent.

## c-169aae0a3760

- At: 2026-10-17 21:39 HKT
- By: codex-release-finish

claim: ready -> active.

## c-0cb10615c09c

- At: 2026-10-17 21:46 HKT
- By: codex-release-finish

Keyboard and reflow checks complete; accessible names repaired

The audit at docs/audits/calculator_accessibility_2026-10-17.md records all 19 keyboard stops, skip-link focus, scenario/reset actions, fractional exposure, invalid-result retention, narrow-table keyboard scrolling, accessible names and a screenshot. All 18 calculator/server tests and Node syntax checks pass. At 640 CSS px (200%-reflow equivalent from 1280) and 320 px there is no page-wide overflow. Native zoom shortcut did not alter this in-app browser; actual native zoom, screen-reader announcements, physical devices and participant research remain open.

Global refcheck currently reports two dangling links from concurrent documentation edits to the other agent’s not-yet-tracked checker/test, and global diff whitespace checking flags their SPEC.md. Own-path checks pass. Those foreign paths are preserved and will be rechecked after @task:2026-10-17-doc-reliability commits.
