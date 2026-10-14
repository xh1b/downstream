# comments

## c-df0d0a00cf51

- At: 2026-10-15 01:46 HKT
- By: eli

Created in inbox.

## c-3b78b9c08b8f

- At: 2026-10-15 01:46 HKT
- By: eli

triage: inbox -> ready.

## c-1158d26d2778

- At: 2026-10-15 01:46 HKT
- By: eli

claim: ready -> active.

## c-32cc25e105ae

- At: 2026-10-15 02:01 HKT
- By: eli

Source repair d8f1bc8; adapter/CLI ccb34d9. [Contract](../../../docs/RECEIVING_COMMUNITY_0_4.md), [source-unit receipt](../../../validation/receiving_source_units_20261015.json), [regressions](../../../tests/test_receiving_adapter.py). Original Light–Miller hash matches; b=-.12 SE=.03 is semi-log per percentage-point share. Bianchi mirror b=.105 SE=.187 is log valid-residence-permit share; canonical working-paper tier and published reconciliation queued. Engine0.4.0/paramsv1.52. All typed paths preserve unchanged coefficients, population denominators, signs/null support, caller identity, unavailable count states, source-specific FE/IV roles and unchanged-residual retransformation assumption; old stock links refuse migration. Affected version/source tests321 passed in6.52s; focused adapter/CLI/employer/ledger/params/evidence90 passed in0.60s; Ruff clean; audit0errors/0warnings. Root owns final generated-artifact refresh and full release qualification. Parent task:2026-10-14-full-comparison remains open.

## c-4e934534976d

- At: 2026-10-15 02:01 HKT
- By: eli

done: active -> review.

## c-534cbcbde3ce

- At: 2026-10-15 02:06 HKT
- By: codex

request-changes: review -> active.

Independent review found Bianchi log(post)-log(reference) cancels adjacent signed share changes to zero. Use stable log1p near equal shares with an extreme-ratio fallback and add positive/negative adjacent-share regressions before acceptance.

## c-95236bc63207

- At: 2026-10-15 02:07 HKT
- By: eli

Fixed independently reproduced Bianchi cancellation: bounded near-equal share differences now use log1p((post-reference)/reference); extreme ratios retain safe log subtraction. Positive and negative adjacent-share regressions use independent 80-digit Decimal reference calculations, strict relative/no absolute tolerances, and test native plus CLI signed rate/count changes. Smallest-positive-float extreme-ratio checks preserve finite fallback behavior. [Tests](../../../tests/test_receiving_adapter.py). Receiving/source suite46 passed in1.60s; Ruff clean. No parameter version/value changes.

## c-7b2e6f53e079

- At: 2026-10-15 02:07 HKT
- By: eli

done: active -> review.

## c-95d647f84657

- At: 2026-10-15 02:08 HKT
- By: fenix

Independent code/source-unit review approves the corrected adapter. Re-ran 46 focused adapter/source-chain checks successfully. Near-equal Bianchi shares now use bounded log1p; positive and negative nextafter cases match 80-digit Decimal references in native and CLI outputs, while minimum-positive-share extremes retain a finite log-difference fallback. The earlier false-null precision finding is resolved. Verified local primary PDF hashes against the unit receipt and source definitions: Light uses percentage-point undocumented share with logged crime rate; Bianchi uses log valid-permit population share. Signed support, same post-population endpoint counts, causal-role/window/retransformation disclosures and retired-stock-link refusals remain intact. Acceptance does not establish H-1B/target transport, resolve published Bianchi source-version reconciliation or complete other receiving-community channels.

## c-bfddf2cae8a2

- At: 2026-10-15 02:08 HKT
- By: fenix

accept: review -> done.
