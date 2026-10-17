# XH1B model-side 0.4 handoff — 2026-10-17

<!-- @ref:xh1b-handoff-2026-10-17; @tag:consumer -->
<!-- @link:code-bundle; @link:doc-consumer-fixtures-0-4; @link:code-consumer. -->

This is a local handoff of engine 0.4.0 / parameters v1.52. The
[integration contract](../integration.md#identity-and-handoff),
[consumer fixtures](../../validation/consumer_fixtures_0_4.json) and
[earlier consumer review](xh1b_usage_plan_0_4.md) define the calling and
acceptance requirements. Work history: @task:2026-10-14-xh1b-handoff.
The companion pin, database, caches, generated website and deployed pages
were not changed. Model-side readiness does not establish companion acceptance.

The [fixed-candidate qualification](release_qualification_2026-10-17.md)
identifies source revision `429af5397752a8fd4c1062b54b0835d82d2b13e4`, the
tested sdist/wheel and full comparison. Its 74-file standalone bundle verifies
as SHA-256 `6af38c54fa3131a0a5665ea034d664c64bf64152132fa7ae1f62f02fced611d2`.
The consumer fixture file SHA-256 is
`d6b29db411020f35c6c989f88878330a3bd9be070d1c1c1dc4e44e6da586e866`.
Both are retained together with exact parameter exports and raw probe results
in `build/release04-qualification-20261017/`.

## Inspection and executable probes

The existing local companion pin verifies as engine 0.3.0 / parameters v1.49,
bundle SHA-256 `bb2b77ddfb379bb71d40b91abb25658940160a679c3a22be1ac7f116f8a1a606`.
All seven database-free tests in `scripts/tests/test_downstream_release.py`
pass using the companion scraper environment. Those tests qualify its old pin;
their hardcoded versions and old child-applicability expectations require
review when moving to 0.4.

Eight synthetic direct-worker cases exercise national, county, county/national
mixture, unsupported-county fallback, synthetic reviewed transport, incompatible
population, custom mortality profile and separately supplied tradable-job loss.
The inputs, full outputs, inspected source hashes and findings are archived in
`build/release04-qualification-20261017/companion-*.json`. Synthetic transport
decisions are fixtures, never evidence of real target applicability.

The 0.4 probe preserves the default illustrative status, blocks the incompatible
female population, records a 0.3 national fallback share, and gives 16 service
jobs for 10 independently supplied tradable jobs with the manufacturing class.
A synthetic mortality transport decision qualifies mortality only. The child
output correctly stays illustrative when child ages and source-matched income
rank are absent; the existing worker does not forward those new inputs.

The known mixture defect is reproduced with current code. For 60% county 17043
and 40% national at 1,000 workers:

| Mortality field | Existing worker | Required weighted point |
| --- | ---: | ---: |
| Main expected deaths | 21.716 | 21.716 |
| Nested source-profile comparison | 17.02 | 21.716 |
| Nested no-sustained-excess comparison | 12.12 | 15.48 |

The worker scales only top-level point/low/high. Nested comparisons and signed
sensitivity must be transformed under the same exposure and place weights.
Use the engine's checked [consumer transforms](../../src/downstream/consumer.py)
and fixture expectations; retain unavailable joint intervals. A passing main
point is insufficient to accept the 0.4 consumer.

## Companion tasks

These existing cards in the sibling `xh1b` checkout own the actual integration.
Resolve their permanent IDs with `python3 scripts/tasks.py show <id>` there:

| Permanent task ID | Companion card path | Acceptance scope |
| --- | --- | --- |
| `2026-10-15-verify-downstream-0-3-0-integration-before-deployment` | `tasks/ready/2026-10-15-verify-downstream-0-3-0-integration-before-deployment/card.md` | Adapter/website fixtures, county mixtures, reviewed/blocked/custom-profile paths, DB isolation and later deployed-page checks. Its historical title names the current pin; use the candidate identity when authorizing the update. |
| `2026-10-15-recheck-downstream-cache-rows-and-scheduler-readiness` | `tasks/ready/2026-10-15-recheck-downstream-cache-rows-and-scheduler-readiness/card.md` | Per-entity current rows, stale queues, scheduler/drain readiness, preserved weights/fallback/provenance and input hashes. |
| `2026-10-15-finish-downstream-exposure-stamps-and-deployed-page-acceptance` | `tasks/ready/2026-10-15-finish-downstream-exposure-stamps-and-deployed-page-acceptance/card.md` | Exposure stamps, mixed-version handling, displayed identities and fresh page evidence. |

These cards remain open. This handoff neither approves the repin nor checks off
cache or deployment work. Preserve applicability, uncertainty scope, normalization,
source identities and fallback reasons through runner, cache, explorer, HTML and
Markdown. Include a mixture that distinguishes the nested comparison from its
first component. Keep reference-exposure interpretation and missing demographics
visible; a source response plus a local baseline does not establish target fit.

## Local integration follow-up — 2026-10-17

The local companion now selects the [corrected candidate](release_qualification_2026-10-17_interval_fix.md),
including the interval-alias repair discovered during cross-language parity.
Its adapter uses checked expected-value mixtures, preserves full-precision nested
alternatives, source records, signed sensitivity and explicit child/valuation
inputs, and keeps unavailable joint intervals unavailable. The website uses
the same scaling semantics and exposes the structural comparison records.
A content-addressed copy of the current methods HTML is linked as a readable
artifact; PDF, parameter and model-card links name the exact source revision.

Focused local model/consumer/display tests verify this preparation. These facts
supersede the earlier local-pin and adapter status above. They do not establish
remote publication, live cache freshness, served browser acceptance or deployment.
Those remain the companion's separate acceptance work.
