# comments

## c-90ac2be9d64a

- At: 2026-10-27 17:20 HKT
- By: codex-release041

Created in inbox.

## c-87e856fe95bd

- At: 2026-10-27 17:20 HKT
- By: codex-release041

triage: inbox -> ready.

## c-120a77bb7621

- At: 2026-10-27 17:20 HKT
- By: codex-release041

claim: ready -> active.

## c-7a5aadd4b827

- At: 2026-10-27 17:23 HKT
- By: codex-release041

Approved stable/latest 0.4.1 publication verified

Published https://github.com/xh1b/downstream/releases/tag/v0.4.1 after the owner explicitly confirmed the exact candidate. Release ID 425241293; tag resolves to approved source 1691850d70a27be5cfadf775c7a3edc9ce17b465. All eleven uploaded asset sizes and SHA-256 digests match the sealed candidate and manifest; latest-release API points to 0.4.1. The 0.4.0 body/metadata and all nine asset IDs/sizes/digests are unchanged.

Machine receipt: docs/audits/release_publication_0_4_1_2026-10-27.json. Human receipt: docs/audits/release_0_4_1.md. Both committed in 5cab8be. Current README links the published patch. Documentation and reference checks pass; no companion repin, cache write or deployment was performed.

## c-ff2ecc615f12

- At: 2026-10-27 17:23 HKT
- By: codex-release041

XH1B integration prompt

Update XH1B to the published Downstream 0.4.1 release:
https://github.com/xh1b/downstream/releases/tag/v0.4.1
Pin source commit 1691850d70a27be5cfadf775c7a3edc9ce17b465, engine 0.4.1 and parameters v1.54. Verify the release-manifest.json asset hashes. Read upstream docs/integration.md, docs/evidence.md and docs/audits/source_repairs_2026-10-27.md at that revision.

Follow this repository's AGENTS.md and coordinate through the existing integration task 2026-10-15-verify-downstream-0-3-0-integration-before-deployment, preserving its history and current source-publication holds.

1. Update the engine pin, complete parameter bundle and adapter together. Verify parameter snapshot schema 3. Rebuild and record the bundle identity; expected bundle SHA-256 is d84162591c94d06c8148c4834ae705ff3f9a015c29955d95d26749834cd136ed. Keep bundle, input, exposure and adapter identities distinct in cache keys.
2. Replace stale blanket statements that all sixteen inputs remain withdrawn: six original estimates are restored, seven corrected source contrasts are available, and three original earnings relationships remain unsupported. The current inventory has 64 available rows and ten retired identifiers: seven superseded and three unsupported. Preserve original records and unavailable states; do not convert nulls to zero or revive retired aliases.
3. Preserve corrected units, outcomes and study windows. Do not reinterpret corrected contrasts as generic displacement effects or add them to headline totals. Transport/dependence cases are declared sensitivity assumptions, not calibrated probabilities or independent validation.
4. Run upstream consumer fixtures against the actual XH1B adapter. Check national/county/fallback, zero/fractional exposure, signed benefits, reviewed/blocked applicability, custom profiles, scaling, mixtures and nested persistence/sensitivity alternatives. Preserve normalization precision; do not average quantiles. Verify matching values, units, unavailable states and source metadata across JSON, HTML, Markdown and citations. The 48 published 0.4.0 fixture point/range endpoints are unchanged; provenance and availability still require migration.
5. Prepare and test cache invalidation/recomputation locally, with before/after receipts. Report code changes, tests, bundle/adapter identities, remaining source holds and deployment readiness.

Complete local integration and verification. Ask for explicit approval before production cache writes, publication or deployment; this prompt does not waive existing source-publication holds.

## c-1d105720e186

- At: 2026-10-27 17:24 HKT
- By: codex-release041

done: active -> review.
