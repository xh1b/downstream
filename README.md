# downstream

<!-- @ref:repository-overview; @tag:model -->
<!-- Context: @link:docs-index; @link:doc-model-card; @link:specification; @link:paper-methods. -->

`downstream` estimates consequences of a supplied worker-displacement exposure.
The current engine applies published response coefficients and declared
composition rules to population-average worker, family and community scenarios.
Its experimental annual household comparison is limited to employment-state
probabilities and gross earnings under declared assumptions. Every computed effect
traces to cited research or an explicitly labeled structural assumption. Each result shows its uncertainty and
the full path that produced it. The engine has no runtime dependencies.

Worker displacement is the first seed event. It is not the boundary. The
long-term goal is a versioned graph of published causal evidence. Distant
consequences then emerge from cited bridges, not from a hand-written narrative.
The engine adds an effect only when the evidence supports the bridge, the
bridge is compatible, and the uncertainty is explicit. Current results remain
conditional on the supplied exposure and stated transport assumptions. They
do not predict the future of an identified person. See the [paper](paper/downstream.tex) for mathematical explanation and [software docs](docs/readme.md) for implementation contracts.

<!-- BEGIN GENERATED ATTRIBUTION -->
The bibliography contains 110 sources and 216 named author records (people and organizations), 1979-2026.

The parameters cite 53 sources with 121 named author records; these are not counts of independent research teams.

The bibliography includes research, methods and context sources; inclusion does not establish peer review or independent validation. Modeled numbers carry their cited inputs and declared structural assumptions.

See [CREDITS.md](CREDITS.md) for the complete attribution record.
<!-- END GENERATED ATTRIBUTION -->

## Calculator

```sh
make serve
```

