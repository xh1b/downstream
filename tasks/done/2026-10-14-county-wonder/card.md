---
title: County WONDER mortality integration
area: mortality
priority: P2
assignee:
due:
blocked-by: []
expected-paths: []
---

# County WONDER mortality integration

## Context

Migrated from TODO entry 32, section "Engine", original line 211.

- **[DONE 2026-09-13] #31: county WONDER mortality** — export landed via `scripts/fetch_wonder.py county` (web-UI
session; the machine XML API is national-only); v1.36 wired the strict Gamma–Poisson posteriors into the place layer,
and v1.41 fills the generated places.csv plug columns (shrunk posterior mean + person-years precision label) in the same
build-places pass.

## Acceptance

- [x] Record the county export, strict posteriors and generated place-layer integration. [county integration tests](../../../tests/test_county_rates.py) [county likelihood tests](../../../tests/test_county_mortality.py)
