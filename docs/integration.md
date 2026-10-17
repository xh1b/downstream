# Integrating Downstream

<!-- @ref:doc-integration; @tag:consumer -->
<!-- @link:docs-index; @link:code-cli; @link:code-scenario; @link:paper-exposure. -->

Use the package or JSON CLI to evaluate a supplied scenario. Read the
[model card](model_card.md) before selecting a calculation. The authoritative
calling contracts are the dataclasses, loaders and public functions in
[scenario.py](../src/downstream/scenario.py), [employer.py](../src/downstream/employer.py)
and the outcome modules below. The paper explains equations and rationale
(@link:paper-exposure, @link:paper-counts); this guide describes software use.

## Choose an entry point

| Input or purpose | Entry point | Contract checks |
| --- | --- | --- |
| Worker exposure and assumptions | `ScenarioInput`, `compute_counts`, `sample_counts`; `downstream scenario` | [Scenario tests](../tests/test_vignette_scenario_mc.py) |
| Documented entity exposure | `DocumentedExposure`, `compute_entity_counts`; `downstream entity` | [Exposure tests](../tests/test_exposure_semantics.py) |
| Receiving-population shares | `downstream receiving-community` | [Receiving adapter tests](../tests/test_receiving_adapter.py) |
| Annual adult/household inputs | `household_comparison`; `downstream household` | [Household summary tests](../tests/test_household_summary.py) |
| Supported male age-at-displacement strata | `downstream mortality-cohort` | [Mortality admission tests](../tests/test_mortality_admission_0_4.py) |
| Child/descendant explanation or source support | `child_gap_view`, `child_support_report` | [Gap tests](../tests/test_child_gap_view.py), [support tests](../tests/test_child_support.py) |

Load one bundle and pass its components together:

```python
from downstream.params import load_all
from downstream.scenario import ScenarioInput, compute_counts

bundle = load_all()
result = compute_counts(
    bundle["params"], bundle["baselines"],
    ScenarioInput(displaced_workers=1000, n_children=2),
)
```

This is an illustrative national reference. Two children is an assumption,
not an observed family distribution. APIs that also load source contrasts
need the custom `params_dir` passed through; missing custom files must not
fall back to bundled evidence. CLI installation and examples are in the
[root README](../README.md).

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

`child_gap_view(params, baselines, scenario, ...)` returns child, grandchild
and great-grandchild relative earnings gaps with source steps and eligibility.
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
