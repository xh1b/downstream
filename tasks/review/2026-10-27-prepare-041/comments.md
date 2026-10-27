# comments

## c-45a943518dfb

- At: 2026-10-27 17:02 HKT
- By: codex-release041

Created in inbox.

## c-649968ae089f

- At: 2026-10-27 17:03 HKT
- By: codex-release041

triage: inbox -> ready.

## c-b2ee60ee2422

- At: 2026-10-27 17:03 HKT
- By: codex-release041

claim: ready -> active.

## c-3b28d9259e3c

- At: 2026-10-27 17:04 HKT
- By: codex-release041

Remaining board work is substantive research, data collection or human evaluation

Reviewed all 18 inbox/ready cards and the existing release handoff. Open work includes additional independent coefficients, expanded age/sex/source eligibility, target-cohort and matched-event bridges, mortality covariance, SIPP pooling/design uncertainty, monthly/resource models, comprehension/accessibility studies, and owner decisions on headline streams. None is a small implementation omission suitable for this source-repair patch. Existing completed subsets remain recorded without marking the broader research finished.

The concrete cleanup found was stale current release prose claiming v1.54 withdraws all sixteen inputs. The patch corrects that to six restored estimates, seven reviewed replacements and three unsupported original relationships, alongside engine version/artifact synchronization. Publication remains pending candidate-specific approval.

## c-529ad449d1ca

- At: 2026-10-27 17:12 HKT
- By: codex-release041

Candidate frozen at 1691850d70a27be5cfadf775c7a3edc9ce17b465

Engine 0.4.1 / parameters v1.54. Also reviewed all six review cards and the active parent handoff; historical receipts and ownership remain intact. Version synchronization and the stale README source statement are committed. Twelve isolated-wheel checks, audit (zero errors/warnings), ruff, vulture, make check-docs (19 tests) and the 21-page paper review pass. All 48 published consumer-fixture endpoints are unchanged.

The source was pushed solely for CI. Linux/Windows distribution combinations, Python fast tests and lint pass. Scheduled run 40478624183 at the same exact commit superseded push run 40478321662; full coverage remains pending. No release/tag/assets have been created or changed. Eleven local assets are staged for an eventual candidate-specific publication confirmation.

## c-f08e4f31403e

- At: 2026-10-27 17:19 HKT
- By: codex-release041

0.4.1 candidate qualified and sealed for publication review

Source 1691850d70a27be5cfadf775c7a3edc9ce17b465; engine 0.4.1 / parameters v1.54. Full local suite: 1,552 passed in 725.50s. Coverage 96.7% lines / 93.8% branches, twelve isolated-wheel checks, 48 unchanged consumer endpoints, zero audit errors/warnings, ruff/vulture and final documentation checks (51 documents, 615 local links, 36 examples, 19 tests) pass.

All eight release qualification jobs pass in exact-source CI run 40478624183; scheduled mutation/benchmark work is separate and its recorded status is preserved. The original push run was superseded by this scheduled run at the same SHA.

Receipt: docs/audits/release_0_4_1.md and release_0_4_1.json, committed in ab92663. Eleven local assets are sealed under build/release041-20261027/assets; manifest hashes and unchanged src/params/validation trees were rechecked. Publication is pending explicit confirmation of a stable/latest v0.4.1 release with these assets. Existing v0.4.0 and companion deployment remain unchanged.

## c-1e1cebf7237c

- At: 2026-10-27 17:19 HKT
- By: codex-release041

done: active -> review.
