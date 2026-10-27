# Developing Downstream

<!-- @ref:doc-development; @tag:development -->
<!-- @link:docs-index; @link:contributing; @link:quality-workflow; @link:package-configuration. -->

The code and admitted data define behavior. Use the paper to understand the
mathematical rationale, these guides for software operations, and task cards
for work status and receipts. [CONTRIBUTING.md](../CONTRIBUTING.md) covers setup
and external contribution checks. Shared-checkout agents follow
[AGENTS.md](../AGENTS.md): claim tasks, preserve concurrent work, commit isolated
logical units on `master`, and keep remote operations separately authorized.

Jump to [task workflow](#task-system-and-work-receipts), [tool map](#development-tools-and-their-checks),
[implementation](#find-the-implementation), [paper](#paper-and-implementation),
[tests/CI](#tests-and-quality-gates), [docs checks](#documentation-and-reference-checks),
[release](#release-and-companion-handoff), or [troubleshooting](#troubleshooting).

## Environment and tool configuration

Use Python 3.12 or later and install the `dev` extra from
[CONTRIBUTING.md](../CONTRIBUTING.md#development-setup). The engine has no runtime
package dependencies; development tools are configured in
[pyproject.toml](../pyproject.toml), with resolved versions in
[uv.lock](../uv.lock). Use the repository virtual environment consistently when
running the commands below. Node is needed for browser JavaScript checks;
LaTeX and `latexmk` are needed for PDF builds.

## Task system and work receipts

<!-- @ref:development-task-system; @tag:tooling -->
<!-- @link:script-tasks; @link:task-workflow; @link:task-command-reference; @link:test-tasks-board; @link:test-tasks-workflow. -->

All work tracking lives in `tasks/`. Start with the
[board overview](../tasks/README.md); the authoritative format, ownership,
reference and transition rules are in [tasks/AGENTS.md](../tasks/AGENTS.md)
(@link:task-workflow). [scripts/tasks.py](../scripts/tasks.py) is the executable
implementation. Cards and their threads are the authoritative work records.

Read-only discovery and validation:

```sh
python3 scripts/tasks.py list
python3 scripts/tasks.py next
python3 scripts/tasks.py show <id>
python3 scripts/tasks.py tags
python3 scripts/tasks.py refs @task:<id>
python3 scripts/tasks.py validate
```

A task's directory ID is permanent; its column records status. The normal
sequence is `inbox → ready → active → review → done`. `done` means work is
ready for review; `accept` records owner/reviewer acceptance. Dependencies in
`blocked-by` must be accepted before `next` offers dependent work. Parent and
related-task links provide context without automatically blocking or completing
anything. `expected-paths` is advisory, not a file lock.

Create and claim an authorized scope, then record findings and evidence:

```sh
python3 scripts/tasks.py create <id> --title 'Task summary' --area docs --tags tooling --file /tmp/task-body.md
python3 scripts/tasks.py triage <id>
python3 scripts/tasks.py claim <id> --as <agent-name>
python3 scripts/tasks.py comment <id> --as <agent-name> --file /tmp/receipt.md
```

The task body contains acceptance criteria. Each completed criterion needs a
Markdown evidence link on the same line; link to code, tests, a report or a
permanent comment receipt. Inspect, validate and commit checklist edits before
calling `done`. The owner or trusted reviewer then uses `accept`, or
`request-changes` with a reason. Use the CLI for all column moves, comments,
replies and resolutions; do not rename card IDs or move task directories by hand.

Mutating board commands **make local Git commits**. They require `master`,
refuse an in-progress merge/rebase and protect dirty cards. Comments are
append-only; use a new reply or resolution to correct prior discussion.
Board commits stay separate from implementation commits. Follow the shared
checkout rules in [root AGENTS.md](../AGENTS.md) for explicit pathspecs,
concurrent edits and remote authorization.

`drop`, `cancel` and `reopen` cover released ownership, closure and resumed work;
see the [command reference](../tasks/AGENTS.md#process-and-commands) and
`python3 scripts/tasks.py <command> --help` for arguments. Task validation
checks structure, references, relationships and evidence-link presence; it
does not execute tests or independently verify a receipt's claims. All tasks
in review or done use the same completion-evidence rules.

## Development tools and their checks

<!-- @ref:development-tooling; @tag:tooling @tag:testing -->
<!-- @link:quality-workflow; @link:package-configuration; @link:script-quality-gate; @link:script-benchmark. -->

| Tool | What to run | What it checks |
| --- | --- | --- |
| Task board | `python3 scripts/tasks.py validate` | Card structure, relationships, refs and completion evidence links. |
| Repository refs | `python3 scripts/refcheck.py check` | Unique anchors, resolvable stable links and token syntax. |
| Documentation | `make check-docs` | Refs/tasks, exact-case paths/headings, lowercase filenames, executable examples and generated-doc freshness. |
| Ruff | `python -m ruff check src scripts` | Configured Python correctness and unused-import rules. |
| Vulture | `python -m vulture` | Unused code, with reasoned exceptions in [the whitelist](../scripts/vulture_whitelist.py). |
| Evidence audit | `downstream audit` | Mechanical parameter, citation and evidence consistency. |
| pytest / Hypothesis | `python -m pytest -q <test-paths>` | Named regressions, mathematical properties and workflow lifecycles. |
| Coverage.py | `python -m coverage run -m pytest` | Full-suite statement and branch execution. |
| Coverage gate | `python -m coverage json -o coverage.json`, then `python scripts/quality_gate.py coverage.json` | At least 95% statements and 90% branches. |
| mutmut | `python -m mutmut run --max-children 4`, then `python -m mutmut results --all true` | Mutation diagnostics on the configured numerical kernel. |
| Benchmark | `python scripts/benchmark.py` | Local timings with Python/platform metadata; no fixed performance gate. |
| Distribution build | `python -m build`, then `python scripts/check_distribution.py <wheel>` | Wheel built from sdist and installed-package contracts in isolation. |
| Calculator | `make check-calculator` | Generated browser app matches current sources/inputs. |
| Paper | `make -C paper` | Tables/HTML from the engine, then compiled manuscript. |

See [evidence operations](evidence.md#add-or-revise-evidence) for report builders
and [calculator checks](calculator.md#build-and-verify) for browser/native parity.
The task-board Markdown formatting rules live in
[tasks/.markdownlint.json](../tasks/.markdownlint.json); the checked-in quality
workflow runs task/ref validation, without a separate Markdown-lint job.

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
| How do source-specific receiving responses map shares to rates? | @link:paper-receiving | @link:code-receiving-community |
| What can missing covariance establish? | @link:paper-mortality-covariance | @link:code-mortality-covariance |
| Why can expected mixtures be combined but not their quantiles? | @link:paper-consumer-transforms | @link:code-consumer |
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
and test counts belong in [review receipts](audits/testing_quality.md), not
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

### Choosing and reproducing checks

For a focused change, run the affected public-contract tests first. The
following group checks the development tooling itself:

```sh
python -m pytest -q tests/test_refcheck.py tests/test_tasks_board.py tests/test_tasks_workflow.py
```

The fast numerical/lifecycle selection is defined directly in the
[quality workflow](../.github/workflows/quality.yml). To reproduce it locally:

```sh
python -m pytest -q tests/test_mathematics_v02.py tests/test_properties_hypothesis.py tests/test_ledger.py tests/test_place.py tests/test_build_places_adversarial.py tests/test_v2_backtest.py tests/test_forecast_fsm.py tests/test_bundle_fsm.py tests/test_compare.py tests/test_release_repairs.py
```

Use the full coverage and distribution sequence in
[CONTRIBUTING.md](../CONTRIBUTING.md#before-submitting) for behavior/data release
qualification. Generated evidence, pool-readiness and consumer-fixture reports
also have `--check` modes; use the relevant checks after their inputs change.
Reference and task validation do not check equations. `make check-docs` adds
ordinary Markdown path/heading, exact-case and example checks; relevant model
tests and artifact review still establish the underlying behavior and explanation.

### CI and scheduled diagnostics

[quality.yml](../.github/workflows/quality.yml) runs on pull requests, pushes to
`master`, a daily schedule and manual dispatch. Its jobs cover lint/docs/refs/tasks,
fast tests on Python 3.12 and 3.14, full coverage on 3.12, and distribution
checks on Linux/Windows across both versions. Mutation testing and benchmarks
run only on the scheduled/manual paths. Mutmut's configured selection and copied
inputs are in `pyproject.toml`; the mutation results are diagnostic, without a
mutation-score release threshold. Timing comparisons require matching hardware
and Python; benchmark results are not a numerical correctness check.

[compare.yml](../.github/workflows/compare.yml) produces the before/after model
inventory. [publish-paper.yml](../.github/workflows/publish-paper.yml) builds and
publishes methods-paper releases separately from engine/data release review.
The workflow files define current job selection and artifacts; local success
does not assert that a hosted run or deployment occurred.

## Documentation and reference checks

<!-- @ref:test-refcheck; @tag:tooling @tag:testing -->
<!-- @link:script-refcheck; @link:reference-token-contract; @link:documentation-workflow. -->

Define stable refs beside their subjects and preserve them when consolidating
content. Use ordinary relative links for clickable paths and `@link:<id>` for
stable relationships. Tests should connect the calling contract and code;
implementation should connect the paper's rationale and the software guide.
The [token contract](../tasks/README.md#reference-tokens) defines syntax.

```sh
make check-docs
python3 scripts/refcheck.py show paper-counts
python3 scripts/tasks.py refs @task:2026-10-17-documentation-consolidation
```

The [reference tests](../tests/test_refcheck.py) exercise duplicates, dangling
refs, malformed names and source-comment tokens. Literal fixtures are excluded
via the [allowlist](../scripts/refcheck-allowlist.txt). Ref checking scans tracked
text, so include newly authored files in the commit before the final run.
[doccheck.py](../scripts/doccheck.py) adds exact-case local paths, Markdown
headings, lowercase docs filenames and executed `pycon` examples in the five
maintained guides. The full target also checks six generated outputs and runs
the checker regressions. Use `python3 scripts/doccheck.py` for navigation only,
or `--examples` and `--freshness` to select the additional checks. It does not
execute shell recipes, task mutations, historical audit examples or remote links.
The consumer-fixture and calculator checks preserve exported full precision.
Their [comparison helper](../scripts/artifact_checks.py) permits at most 32
floating-point steps (ULP) for finite computed JSON floats, covering observed
Linux/macOS math-library variation amplified by subtraction. Zero, numeric
types, structure, source hashes and metadata remain exact. Calculator HTML
outside its embedded result JSON remains byte-exact. This allowance neither
rounds results nor changes the engine or source inputs; its [regressions](../tests/test_artifact_checks.py)
reject larger numeric drift and changed metadata or authored markup.
Task cards and comment threads are outside live-link checking.
Missing semantic bridges and incorrect equations still need code/paper review.
Historical task comments stay intact;
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

Follow the mandatory [publication approval rule](../AGENTS.md#publication-requires-explicit-confirmation)
(@link:publication-approval): finish local preparation, present the exact version,
source commit, artifacts, checks and limitations, then ask the user for explicit
permission and wait for confirmation before publishing. Preparing a release or
discussing its version does not grant that permission. This also covers release
edits, unpublishing, deployments and tags or workflows that publish automatically.

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
[integration checklist](integration.md#identity-and-handoff). Current candidate
qualification is recorded in the [0.4 review](audits/release_0_4.md) and task
cards. Research milestones, V2 blockers and human calculator review remain
visible there; a software-doc cleanup does not complete those scientific tasks.

## Troubleshooting

| Symptom | Check | Resolution |
| --- | --- | --- |
| Import/tool not found | Interpreter, active environment and Python version. | Use Python 3.12+ and the development extra from CONTRIBUTING; run all commands in the same environment. |
| Docs checker reports an incorrectly cased path | Exact spelling in `git ls-files`, not whether the host filesystem opens it. | Correct the link or filename and its consumers; a case-insensitive machine can conceal a Linux failure. |
| Generated-doc freshness fails | The named builder's diagnostic and changed source inputs. | Review the input change, regenerate that output without `--check`, inspect its diff and rerun checks. Never rewrite a historical evaluation to give it a current identity. |
| Software reference is stale | Parser, dataclass fields and public signatures. | Run `python scripts/build_software_reference.py`; edit authored explanation outside the generated markers. |
| Paper build lacks `latexmk` | Local LaTeX installation. | Install the required PDF tooling for a PDF build; HTML/data generation alone does not verify a rendered PDF. |
| Task move/comment refuses a dirty card | `git status` and the card owner's in-progress edits. | Preserve and coordinate those edits; commit owned checklist/receipts before changing status. Do not stash or discard shared work. |
| Task/comment ref does not resolve | `tasks.py show <id>` and `tasks.py refs <reference>`. | Use the permanent task ID/comment ref, repair the new reference and preserve prior discussion. |
| Checks pass but candidate is not accepted/deployed | Task review status and companion receipts. | Keep local software qualification, owner acceptance, scientific validation and deployment claims separate. |
