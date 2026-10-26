# comments

## c-5203ac9d90aa

- At: 2026-10-17 22:46 HKT
- By: codex-release-finish

Created in inbox.

## c-9c93de1e0934

- At: 2026-10-17 22:47 HKT
- By: codex-release-finish

triage: inbox -> ready.

Confirmed Python/TypeScript fixture mismatch identifies repeated scaling of the same shared interval object.

## c-1c02146c7ac8

- At: 2026-10-17 22:47 HKT
- By: codex-release-finish

claim: ready -> active.

## c-5935f5c415ec

- At: 2026-10-17 23:15 HKT
- By: codex-release-finish

Corrected candidate qualified and companion parity verified

Implementation 51095ed detaches a shared top-level interval before recursive scaling. The real-object five-factor regression failed in three nontrivial cases before repair and passes after it; the source remains unchanged. No coefficient, default point or parameter version changes. Consumer fixtures change twelve nested interval moments plus two identities; 8,698 fields are unchanged. Paper provenance was rebuilt and inspected in b41ca50.

The corrected fixed source is b41ca50731eeca6ce0336a8a66d1a0fbdcd79d72, bundle SHA 99173fbf23e75037da3fb9b4a9017a1e56909260ccb112f9902bc5ac86242153 and fixture SHA 94cbc165a7106d523d426330b6a2314b5f9ba3fd839c7d98d425ab64aea1147a. All 295 recorded source/test/data/build inputs still match the qualification manifest. Full suite: 1,463 tests plus 7 subtests; statement/branch coverage 97.2%/94.1%; Python 3.14 focused selection: 197 pass. Audit, Ruff, Vulture, generators, documentation examples, refs/tasks, eleven isolated installed-wheel checks and eight standalone inventories pass. The latter eight outputs are identical to the earlier 0.4 candidate.

[Corrected qualification](../../../docs/audits/release_qualification_2026-10-17_interval_fix.md) and [machine receipt](../../../docs/audits/release_qualification_2026-10-17_interval_fix.json) are committed in f56ace0. The new archive SHA is e82f05458cf49122b8de7fe894c691d9c464084dc5f443c25f7ef7f6f43d0a10, with all 146 evidence files verified. The previous sealed archive is retained unchanged and marked superseded.

The local companion selects the corrected bundle and fixtures. Its Python and TypeScript scaling regressions verify fractional, zero, reference and large exposures, preserved source metadata, signed alternatives and the shared-object case. Local integration/display tests pass; the handoff follow-up records preparation without claiming live cache, browser or deployment acceptance. Owner publication and independent review remain separate.

## c-b46befe54790

- At: 2026-10-17 23:16 HKT
- By: codex-release-finish

done: active -> review.

Submit corrected interval scaling, superseding qualification and local consumer parity for independent review.
