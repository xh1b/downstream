# downstream

An evidence-locked causal consequence graph: a scientific model of how an
event or changed life condition propagates through a person, their family, and
their community over time. Fully open source.

Worker displacement is the first seed event, not the boundary of the project.
The long-term goal is to grow a versioned graph of published causal evidence so
that distant consequences emerge from cited bridges rather than from a
hand-authored narrative. For example, a modelled event may alter earnings,
family stability, childhood conditions, later adult outcomes, and eventually a
later generation's outcomes — but only when every bridge is supported,
compatible, and explicit about its uncertainty.

The engine is descriptive, not agenda-driven: it retains harmful, beneficial,
null, and conflicting results; reports structural alternatives rather than
silently choosing a preferred story; and blocks paths that the evidence does
not support. It models distributions for synthetic people and populations,
never the destiny of an identified person.

Incorporates the findings of 81 peer-reviewed studies by 166
researchers (1979-2023); its parameters rest directly on 19 studies
by 43 research teams. The claim is computed from the bibliography —
see CREDITS.md and `downstream credits` — never asserted.

Every modeled effect traces to a published study. Current parameter rows carry
their citation, evidence precision tier, population scope, and uncertainty
band. As the graph expands, every edge must additionally carry time semantics
and causal-role metadata. Missing bridges fail loudly. Every generated result
must expose its uncertainty and the path that produced it; the model publishes
its own misses.

- `SPEC.md` — the algorithm: graph primitives, composition, uncertainty, and
  what is computed from which citations
- `docs/LIFE_COURSE_RESEARCH_PLAN.md` — research goals for a person-and-place
  simulator, beginning with baseline household trajectories and a validated
  five-year event comparison
- `docs/CAUSAL_GRAPH_PLAN.md` — model records and composition rules supporting
  the research milestones
- `docs/WEBSITE_EXPERIENCE_PLAN.md` — the future calculator's user journey,
  explanations, visual direction, usability evaluation, and release criteria
- `docs/LITERATURE_ACQUISITION_PLAN.md` — reproducible corpus-building plan
  and initial DOI/open-access acquisition batch
- `params/` — the parameter set (versioned), node units, baselines, references.bib
- `src/downstream/` — the DAG engine, typed ledger (level / gap / direct /
  rate / elasticity composition), modules, scenario aggregation, Monte
  Carlo, audit, validation
- `CREDITS.md` — the computed collective: every researcher, every study, every DOI
- `docs/CITING.md` — the binding citation and evidence-tier rules
- `docs/ATTRIBUTION.md` — how credit is given and kept exact
- `docs/QUEUED_EXTRACTIONS.md` — modeled links awaiting their number, with
  the exact extraction target named
- `docs/PRIOR_ATTEMPTS.md` — related work, including SimPaths, LifeSim,
  DYNASIM, and the Future Elderly Model; similarities and lessons to investigate
- `paper/` — `make` builds `downstream.pdf` (methods paper)
- `tests/` — the compute checks (`pytest tests/`)

CLI:

```
downstream family        # the standard-family vignette, fully cited
downstream scenario --workers 1000  # envelopes + parameter-only and predictive intervals
downstream entity --input exposure.json
downstream simulate --outcome child --place national --draws 1000
downstream sensitivity --outcome child --place national
downstream explain --text   # a claim walked from headline to citations
downstream sensitivity      # Sobol: what drives the remaining range
downstream sensitivity --ci 5   # ...with seed-replicate design noise
downstream knobs --action sweep --link 'earnings_shock->mortality_sustained' --values 1.15,1.17,1.20
downstream knobs --action voi --outcome grandchild   # which knob is worth pinning next
downstream infer --outcome grandchild    # exact moments + normal band (no seed)
downstream ensemble     # structural-variant spread (composition assumptions priced)
downstream synthesize --input studies.csv  # same-scale random-effects evidence synthesis (not parameter admission)
downstream county-posterior --input county_counts.csv --key 01001 --outcome mortality --time-window 2015-19 --national-rate .004944 --national-population-scope "US prime-age men 45-54" --national-citation cdc_wonder --prior-person-years 2000
downstream county-wonder-posterior --export counties.tsv --metadata query.json --key 01001 --national-rate .004944 --prior-person-years 2000
downstream infer --outcome grandchild --action closure   # do the 90% bands cover 90%?
downstream audit         # parameter/citation/DAG/unit checks
downstream validate      # V0 internal consistency + V1 retrodiction target
downstream citations     # coverage report
downstream simulate --links a,b --kinds direct,gap
```

Uncertainty methodology: Latin Hypercube Sampling, log-space sampling
for ratio parameters, optional declared rank correlation (empty until
citable), Sobol sensitivity, CRPS/coverage scoring for the validation
program. See `SPEC.md` §7-10 and `docs/MODEL_CARD.md`.

`scenario` samples the count headlines jointly and adds a central 90%
**parameter-only** interval to each result. Its existing `low`/`high`
fields remain support envelopes, not confidence intervals. Documented
exposure, baseline estimation, county measurement/pooling, structural
assumptions, and unmodeled pathways are separately labeled as fixed or
excluded rather than folded into a falsely comprehensive band.

For integer worker cohorts, it also reports a separately labeled
posterior-predictive mortality simulation: parameter draws plus binomial
variation in deaths for new exposed and counterfactual reference cohorts.
That contrast is not a paired individual-level causal-outcome distribution.
Fractional worker-equivalent aggregates retain expected effects only.

