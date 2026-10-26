# comments

## c-6bc11ec5c472

- At: 2026-10-27 06:50 HKT
- By: John Larue

Created in inbox.

## c-b78b195b2471

- At: 2026-10-27 06:50 HKT
- By: John Larue

triage: inbox -> ready.

## c-95472cd2d955

- At: 2026-10-27 06:50 HKT
- By: codex-release

claim: ready -> active.

## c-c8207f029bf5

- At: 2026-10-27 07:44 HKT
- By: codex-release

Stable 0.4.0 is published and its source and assets are verified

Release: https://github.com/xh1b/downstream/releases/tag/v0.4.0 (draft false, prerelease false), published 2026-10-27 07:43 HKT. Tag v0.4.0 resolves to exact qualified source a1f54ad9390812a03436e4cd68bca81e5506dc75, engine 0.4.0 / parameters v1.53. All nine GitHub asset SHA-256 digests and sizes match the frozen local artifacts. Snapshot schema 3 separates 51 available inputs and 16 withdrawals; engine/data/fixtures must be upgraded together.

Exact-source CI: https://github.com/xh1b/downstream/actions/runs/40420976421 — 1,526 tests pass, coverage 96.8% lines/94.0% branches, all push gates pass (lint, two fast jobs, four Linux/Windows distribution jobs). Scheduled/manual mutation-and-benchmark is skipped by workflow policy. Local audit zero errors/warnings; final wheel passes eleven isolated CLI checks; documentation/generator checks pass; rebuilt paper visually inspected. Machine identities and receipts: [publication JSON](../../../docs/audits/release_publication_2026-10-27.json). Scope and commands: [release record](../../../docs/audits/release_0_4.md#stable-publication--october-27).

Source withdrawals are in review under @task:2026-10-27-source-withdrawals. Declared uncertainty cases are in review under @task:2026-10-14-transport-uncertainty; empirical calibration remains explicitly open under @task:2026-10-27-calibrate-transport-dependence.

Companion status is separate: its existing integration card remains blocked by unresolved NYC contract/Massachusetts WARN source publication holds. No live ingest health recheck, v1.53 companion repin, cache refresh, staging/production deployment, independent causal validation or human evaluation is claimed. The publication receipt records this separation and the existing companion task identities.
