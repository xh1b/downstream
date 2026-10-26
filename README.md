# downstream

<!-- @ref:repository-overview; @tag:model -->
<!-- Context: @link:docs-index; @link:doc-model-card; @link:specification; @link:paper-methods. -->

Downstream evaluates consequences of a supplied worker-displacement exposure
using cited coefficients and declared composition rules. Results describe
conditional population/reference scenarios, with sources, uncertainty scope
and explicit blocked outcomes. They do not predict an identified person's life.
The engine has no runtime package dependencies.

The [code](src/downstream/) and [admitted data](params/) define behavior.
The [paper](paper/downstream.tex) explains the mathematics and scientific
choices. The [software guides](docs/readme.md) explain use and integration.
Read the [model card](docs/model_card.md) before interpreting a result.

## Install

Python 3.12 or later is required. From this checkout:

```sh
python -m pip install .
```

For development, install `python -m pip install -e '.[dev]'` in a virtual
environment. See [development setup](CONTRIBUTING.md#development-setup).

## Run a calculation

```sh
downstream family
downstream scenario --workers 1000
downstream household --input validation/household_five_year_input.json
downstream audit
downstream validate
```

A worker exposure does not establish unique displaced people, a net tradable-job
loss or immigrant arrivals. Default scenario outputs are illustrative and
ineligible for public headlines; missing evidence stays unavailable, not zero.
The [tested examples](docs/integration.md#executable-examples) show successful,
blocked and refused results. The [CLI reference](docs/integration.md#command-reference)
is generated from the parser; use `downstream <command> --help` for options.

## Run the calculator

```sh
make serve
```

Open [127.0.0.1:8000](http://127.0.0.1:8000/); press `Ctrl+C` to stop.
Use `make serve PORT=8001` for another port. The browser calculates locally;
the server rebuilds source data at startup. See the
[calculator guide](docs/calculator.md) for offline builds and checks.

## Find the right guide

| Need | Start here |
| --- | --- |
| Supported populations, outputs and scientific limits | [Model card](docs/model_card.md) |
| Inputs, API/CLI, output fields, errors, versions and caching | [Integration](docs/integration.md) |
| Source records, baselines, citations and evidence admission | [Evidence/data operations](docs/evidence.md) |
| Task system, tests, tooling, CI and release qualification | [Development](docs/development.md) |
| Equations and reasons behind implementation choices | [Paper](paper/downstream.tex), [PDF](paper/downstream.pdf), [HTML](docs/methods.html) |
| Historical algorithm section/anchor | [Implementation map](SPEC.md) |

## Verify and contribute

```sh
make check-docs
```

This checks docs navigation/naming, executable examples and generated-doc
freshness. [CONTRIBUTING.md](CONTRIBUTING.md) gives setup and the full
lint/audit/coverage/distribution sequence. The
[development guide](docs/development.md#tests-and-quality-gates) explains which
checks to run. Track work and review receipts on the [task board](tasks/README.md).

## Companion and release status

Version 0.4.0 is a conditional scenario-model release prepared for
[XH1B integration](https://xh1b.org/downstream). Local qualification is distinct
from companion deployment and scientific validation. Consult the
[model card](docs/model_card.md#evaluation-status),
[release review](docs/audits/release_0_4.md) and task board for scope and status.
Parameters v1.53 withdraw 16 unsupported historical inputs from calculation;
[the source policy](docs/evidence.md#source-withdrawals-and-retained-records)
keeps their original records separate from available estimates.
The database runner, production cache and website surfaces belong to the
companion project. Research/design proposals and dated audits are separate
from the maintained [software guides](docs/readme.md).

## Attribution and license

<!-- BEGIN GENERATED ATTRIBUTION -->
The identified bibliography contains 108 sources and 214 named author records (people and organizations), 1979-2026.

The parameters cite 40 sources with 97 named author records; these are not counts of independent research teams.

The bibliography includes research, methods and context sources; inclusion does not establish peer review or independent validation. Modeled numbers carry their cited inputs and declared structural assumptions.

See [CREDITS.md](CREDITS.md) for the complete attribution record.
<!-- END GENERATED ATTRIBUTION -->

Code is MIT licensed; imported sources/data retain their own terms. See
[LICENSE](LICENSE), [security reporting](SECURITY.md) and
[community conduct](CODE_OF_CONDUCT.md).
