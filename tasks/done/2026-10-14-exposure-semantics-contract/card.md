---
title: Specify exposure semantics for conditional consequence estimates
area: integration
priority: P1
assignee: eli
due:
blocked-by: []
expected-paths: [src/downstream/employer.py, src/downstream/scenario.py]
---

# Specify exposure semantics for conditional consequence estimates

The XH1B usage review finds that its exposure adds requested-position, wage-gap
and matched-layoff terms across filing history. It is not unique displaced
people or worker-years. Current reference scaling is a scenario convention;
a target-specific causal conversion remains unestablished.

See docs/audits/XH1B_USAGE_PLAN_0_4.md and validation/xh1b_usage_inspection_20261014.json.
This is the first recommended next unit. Preserve caller ownership of exposure
inference. Coordinate with 2026-10-14-target-displaced-cohort without claiming
that a metadata contract itself supplies the missing empirical bridge.

## Acceptance

- [x] Specify exposure kind, components, method version, record window and overlap limits. [contract](../../../docs/INTEGRATION.md#exposure-and-event-metadata) [tests](../../../tests/test_exposure_semantics.py)
- [x] Preserve supplied conversion assumptions and distinguish reference equivalents from an admitted cohort. [contract](../../../docs/INTEGRATION.md#exposure-and-event-metadata) [tests](../../../tests/test_exposure_semantics.py)
- [x] Define event-time requirements; historical sums cannot silently become calendar-specific forecasts. [contract](../../../docs/INTEGRATION.md#exposure-and-event-metadata) [tests](../../../tests/test_exposure_semantics.py)
- [x] Keep missing demographics and family composition unknown; generic CPS is not an H-1B bridge. [contract](../../../docs/INTEGRATION.md#exposure-and-event-metadata) [tests](../../../tests/test_exposure_semantics.py)
- [x] Define fractional reference scaling separately from integer-cohort process uncertainty. [contract](../../../docs/INTEGRATION.md#exposure-and-event-metadata) [tests](../../../tests/test_exposure_semantics.py)
- [x] Add meaningful contract checks and documentation without changing the companion exposure formula. [contract](../../../docs/INTEGRATION.md#exposure-and-event-metadata) [tests](../../../tests/test_exposure_semantics.py)
