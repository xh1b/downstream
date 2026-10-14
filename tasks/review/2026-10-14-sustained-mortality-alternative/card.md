---
title: Record the sustained-mortality alternative and source divergence
area: mortality
priority: P1
assignee:
due:
blocked-by: []
expected-paths: []
---

# Record the sustained-mortality alternative and source divergence

## Context

Migrated from TODO entry 18, section "Forward milestones", original line 169.

- **[DONE 0.4.0] Sustained-mortality alternative:** Eliason & Storrie 2009 find no statistically significant long-run
all-cause effect (5-8y HR 0.98, 9-12y 0.91, n.s., 12y follow-up) against the SvW 1.135 sustained anchor; v1.43 records
the divergence as declared notes on `earnings_shock->mortality_sustained` and never averages (CITING 5). The robustness
comparison exposes a named null-persistence assumption without changing that anchor or claiming the two studies share an
estimand. See `docs/MORTALITY_PERSISTENCE_SENSITIVITY.md`; default scenario/entity results expose the two structures and
scenario Monte Carlo uses shared draws for the contrast. Source parameters remain v1.49.

## Acceptance

- [x] Expose the named null-persistence alternative without changing the source anchor or conflating estimands.
