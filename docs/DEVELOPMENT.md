# Developing Downstream

<!-- @ref:doc-development; @tag:development -->
<!-- @link:docs-index; @link:contributing; @link:quality-workflow; @link:package-configuration. -->

The code and admitted data define behavior. Use the paper to understand the
mathematical rationale, these guides for software operations, and task cards
for work status and receipts. [CONTRIBUTING.md](../CONTRIBUTING.md) covers setup
and external contribution checks. Shared-checkout agents follow
[AGENTS.md](../AGENTS.md): claim tasks, preserve concurrent work, commit isolated
logical units on `master`, and keep remote operations separately authorized.

## Find the implementation

| Responsibility | Main modules | Representative checks |
| --- | --- | --- |
| Data admission and evidence | [params](../src/downstream/params.py), [evidence](../src/downstream/evidence.py), [study_library](../src/downstream/study_library.py), [admission](../src/downstream/admission.py) | [Parameters](../tests/test_params.py), [admission](../tests/test_admission_provenance.py) |
| Typed composition | [ledger](../src/downstream/ledger.py), [units](../src/downstream/units.py), [transmissions](../src/downstream/transmissions.py) | [Ledger](../tests/test_ledger.py), [transmissions](../tests/test_transmissions.py) |
| Scenario and adapter orchestration | [scenario](../src/downstream/scenario.py), [employer](../src/downstream/employer.py), [policy](../src/downstream/policy.py), [cli](../src/downstream/cli.py) | [Exposure](../tests/test_exposure_semantics.py), [CLI](../tests/test_cli_direct_contracts.py) |
| Mortality, children and households | [mortality](../src/downstream/mortality.py), [children](../src/downstream/children.py), [household](../src/downstream/household.py) | [Mathematics](../tests/test_mathematics_v02.py), [household](../tests/test_household_summary.py) |
| Uncertainty and sensitivity | [distributions](../src/downstream/distributions.py), [mc](../src/downstream/mc.py), [inference](../src/downstream/inference.py), [result_sensitivity](../src/downstream/result_sensitivity.py) | [Distributions](../tests/test_distributions.py), [sensitivity](../tests/test_result_sensitivity.py) |
| Validation and reproducibility | [validate](../src/downstream/validate.py), [forecast_registry](../src/downstream/forecast_registry.py), [bundle](../src/downstream/bundle.py), [compare](../src/downstream/compare.py) | [V2](../tests/test_v2_backtest.py), [bundle lifecycle](../tests/test_bundle_fsm.py), [comparison](../tests/test_compare.py) |
| Explanation and browser app | [explanation](../src/downstream/explanation.py), [render](../src/downstream/render.py), [calculator](../calculator/) | [Guard rails](../tests/test_guard_rails.py), [calculator](../tests/test_calculator.py) |

Follow stable refs in module headers to specific paper passages, software
contracts and tests. Avoid a second exhaustive module inventory in prose;
source files and reference-tool backlinks supply the detail.

## Paper and implementation

<!-- @ref:doc-paper; @tag:methods -->
<!-- @link:paper-methods; @link:paper-build-tables; @link:script-build-methods-html; @link:test-paper-tables. -->

The authored [paper](../paper/downstream.tex) explains how the implementation
works and why its mathematical and scientific choices are made. Keep scientific
citations and equations in rendered prose; put repository navigation metadata
in adjacent LaTeX comments. Code comments can cite the relevant passage without
copying its derivation. The code remains authoritative if the two diverge.

| Question | Paper ref | Implementation |
| --- | --- | --- |
| Why distinguish exposure equivalents, people and event timing? | @link:paper-exposure | @link:code-scenario, @link:code-employer |
| Which compositions are valid? | @link:paper-composition | @link:code-ledger, @link:code-units |
| How do source custody and applicability differ? | @link:paper-parameters | @link:code-params, @link:code-citations |
| How do mortality timing and survival work? | @link:paper-counts | @link:code-mortality, @link:code-mortality-robustness |
| Why distinguish child effects, valuation and descendants? | @link:paper-children | @link:code-child-applicability, @link:code-transmissions, @link:code-valuation |
| What do age-stratum and place projections assume? | @link:paper-mortality-strata, @link:paper-place | @link:code-mortality-strata, @link:code-place |
| What does the annual household model compute? | @link:paper-household | @link:code-household |
| What do sampling, moments and sensitivity establish? | @link:paper-sampling, @link:paper-inference, @link:paper-sensitivity | @link:code-distributions, @link:code-inference, @link:code-result-sensitivity |
| How are synthesis and county likelihoods qualified? | @link:paper-synthesis | @link:code-synthesis, @link:code-county-rates |
| Which validation claims are supported? | @link:paper-validation, @link:paper-independent-validation | @link:code-validate, @link:code-forecast-registry |

Build from the repository root:

```sh
make -C paper
.venv/bin/python -m pytest -q tests/test_paper_tables.py
```

[paper/Makefile](../paper/Makefile) runs [build_tables.py](../paper/build_tables.py)
and [build_methods_html.py](../scripts/build_methods_html.py), then `latexmk`.
Python uses `.venv` when present; LaTeX must be installed locally. Outputs are
[downstream.pdf](../paper/downstream.pdf) and [methods.html](methods.html).
Edit authored sources/builders and regenerate; do not hand-edit generated
numbers or HTML. Changes to source comments can change the provenance digest
without changing arithmetic.

