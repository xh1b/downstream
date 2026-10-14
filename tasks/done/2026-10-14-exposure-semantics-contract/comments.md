- 2026-10-14 codex: Proposed from the owner-requested XH1B usage review; implementation is not claimed.

## c-e80af116b46a

- At: 2026-10-15 01:25 HKT
- By: eli

triage: inbox -> ready.

## c-a238b4622e5e

- At: 2026-10-15 01:25 HKT
- By: eli

claim: ready -> active.

## c-b46b43ff58a6

- At: 2026-10-15 01:27 HKT
- By: eli

Implementation 2fc4e1c adds backward-compatible exposure_semantics, validated unknown/default fields, authoritative warehouse components, distinct reference-equivalent versus unique-person count basis, event-time limits and exposure provenance fingerprint. Existing engine numbers and outcome applicability unchanged; metadata does not admit a cohort or calendar forecast. [Contract](../../../docs/EXPOSURE_SEMANTICS_0_4.md), [tests](../../../tests/test_exposure_semantics.py). Focused adapter/CLI/warehouse suite 54 passed in 0.54s; Ruff passes. No scenario.py, companion or parameter changes.

## c-f39641c12419

- At: 2026-10-15 01:27 HKT
- By: eli

done: active -> review.

## c-c910617b8e00

- At: 2026-10-15 01:34 HKT
- By: codex

accept: review -> done.

Reviewed optional metadata validation, legacy/warehouse compatibility, preserved unknowns, separate exposure identity and count-basis-only eligibility. Affected integration tests pass. No scientific cohort admission or calendar allocation is inferred.
