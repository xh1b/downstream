- 2026-10-14 22:44 codex: Owner authorized task creation and implementation.
- 2026-10-14 22:44 codex: claimed (ready -> active)

## c-dacec3ce4a1b

- At: 2026-10-15 00:14 HKT
- By: codex

Implemented per-outcome sensitivity in f302593 and documented the schema, numerical example and consumer scaling in docs/RESULT_SENSITIVITY.md. The saved reference is validation/result_sensitivity_reference_20261015.json. Reports preserve signed effects and distinguish removal experiments, endpoint spans and optional correlation-aware variance attribution.

## c-1f7501b30e61

- At: 2026-10-15 00:16 HKT
- By: codex

Verification: full regression rerun passes 1,101 tests after regenerating the methods HTML provenance footer. The final sensitivity file passes 19 focused tests, including one county test added after full-suite collection. Coverage measured 96.9% statements / 93.4% branches; gates stay 95% / 90%. CI-scope Ruff (src/scripts), the new test file, vulture and evidence audit pass. The wheel built from sdist passes isolated installed CLI checks, including both sensitivity layers. Build used cached local setuptools with network disabled.

## c-443ea8de51a8

- At: 2026-10-15 00:16 HKT
- By: John Larue

done: active -> review.
