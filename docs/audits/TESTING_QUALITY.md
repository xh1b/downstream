# Testing quality review — 2026-09-09

<!-- @ref:doc-testing-quality; @tag:testing -->
<!--
Connections: @link:code-ledger; @link:code-validate; @link:doc-scenario-evidence-protocol;
@link:doc-open-source-release; @link:docs-index; @link:script-quality-gate; @link:quality-workflow;
@link:script-benchmark; @link:script-vulture-whitelist; @link:test-properties-hypothesis;
@link:test-mathematics-v02.
-->

Related: [Documentation map](README.md) · [scenario evidence protocol](SCENARIO_EVIDENCE_PROTOCOL.md) · [open source release](OPEN_SOURCE_RELEASE.md).
Implementation: [ledger](../src/downstream/ledger.py), [validate](../src/downstream/validate.py). Checks: [properties_hypothesis](../tests/test_properties_hypothesis.py), [mathematics_v02](../tests/test_mathematics_v02.py).

## Current gate

Engine 0.4.0 / parameters v1.51 verification on 2026-10-14 measured
**96.8% statement coverage** and **93.2% branch coverage**. The complete
coverage run passes all **1,065 tests**. New regressions cover custom study
libraries across APIs/CLI, consumed source scale/window/population compatibility,
wrong currency baselines, source-table arithmetic and signed near-null mortality
against independent high-precision decimal calculations.
Ruff and vulture pass; the evidence audit reports zero errors and zero warnings.
The wheel built from the source distribution passes isolated installation checks,
including all three experimental commands. The 20-page paper was rebuilt and
visually inspected; its generated scorecard retains every validation miss.
These are numerical/software checks, not independent causal validation.

The repository now uses branch-aware Coverage.py and Hypothesis. The measured
previous baseline was **97.3% statement coverage** and **94.0% branch coverage** from a
clean 827-passing run on 2026-09-13 (two transient failures belonged to an
in-flight parameter-set landing by another worker, not to code defects).
`scripts/quality_gate.py` fails below 95% statements or 90% branches. The
full coverage run took about fifteen minutes on the local arm64 development
machine; use focused tests for rapid iteration and the complete run in CI
or a scheduled quality job.

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
  engine and supporting scripts before the test jobs run, and the vulture
  dead-code scan fails the same job on unused functions, classes, and
  attributes (see the dead code policy below).
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

## Dead code policy

Dead code is removed, not tolerated: in a citation-calibrated engine, an
unreachable branch is a claim about behavior that nothing verifies, and
readers cannot tell protection from ornament. The repo runs three
complementary detectors, and the 2026-09-13 sweep shows how they work
together.

Detectors:

- **Ruff (`F` rules, correctness set)** catches unused imports and
  unused local variables at edit time. It runs in the lint job over
  `src` and `scripts`.
- **Vulture (dead-code scan, `python -m vulture`)** catches unused
  functions, classes, methods, and attributes across `src` and
  `scripts`, which import-graph lints cannot see. It fails the lint
  job. Intentionally-unused API surface is allowed only through
  `scripts/vulture_whitelist.py`, where every entry carries a reason;
  an entry whose reason no longer holds should be deleted together
  with the code it excuses. Tests are excluded from the scan because
  pytest and Hypothesis discover test names reflectively.
- **Branch coverage with admission review.** Coverage tells you a
  branch never executed; only reading the admission path tells you
  whether it is *unreachable*. The audit module had six findings that
  could never fire: duplicate links, blank citations, out-of-band
  points, incomplete verified baselines, unknown baseline statuses,
  and unknown place levels are all refused at admission by
  `params.load`, `load_baselines`, and `load_places` before
  `audit()` sees any row. Branch coverage alone would suggest "write a
  test"; admission review shows the honest fix is deletion (landed as
  `842601e`), with the loaders-vs-audit division of labor documented in
  the module docstring.

Rules that keep dead code out:

- Validation has ONE authoritative home per input family: the loader
  admission contracts. Downstream layers (audit, synthesis, CLI) may
  assume admitted data and must not re-check admission facts
  defensively — that re-checking is where dead branches come from.
- Deliberately-unwired public API (SPEC'd caller-invoked branches,
  back-compat wrappers, pipeline entry points) is declared in the
  vulture whitelist with its reason, so "intentional" stays a
  reviewed, finite list rather than an excuse.
- A private helper is written when second use appears, not before;
  speculative generality is pruned on sight.

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

## Reference tooling and source navigation

<!-- @ref:test-refcheck; @link:script-refcheck; @link:reference-token-contract. @tag:tooling @tag:testing -->

[Reference-checker tests](../tests/test_refcheck.py) exercise duplicate anchors,
dangling links, malformed names, source-comment tokens and fenced examples.
Their literal fixtures are exempt from repository scanning through
[the fixture allowlist](../scripts/refcheck-allowlist.txt); this section is the
verification anchor for that intentionally exempt file.
[Task workflow tests](../tests/test_tasks_workflow.py) and
[board safeguards](../tests/test_tasks_board.py) cover task references, tags,
comments and isolated local commits. Run the reference and task validators
before review. These checks establish navigability, not scientific validity.
