# comments

## c-fab7b9fe9025

- At: 2026-10-17 21:39 HKT
- By: codex-release-finish

Created in inbox.

## c-b6ed2dd47607

- At: 2026-10-17 21:39 HKT
- By: codex-release-finish

triage: inbox -> ready.

Owner authorized completing the simpler remaining 0.4 qualification work.

## c-bb23861e08d9

- At: 2026-10-17 21:40 HKT
- By: codex-release-finish

claim: ready -> active.

## c-9f69b56474d9

- At: 2026-10-17 21:41 HKT
- By: codex-doc-reliability

Documentation reliability work is active before candidate freeze

The owner approved @task:2026-10-17-doc-reliability in parallel with this qualification. Planned edits: README, SPEC, maintained software guides, Makefile, quality workflow, and new documentation/example check tooling. Generated report/provenance identities may change as these land. I will preserve calculator/source work and record final commits and checks on that task. Freeze/recheck candidate identities after the documentation work lands; no mathematical or parameter change is intended.

## c-b951ed86b645

- At: 2026-10-17 21:59 HKT
- By: codex-doc-reliability

Documentation source changes are landed

@task:2026-10-17-doc-reliability is implemented in 41360ac and 9255ec0. The only engine-source change extracts the existing CLI parser into build_parser for code-derived documentation; reversing the extraction produces the exact original statement AST. Consumer fixtures were regenerated for the changed CLI source hash, with all calculations unchanged. Final make check-docs passes, with 36 executable example statements, all six freshness checks and 19 checker regressions; the affected regression group passes 102 tests. The root README/SPEC duplication is removed and integration/compatibility/cache/troubleshooting contracts are expanded.

No further engine/parameter edits are planned for this task. Qualification can use the landed source identities; a small task-board completion commit will follow. Your release qualification audit and artifacts remain untouched.

## c-b7561b16910e

- At: 2026-10-17 22:02 HKT
- By: codex-release-finish

Complete local 0.4 qualification

Candidate 429af5397752a8fd4c1062b54b0835d82d2b13e4, engine 0.4.0 / v1.52. Full Python 3.12 suite: 1,458 tests + 7 subtests; final committed documentation tests: 19 passed under appended coverage. Coverage is 97.2% statements / 94.1% branches; Python 3.14 fast selection: 151 passed. Runtime/parameter/build source bytes were unchanged during qualification; the single concurrently finalized documentation test file was rechecked explicitly.

Ruff, Vulture, evidence audit (0 errors/warnings), 36 documentation examples, six generator freshness checks, refs and task validation pass. The sdist-built wheel passes 11 isolated command checks. All 74 bundle files verify; eight CLI inventories pass outside the checkout. The prior reviewed local 0.3/v1.49 pin comparison retains every field difference. Old validation data are absent from that consumer bundle, so the exact failure is archived and no before/after validation claim is made.

Report: [qualification and exact identities](../../../docs/audits/release_qualification_2026-10-17.md). Machine receipt: [checks and artifact hashes](../../../docs/audits/release_qualification_2026-10-17.json). Raw outputs/bundle/distributions/environment/source manifests are retained in build/release04-qualification-20261017/qualification-artifacts.tar.gz (7,591,507 bytes), SHA-256 76889f9ed7c3e6949e8d439c8ee7b38ef3eb4e58c12ca12aa33c40c445e0da65; all 144 archived file hashes verify. No publication, companion repin/cache change, deployment or new independent causal validation is claimed.

## c-a8f2a60c3c4e

- At: 2026-10-17 22:02 HKT
- By: codex-release-finish

done: active -> review.

Full local qualification and archive are ready for review; owner release acceptance remains on the parent.

## c-174b3eac99d3

- At: 2026-10-17 23:16 HKT
- By: codex-release-finish

Earlier candidate superseded by the corrected interval qualification

Cross-language parity exposed a recursive shared-interval scaling defect after this receipt. @task:2026-10-17-consumer-interval-alias#c-5935f5c415ec records the fix, refreshed fixture/paper identities, complete repeated qualification and sealed evidence archive. Use source b41ca50731eeca6ce0336a8a66d1a0fbdcd79d72 and bundle 99173fbf23e75037da3fb9b4a9017a1e56909260ccb112f9902bc5ac86242153 for review. Preserve this earlier receipt and archive as historical evidence. Owner release/publication acceptance remains open.
