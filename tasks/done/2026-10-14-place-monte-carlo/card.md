---
title: Place layer in Monte Carlo, knobs and sensitivity
area: places
priority: P2
assignee:
due:
blocked-by: []
expected-paths: []
---

# Place layer in Monte Carlo, knobs and sensitivity

## Context

Migrated from TODO entry 37, section "Engine", original line 216.

- **[DONE 2026-09-09] Place layer into MC/knobs/sensitivity** — `simulate --outcome`, knob sweep/VOI, and Sobol/CI
accept `--place`; gamma is recomputed per draw. Place measurements and pooling weights remain fixed.

## Acceptance

- [x] Preserve place recomputation per draw/pin and labels for fixed place measurements. [place sampling tests](../../../tests/test_place_sampling.py)
