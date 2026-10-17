# comments

- 2026-10-14 19:56 codex: Migrated unfinished scope and original context; no work has been claimed.
- 2026-10-14 22:15 John Larue: See docs/XH1B_USAGE_PLAN_0_4.md. Qualify exposure and mixture metadata before repinning 0.3.0/v1.49.

## c-43a52ba6e8ad

- At: 2026-10-15 00:14 HKT
- By: codex

Result sensitivity now has its own consumer contract: docs/RESULT_SENSITIVITY.md. Normalize nested result points and changes linearly, output variance quadratically, and keep input coefficients and variance indices unchanged. Mixtures must recompute shared experiments; do not inherit the first county report. See task:2026-10-14-result-sensitivity. No companion code or pin changed.

## c-955fb69500db

- At: 2026-10-17 21:40 HKT
- By: codex-release-finish

triage: inbox -> ready.

Owner authorized remaining simple 0.4 work. Scope is local companion-task inspection and a verified model bundle/provenance handoff; no companion repin or deployment.

## c-d4863556697a

- At: 2026-10-17 21:40 HKT
- By: codex-release-finish

claim: ready -> active.

## c-d3b3d92ec040

- At: 2026-10-17 22:02 HKT
- By: codex-release-finish

Complete the model-side 0.4 handoff

[The handoff](../../../docs/audits/xh1b_handoff_2026-10-17.md) links the existing companion runner/website, cache/scheduler and exposure/page acceptance tasks. It records a fresh read-only inspection, seven passing old-pin tests, eight candidate worker cases, exact bundle/fixture identities and the qualified artifact archive. Engine stays 0.4.0 / parameters v1.52.

The known nested-mixture incompatibility remains reproducible: main 21.716 agrees, but nested source-profile 17.02 must be 21.716 and no-sustained 12.12 must be 15.48. A synthetic mortality review no longer qualifies child outputs without age/income-rank inputs, which the current worker does not forward. These are explicit companion acceptance requirements; completing this local coordination card does not complete its runner, cache, rendering or deployment tasks. The pin and companion files remain untouched.

## c-08b36805cfd0

- At: 2026-10-17 22:02 HKT
- By: codex-release-finish

done: active -> review.

Model-side coordination and bundle/provenance handoff are ready for review; companion integration tasks remain open.