Open **[127.0.0.1:8000](http://127.0.0.1:8000/)**. Press `Ctrl+C` to stop.
Use `make serve PORT=8001` if the port is busy.

The app lives in [`calculator/`](calculator). It calculates in the browser;
the local server builds its source data at startup. No Node packages are needed.
See [calculator setup and method](docs/calculator.md).

## Install

Python 3.12 or later is required.

```sh
python -m pip install .
```

For development and tests:

```sh
python -m pip install -e '.[dev]'
```

## Reproduce

Run the full test and coverage gate:

```sh
python -m coverage run -m pytest
python -m coverage json -o coverage.json
python scripts/quality_gate.py coverage.json
```

The gate requires at least 95% statement coverage and 90% branch coverage.
The 2026-10-15 engine 0.4.0 check measures 97.2% and 94.1%. The suite contains Hypothesis
property tests for ledger envelopes, survival bounds, and county-pooling
convexity. Deterministic fixtures cover citations, published coefficients, and
regression examples.

The pending 0.4.0 update adds reproducible reference cohorts, sourced subgroup scenarios,
age-timed child present values, household earnings comparisons, and a separate
baseline/exposure/process uncertainty budget. See the
[update record](docs/audits/release_0_4.md) for the source correction, verification,
and research dependencies that remain open.
These changes have not yet been applied to XH1B.

Additional checks:

```sh
python -m ruff check src scripts        # correctness lint; blocks CI
python -m vulture                       # dead code; blocks CI
python scripts/benchmark.py             # numerical microbenchmarks
python -m mutmut run --max-children 4   # mutation campaign
python -m mutmut results --all true     # all mutation results
```

The benchmarks are comparison baselines. They are not a performance gate. See
`docs/audits/testing_quality.md` for the measured baseline and scaling notes. GitHub
Actions runs a fast property/FSM/CLI suite on each change, the full coverage
gate on pull requests, and a scheduled mutation-plus-benchmark job.

## Quick start

```sh
downstream family                        # standard-family vignette, all citations
downstream scenario --workers 1000       # envelopes + 90% parameter-only intervals
downstream simulate --outcome child --place national --draws 1000
downstream explain --text                # one claim, from headline to citations
downstream audit                         # parameter, citation, DAG, unit checks
downstream validate                      # V0 consistency + V1 retrodiction
downstream mortality-cohort --input validation/cps2024_hypothetical_mortality_input.json
downstream household --input validation/household_five_year_input.json
downstream uncertainty --input validation/uncertainty_budget_input.json
```

## Command reference

| Command | Function |
| --- | --- |
| `family` | standard-family vignette with full citations |
| `scenario` | effect envelopes for a worker cohort; parameter-only and predictive intervals |
| `entity` | accepts a computed displacement exposure from a JSON file |
| `policy` | compares supplied baseline and policy exposures |
| `mortality-cohort` | exact sourced age-stratum aggregation; aging/fixed-baseline comparison; uncovered workers stay unknown |
| `household` | annual employment and gross-earnings comparison under a supplied displacement duration |
| `uncertainty` | documented baseline-count, declared exposure, parameter and process uncertainty kept separate |
| `simulate` | Monte Carlo simulation for an outcome and place |
| `child-gaps` | Side-by-side child and descendant earnings gaps; structural projections stay separate |
| `sensitivity` | Sobol analysis of the result range; `--ci` adds seed-replicate design noise |
| `knobs` | sweeps one parameter, or ranks parameters by value of information |
| `infer` | exact moments and normal bands; `--action closure` checks band coverage |
| `ensemble` | spread across structural variants |
| `synthesize` | random-effects evidence synthesis from same-scale studies |
| `county-posterior` | county mortality posterior from supplied counts |
| `county-wonder-posterior` | county mortality posterior from a CDC WONDER export |
| `explain` | one claim, from headline to citations |
| `audit` | parameter, citation, DAG, and unit checks |
| `validate` | V0 internal consistency and the V1 retrodiction target |
| `citations` | citation coverage report |
| `credits` | computed researcher and study credit |
| `compare` | complete before/after inventory of saved outputs or parameter snapshots; Markdown, CSV, JSON |
| `bundle` | exports a standalone engine and data bundle with checksums |
| `forecast-register` | freezes a prospective forecast locally |
| `forecast-score` | scores the forecast after the outcome window |

## Inputs

`entity --input exposure.json` accepts a computed displacement exposure:

```json
{
  "subject_id": "example",
  "subject_type": "employer",
  "displaced_workers": 100,
  "source": "reference to the documented input records",
  "method": "reference to the upstream exposure calculation"
}
```

- The entity adapter uses the same scenario arithmetic. It accepts `--place`,
  `--children`, `--tradable-share`, and `--exposure-years`.
- The caller owns the exposure conversion. Filing counts, wage-gap dollars, and
  WARN notices are not worker counts.
- Local service employment computes only when the input also supplies a
  documented net local tradable-job loss.
- The adapter preserves the `source` and `method` references.
- For one person, use `subject_type: "person"`. Results are population-average
  modeled impacts. They are not predictions for one person.

For a warehouse aggregate, use `entity --input-format warehouse --input row.json`:

```json
{
  "subject_id": "example",
  "subject_type": "employer",
  "source": "reference to the source aggregate and its version",
  "americans_displaced": 137.125,
  "displacement_breakdown": {
    "base": 100,
    "wage_depression": 12.125,
    "warn_layoffs": 25,
    "total": 137.125,
    "formula": "reference or description of the upstream exposure method"
  }
}
```

The example values are synthetic fixtures. The components are in
worker-equivalent units.

- The adapter preserves `americans_displaced` and requires it to equal `total`.
  It checks the component sum within 0.002.
- Employer rows require `warn_layoffs`. Person rows can omit it.
- Missing fields fail. Empty breakdowns fail, including an empty breakdown with
  zero exposure. A known zero needs explicit zero components.
- Additional breakdown fields stay caller-owned. They do not enter the exposure
  calculation.

`policy --input comparison.json` compares supplied baseline and policy
exposures. Each case has `name`, `source`, `method`, and a `scenario` object
with `displaced_workers`. `exposure_low`, `exposure_high`, and `place_key` are
optional. They add exposure uncertainty and geography. Output reports policy
minus baseline. The command does not infer how a policy causes displacement.

## Place experiments

`simulate --outcome child|grandchild`, `sensitivity` (with `--ci`), and `knobs`
(sweep and VOI) accept a `places.csv` key through `--place`. The engine
recomputes the mobility parameter for every draw or pin. Place measurements and
pooling weights are fixed. The bands do not include uncertainty in county
measurements. Output shows the place sources and the declared composition
assumption. Chains from `simulate --links` do not accept `--place`.

## Uncertainty method

- Latin Hypercube Sampling. Log-space sampling for ratio parameters.
- Optional declared rank correlation. It stays empty until citable.
- Sobol sensitivity. CRPS and coverage scores for the validation program.
- `scenario` adds a central 90% **parameter-only** interval. The `low` and
  `high` fields are support envelopes. They are not confidence intervals.
- Documented exposure, baseline estimation, county pooling, structural
  assumptions, and unmodeled pathways are labeled as fixed or excluded. The
  engine does not fold them into one falsely complete band.
- Integer worker cohorts also get a labeled posterior-predictive mortality
  simulation: parameter draws plus binomial variation in deaths. This is not a
  paired individual-level causal distribution. Fractional worker-equivalent
  aggregates keep expected effects only.

See `SPEC.md` §7–10 and `docs/model_card.md`.

## Mortality timing

The default is `source_profile`: the displacement year, offsets 1, 2–3, 4–5,
and 6+ from Sullivan–von Wachter Table 5 column 3. Displacement occupies
follow-up year 1, so +6 starts in year 7. `source_aligned` exists only to
reproduce the former incomplete timing. `immediate_sustained` is a sensitivity
assumption.

## Child scope and income contrasts

Child scenarios can supply `--child-profiles children.json` (one object with
`age_at_displacement` and `sex` per child), plus `--child-income-quartile 1|2|3|4`
and `--income-rank-definition`. Known children outside the source's male
10–14 cohort block the child count; unknown profiles remain illustrative.
Income contrasts use Oreopoulos Table 8, preserve signed effects and include
null/beneficial possibilities. They do not identify an age-response curve or
a constant effect over a whole career. `params/study_estimates.csv` contains
hash-pinned source contrasts and overlap metadata; these are not automatically
pooled or admitted as universal effects.

With known child ages, `--real-discount-rate 0.03 --valuation-year 2026`
adds a separate `child_valuation` report. It preserves undiscounted dollars,
shows real present values at the event date, and separates the observed
adult-age window (25–33) from a declared constant-gap career projection
(20–64). The latter is an extrapolation, not an identified annual effect path.
Zero-rate career valuation reproduces the existing undiscounted count.
Custom `--params` directories supply the subgroup study library as well as
parameters and baselines. API callers pass `params_dir` for the same behavior.
Selected contrasts must match the consumed effect scale, population and window;
missing custom libraries fail. Child-dollar baselines must use `usd_2024`.

## Per-result sensitivity (0.4.0)

Scenario counts and child present-value projections now include `sensitivity`:
each applied coefficient's value/source, its removal experiment and refits at
supported endpoints. Fixed inputs and unavailable ranges remain explicit.
Entity results and policy-arm scenario records inherit these reports.
Add `--sensitivity-base 512` to `scenario` for a separate correlation-aware
parameter variance breakdown. See [the result contract and example](docs/integration.md#per-result-sensitivity).

## Mortality persistence comparison (0.4.0)

Default scenario and entity mortality outputs now include
`persistence_sensitivity`: the existing source profile beside a declared
alternative with no excess annual risk from follow-up year seven onward.
The alternative keeps the early profile and the same resolved baseline.
Each structure has a separate parameter interval, and their difference uses
shared parameter draws. Their point-estimate spread is not a confidence
interval; neither structure receives a model-average weight.

For 1,000 workers over 20 years, the reference point is 28.76 excess deaths
and the alternative is 20.52. This prices the long-run persistence assumption
without replacing the source anchor or treating a nonsignificant finding as
proof of zero. Both retain the population-applicability and fixed-baseline
limits. See [the method and reproducible example](docs/integration.md#persistence-comparison).
Parameters v1.50 correct the offset +4–5 source standard error to 0.138,
widening intervals while preserving the point estimate. Revision v1.51
re-executes all five source transformations, corrects working-paper tiers and
cross-study provenance, and yields the reference values above. Production
website rendering needs integration.

## Website readiness repairs (0.3.0)

Engine 0.3.0 / parameters v1.49 enforce county mortality compatibility and posterior arithmetic, use the complete mortality profile in validation and exports, share repeated transmission draws, preserve custom sampling context, and reject invalid or nonfinite public inputs. Credits regenerate from full author identities. The methods paper uses independent net-job exposure and readable labels; [the HTML methods companion](docs/methods.html) is available for website integration.

Default scenario and entity counts are **illustrative reference calculations**, with `applicability.eligible_for_public_headline = false` on each outcome. A reviewed conditional transport decision requires structured `target_population` fields (`sex`, `age`, `worker_tenure`, `geography`, `calendar_window`, `exposure_type`, `children_sex`) and per-outcome `applicability_decisions` (`status: reviewed`, `reviewer`, `rationale`, `citations`). Incompatible target demographics block the corresponding outcome. The adapter accepts this metadata on `DocumentedExposure` or `ScenarioInput`. A reviewed transport decision does not establish independent empirical validation.

Website consumers must preserve outcome applicability, baseline derivation notes, lifetime versus follow-up horizons, support-envelope versus parameter-interval labels, blocked outcomes and fallback provenance. Use bundle content identities for cache keys and retain scenario `input_content_sha256`. Actual site rendering and production cache invalidation require integration outside this repository.

## Engine corrections (0.2.0)

Engine 0.2.0 corrects mortality odds-to-risk conversion and survival timing. It
scales optional place effects as a same-place displacement-loss contrast. It
fixes signed uncertainty envelopes and normal/lognormal analytic moments. See
`docs/model_card.md` for model limits and remaining assumptions. Correlated
Monte Carlo results change at historical seeds after the copula repair. County
results stay experimental until their population and window metadata enter
through a validated integration bridge.

Historical scenario arithmetic:

```sh
downstream scenario --workers 1000 --mortality-method legacy_additive \
  --place-application legacy_repeated
```

Legacy additive mortality keeps expected counts only.

## Methods paper

```sh
make -C paper
```

The build regenerates the parameter inventory, the V1 scorecard, and the chart
coordinates from the engine. It then compiles `paper/downstream.pdf`.
`paper/generated/results.json` holds the full validation output and a
source-content hash. Git ignores generated files. `paper/build_tables.py`
generates the numerical data. Vector diagrams and chart layouts live in
`paper/figures/`.

The reviewed PDF is checked in, so public links stay stable. Tag a reviewed
release as `paper-v*`. GitHub Actions then rebuilds the paper and attaches the
same PDF to the release. A manual workflow run stores the build as an artifact.

## Bundle and forecasts

`bundle --out /path/to/new-directory` exports a standalone engine and data
bundle. Each file has a checksum. The bundle has a content-based version. The
destination must not exist.

`forecast-register --input proposal.json --out registration.json` freezes a
prospective forecast locally. `forecast-score` reports misses and coverage
after the outcome window. The required proposal fields are in
`src/downstream/forecast_registry.py`. Registration still needs an independent
timestamp to establish public preregistration.

## Repository layout

| Path | Content |
| --- | --- |
| `SPEC.md` | secondary algorithm reference; code and admitted data define behavior |
| `params/` | versioned parameter set, node units, baselines, `references.bib` |
| `src/downstream/` | DAG engine, typed ledger, modules, Monte Carlo, audit, validation |
| `tests/` | the compute checks (`pytest`) |
| `paper/` | the methods paper (`make -C paper`) |
| `CREDITS.md` | every researcher, study, and DOI, computed from the bibliography |
| `scripts/` | quality gate, benchmarks, data acquisition, task board CLI |
| `tasks/` | task cards and agent workflow; `python3 scripts/tasks.py list` |
| `docs/` | software guides, with reviews in `audits/` and supporting plans in `research/` |

Current work is tracked in [the task board](tasks/README.md), using the XH1B card format.
Run `python3 scripts/tasks.py next` to see claimable work.

Start with [the documentation map](docs/readme.md) for connected guides, code,
tests and paper sources.

The implementation and admitted data define behavior. The [paper](paper/downstream.tex)
explains the math and scientific choices. Five software guides cover
[scope](docs/model_card.md), [integration](docs/integration.md),
[evidence/data operations](docs/evidence.md), [the calculator](docs/calculator.md)
and [development](docs/development.md). Dated reviews live in
[docs/audits](docs/audits/readme.md); research and design plans are separate in
[docs/research](docs/research/readme.md).

## Companion project

[xh1b.org/downstream](https://xh1b.org/downstream) integrates this model into
employer, county, state, and family surfaces. Integration is in progress. It is
deferred while the team strengthens this model. This repo contains the model,
parameters, calculator and paper. The database runner and its record-selection
rules belong to the companion project.

## Contributing and version comparisons

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, evidence rules, and PR checks.
Pull requests produce a model comparison with before/after values, numerical
deltas, and added or removed fields. The complete report is available as a
workflow artifact, and every changed, added, and removed field appears in the job summary.

```sh
downstream compare --before old-result.json --after new-result.json
downstream compare --before old-results/ --after new-results/ --format csv --out changes.csv
```

Run each version's own engine with identical inputs before comparing its
saved JSON. See [version comparisons](docs/development.md#compare-saved-calculations) and the
[release checklist](docs/development.md#release-and-companion-handoff).

## License

MIT. See `LICENSE`.

## Local 0.4 review tools

- [Calculator](calculator/index.html): edit exposure, timing, baseline,
  odds ratios and child earnings inputs. Survival and sensitivity recalculate in
  the browser. See [method and checks](docs/calculator.md).
- [Child-gap view](docs/integration.md#child-and-descendant-outputs): `downstream child-gaps --workers 1000`.
- [Evidence classification](docs/audits/evidence_classification_0_4.md): inspect source
  applicability separately from structural runtime use.
- [Consumer fixtures](docs/integration.md#scaling-mixtures-and-acceptance-fixtures): normalization and mixture
  expectations for the pending companion handoff.

- [Exposure semantics](docs/integration.md#exposure-and-event-metadata): caller-owned quantity,
  event time, overlap and provenance contract.
- [Child source support](docs/integration.md#inspect-source-support): current eligibility and signed
  income contrasts; `python scripts/inspect_child_support.py`.
- [Pool readiness](docs/audits/pool_readiness_0_4.md): compatibility and sample overlap.
- [Mortality covariance](docs/audits/mortality_covariance_0_4.md): additive phase precision
  bounds with unknown covariance.

- [Receiving-community comparisons](docs/integration.md#receiving-community-adapter): typed share
  exposures and optional annual endpoint incident differences, separate from displacement.
- [Household summaries](docs/integration.md#annual-household-comparisons): paired member and household
  gross earnings and expected state person-years.
- [Remarriage screen](docs/audits/remarriage_margin_screen_0_4.md): source-based refusal of an
  unsupported transition coefficient.
