# Corrected 0.4 qualification — 2026-10-17

<!-- @ref:release-qualification-interval-fix-2026-10-17; @tag:release -->
<!-- @link:code-consumer; @link:test-consumer-api; @link:doc-consumer-fixtures-0-4; @link:doc-open-source-release. -->

**Use this candidate instead of the earlier October 17 bundle.** Engine
0.4.0 / parameters v1.52, source commit
`b41ca50731eeca6ce0336a8a66d1a0fbdcd79d72`, bundle content SHA-256
`99173fbf23e75037da3fb9b4a9017a1e56909260ccb112f9902bc5ac86242153`.
The [previous qualification](release_qualification_2026-10-17.md) and its sealed
archive remain historical receipts. Work: @task:2026-10-17-consumer-interval-alias.

## Repair and evidence

Cross-language fixture parity exposed a shared-object bug in
[consumer scaling](../../src/downstream/consumer.py): the sampled main mortality
interval and its source-profile alternative can reference the same dictionary.
Deep-copying the result preserves that alias. Scaling the main interval before
recursing into the alternative therefore scaled the alternative twice.
The repair detaches the main interval before scaling. The input remains intact,
and both representations of the same interval now scale exactly once.

The new five-case regression failed at three nontrivial factors before the fix;
zero and one masked the defect. All 46 focused consumer/API tests pass after
repair. The refreshed consumer fixtures change exactly **12 nested interval
moments and two content identities**. All other 8,698 flattened fields remain
unchanged. No source coefficient, default point, applicability gate or model
parameter version changes.

## Qualification

| Check | Result |
| --- | --- |
| Full Python 3.12.14 suite | 1,463 tests and 7 subtests passed in 358.58 seconds. |
| Statement / branch coverage | 97.2% / 94.1%, above the unchanged 95% / 90% gates. |
| Python 3.14 fast selection plus consumer checks | 197 passed. |
| Runtime/data/test/build content stability | Exact recorded source hashes unchanged throughout the full run. |
| Ruff, Vulture, audit, docs/examples/freshness, refs and task validation | Pass; audit has zero errors and warnings. |
| sdist → wheel → isolated install | All 11 installed command checks pass. |
| Standalone bundle | All 74 files verify; eight CLI inventories pass from outside the checkout. |

The eight calculation inventories are identical to the prior 0.4 candidate.
Comparing them with the retained, previously verified 0.3/v1.49 inventory gives
33,654 unchanged, 199 changed, 881 added and 30 removed fields, without tolerance
or filtering. The original 0.3 outputs and identity are reused; its replaced
companion pin is not re-executed. Its missing standalone validation dataset is
still explicitly unavailable. Current installed validation passes separately.
Known scientific limitations remain in [release scope](release_0_4.md).

The paper was rebuilt after the corrected fixtures. Its source digest verifies
as `8bf3f8279f832f05aa7e89e92eeb7650cf44539a94b341918b07a9dc847933ca`.
Only the page-15 fingerprint changes in extracted text; that page was rendered
and visually checked. The [PDF](../../paper/downstream.pdf) retains the same
numerical results.

## Artifacts and reproduction

The [machine receipt](release_qualification_2026-10-17_interval_fix.json)
records checks and artifact hashes. Raw manifests, exact before/after and
consumer-fixture comparisons, coverage, logs, environment, distributions,
bundle and rendered-paper evidence are retained under
`build/release04-qualification-20261017-interval-fix/`.
Its `run_qualification.py` records the complete local command sequence;
`commands.json` records the standalone comparison arguments. Use the
[development release workflow](../development.md#release-and-companion-handoff)
with the recorded environment. Preserve the unavailable old validation status.

The compressed artifact archive is `qualification-artifacts.tar.gz` in that
directory. SHA-256: `e82f05458cf49122b8de7fe894c691d9c464084dc5f443c25f7ef7f6f43d0a10`. All 146 archived evidence files verify against the included hash manifest.

Publication, owner release acceptance and companion live cache/render/deployment
acceptance remain separate. Software and fixture parity do not establish target
transport, independent causal validation, screen-reader or physical-device
acceptance, or participant comprehension.
