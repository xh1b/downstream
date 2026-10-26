# comments

- 2026-10-14 19:56 codex: Migrated unfinished scope and original context; no work has been claimed.

## c-72782b027c86

- At: 2026-10-27 06:48 HKT
- By: codex-uncertainty

claim: ready -> active.

## c-573b772d4817

- At: 2026-10-27 07:38 HKT
- By: codex-uncertainty

Declared transport, persistence and dependence cases are implemented

Commit db2cd05 adds mortality-only caller-declared log-odds scales and independent/aligned/opposed exposure and baseline ranks. Study vectors and auxiliary marginals are preserved; cases retain separate conditional intervals and paired differences. There are no case probabilities, model averages, calibrated target-error claims or new headline eligibility. The original parameter/baseline/exposure/process budget remains unchanged when cases are absent.

Implementation: [uncertainty cases](../../../src/downstream/uncertainty_cases.py), [budget](../../../src/downstream/uncertainty_budget.py). Contract and limitations: [integration](../../../docs/integration.md#declared-uncertainty-assumption-cases). Checks: [regressions](../../../tests/test_uncertainty_cases.py), [saved input](../../../validation/uncertainty_assumptions_input.json) and [saved output](../../../validation/uncertainty_assumptions_result.json). Local full suite: 1,526 tests plus 9 subtests passed; lines 96.8%, branches 94.0%. Source candidate a1f54ad includes the final narrative and portable archive-check follow-ups; CI is recorded under @task:2026-10-27-publish-04.

No matched target evidence currently identifies calibrated transport/dependence distributions. That empirical requirement remains explicit in @task:2026-10-27-calibrate-transport-dependence and the existing matched-event/validation cards. This implementation closes the defensible declared-model scope without treating absent evidence as zero error.
