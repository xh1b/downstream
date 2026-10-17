---
title: Qualify 0.4 normalization and consumer metadata with fixtures
area: integration
priority: P1
assignee: codex
due:
blocked-by: []
expected-paths: [src/downstream/scenario.py, tests/, validation/]
---

# Qualify 0.4 normalization and consumer metadata with fixtures

The inspected XH1B worker combines top-level point/low/high only. A synthetic
0.4 probe gives a correct mixed mortality point of 21.716, but its nested
source and alternate points remain 17.02 and 12.12 from the first county.
Weighted component points are 21.716 and 15.48. The website parser also drops
the new persistence comparison. A bundle repin alone is insufficient.

See docs/audits/xh1b_usage_plan_0_4.md and validation/xh1b_usage_inspection_20261014.json.
This is the second recommended next unit. Model-side fixtures and any needed
export contract belong here; runner, TypeScript and cache fixes belong in XH1B.
This proposal does not authorize a companion repin or deployment.

## Acceptance

- [x] Specify required output fields and scaling rules for totals, sensitivities, applicability and provenance. [contract](../../../docs/integration.md#scaling-mixtures-and-acceptance-fixtures)
- [x] Provide national, county, mixed, unsupported-place, blocked, zero and fractional consumer fixtures. [fixtures](../../../validation/consumer_fixtures_0_4.json)
- [x] Preserve child applicability, signed subgroup estimates and explicit valuation in relevant fixtures. [signed and valuation checks](../../../tests/test_consumer_fixtures.py)
- [x] Verify every combined alternative uses the same weights and inputs; never inherit first-place totals or eligibility. [mixture checks](../../../tests/test_consumer_fixtures.py)
- [x] Keep support envelopes, parameter intervals and structural comparisons distinct; do not average quantiles as joint intervals. [joint-uncertainty limits](../../../docs/integration.md#scaling-mixtures-and-acceptance-fixtures)
- [x] Record input, source, bundle and adapter identity requirements and cache invalidation expectations. [identity and cache contract](../../../docs/integration.md#scaling-mixtures-and-acceptance-fixtures)
- [x] Prepare companion acceptance steps for parsed/scaled results, explorer, HTML and Markdown parity. [companion acceptance steps](../../../docs/integration.md#scaling-mixtures-and-acceptance-fixtures)
- [x] Mark unsupported combinations unavailable and document remaining transport and dependence limits. [unavailable combinations](../../../tests/test_consumer_fixtures.py)
