# downstream

`downstream` calculates displacement impact through a causal consequence graph.
You supply an initiating event, such as worker displacement. The engine
composes published causal links and calculates how the event propagates through
a person, their family, and their community over time. Every computed effect
traces to cited research or an explicitly labeled structural assumption. Each result shows its uncertainty and
the full path that produced it. The engine has no runtime dependencies.

Worker displacement is the first seed event. It is not the boundary. The
long-term goal is a versioned graph of published causal evidence. Distant
consequences then emerge from cited bridges, not from a hand-written narrative.
The engine adds an effect only when the evidence supports the bridge, the
bridge is compatible, and the uncertainty is explicit. The engine models
synthetic people and populations. It does not predict the future of an
identified person. See `SPEC.md` for the full design rules.

<!-- BEGIN GENERATED ATTRIBUTION -->
The bibliography contains 110 sources and 216 named author records (people and organizations), 1979-2026.

The parameters cite 53 sources with 121 named author records; these are not counts of independent research teams.

The bibliography includes research, methods and context sources; inclusion does not establish peer review or independent validation. Modeled numbers carry their cited inputs and declared structural assumptions.

See [CREDITS.md](CREDITS.md) for the complete attribution record.
<!-- END GENERATED ATTRIBUTION -->

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

The gate requires at least 95% statement coverage and 90% branch coverage. The
current parameter set measures 97.3% and 94.0%. The suite contains Hypothesis
property tests for ledger envelopes, survival bounds, and county-pooling
convexity. Deterministic fixtures cover citations, published coefficients, and
regression examples.

Additional checks:

```sh
python -m ruff check src scripts        # correctness lint; blocks CI
python -m vulture                       # dead code; blocks CI
python scripts/benchmark.py             # numerical microbenchmarks
python -m mutmut run --max-children 4   # mutation campaign
python -m mutmut results --all true     # all mutation results
```

The benchmarks are comparison baselines. They are not a performance gate. See
`docs/TESTING_QUALITY.md` for the measured baseline and scaling notes. GitHub
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
```

## Command reference

| Command | Function |
| --- | --- |
| `family` | standard-family vignette with full citations |
| `scenario` | effect envelopes for a worker cohort; parameter-only and predictive intervals |
| `entity` | accepts a computed displacement exposure from a JSON file |
| `policy` | compares supplied baseline and policy exposures |
| `simulate` | Monte Carlo simulation for an outcome and place |
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

See `SPEC.md` §7–10 and `docs/MODEL_CARD.md`.

## Mortality timing

The default is `source_profile`: the displacement year, offsets 1, 2–3, 4–5,
and 6+ from Sullivan–von Wachter Table 5 column 3. Displacement occupies
follow-up year 1, so +6 starts in year 7. `source_aligned` exists only to
reproduce the former incomplete timing. `immediate_sustained` is a sensitivity
assumption.

## Website readiness repairs (0.3.0)

Engine 0.3.0 / parameters v1.49 enforce county mortality compatibility and posterior arithmetic, use the complete mortality profile in validation and exports, share repeated transmission draws, preserve custom sampling context, and reject invalid or nonfinite public inputs. Credits regenerate from full author identities. The methods paper uses independent net-job exposure and readable labels; [the HTML methods companion](docs/methods.html) is available for website integration.

Default scenario and entity counts are **illustrative reference calculations**, with `applicability.eligible_for_public_headline = false` on each outcome. A reviewed conditional transport decision requires structured `target_population` fields (`sex`, `age`, `worker_tenure`, `geography`, `calendar_window`, `exposure_type`, `children_sex`) and per-outcome `applicability_decisions` (`status: reviewed`, `reviewer`, `rationale`, `citations`). Incompatible target demographics block the corresponding outcome. The adapter accepts this metadata on `DocumentedExposure` or `ScenarioInput`. A reviewed transport decision does not establish independent empirical validation.

Website consumers must preserve outcome applicability, baseline derivation notes, lifetime versus follow-up horizons, support-envelope versus parameter-interval labels, blocked outcomes and fallback provenance. Use bundle content identities for cache keys and retain scenario `input_content_sha256`. Actual site rendering and production cache invalidation require integration outside this repository.

## Engine corrections (0.2.0)

Engine 0.2.0 corrects mortality odds-to-risk conversion and survival timing. It
scales optional place effects as a same-place displacement-loss contrast. It
fixes signed uncertainty envelopes and normal/lognormal analytic moments. See
`docs/MATH_REVIEW.md` for the findings and remaining assumptions. Correlated
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
| `SPEC.md` | the algorithm: graph primitives, composition, uncertainty, citation rules |
| `params/` | versioned parameter set, node units, baselines, `references.bib` |
| `src/downstream/` | DAG engine, typed ledger, modules, Monte Carlo, audit, validation |
| `tests/` | the compute checks (`pytest`) |
| `paper/` | the methods paper (`make -C paper`) |
| `CREDITS.md` | every researcher, study, and DOI, computed from the bibliography |
| `scripts/` | quality gate, benchmarks, data acquisition |
| `docs/` | plans and binding rules; see below |

Key documents:

- `docs/CITING.md` — the binding citation and evidence-tier rules
- `docs/ATTRIBUTION.md` — how credit is given and kept exact
- `docs/QUEUED_EXTRACTIONS.md` — modeled links that await their number
- `docs/PRIOR_ATTEMPTS.md` — SimPaths, LifeSim, DYNASIM, the Future Elderly Model
- `docs/MODEL_CARD.md`, `docs/MATH_REVIEW.md` — model limits and corrections
- Plans: `docs/LIFE_COURSE_RESEARCH_PLAN.md`, `docs/CAUSAL_GRAPH_PLAN.md`,
  `docs/WEBSITE_EXPERIENCE_PLAN.md`, `docs/LITERATURE_ACQUISITION_PLAN.md`

## Companion project

[xh1b.org/downstream](https://xh1b.org/downstream) integrates this model into
employer, county, state, and family surfaces. Integration is in progress. It is
deferred while the team strengthens this model. This repo contains only the model, the
parameters, and the paper. The database runner and its record-selection rules
belong to the companion project.

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
saved JSON. See [version comparisons](docs/VERSION_COMPARISON.md) and the
[release checklist](docs/OPEN_SOURCE_RELEASE.md).

## License

MIT. See `LICENSE`.
