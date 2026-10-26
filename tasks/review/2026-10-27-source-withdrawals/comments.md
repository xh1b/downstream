# comments

## c-30ac1857fe3b

- At: 2026-10-27 06:59 HKT
- By: John Larue

Created in inbox.

## c-7a569f1efdfa

- At: 2026-10-27 06:59 HKT
- By: John Larue

triage: inbox -> ready.

## c-484cf5163e27

- At: 2026-10-27 06:59 HKT
- By: codex-source-repair

claim: ready -> active.

## c-f5e22e126ff7

- At: 2026-10-27 07:38 HKT
- By: codex-source-repair

All 16 withdrawn inputs are blocked while original records remain intact

Commit 6575700 introduces parameter set v1.53 and [source policy](../../../params/source_support.json): seven public source mismatches, nine unverified extractions, their provenance and reasons. Original parameters.csv and references.bib remain byte-identical to d7691da. Snapshots use schema 3 with 51 available records and 16 separately archived records; unresolved reference identities are explicitly archived.

The engine refuses withdrawn links in ledger/API/CLI calculations, sampling, custom overrides and dependent transmissions. Grouped results return explicit unavailable branches. Great-grandchild earnings and the additive divorce/family-size variant are unavailable. Forty-eight supported mortality/direct-child fixture point/low/high endpoints remain unchanged from the pre-withdrawal uncertainty implementation. Bundle identity: d4e7a217741a237ed61c77e6c3700427201ac428b2c890212fe951305ef20227.

Tests: [source withdrawals](../../../tests/test_source_withdrawals.py), [consumer fixtures](../../../tests/test_consumer_fixtures.py). Contract: [evidence](../../../docs/evidence.md#source-withdrawals-and-retained-records). Local full suite: 1,526 tests plus 9 subtests, coverage 96.8% lines/94.0% branches, evidence audit zero errors/warnings. Final a1f54ad source adds a shallow-checkout-safe digest test (22 source checks pass) and corrected paper narrative (32 paper/artifact/release checks pass), with no runtime/data changes from the full-suite candidate. The final source-built wheel passes all eleven isolated CLI checks; paper and HTML rebuilt, changed pages visually reviewed, no LaTeX warnings or overfull boxes. Exact CI/publication receipts follow on @task:2026-10-27-publish-04.

## c-aa36046919f3

- At: 2026-10-27 07:38 HKT
- By: codex-source-repair

done: active -> review.

All source withdrawals implemented and qualified; publication tracked separately.