Mortality defaults to `source_profile`: the extracted displacement, offset 1,
offsets 2–3, offsets 4–5, and offset 6+ profile from Sullivan--von Wachter Table 5 column 3.
With displacement occupying follow-up year 1, +6 begins in year 7.
`source_aligned` is retained only to reproduce the former incomplete timing;
`immediate_sustained` remains a sensitivity assumption.

Companion project: [xh1b.org/downstream](https://xh1b.org/downstream). Integration
into its employer, county, state, and family surfaces is in progress. This repo
contains only the model, the parameters, and the paper — no confidential material.

Place experiments accept a `places.csv` key through `--place` on
`simulate --outcome child|grandchild`, `sensitivity` (including `--ci`),
and `knobs` (sweep and VOI). The mobility parameter is recomputed for
every draw or pin. Place measurements and pooling weights are fixed;
these bands do not include uncertainty in county measurements. Output
includes the place sources and the declared composition assumption.
Arbitrary `simulate --links` chains do not accept `--place`.

`entity --input exposure.json` accepts an already computed exposure:

```json
{
  "subject_id": "example",
  "subject_type": "employer",
  "displaced_workers": 100,
  "source": "reference to the documented input records",
  "method": "reference to the upstream exposure calculation"
}
```

The entity adapter uses the same scenario arithmetic and accepts
`--place`, `--children`, `--tradable-share`, and `--exposure-years`.
It preserves source and method references. The caller owns the exposure
conversion: filing counts, wage-gap dollars, and WARN notices cannot be
passed as worker counts without an explicit upstream method. Persons
use `subject_type: "person"`; results describe population-average
modeled impacts, never an individual's predicted outcomes.

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

These are synthetic fixture values. The components are already in
worker-equivalent units. The adapter preserves `americans_displaced`,
requires it to equal `total`, and checks the component sum within 0.002
(the maximum discrepancy from rounding three components and their total
to three decimal places). Employer rows require `warn_layoffs`; person
rows may omit it. Missing fields and empty breakdowns fail, including an
empty breakdown paired with zero exposure. A known zero must carry
explicit zero components. Additional breakdown fields remain caller-owned
and do not enter the exposure calculation. The database runner and its
record-selection rules belong to the companion project.

Build the methods paper with `make -C paper`. The build regenerates its
parameter inventory, V1 scorecard, and chart coordinates from the engine, then compiles
`paper/downstream.pdf`. `paper/generated/results.json` contains the full
validation output and a source-content hash. Generated files are ignored
by git; `paper/build_tables.py` generates the numerical data. Vector diagrams
and chart layouts live in `paper/figures/`. The PDF uses TikZ and PGFPlots,
with the numerical scorecard tables retained in an appendix.


Engine 0.2.0 corrects mortality odds-to-risk conversion and survival timing,
uses a source-offset mortality profile, scales optional place effects as a
same-place displacement-loss contrast, and fixes
signed uncertainty envelopes and normal/lognormal analytic moments. See
`docs/MATH_REVIEW.md` for the findings and remaining assumptions.
Historical scenario arithmetic is available through
`--mortality-method legacy_additive --place-application legacy_repeated`.

The September 10 review additionally repairs independent copula designs,
custom-chain connectivity and starting values, county predictive baselines,
and rate-likelihood semantics. Generic county mortality values are not used
by scenarios; county results remain experimental until their matching
population/window metadata enter through a validated integration bridge.
Correlated Monte Carlo results change at historical seeds after the copula
repair. Legacy additive mortality retains expected counts only.

`downstream policy --input comparison.json` compares supplied baseline and
policy exposures. Each case has `name`, `source`, `method`, and a `scenario`
object with `displaced_workers`; optional `exposure_low`, `exposure_high`,
and `place_key` add exposure uncertainty and geography. Output reports
policy minus baseline. It does not infer how a policy causes displacement.

`downstream bundle --out /path/to/new-directory` exports a standalone engine
and data bundle with per-file checksums and a content-based version.
The destination must not exist. Integration into XH1B is deferred while
this model is strengthened.

`downstream forecast-register --input proposal.json --out registration.json`
freezes a prospective forecast locally. `forecast-score` reports misses as
well as coverage after the outcome window. Required proposal fields are
listed in `src/downstream/forecast_registry.py`; registration still needs
an independent timestamp to establish public preregistration.

## Test quality

Install the development extras, then run the complete test and coverage gate:

```sh
python -m pip install -e '.[dev]'
python -m coverage run -m pytest
python -m coverage json -o coverage.json
python scripts/quality_gate.py coverage.json
```

The gate requires at least 80% statement coverage and 70% branch coverage. The
suite includes Hypothesis property tests for ledger envelopes, mortality
survival bounds, and county-pooling convexity; deterministic fixtures remain
for citations, published coefficients, and regression examples.

Ruff runs as a blocking CI check for production code and scripts. Run it
locally with `python -m ruff check src scripts`.

Run the local numerical microbenchmarks with `python scripts/benchmark.py`.
They are comparison baselines, not a flaky performance gate; see
`docs/TESTING_QUALITY.md` for the measured baseline and scaling notes.

GitHub Actions runs a fast property/FSM/CLI contract suite for changes, the
full coverage gate for pull requests, and a scheduled mutation-plus-benchmark
job. Run the mutation campaign locally with `python -m mutmut run
--max-children 4`; inspect all results with `python -m mutmut results --all
true`.
