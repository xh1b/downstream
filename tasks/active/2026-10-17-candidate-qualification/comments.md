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
