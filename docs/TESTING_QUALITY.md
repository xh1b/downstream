# Testing quality review — 2026-09-09

## Current gate

The repository now uses branch-aware Coverage.py and Hypothesis. The measured
baseline is **89.6% statement coverage** and **70.3% branch coverage** from a
clean 565-test run on 2026-09-10. `scripts/quality_gate.py` fails below 80%
statements or 70% branches. The full coverage run took roughly four minutes on
the local arm64 development machine; use focused tests for rapid iteration and
the complete run in CI or a scheduled quality job.

Hypothesis complements rather than replaces the evidence fixtures:

- generated ledger level/gap envelopes are checked against all endpoint
  corners;
- survival excess deaths are bounded and monotone for broad valid inputs;
- county pooling is always a convex combination (this caught a one-ulp bug);
- deterministic tests retain the specific citations, reported coefficients,
  CLI contracts, and historical-scorecard fixtures that a generator cannot
  independently establish.

## What is strong

- Ruff blocks Python correctness linting (`E4`, `E7`, `E9`, and `F`) over the
  engine and supporting scripts before the test jobs run.
- Core numerical kernel: distribution materialization, ledger algebra,
  parameters, child-line propagation, and place handling have high line
  coverage and adversarial invariant tests.
- The prospective forecast registry has an adversarial Hypothesis state
  machine. It explores draft-to-registered-to-scoreable sequences and proves
  that duplicate registration, pre-window scoring, and record tampering are
  rejected on every generated sequence.
- Bundle export has the companion lifecycle test: export is transactional,
  verification accepts a complete manifest only, tampering is detected, and a
  simulated write failure leaves no partial bundle or staging directory.
- Synthetic V2 fixtures now cover a scoreable mortality result plus malformed
  bridge baselines/windows and malformed measured estimates. V2 accepts either
  signed job-loss changes or positive worker counts and evaluates all interval
  corners after converting to magnitudes.
- The county-place builder has small adversarial fixtures for territory
  filtering, weighted-national aggregation, malformed finite/range/FIPS
  inputs, duplicate Atlas or geoid FIPS, and byte-stable sorted output.
- Direct in-process CLI tests cover every public verb's routing and JSON
  contract, with explicit checks for parser exits versus manual return-code
  validation. Subprocess smoke tests remain as the installed-user check.
- Regression traps cover the previously discovered failure modes: mortality
  timing, invalid arbitrary composition, asymmetric normal centering,
  Spearman copula mapping, raw count quantiles, and negative school-spending
  interval ordering.
- Tests check properties that could survive a superficially plausible output:
  exact corner extrema, bounded survival loss, repeatability by seed,
  preserved LHS marginals, and sampled-version/correlation stamps.

## Remaining testing priorities

1. **External adapters.** BRAC download failure/HTML changes and
   county-mortality malformed sources need mocked I/O properties in addition
   to their current fixtures.
2. **Validation breadth.** V1 is exercised and V2 has synthetic scoreable
   fixtures, but real independently sourced V2 bridges and outcome estimates
   are still required before a genuine event verdict is possible.
3. **Metamorphic checks.** Add relations across independent implementations:
   deterministic count envelopes must contain all parameter draws; changing
   exposure by a scalar scales every count while preserving multipliers; and
   `scenario`, V1, and V2 mortality outputs must agree for the same synthetic
   input.
4. **Mutation testing.** Run a mutation tool against the numerical kernel in
   CI or a scheduled job. Branch coverage records execution, while mutation
   survivors identify assertions that fail to distinguish plausible wrong
   formulas.

## Mutation baseline

`mutmut` is pinned in the development extra and runs in an isolated workspace
containing the package, parameters, validation fixtures, and focused numerical
tests. The initial local campaign over mortality, ledger, scenario, place, and
V2 validation generated 2,963 covered mutants: 1,578 killed and 1,385
survived. This is a diagnostic baseline, not a release threshold. It found a
real boolean-as-number mortality input bug, now fixed, and prompted tests for
probability boundaries and the legacy mortality method. Many remaining
survivors are message-string or unexercised-path mutations; triage and a
meaningful mutation-score floor belong in the scheduled job after the first
few iterations.

## Test design rules

- Use property tests for invariants over a broad valid domain; use fixtures
  for literature transcription and named behavior.
- Never test random numbers without a mathematical oracle or a distributional
  tolerance justified by sample size.
- Every bug fix gets a minimal regression test that fails on the old behavior.
- Prefer public API/CLI tests for contracts, then focused unit tests to locate
  failures. Do not chase coverage by testing private implementation details
  alone.
- Use metamorphic tests when a fixed expected result is unavailable: exposure
  scaling and disjoint-cohort additivity must preserve every count, and the
  evidence-aligned mortality timing must never apply a year-6+ estimate early.
- Raise coverage floors only after the new target is stably attained across a
  full clean run; aggregate percentage is a floor, not proof of correctness.

## What state machines can prove

Finite-state-machine tests are appropriate for file and workflow lifecycles:
forecast registration, bundle export/verification, and ingestion status. They
can exhaustively exercise legal and illegal transitions in a bounded abstract
state model. They cannot guarantee all paths through continuous numerical
inputs, random sampling, filesystem failures, or third-party data. Those need
property/metamorphic tests, fuzzed malformed inputs, deterministic fixtures,
and branch coverage together. The forecast-registry state machine is the
first such test; bundle lifecycle testing is the next best candidate.

## Local performance baseline

Measured on 2026-09-09 with the repository virtual environment, using
`python scripts/benchmark.py`. Values are median wall-clock milliseconds and
are local microbenchmarks, so compare only like-for-like Python and hardware.

| Workload | Work | Median |
| --- | ---: | ---: |
| Deterministic scenario | one calculation | 0.030 ms |
| Scenario interval | 1,000 parameter draws | 343.936 ms |
| Child Monte Carlo | 1,000 draws | 323.169 ms |
| Sobol child sensitivity | base 32 | 277.980 ms |

The deterministic path is effectively constant-time at this scale. Monte
Carlo is linear in draw count. Sobol requires many model evaluations (roughly
proportional to parameter count times its base sample), and should be run as
an analysis job rather than on an interactive request path. Do not enforce a
fixed timing threshold in ordinary CI: host contention makes it flaky; retain
the benchmark output as a trend baseline and investigate material regressions.
