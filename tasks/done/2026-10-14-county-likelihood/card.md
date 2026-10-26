---
title: County likelihood and national fallback
area: mortality
priority: P2
assignee:
due:
blocked-by: []
expected-paths: []
---

# County likelihood and national fallback

## Context

Migrated from TODO entry 44, section "Review priorities — 2026-09-10", original line 238.

- **[DONE 2026-09-13] County likelihood:** Gamma--Poisson estimation and strict national-prior metadata; v1.36 completed
extraction #31 (validated county export with matching outcome/population/window metadata) and wired the posteriors into
the place layer end to end; v1.41 also fills the generated places.csv mortality_rate/mortality_n columns (posterior mean
+ person-years precision label) in the same build-places pass, keeping suppressed/absent counties on the national
fallback.

## Acceptance

- [x] Preserve verified county likelihood metadata, pooled place integration and fallback provenance. [county likelihood tests](../../../tests/test_county_mortality.py) [place integration](../../../tests/test_county_rates.py)
