# Integrating Downstream

<!-- @ref:doc-integration; @tag:consumer -->
<!-- @link:docs-index; @link:code-cli; @link:code-scenario; @link:paper-exposure. -->

Use the package or JSON CLI to evaluate a supplied scenario. Read the
[model card](model_card.md) before selecting a calculation. The authoritative
calling contracts are the dataclasses, loaders and public functions in
[scenario.py](../src/downstream/scenario.py), [employer.py](../src/downstream/employer.py)
and the outcome modules below. The paper explains equations and rationale
(@link:paper-exposure, @link:paper-counts); this guide describes software use.

Jump to [examples](#executable-examples), [input fields/API/CLI](#command-reference),
[result fields](#result-fields-and-units), [errors and compatibility](#errors-and-compatibility),
[cache identity](#identity-and-handoff), or [troubleshooting](#troubleshooting).
Outcome contracts: [mortality](#mortality-outputs), [children](#child-and-descendant-outputs),
[household](#annual-household-comparisons), [receiving community](#receiving-community-adapter).

## Choose an entry point

| Input or purpose | Entry point | Contract checks |
| --- | --- | --- |
| Worker exposure and assumptions | `ScenarioInput`, `compute_counts`, `sample_counts`; `downstream scenario` | [Scenario tests](../tests/test_vignette_scenario_mc.py) |
| Documented entity exposure | `DocumentedExposure`, `compute_entity_counts`; `downstream entity` | [Exposure tests](../tests/test_exposure_semantics.py) |
| Receiving-population shares | `downstream receiving-community` | [Receiving adapter tests](../tests/test_receiving_adapter.py) |
| Annual adult/household inputs | `household_comparison`; `downstream household` | [Household summary tests](../tests/test_household_summary.py) |
| Supported male age-at-displacement strata | `downstream mortality-cohort` | [Mortality admission tests](../tests/test_mortality_admission_0_4.py) |
| Child/descendant explanation or source support | `child_gap_view`, `child_support_report` | [Gap tests](../tests/test_child_gap_view.py), [support tests](../tests/test_child_support.py) |

## Executable examples

<!-- @ref:integration-examples; @link:script-doccheck; @link:test-documentation-checks. -->

These examples run from the checkout root with the development environment.
`make check-docs` executes every `pycon` block in the five maintained guides.
The assertions check contracts, rather than pinning transient numerical outputs.
Shell recipes and task-mutation commands are not executed by the docs checker.

Load one bundle and inspect a conditional reference result:

```pycon
>>> from downstream.params import load_all
>>> from downstream.scenario import ScenarioInput, compute_counts
>>> bundle = load_all()
>>> scenario = ScenarioInput(displaced_workers=1000, n_children=2)
>>> result = compute_counts(bundle["params"], bundle["baselines"], scenario)
>>> sorted(result["modeled"])
['child_lifetime_earnings_lost_usd', 'excess_deaths']
>>> result["modeled"]["excess_deaths"]["applicability"]["eligible_for_public_headline"]
False
>>> [row["outcome"] for row in result["blocked"]]
['local_service_jobs_lost']
```

The local-job result is blocked because worker displacement does not identify
net tradable-job loss. The computed mortality/child reference remains available;
its headline eligibility is a separate decision. Known-incompatible child
metadata withholds the child path instead of assigning a zero response:

```pycon
>>> from downstream.params import load_all
>>> from downstream.scenario import ScenarioInput, compute_counts
>>> bundle = load_all()
>>> target = ScenarioInput(1000, n_children=1, child_profiles=[{"age_at_displacement": 4, "sex": "Female"}])
>>> result = compute_counts(bundle["params"], bundle["baselines"], target)
>>> "child_lifetime_earnings_lost_usd" in result["modeled"]
False
>>> any(row["outcome"] == "child_lifetime_earnings_lost_usd" for row in result["blocked"])
True
>>> ScenarioInput(displaced_workers=-1)
Traceback (most recent call last):
...
ValueError: displaced_workers must be finite and nonnegative
```

CLI output can be parsed without scraping human-readable summaries. This smoke
example uses two draws to check shape only; it does not qualify interval precision:

```pycon
>>> import json, subprocess, sys
>>> command = [sys.executable, "-m", "downstream.cli", "scenario", "--workers", "1000", "--draws", "2"]
>>> completed = subprocess.run(command, capture_output=True, text=True, check=True)
>>> result = json.loads(completed.stdout)
>>> "parameter_interval_90" in result["modeled"]["excess_deaths"]
True
>>> result["exposure"]["displaced_workers"]
1000.0
```

Custom-data APIs that load source contrasts also need the custom `params_dir`;
missing custom files must not fall back to bundled evidence. See the
[calling reference](#command-reference) and source-specific sections below.

## Exposure and event metadata

<!-- @ref:doc-exposure-semantics-0-4; @tag:exposure -->
<!-- @link:code-employer; @link:code-scenario; @link:test-exposure-semantics; @link:paper-exposure. -->

`DocumentedExposure` takes subject identity, `displaced_workers`, `source`
and `method`, plus optional `exposure_semantics`. The adapter uses the supplied
authoritative quantity. It never converts wages, filings, worker-years or raw
audit components into displaced people.

```json
{
  "subject_id": "synthetic-employer",
  "subject_type": "employer",
  "displaced_workers": 100.125,
  "source": "synthetic upstream aggregate",
  "method": "caller-owned exposure formula",
  "exposure_semantics": {
    "schema": "downstream-exposure-semantics/1",
    "kind": "reference_worker_equivalents",
    "method_version": "upstream/2",
    "components": {
      "requested_positions": {"value": 100.125, "unit": "worker_equivalents"}
    },
    "record_window": {"start": "2010-01-01", "end": "2025-12-31"},
    "overlap": {"status": "not_deduplicated", "note": "Repeated records can overlap."},
    "conversion_assumptions": ["Reference scaling under the upstream method."],
    "event_time": {"basis": "historical_aggregate"}
  }
}
```

This fixture documents shape, not an empirical conversion. Unknown fields and
schema versions fail. Optional fields remain explicitly unknown when omitted.

| Field | Accepted meaning |
| --- | --- |
| `kind` | `unspecified_reference_exposure`, `reference_worker_equivalents`, or `unique_displaced_people`. Unique people require an integer. |
| `components` | Named finite nonnegative values with explicit units; preserved, never automatically added or converted. |
| `method_version` | Nonempty upstream version, separate from the required method description. |
| `record_window` | Ordered inclusive ISO dates for records, not an inferred event date. |
| `overlap` | `unknown`, `not_deduplicated`, `deduplicated`, or `disjoint_by_design`; nonunknown claims need a note. Unique people cannot be labeled not deduplicated. |
| `conversion_assumptions` | List of nonempty caller assumptions, retained without endorsement. |
| `event_time` | `unknown`, `single_event`, `historical_aggregate`, or `distributed_events`; a single event requires its ISO date. |

The warehouse mapping retains its reported rounded total and worker-equivalent
`base`, `wage_depression` and `warn_layoffs` components. Supplied metadata cannot
replace those components or relabel the aggregate as unique people.

`integer_cohort_count_basis_eligible` requires unique people, an integer count,
documented deduplication/disjointness, and one dated event. It qualifies only
the caller's count basis. It does not verify those claims, admit transport or
compute process uncertainty. Fractional equivalents can scale expectations;
rounding them does not create a binomial cohort.

`calendar_forecast_available` remains false for the entity adapter. Follow-up
is relative to a modeled event; record dates and distributed histories do not
create a calendar forecast. Missing target/child demographics stay null.
`exposure_input_sha256` fingerprints full exposure provenance; retain it beside
the scenario's separate `input_content_sha256`.

## Read a result without losing its contract

Preserve points, signed support endpoints, units, source steps, resolved
baseline/place provenance, target/child applicability, structural projection
labels, blocked reasons, versions and input hashes. Keep optional valuation,
parameter intervals, persistence comparisons and sensitivity reports.

Blocked means unavailable, not zero. Unknown demographics may leave an
illustrative reference available while headline eligibility stays false.
Reviewed conditional transport needs a reviewer, rationale and citations;
exposure metadata cannot confer it.

| Range or comparison | Consumer interpretation |
| --- | --- |
| Parameter-support envelope | Bounds over declared inputs; not a confidence interval. |
| Central parameter interval | Joint parameter propagation conditional on fixed scenario assumptions. |
| Process/predictive distribution | Available only in separately qualified tools; retain their cohort assumptions. |
| Structural alternative | Named model choice without an inferred probability weight. |
| Removal/endpoint experiment | Refit with other inputs fixed; not an additive causal share. |

## Mortality outputs

<!-- @ref:integration-mortality; @tag:mortality -->
<!-- @link:code-mortality; @link:code-mortality-profiles; @link:code-mortality-strata; @link:paper-counts; @link:paper-mortality-strata. -->

Default `source_profile` uses source offsets 0, +1, +2–3, +4–5 and +6+.
Offset 0 is follow-up year one; +6 starts year seven. The standard response
needs a compatible male 45–54 all-cause baseline. A verified rate for another
group does not admit the displacement response for that group. Explicit
profiles/mixtures retain population and source window. Unsupported positive
exposure withholds the whole-cohort total. See [baseline import](evidence.md#mortality-baseline-import).

The separate age-stratum tool uses Table 7 coefficients for men displaced at
30–39, 40–49, 50–59 or 60–69 with tenure at least six years. Custom rows must
match treatment, comparator, scale, sex, exact age band, tenure and window.
`constant_source_window_log_odds` changes attained-age baselines while holding
the source-window response constant. Headline eligibility stays false. See
[admission tests](../tests/test_mortality_admission_0_4.py) and the
[applicability review](audits/mortality_applicability_0_4.md).

The separate `mortality_covariance.linear_se_bounds` and
`additive_phase_diagnostic` APIs inspect additive coefficients with unknown
covariance; [analyze_mortality_covariance.py](../scripts/analyze_mortality_covariance.py)
reproduces the diagnostic. They do not admit a response or generate joint
mortality draws. The bound and proof are in @link:paper-mortality-covariance;
the [review receipt](audits/mortality_covariance_0_4.md) records source details.

### Persistence comparison

<!-- @ref:doc-mortality-persistence-sensitivity -->
<!-- @link:code-mortality-robustness; @link:test-mortality-robustness; @link:paper-counts. -->

`modeled.excess_deaths.persistence_sensitivity` compares `source_profile` with
`no_sustained_excess`: early phases stay fixed, offset +6 onward becomes OR=1.
Entity and policy-arm scenario records inherit it. Both arms use the same
exposure, baseline, early inputs and shared draws. Render each structure and
its conditional interval separately, plus the shared-draw difference where
available. Do not pool arms, assign probabilities or call their spread a
confidence interval. This hybrid is not a Swedish-study replication. The
[persistence analysis](audits/mortality_persistence_analysis_2026-10-14.md)
retains the detailed review; the paper explains the survival calculation.

## Child and descendant outputs

<!-- @ref:doc-child-gap-view; @tag:children -->
<!-- @link:code-child-gap-view; @link:code-children; @link:code-transmissions; @link:code-valuation; @link:paper-children. -->

`child_gap_view(params, baselines, scenario, ...)` returns child and grandchild
relative earnings gaps with source steps and eligibility. The great-grandchild
row is explicitly unavailable following source withdrawal.
Positive means earnings below reference; negative means above. Preserve benefits
and intervals crossing zero. Descendant paths are structural projections;
repeated relationships share an exact uncertainty draw.

Only the child row can carry the existing aggregate lifetime dollar conversion
in `usd_2024`. Descendant populations/dollar baselines are not inferred.
Optional age-timed present valuation is separate from undiscounted lifetime
conversion. Zero exposure can leave a per-person gap while aggregate dollars
become zero. Known incompatible age/sex/parent/event metadata withhold the
path; unknown children do not gain headline eligibility.

Place rows retain `initial_only` or `legacy_repeated` and remain exploratory.
Do not add generations, or add divorce, school and family-size paths to the
direct child effect. `housing_chain` stays unavailable until the displacement/
foreclosure, geographic overlap, property-dollar and household-resource
bridges exist. Its total is null, not zero.

### Inspect source support

<!-- @ref:doc-child-support-0-4 -->
<!-- @link:code-child-support; @link:code-child-applicability; @link:test-child-support. -->

Use `child_support_report()` or the inspection script before selecting a subgroup.
A validated `ScenarioInput` and optional numeric `parent_tenure_years` let the
report inspect supplied target metadata:

```sh
python3 scripts/inspect_child_support.py
python3 scripts/inspect_child_support.py --input scenario.json --parent-tenure-years 6
```

The source covers Canadian sons aged 10–14 at fathers' 1980–1982 firm closure,
parent tenure at least two years, and son earnings averaged 1995–1999 at ages
25–33. Income groups use fathers' 1978–1979 income. Table 2 column 3 is the
overall contrast; Table 8 columns 1–4 stay separate. A qualitative tenure label
does not establish a numeric minimum.

States are `refused`, `unknown`, `conditional_transport` and
`reviewed_conditional_transport`. Inspection never creates headline eligibility
or changes scenario gates. Country/period differences remain transport
conditions. Beta/SE transforms give marginal approximate 95% Wald intervals,
not joint group bands or lifetime uncertainty. All quartile intervals cross
zero; Q3 retains its beneficial point. No income-group pooling occurs.

### Published child-source selection

<!-- @ref:child-source-selection; @tag:children -->
<!-- @link:code-child-support; @link:test-child-support; @link:paper-children. -->

`source_selection_assessment` records additional restrictions from Oreopoulos,
Page and Stevens (2008), pp. 459, 462–463 (PDF pp. 6, 9–10), with the pinned
source hash. These are sample-selection conditions, not newly admitted effects:

| Dimension | Published restriction |
| --- | --- |
| Father age | 30–50 in 1978; a target's current or event-age band does not establish this. |
| Tax records | Fathers with missing tax records are excluded. |
| Initial firm | 2–500 fathers represented in the IID sample; total employer headcount is a different quantity. |
| Earnings outliers | Fathers earning over CAD 1,000,000 in 1999 purchasing power in a single year are excluded. |
| Preclosure history | Same firm in 1978 and 1979; no unemployment-insurance receipt in those years. |
| Closure definition | No IID fathers remain at the firm in later years through 1999; apparent closures with at least 35% moving to one new firm are excluded. |

The report leaves this assessment `unassessed`: `ScenarioInput` and numeric
tenure do not supply all these conditions. `support_state_scope` identifies the
dimensions actually checked by `support_state`. Even `reviewed_conditional_transport`
does not establish that the additional selection conditions match a target.
Custom contrast libraries must retain the cited publication and pinned hash
before this source-specific description can be attached.

The source's main text specifies sons aged 10–14 **in 1980**, while footnote 9
also describes a restriction to children at most 14 **in 1982**. These calendar
references do not establish a response curve indexed by age at each closure.
The report records this unresolved detail in `child_age_reference`; existing
age gates and numerical estimates remain as documented above. Wider child ages,
other countries, and exact event-age transport still need source reconciliation.
The [acquisition manifest](../validation/followthrough_sources.json) identifies
the inspected PDF; extraction decisions and receipts are on
@task:2026-10-14-child-heterogeneity.

## Annual household comparisons

<!-- @ref:doc-household-comparison-0-4; @tag:household -->
<!-- @link:code-household; @link:test-household-summary; @link:paper-household. -->

`household_comparison(payload, params_dir=None)` returns annual rows and
`summary.members`/`summary.household`. Each summary has `reference`,
`displacement` and `displacement_minus_reference` blocks with cumulative
`gross_earnings_usd_2024` and E/U/N `expected_state_person_years`. Preserve
member order/IDs. Gross undiscounted earnings exclude taxes, transfers,
savings, consumption, housing and child earnings.

Negative paired earnings differences mean less earnings. Use returned paired
differences rather than subtracting rounded displays; the legacy cumulative
field equals the household difference. Member state-years sum to follow-up;
household state-years sum to adults times follow-up. State-time differences
sum to zero. Summing annual expectations does not identify joint unemployment
risk, partner responses or a household-resource distribution.

`year_after_event` is zero-based; `follow_up_year_number` is one-based.
Intervals are `[start, end_exclusive)`. Optional `event.calendar_year`
(integer 1900–2200) labels whole-year intervals. Without it, calendar labels
stay null. Five years from 2026 labels 2026–2030 with exclusive end 2031.
The source's 2021–2022 window is never substituted for a missing event year.

The loader requires positive source counts, valid normalized-for-rounding
probabilities and explicit sparse-cell acceptance. During forced unemployment,
overwritten states do not cause transition lookups; actually used reference,
partner and post-spell transitions remain gated. The stationary annual Markov
reuse of observational shares does not identify causal recovery or a full
prediction interval.

```sh
downstream household --input validation/household_five_year_input.json
```

The checked-in household fixture can be used directly:

```pycon
>>> import json
>>> from pathlib import Path
>>> from downstream.household import household_comparison
>>> payload = json.loads(Path("validation/household_five_year_input.json").read_text())
>>> summary = household_comparison(payload)["summary"]["household"]
>>> sorted(summary)
['displacement', 'displacement_minus_reference', 'reference']
>>> summary["displacement_minus_reference"]["gross_earnings_usd_2024"] < 0
True
```

The [saved input](../validation/household_five_year_input.json),
[result](../validation/household_five_year_result.json) and
[reconciliation tests](../tests/test_household_summary.py) specify and verify it.

## Receiving-community adapter

<!-- @ref:doc-receiving-community-0-4; @tag:receiving -->
<!-- @link:code-receiving-community; @link:test-receiving-adapter; @link:test-receiving-community. -->

`downstream receiving-community --input receiving.json` accepts one named
source model. Generic `immigrant_influx` links are retired. A worker exposure
cannot be supplied as arrivals or population-share growth.

| Model | Exposure margin / response window | Compatible baseline outcome |
| --- | --- | --- |
| `light_miller_2018` | `undocumented_residents` / `annual_one_year_lag`; percentage-point share change | `violent_crime` |
| `bianchi_2010` | `valid_residence_permit_residents` / `ten_year_endpoint_difference`; post/reference share ratio | `total_crime` |

`unit: population_share_fraction` takes `reference_share` and `post_share`;
0.02 means 2%. Semi-log permits zero shares; log-share needs both positive.
Alternatively, `unit: resident_counts` requires reference/post immigrant counts
and reference/post total populations. The adapter derives both shares,
including changing denominators. Source/population descriptions are required.
Unknown fields, unsupported margins/horizons and worker counts fail. Optional
`transport_assumption` is caller rationale, not reviewed applicability.
[Adapter fixtures](../tests/test_receiving_adapter.py) provide complete payloads.
The [source-unit receipt](../validation/receiving_source_units_20261015.json)
records versions, hashes and locators.

Without a baseline, `rate_ratio` and signed `percent_rate_change` remain
available. A baseline must match outcome, population, annual endpoint window
and `incidents_per_100000_residents`. Post population additionally enables
annual endpoint incident changes using that same population for both arms.
Missing baseline/population means unavailable counts. Do not multiply an
endpoint contrast by ten years to manufacture cumulative incidents.

Retain source causal role, version limits, fingerprints, fixed-input support
and the unchanged residual retransformation-factor assumption. Headline
eligibility stays false. Violent/total crime overlap and come from different
populations; do not add them. Unmodeled channels stay unknown. The
[evidence scan](audits/immigration_replacement_evidence_scan_2026-09-14.md)
retains source-unit review.

## Per-result sensitivity

<!-- @ref:doc-result-sensitivity; @tag:uncertainty -->
<!-- @link:code-result-sensitivity; @link:code-sensitivity; @link:test-result-sensitivity; @link:paper-sensitivity. -->

Public scenario counts and optional child valuations carry `sensitivity`;
entity/policy arms inherit it. Reports retain `reference_point`, ordered
`effect_drivers`, `effect_removed`, `supported_range`, `fixed_inputs` and
optional `variance_attribution`. `change_from_reference` is variant minus
reference; `reference_minus_variant` has the opposite sign.

Experiments refit under the same custom sources, subgroup, place and gates.
They cannot unblock a population. Removal effects do not sum. Source-endpoint
spans are not variance shares. Fixed inputs acquire no inferred distribution.
Internal `_raw=True` results omit reports; consumers normalizing raw points
must obtain reports from a public calculation.

```sh
downstream scenario --workers 1000 --draws 2000 --seed 1901 --sensitivity-base 512
```

`draws` controls the parameter interval; `sensitivity_base` controls a separate
variance design. Correlated parameters stay in connected joint blocks.
`S_first`/`S_total` can leave [0,1] and are not clipped. Total indices need not
sum to one. Constant outcomes have no decomposition. This does not decompose
policy deltas, household trajectories, process outcomes or every source effect.
The paper explains the estimators (@link:paper-sensitivity, @link:paper-uncertainty).

## Scaling, mixtures and acceptance fixtures

<!-- @ref:doc-consumer-fixtures-0-4; @tag:consumer -->
<!-- @link:code-consumer; @link:code-bundle; @link:test-consumer-api; @link:test-consumer-fixtures; @link:script-build-consumer-fixtures. -->

Use `downstream.consumer.scale_outcome` and `mix_expected`; they return
independent copies and retain provenance. Declare a positive source worker
denominator. A zero-worker scenario cannot identify a per-worker coefficient.
Normalize raw engine points with public metadata; scaling a rounded one-worker
death count can erase the effect.

For factor `s`, scale result-valued points, bounds, alternatives, signed changes
and experiment spans by `s`; output variance scales by `s²`. Coefficients,
source endpoints, baseline rates, per-family schedules, metadata and variance
indices do not scale. At zero exposure variance indices are undefined. Label
the source basis separately; a display transform is not a native refit.
Each reported interval scales exactly once, including when the sampled main
result and its source-profile alternative share the same interval object.

Mixture weights must be finite, nonnegative and sum to one. Active components
need the same worker denominator; mortality additionally needs the same
follow-up, method and phase timing. A positive-weight blocked component
withholds the total. Every active component must be eligible for a reviewed
mixture. Retain each baseline, source index, weight and identity; never inherit
the first component's context.

Apply the same weights to all structural alternatives and removal comparisons.
Endpoint experiments need matching input endpoints. A missing coefficient
leaves a component at reference for removal. Missing sensitivity can leave the
point available while withholding comparisons. Do not average quantiles.
Mixture parameter intervals and variance attribution remain unavailable until
a joint draw/dependence calculation exists.

```sh
python3 scripts/build_consumer_fixtures.py --check
.venv/bin/python -m pytest -q tests/test_consumer_api.py tests/test_consumer_fixtures.py
```

The [fixture pack](../validation/consumer_fixtures_0_4.json) covers national,
county/fallback, zero/fractional exposure, signed child contrasts, valuation,
synthetic transport decisions, blocked outcomes and nested mixtures. Small
draw designs test contracts, not research precision. Synthetic reviewers are
not evidence of a real transport review.

### Identity and handoff

Keep engine/parameter versions, scenario input hash, exposure hash where used,
bundle manifest/code identity and adapter identity distinct. A fixture digest
is not a bundle hash. Cache keys cover consumed inputs, place shares,
transport/cohort choices, exposure provenance and analysis settings (seed/base).
Edited browser results have a separate identity from their source receipt.

Before a companion handoff, freeze the candidate and regenerate bundle/fixtures
together. Verify installed-package/bundle behavior; compare native, scaled and
mixed fields; check JSON, HTML, Markdown and receipts for identical unavailable
states, signs and interval meanings. Inspect cache coverage, fallback disclosure,
runner selection and queue/lease behavior in the companion. Record deployment
receipts there. Local fixtures do not establish that an integration is deployed.

Snapshots use schema 3 and separate available parameters from retained
withdrawal records. Load the matching engine and parameter bundle together;
updating the raw CSV alone does not apply the source policy. Grouped reports
can include explicitly unavailable branches with null numeric fields. See
[the source-withdrawal contract](evidence.md#source-withdrawals-and-retained-records)
for archive fields, override refusals and consumer migration requirements.

## Warehouse inputs

<!-- @ref:integration-warehouse; @link:code-employer; @link:test-exposure-semantics. -->

`entity --input-format warehouse --input row.json` accepts the existing
upstream aggregate shape. This synthetic fixture preserves worker-equivalent
components; it does not identify unique displaced people:

```json
{
  "subject_id": "example",
  "subject_type": "employer",
  "source": "source aggregate and version",
  "americans_displaced": 137.125,
  "displacement_breakdown": {
    "base": 100,
    "wage_depression": 12.125,
    "warn_layoffs": 25,
    "total": 137.125,
    "formula": "caller-owned upstream exposure method"
  }
}
```

`americans_displaced` must equal `total`; component sums must reconcile within
0.002. Employer rows require `warn_layoffs`; person rows may omit it. Missing
fields and empty breakdowns fail, including at zero exposure: known zero requires
explicit zero components. Additional audit fields stay caller-owned and are
not added into the exposure calculation.

## Uncertainty and experiment tools

The generated command inventory lists all supported tools. Their mathematical
meaning is explained in the paper (@link:paper-uncertainty,
@link:paper-inference, @link:paper-sensitivity). Important calling distinctions:

- `simulate`, `sensitivity` and `knobs` accept a declared `--place` key. Place
  measurements/pooling weights remain fixed; custom `simulate --links` chains
  do not accept `--place`.
- `infer` uses an independent-input analytic contract and refuses incompatible
  repeated shared variables. It is not a substitute for the declared dependent
  production sampler.
- `uncertainty --input validation/uncertainty_budget_input.json` uses a separate
  national baseline/exposure/process contract; it does not extend every entity,
  county or demographic result into a full prediction interval.
- `ensemble` reports named structural variants without inferred probabilities.
  `policy --input comparison.json` subtracts supplied exposure scenarios; it
  does not infer a policy-to-displacement causal bridge. Each case needs `name`,
  `source`, `method` and a `scenario` with `displaced_workers`.
- `source_profile` is the default mortality timing. `source_aligned`,
  `immediate_sustained`, `legacy_additive` and `legacy_repeated` are explicit
  historical/sensitivity choices. They are never silently substituted.

Current dependence declarations live in [correlations.csv](../params/correlations.csv).
Their magnitude is declared judgment; a sampler feature is not evidence of
causal transport or an extracted study covariance.

### Declared uncertainty assumption cases

<!-- @ref:uncertainty-assumption-cases; @tag:uncertainty -->
<!-- @link:code-uncertainty-cases; @link:code-uncertainty-budget; @link:test-uncertainty-cases; @link:paper-uncertainty-budget. -->

The national `uncertainty` payload optionally accepts `assumption_cases`.
Each of up to 16 cases requires exactly `name`, `source`, `method`,
`mortality_log_odds_scale`, `exposure_rank` and `baseline_rank`. Names must be
unique and provenance strings nonempty. There are no default cases or weights.
Run the explicitly hypothetical [example input](../validation/uncertainty_assumptions_input.json):

```sh
downstream uncertainty --input validation/uncertainty_assumptions_input.json
```

The fixed finite scale changes each sampled mortality phase through
`OR_target = exp(scale * log(OR_source))`. One retains the source effect,
zero sets every phase to the null, and a negative scale reverses its direction.
These are caller declarations about transport, not extracted target effects or
estimated transport-error distributions. They do not change child effects.

Each rank setting is `independent`, `aligned` or `opposed`. Independent retains
the existing draw pairing. The alternatives reorder only the sampled exposure
or baseline marginal against the **signed source-profile excess-death probability
per worker at the pinned baseline and horizon**. Both input marginals and every
study parameter draw remain intact. Ties use the original draw index; a constant
anchor refuses aligned/opposed settings. These selected arrangements are
sensitivity experiments, not bounds over every possible dependence structure.

`assumption_sensitivity` returns each case's conditional 90% expected-effect
intervals, its separate persistence alternative and within-draw structural
difference, sampled-input summaries, and paired differences against the
original independent source reference. It supplies no case-specific process
interval or combined confidence envelope. The ordinary budget, its independent
process contrasts, and fixed-input parameter-only reference retain their scope.
Known demographic refusals still apply; every case stays headline-ineligible.
The [saved result](../validation/uncertainty_assumptions_result.json) uses 256
draws for illustration, not precision-qualified research intervals.

Calibrated transport error, empirically estimated cross-component dependence,
probabilities over structures, child/lifetime-profile uncertainty and unmodeled
pathways remain unavailable. For general guidance on transparent uncertainty and sensitivity analysis, see
the [JRC introductory guide](https://publications.jrc.ec.europa.eu/repository/handle/JRC122132).
That guidance supplies no empirical support for the illustrative case values.

## Result fields and units

<!-- @ref:integration-results; @link:code-scenario; @link:code-consumer. -->

The scenario API returns a mapping; `sample_counts` adds sampling reports to
that mapping. Other commands have their own shapes: household, receiving,
forecast and comparison results must not be parsed as scenario records.

| Field | Consumer contract |
| --- | --- |
| `engine_version`, `parameter_set_version` | Keep both version labels; they are not complete content identities. |
| `label`, `exposure` | Caller label and actual scenario assumptions, including worker basis and follow-up. |
| `modeled` | Available outcome records keyed by outcome name; never prefill a missing outcome with zero. |
| `blocked` | Records with `outcome` and `reason`; preserve them even when other outcomes compute. |
| `uncertainty` | Meaning of support bounds, fixed inputs and excluded uncertainties. |
| `assumptions` | Mortality method/timing, source profile contract and place application. |
| `multipliers`, `projection_eligibility` | Relative paths and evidence/projection status, separate from admitted absolute counts. |
| `target_population`, `child_applicability` | Declared target information and child source compatibility; missing information stays unknown. |
| `place` | Resolved place/provenance, or null at the national reference. |
| `input_content_sha256` | Native scenario input identity; preserve it through display transforms. |
| `parameter_uncertainty`, `predictive_uncertainty` | Optional sampling reports with their own availability, seed/design and exclusion metadata. |
| `child_valuation` | Optional present-value projection; separate from undiscounted lifetime dollars. |

Available scenario outcomes share `point`, `low`, `high`, `unit` and
`applicability`. Preserve their outcome-specific metadata too: mortality and
child-dollar rows provide `steps`, `baseline` and `interpretation`; local jobs
provide fields such as `citation`, `tier`, `job_class`, `population_scope` and
`support_note` instead. Public results attach sensitivity where supported;
persistence and `parameter_interval_90` are optional. Do not require every
outcome to have the same source-metadata shape.

```pycon
>>> from downstream.params import load_all
>>> from downstream.scenario import ScenarioInput, compute_counts
>>> bundle = load_all()
>>> scenario = ScenarioInput(1000, net_tradable_jobs_lost=100, local_job_mix="manufacturing")
>>> jobs = compute_counts(bundle["params"], bundle["baselines"], scenario)["modeled"]["local_service_jobs_lost"]
>>> {"point", "low", "high", "unit", "applicability"} <= jobs.keys()
True
>>> "citation" in jobs and "job_class" in jobs
True
```

Read the returned `unit`; mortality expectations are expected counts,
child dollars are aggregate lifetime `usd_2024`, and jobs use the independently
declared net-employment basis. Household earnings are gross follow-up totals;
receiving incidents are annual endpoint differences. These are distinct units
and windows even when each value is numeric.

The scenario has no universal JSON schema-version field. Exposure semantics,
consumer reports and other adapters can carry their own named schemas. Retain
each schema where present; do not manufacture one from an engine version.

## Errors and compatibility

<!-- @ref:integration-errors; @link:code-cli; @link:code-scenario; @link:code-bundle. -->

| Situation | Software behavior | Caller action |
| --- | --- | --- |
| Valid input with an unsupported outcome | Scenario returns a blocked record; CLI can exit 0 with other results. | Inspect `blocked` and applicability, not just the process exit code. |
| Missing/unverified required baseline | Normal mode blocks that conversion; `strict=True`/`--strict` raises/fails on missing baselines. | Supply compatible verified evidence; strict mode does not make every unavailable field an exception. |
| Malformed values, unsupported unit labels or invalid metadata shapes | APIs raise contract errors such as `ValueError`; missing files can raise `OSError`. | Correct the input; do not retry unchanged data as if it were transient. |
| Invalid CLI arguments or a caught data-contract failure | CLI writes errors to stderr and exits 2. `--help` exits 0. | Parse stdout as result data only after success. |
| Incompatible mixture basis or source endpoints | Consumer helpers refuse incompatible points/experiments or mark joint analysis unavailable. | Refit compatible components; never inherit the first component's missing context. |
| Bundle manifest/content mismatch | Bundle verification fails. | Rebuild from a fixed revision and verify the actual manifest. |

Support the result shapes and schema names verified by your integration tests.
Optional fields may be absent or explicitly unavailable; required fields must
not be silently fabricated. A new engine pin requires rerunning the
[acceptance fixtures](#scaling-mixtures-and-acceptance-fixtures) and
[before/after comparison](development.md#compare-saved-calculations). Review
changed field names, units, meanings, defaults and unavailable states as well
as numerical deltas. Version labels alone do not promise schema compatibility.

### Cache invalidation

The [identity/handoff contract](#identity-and-handoff) defines the distinct
native, exposure, bundle and adapter identities. Recompute when any consumed
input, source content, engine/adapter code, place mixture, transport/cohort
choice or requested sampling design changes. Keep display-only scaling separate
from the cached native calculation. A cache hit requires the complete key and
current schema/coverage checks; a plausible hash or equal point is insufficient.

<!-- BEGIN GENERATED SOFTWARE REFERENCE -->

## Command reference

<!-- @ref:integration-command-reference -->

Generated from the running CLI parser. Use `downstream <command> --help`
for required arguments, option choices and defaults. This table is an
inventory of commands, not a statement that every command returns the
scenario result shape below.

| Command | Parser description |
| --- | --- |
| `mortality-cohort` | exact age-stratum mortality with an explicit projection assumption |
| `receiving-community` | source-specific immigrant-share crime-rate scenarios |
| `household` | annual household earnings under a supplied displacement duration |
| `uncertainty` | conditional parameter, exposure, baseline and process uncertainty budget |
| `compare` | compare saved outputs or parameter snapshots from two versions |
| `family` | standard-family vignette |
| `scenario` | modeled counts for a displacement exposure |
| `child-gaps` | child and descendant earnings gaps side by side |
| `forecast-register` | freeze a prospective forecast locally |
| `forecast-score` | score a completed registered forecast |
| `synthesize` | random-effects synthesis of source-extracted, same-scale study estimates |
| `county-posterior` | Gamma-Poisson county event/person-time rate posterior |
| `county-wonder-posterior` | posterior directly from a validated CDC WONDER county export |
| `bundle` | export a pinned standalone engine and data directory |
| `policy` | compare baseline and policy exposure assumptions |
| `entity` | modeled impacts from documented entity exposure |
| `explain` | walk a claim from headline to citations |
| `sensitivity` | Sobol decomposition of an outcome |
| `knobs` | knob experiments (sweep a parameter / rank what is worth pinning) |
| `simulate` | Monte Carlo over a link chain |
| `infer` | exact moments, log-space shares, closure coverage |
| `ensemble` | structural-variant ensemble (plan #9) |
| `place` | place-resolved baselines + mobility modifier for one geography |
| `build-places` | regenerate params/places.csv from the committed Atlas + WONDER county inputs |
| `audit` | parameter/citation/DAG checks |
| `export` | version-stamped parameter_set.json snapshot (consumed by production; refuses while audit has ERRORs) |
| `validate` | V0 internal consistency + V1 target |
| `citations` | citation coverage report |
| `transmissions` | which outcomes walk to grandchildren, on whose evidence — and what is one extraction away |
| `credits` | the computed collective behind the model |

### Python calling signatures

These signatures are inspected from the implementation. The APIs do not
silently accept every JSON field; use the appropriate input record.

```python
def load_all(params_dir: 'str | Path | None' = None): ...
def compute_counts(params: 'ParameterSet', baselines: 'dict[str, Baseline]', scenario: 'ScenarioInput', strict: 'bool' = False, places: 'dict | None' = None, place_key: 'str | None' = None, mortality_profiles: 'dict | None' = None, county_mortality: 'dict | None' = None, _raw: 'bool' = False, params_dir=None) -> 'dict': ...
def sample_counts(params: 'ParameterSet', baselines: 'dict[str, Baseline]', scenario: 'ScenarioInput', *, draws: 'int' = 2000, seed: 'int' = 1901, strict: 'bool' = False, places: 'dict | None' = None, place_key: 'str | None' = None, mortality_profiles: 'dict | None' = None, county_mortality: 'dict | None' = None, nodes: 'dict | None' = None, params_dir=None, sensitivity_base: 'int | None' = None) -> 'dict': ...
def compute_entity_counts(params: 'ParameterSet', baselines: 'dict[str, Baseline]', exposure: 'DocumentedExposure', scenario: 'ScenarioInput | None' = None, *, places: 'dict | None' = None, place_key: 'str | None' = None, mortality_profiles: 'dict | None' = None, county_mortality: 'dict | None' = None, strict: 'bool' = False, params_dir=None) -> 'dict': ...
def child_gap_view(params: 'ParameterSet', baselines: 'dict[str, Baseline]', scenario: 'ScenarioInput', *, places=None, place_key=None, mortality_profiles=None, county_mortality=None, params_dir=None) -> 'dict': ...
def child_support_report(scenario: 'ScenarioInput | None' = None, *, params_dir: 'str | Path | None' = None, parent_tenure_years: 'float | None' = None) -> 'dict': ...
def household_comparison(payload, params_dir=None): ...
def project_mortality_cohort(payload: 'dict', params_dir: 'Path | None' = None) -> 'dict': ...
def receiving_comparison(params: 'ParameterSet', payload: 'dict') -> 'dict': ...
def scale_outcome(row, factor): ...
def mix_expected(results, weights, outcome): ...
```

### Scenario input fields

`ScenarioInput` accepts the fields below. Defaults describe a reference
scenario; they are not observed target data. Types and validation are
defined by [scenario.py](../src/downstream/scenario.py).

| Field | Declared type | Default |
| --- | --- | --- |
| `displaced_workers` | `float` | `required` |
| `n_children` | `int` | `2` |
| `tradable_share` | `float` | `1.0` |
| `net_tradable_jobs_lost` | `float \| None` | `None` |
| `local_job_mix` | `str \| None` | `None` |
| `wage_multiplier` | `float \| None` | `None` |
| `exposure_years` | `float` | `20.0` |
| `label` | `str` | `'scenario'` |
| `mortality_method` | `str` | `'odds_survival'` |
| `mortality_timing` | `str` | `'source_profile'` |
| `mortality_profile` | `str \| None` | `None` |
| `mortality_mix` | `dict[str, float] \| None` | `None` |
| `place_application` | `str` | `'initial_only'` |
| `target_population` | `dict[str, str] \| None` | `None` |
| `applicability_decisions` | `dict[str, dict] \| None` | `None` |
| `child_profiles` | `list[dict] \| None` | `None` |
| `child_income_quartile` | `int \| None` | `None` |
| `income_rank_definition` | `str \| None` | `None` |
| `real_discount_rate` | `float \| None` | `None` |
| `valuation_year` | `int \| None` | `None` |

`DocumentedExposure` requires `subject_id`, `subject_type`, `displaced_workers`, `source`, `method`.
See [exposure metadata](#exposure-and-event-metadata) for normalized
semantics and [warehouse inputs](#warehouse-inputs) for that separate adapter.

<!-- END GENERATED SOFTWARE REFERENCE -->

## Troubleshooting

<!-- @ref:integration-troubleshooting; @link:integration-errors; @link:code-scenario. -->

| Symptom | Inspect | Resolution |
| --- | --- | --- |
| Outcome missing or null | `blocked`, child/target applicability, baseline/source compatibility. | Follow the named missing input or refusal; do not display a fabricated zero. |
| Number exists but headline eligibility is false | Outcome `applicability` and target metadata. | Keep it illustrative unless an actual reviewed transport decision is supplied; numerical success is not scientific admission. |
| Local jobs are blocked | Separate `net_tradable_jobs_lost` and `local_job_mix`. | Supply documented net employment and its class; worker exposure and `tradable_share` do not infer them. |
| No parameter interval | Deterministic versus sampled entry point, or tool-specific unavailable status. | Use `sample_counts`/CLI draws where supported; never infer an interval for an unsupported tool or mixture. |
| Tiny counts round to zero on display | Native precision and source normalization basis. | Use the checked consumer/fixture construction; do not divide a rounded one-worker result and scale it back up. |
| Same versions, changed hash or output | Full input/source/bundle/adapter identities and seed/design. | Compare fixed inputs and receipts; version labels alone do not identify code or all consumed source content. |
| Mixture or scaling raises | Units, worker denominators, timing and input endpoints. | Refit compatible components and preserve every baseline; do not copy the first component's nested reports. |
| Receiving adapter rejects worker counts | Selected source model, margin, share units and response window. | Provide its separate source-specific share/count exposure; no displacement-to-arrivals bridge is implemented. |
| Custom parameters unexpectedly fail | The selected directory's source library and required files. | Supply the complete custom source set and pass `params_dir` through; do not substitute bundled contrasts. |

For stale generated references, environment or task-command problems, see
[development troubleshooting](development.md#troubleshooting).
