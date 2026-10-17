---
title: Define the target displaced cohort
area: cohorts
priority: P1
assignee:
due:
blocked-by: []
expected-paths: []
---

# Define the target displaced cohort

## Context

Migrated from TODO entry 02, section "Next version — review follow-through (2026-10-14)", original line 35.

- **[DONE reference / target-specific bridge pending] Define the displaced cohort:** pin survey release, weighted
inclusion rules, age, sex, tenure, industry, earnings and family structure; distinguish generic displacement from any
H-1B-specific exposure bridge. Reproduce weighted cohort summaries before individual simulation. The review's 31.8
deaths per 1,000 remains unverified without its data/code. Implemented CPS January-2024 known-year >=3/6-year-tenure
reference summaries, with source hashes and BLS total reproduction (2,578,128 versus published rounded 2,578,000).
Interview age/family structure are not relabeled as historical event characteristics.
`scripts/build_displaced_cohort.py`.

## Acceptance

- [x] Weighted CPS reference cohorts and BLS total reproduction are implemented.
- [ ] Document a target-specific displacement bridge and demographic composition with provenance.
- [x] Keep generic CPS references distinct from H-1B-specific exposures. [exposure and cohort contract](../../../docs/EXPOSURE_SEMANTICS_0_4.md)

## Release disposition — 2026-10-17

The reference-only contract is implemented; a target-specific bridge is still
an empirical dependency. Missing demographics and event timing remain unknown.
Do not block a clearly labeled reference-scenario release on a fabricated bridge,
or promote it to identified H-1B consequences. Scope review:
@task:2026-10-17-release-task-review.
