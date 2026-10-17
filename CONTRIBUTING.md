# Contributing to downstream

<!-- @ref:contributing; @tag:development -->
<!-- Context: @link:docs-index; @link:documentation-workflow; @link:doc-testing-quality; @link:doc-citing. -->

Contributions to the engine, evidence, tests, and documentation are welcome.
Start with a bug or evidence proposal issue for changes to model behavior;
small fixes can go straight to a pull request. Explain the causal question,
the numerical change, and how a reviewer can reproduce it.

## Development setup

Use Python 3.12 or later. Fork the repository, clone your fork, and create a
branch for your contribution. These instructions are for external contributors;
agents in the maintainer's shared checkout must follow `AGENTS.md` instead.

```sh
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
downstream family
downstream audit
```

The engine has no runtime dependencies. Development tools are installed by
the `dev` extra. Commands use the checkout's `params/` during development and
the bundled data when installed from a wheel.

## Before submitting

```sh
python -m ruff check src scripts
python -m vulture
downstream audit
python -m coverage run -m pytest
python -m coverage json -o coverage.json
python scripts/quality_gate.py coverage.json
python -m build
python scripts/check_distribution.py dist/downstream-0.4.0-py3-none-any.whl
```

Use the wheel filename produced by the build if the engine version changes.
The coverage gate requires 95% statements and 90% branches. Run focused tests
while developing, then the complete gate before submitting. Benchmark and
mutation campaigns run separately; see [development](docs/development.md#tests-and-quality-gates).

Add regression coverage for meaningful behavior changes. Preserve deterministic
seeds and explicit uncertainty. Do not regenerate unrelated data or format the
whole codebase as part of a small fix. Use synthetic examples in issues and tests.

## Evidence contributions

Read [evidence operations](docs/evidence.md), [model limits](docs/model_card.md)
and the relevant [paper passage](docs/development.md#paper-and-implementation)
before editing the graph. Code and admitted data define behavior; the paper
explains mathematical and scientific choices.
Each admitted row needs a source locator, extraction tier, units, uncertainty
envelope, population scope, and evidence role. Distinguish source estimates
from composition and transport assumptions. Missing evidence stays explicit.

Update `params/VERSION` and `params/CHANGELOG.md` for parameter changes.
Run `downstream credits --write` if the bibliography changes and include the
resulting `CREDITS.md`. Explain downstream numerical changes in the PR; do not
quietly tune parameters to pass a validation target.

## Pull request checks

PRs run lint/dead-code checks, a fast suite on Python 3.12 and 3.14, the full
coverage gate, wheel/sdist installation checks on Linux and Windows, and a
model comparison. The comparison runs the baseline engine at the PR base
commit and the candidate engine at GitHub's proposed merge commit using
identical inputs. It checks source parameters and fixed-input calculations.

Open the **model comparison → compare** job summary and download the
`model-comparison` artifact. Its complete JSON, CSV, and Markdown inventory
includes unchanged fields, changes, additions, and removals. The job summary
shows every changed, added, and removed field without truncation.
Expected model changes are reported without failing the build; execution,
audit, or comparison errors fail it. Explain meaningful changes in the PR.

Fork PR checks use a read-only token and no secrets. GitHub may require a
maintainer to approve a first-time contributor's workflow run. Scheduled
mutation testing is separate from PR checks.

See [version comparisons](docs/development.md#compare-saved-calculations) for local reports and
comparisons between release tags. Keep PRs focused and respond to review
comments with the source or test that supports your change.

Contributions are provided under the repository's MIT license. Respect
third-party source and dataset licenses; do not commit restricted microdata,
credentials, or private records. See [conduct](CODE_OF_CONDUCT.md) and
[security reporting](SECURITY.md).

## Connected documentation

The [development guide](docs/development.md) maps the task workflow, tools,
focused/full test commands, CI jobs and scheduled diagnostics. Task format and
command rules remain in [tasks/AGENTS.md](tasks/AGENTS.md).

Use [the documentation map](docs/readme.md) to find existing methods and contracts.
Extend the five maintained software guides in `docs/`; put reviews in
`docs/audits/` and supporting research/design material in `docs/research/`. Link
from the relevant entry point, and
connect implementation and verification with the [reference-token conventions](tasks/README.md).
Use source comments for paper navigation metadata. Run `python3 scripts/refcheck.py check`
and `python3 scripts/tasks.py validate` alongside the relevant behavior or build checks.
