---
title: Expand supported mortality strata
area: mortality
priority: P1
assignee:
due:
blocked-by: []
expected-paths: []
---

# Expand supported mortality strata

## Context

Migrated from TODO entry 03, section "Next version — review follow-through (2026-10-14)", original line 44.

- **[DONE conditional path / wider admission pending] Effects by mortality stratum:** separate baseline-risk variation
from evidence of effect modification; source age/sex-compatible response profiles before expanding admissible cohorts.
Reconcile original study inclusion ages and tenure with the engine's reference-baseline age band; they must not be
conflated as one restriction. Evaluate annual aging baselines against fixed-baseline sensitivity. Compare exact
weighted-stratum aggregation with any sampled implementation. Table 7 source contrasts for male event ages 30–69 are
extracted separately from Table 5 phases. `mortality-cohort` compares exact age-band aging/fixed baselines under an
explicit constant-window-response projection. Incompatible strata remain unknown; no whole-cohort total is emitted if
coverage is partial. Single-age hazards, women/other age responses, and transport validation remain open.

## Acceptance

- [x] The sourced male age-stratum projection and aging/fixed-baseline comparison are implemented.
- [ ] Admit compatible age/sex/tenure response estimates before widening supported cohorts.
- [ ] Evaluate single-age hazards, aging baselines and target transport; retain unknown uncovered strata.