The HTML companion records exact input-content SHA-256 and a separate display
result fingerprint (@link:methods-result-digest). The latter normalizes floats
to 12 significant digits to tolerate observed cross-platform last-bit math
variation. Exported JSON retains full precision. That display fingerprint is
not a byte-exact export checksum.

## Tests and quality gates

<!-- @ref:doc-testing-quality; @tag:testing -->
<!-- @link:script-quality-gate; @link:quality-workflow; @link:test-properties-hypothesis; @link:test-mathematics-v02. -->

Run focused public-contract and numerical tests during development. For a
behavior/data change, run the complete checks in [CONTRIBUTING.md](../CONTRIBUTING.md):
Ruff, Vulture, evidence audit, branch coverage and installed distributions.
The coverage gate is 95% statements and 90% branches; historical percentages
and test counts belong in [review receipts](audits/TESTING_QUALITY.md), not
in the current software contract.

Use fixtures for source transcription and named regressions, properties for
broad mathematical invariants, and state machines for bounded lifecycle rules.
A regression should distinguish the actual bug, not mirror an implementation.
A deterministic seed alone is not an oracle for a random estimator. Preserve
support signs, near-null effects, zero exposure, missing inputs and refusal
paths in relevant changes. Passing tests does not establish causal validity.

Admission belongs in the loader for each input family. Downstream code may
assume admitted invariants; duplicated defensive checks can create dead branches.
Intentional unused API surface needs a reason in
[vulture_whitelist.py](../scripts/vulture_whitelist.py). Benchmark and mutation
campaigns are separate diagnostics; do not impose machine-specific timing
thresholds in ordinary tests. See the [quality workflow](../.github/workflows/quality.yml)
for the executable job selection.

## Documentation and reference checks

<!-- @ref:test-refcheck; @tag:tooling @tag:testing -->
<!-- @link:script-refcheck; @link:reference-token-contract; @link:documentation-workflow. -->

Define stable refs beside their subjects and preserve them when consolidating
content. Use ordinary relative links for clickable paths and `@link:<id>` for
stable relationships. Tests should connect the calling contract and code;
implementation should connect the paper's rationale and the software guide.
The [token contract](../tasks/README.md#reference-tokens) defines syntax.

```sh
python3 scripts/refcheck.py check
python3 scripts/tasks.py validate
python3 scripts/refcheck.py show paper-counts
python3 scripts/tasks.py refs @task:2026-10-17-documentation-consolidation
```

The [reference tests](../tests/test_refcheck.py) exercise duplicates, dangling
refs, malformed names and source-comment tokens. Literal fixtures are excluded
via the [allowlist](../scripts/refcheck-allowlist.txt). Ref checking scans tracked
text, so include newly authored files in the commit before the final run.
It does not validate ordinary Markdown paths or equations: inspect file links,
examples and relevant builds as well. Historical task comments stay intact;
use a new receipt to document moved paths rather than rewriting discussion.

## Compare saved calculations

<!-- @ref:doc-version-comparison; @tag:consumer -->
<!-- @link:code-compare; @link:code-snapshot; @link:test-compare; @link:test-export. -->

Run each version's engine with identical inputs, then compare its saved JSON.
The comparator does not run an old engine, replace parameters or recalculate.

```sh
downstream compare --before old-result.json --after new-result.json
downstream compare --before old-results/ --after new-results/ --format json --out comparison.json
```

Directories match calculations by filename. Keep unrelated JSON outside them.
`--before-label`, `--after-label`, `--changes-only`, `--format` and `--out`
control report presentation. All fields appear by default without truncation.
Stable IDs key record lists when possible; unnamed lists remain positional.
Duplicate keys and nonfinite values fail. Fields use escaped JSON-pointer paths.
Numeric deltas are after minus before; percentages use the absolute before
value and are unavailable at zero. Null differs from a missing field, and
booleans are not numeric deltas. No tolerance or display rounding hides a
small change. Inspect units, sources, assumptions and identity with each delta.

The [comparison workflow](../.github/workflows/compare.yml) records exact SHAs
and fixed-input inventories for review. Its fixtures are not exhaustive across
all populations or settings. Equal points do not imply equal provenance;
seeded intervals may change if draw sequences change.

## Release and companion handoff

<!-- @ref:doc-open-source-release; @tag:release -->
<!-- @link:code-bundle; @link:script-check-distribution; @link:paper-reproducibility. -->

Engine versions live in both `pyproject.toml` and `src/downstream/__init__.py`;
parameter versions live in `params/VERSION` with `params/CHANGELOG.md`.
A documentation-only reorganization does not change model versions. For a
release, compare the candidate with the previous reviewed version under the
same inputs; retain raw calculations, parameter export, tested distributions
and review receipts. Check citations, credits, model limits, source rights,
security contact and publication metadata before making a release public.

```sh
python -m build
python scripts/check_distribution.py dist/downstream-0.4.0-py3-none-any.whl
```

Use the actual wheel filename produced. The build creates the wheel from the
sdist; the distribution check installs it in isolation. This repository does
not automatically publish Python packages. Hosting/registry publication and
companion deployment are owner actions, distinct from local qualification.
The `paper-v*` workflow publishes methods-paper artifacts separately.

For consumer normalization, mixture, cache and deployment acceptance, use the
[integration checklist](INTEGRATION.md#identity-and-handoff). Current candidate
qualification is recorded in the [0.4 review](audits/RELEASE_0_4.md) and task
cards. Research milestones, V2 blockers and human calculator review remain
visible there; a software-doc cleanup does not complete those scientific tasks.
