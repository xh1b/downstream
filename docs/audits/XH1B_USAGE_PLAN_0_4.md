# Downstream 0.4 priorities informed by XH1B usage

<!-- @ref:doc-xh1b-usage-plan-0-4; @tag:consumer -->
<!--
Connections: @link:code-employer; @link:code-consumer; @link:doc-consumer-fixtures-0-4; @link:doc-exposure-semantics-0-4; @link:docs-index; @link:test-consumer-fixtures; @link:test-consumer-api;
@link:test-exposure-semantics.
-->

Related: [Documentation map](README.md) · [consumer fixtures 0 4](CONSUMER_FIXTURES_0_4.md) · [exposure semantics 0 4](EXPOSURE_SEMANTICS_0_4.md).
Implementation: [employer](../src/downstream/employer.py), [consumer](../src/downstream/consumer.py). Checks: [consumer_fixtures](../tests/test_consumer_fixtures.py), [consumer_api](../tests/test_consumer_api.py), [exposure_semantics](../tests/test_exposure_semantics.py).

Inspected 2026-10-14. Keep engine 0.4.0; current parameters are v1.51.

The next priority is a trustworthy exposure-to-outcome contract and a tested
consumer handoff. XH1B already has a substantial explorer and evidence display.
Adding more channels before it preserves the current model's assumptions would
have less value than making its existing two consequence totals dependable.

## Inspection scope and receipt

This review reads the local companion checkout and executes its Python worker
with synthetic inputs. It does not inspect a database, a browser or deployed
pages. It does not repin XH1B or change either project's runtime code.

[The inspection receipt](../validation/xh1b_usage_inspection_20261014.json)
records both Git revisions, inspected source hashes, the verified bundle,
synthetic inputs and outputs. Candidate checks execute the existing companion
worker against this repository's source and parameters without copying or
installing them. They are compatibility probes, not production acceptance.
Companion paths below are relative to the XH1B checkout.

## What XH1B currently does

| Stage | Observed behavior | Source in XH1B |
|:---|:---|:---|
| Pin | Engine 0.3.0 / v1.49, source e16440fe; all 58 listed bundle files verify. | `scraper/vendor/downstream-source.json`, `manifest.json` |
| Exposure | v1.2 adds requested positions, a wage-gap term and eligible matched WARN counts. | `scraper/scraper/aggregate.py` |
| Time basis | Adds available filing history; repeated filings may represent the same person. | `website/src/content/displacement-method.ts` |
| Worker | Computes a deterministic reference per 1,000 workers; exposure is applied at read time. | `scraper/scraper/entity_analysis_worker.py` |
| Defaults | Two children per worker; 20-year mortality follow-up; no target population on scheduled rows. | Worker and `entity_analysis.py::run` |
| County | Uses county place inputs and compatible county mortality baselines. | Worker |
| Employer | Supports top-five worksite county shares plus a national residual; unresolved counties stay national. | Runner and worker |
| State / ZIP | Website directly scales the generated national reference. | `website/src/lib/queries/downstream.ts` |
| Other surfaces | Compact scores use the national reference unless passed a parsed analysis. | `website/src/components/downstream-summary.tsx` |
| Cache | Checks engine, parameter, bundle and adapter identity; writes use lease and release fences. | Runner and query adapter |
| Fallback | Missing or stale entity results fall back to the current national reference. | Query adapter and impact component |
| Explorer | Changes exposure; offers a separate place comparison when a valid baseline is supplied. | `downstream-model-explorer.tsx` |
| Study rows | Uses generated parameter data plus TypeScript formulas and several fixed study baselines. | `website/src/lib/downstream-calculations.ts` |

The scheduled drain includes state, county, ZIP, identity, law firm, hospital
and university. It excludes employer and person. Employer share changes feed
the queue, but the inspected scheduler explicitly awaits employer drain
qualification. Capability in the worker is not proof of cache coverage.

The default consequence rows are child lifetime earnings and expected excess
deaths. Local service jobs are correctly blocked without a separate net local
tradable-job loss and job class. Broader study rates, scores and structural
projections are displayed separately; they are not all exposure-scaled counts.

XH1B already preserves outcome applicability, blocked reasons, source population,
source steps, hashes and place contributions. HTML and Markdown entity sections
use the same parsed analysis. Default outcomes remain illustrative and ineligible
for public headlines, and the UI labels their unverified population fit.
These safeguards should be retained and extended rather than rebuilt.

## Findings that change our priorities

### 1. Worker-equivalent exposure is not an identified displaced cohort

The companion's public method says its exposure is neither unique people nor
worker-years. A wage-gap increment measures a different kind of exposure from
a layoff. Repeated filings and WARN terms can overlap. Nevertheless, the
consequence adapter scales the whole scalar as a displaced-worker reference.

That is a stated scenario convention, not an empirical displacement bridge.
More decimal places, a local baseline, or a wider coefficient interval cannot
establish that bridge. Generic CPS displaced-worker composition cannot identify
it either. Worksite shares describe requested positions, not necessarily the
places or characteristics of displaced workers.

Model-side work should preserve exposure kind, components, method version,
record window, overlap limits and the caller's conversion assumption. Distinguish
an illustrative equivalent-exposure scenario from an admitted cohort estimate.
Unknown age, sex, tenure, family structure and event timing must stay unknown.
An accumulated filing-history exposure also cannot become a calendar-specific
20-year death forecast without an event-time mapping.

Keep exposure inference in the companion project. Downstream should validate and
report the supplied contract, not infer one displaced person per filing or invent
a conversion probability. Fractional exposure is valid for a reference expected
value; it is not automatically an integer cohort for process simulation.

### 2. A repin alone loses or miscombines new model information

The TypeScript parser retains main totals, parameter intervals and selected
provenance. It has no field for 0.4's `persistence_sensitivity`, child applicability,
child valuation, or the full scenario assumptions. The scheduled worker accepts
only its existing six scenario-context keys and fixes family size and follow-up.
New model capabilities therefore do not automatically reach the consumer.

A synthetic compatibility probe confirms an additional problem. For a 60%
county 17043 / 40% national mixture at 1,000 workers, the candidate main mortality
point is correctly 21.716. Its nested source-profile point remains 17.02, and
its nested no-sustained-excess point remains 12.12. The corresponding weighted
points are 21.716 and 15.48. `_scale` and `_mix` operate only on the top-level
point/low/high statistics; nested comparisons retain the first component.
This is a pending 0.4 compatibility defect, not an observed deployed defect.

Make normalization and mixture behavior explicit for every consumed field.
Aggregate structural alternatives under the same exposure, baseline, horizon
and place weights. Do not average interval quantiles as though they were a joint
interval. Shared coefficient draws need an explicit dependence rule. If a field
cannot be combined defensibly, mark it unavailable instead of inheriting the
first component. All components must qualify before a mixture can claim reviewed
applicability; retaining per-place records alone is not that decision.

### 3. Scientific uncertainty matters more than the small point correction

For the national 1,000-worker reference, the pinned mortality point is 28.73;
the candidate is 28.76. In the candidate, fixing the sustained phase at OR=1
from follow-up year 7 gives 20.52. The 8.24 difference is much larger than the
arithmetic correction. It is a declared structural comparison, not a new
confidence interval, a model probability, or a replication of a Swedish estimate.

This comparison should survive the entire consumer path. Keep the support
envelope, parameter-only interval, structural alternatives and any broader
uncertainty budget distinct. Unsupported transport and unknown dependence stay
named. Caller-declared exposure scenarios are useful, but an arbitrary uniform
range does not quantify uncertainty in XH1B's exposure method.

### 4. Defaults must remain visible as family and valuation assumptions

Two children per worker and a male synthetic lifetime-earnings benchmark are
reference inputs. They are not measured family composition. The default total
is an undiscounted lifetime earnings difference in 2024 dollars, not a present
value or annual loss. A richer child scenario needs sourced child age at event,
sex and income-rank definitions. Discounting also needs event/valuation timing.

The present XH1B input contract does not supply these data. Retain the reference
scenario as such. When supported inputs become available, consume the existing
0.4 eligibility and valuation paths and preserve unknown and blocked outcomes.
Do not populate an employer's children from filing demographics by assumption.

### 5. The website has some calculation logic outside the engine

Generated reference data reduces drift, but TypeScript still constructs study
comparisons using fixed baseline values and constants, including the parent
layoff-year income total. Some formulas also embed coefficient text. These rows
need explicit versioned inputs and parity checks when the evidence changes.
Prefer exported authoritative numeric inputs and operation identifiers for the
rows already displayed. A new general rendering framework is not required.

## Recommended work order

| Order | Work and concrete result | Existing or proposed cards |
|:---|:---|:---|
| 1 | Specify exposure units, timing, overlap and unknown composition. | `exposure-semantics-contract`, `target-displaced-cohort` |
| 2 | Verify consumer fixtures, scaling, mixtures and required 0.4 fields. | `consumer-contract-fixtures`, `xh1b-handoff` |
| 3 | Carry mortality persistence alternatives through runner, cache, HTML and Markdown. | `mortality-persistence`, `sustained-mortality-alternative` |
| 4 | Audit independent evidence, target fit and signed effects. | `coefficient-library`, `mortality-applicability`, `mortality-strata` |
| 5 | Specify child scenarios, valuation and unknown composition. | `child-heterogeneity`, `child-present-values`, `target-displaced-cohort` |
| 6 | Improve SIPP accuracy and survey uncertainty. | `sipp-trajectories`, `household-dynamics`, `full-comparison` |
| 7 | Qualify the fixed candidate, regenerate companion materials and check actual cache/page coverage. | `release-04-readiness`, `xh1b-handoff` |

Card ids in this table have prefix `2026-10-14-`. New proposed cards are in
`tasks/inbox/`. Existing cards retain their present ownership and status.
The first two units are the recommended next implementation work. Source
acquisition can proceed alongside them when accessible; the table does not
require all research questions to be solved before a conditional release.

Review the completed audit, persistence and valuation cards before duplicating
that work. Verify the migrated place-counterfactual card against its existing
null-effect regression and reconcile its board status. `classify-evidence`
should record which remaining claims still need classification after the audit.

The published-QJE covariance gap remains an explicit research dependency.
Do not manufacture a published profile to close its card. Likewise, matched
external event evaluation remains blocked by suitable independent data; tests
and bundle parity cannot substitute for it. Transport uncertainty research
should not turn absent evidence into invented model weights.

SIPP is valuable for a later supported household comparison, but the inspected
XH1B production adapter does not consume it. Its annual observational prototype
and known held-out misses must remain explicit in 0.4. Separate qualification
of that prototype from qualification of the reference-count consumer.

Receiving-community effects, protective interventions, additional headline
streams and a larger calculator redesign follow these contracts. Evaluate both
harms and benefits under the same admission rules and declare omitted effects.
Keep receiving-community exposures distinct from displacement; do not net unlike
outcomes or imply that an unmodeled benefit or harm equals zero.

## Minimum 0.4 consumer acceptance

- A frozen consumer input/output contract names exposure units, record window,
  event timing, target information, normalization and assumptions. A model or
  adapter behavior change alters the appropriate content identity.
- Golden fixtures cover zero, fractional and large reference exposure; a national
  reference; one county; a county mixture; an unsupported county fallback; and
  blocked or partially covered outcomes. No silent demographic imputation.
- Fixtures exercise unknown child profiles, a known incompatible profile,
  an admitted signed income contrast, explicit valuation and a synthetic reviewed
  transport decision. Synthetic decisions are never described as real evidence.
- Main totals, structural alternatives and required metadata agree between model
  output, normalized cache, scaled reader, explorer, HTML and Markdown. Comparing
  a mixture with its first component must detect the reproduced defect.
- Parameter support, parameter intervals and structural comparisons retain their
  separate meanings. Broader uncertainty is enabled only for compatible inputs.
- Generated references, study inputs, bibliography and method links agree with
  the fixed engine/parameter/source bundle. Versioned methods links should resolve
  to the source used for the displayed result rather than a changing master file.
- Missing/stale county or employer results retain an explicit national-reference
  fallback reason. A valid hash shape is not proof of current input provenance.
- Companion cache checks distinguish configured entity types, actual current
  rows, dirty queues and fallback usage. Employer drain qualification is explicit.
  Deployment acceptance requires fresh page evidence; this review supplies none.
- The release report separates completed arithmetic/source audits, conditional
  scientific assumptions, held-out misses and pending independent validation.

Do not make the household prototype, exact age-stratum tool or extended
uncertainty command silently replace the current reference engine. Each has
additional input and interpretation requirements. Release each supported path
with its own stated scope while keeping engine 0.4.0 until the owner's decision.

## Source index for implementation

In Downstream: `src/downstream/scenario.py`, `employer.py`, `mortality_robustness.py`,
`child_applicability.py`, `valuation.py`, `docs/RELEASE_0_4.md` and the task board.

In XH1B: `scraper/scraper/entity_analysis.py`, `entity_analysis_worker.py`,
`aggregate.py`, `scheduler.py`; `website/scripts/build-downstream-reference.py`,
`gen-downstream-pinned.mjs`; `website/src/lib/downstream-analysis.ts`,
`downstream-calculations.ts`, `downstream-baseline.ts`, `queries/downstream.ts`;
`website/src/components/downstream-impact.tsx`, `downstream-summary.tsx`,
`downstream-summary-details.tsx`, `downstream-model-explorer.tsx`;
`website/src/lib/markdown/renderers/downstream-impact.ts` and `downstream.ts`;
`scripts/repin-downstream.py`, `verify-downstream-package.py`,
`review-downstream-cache.py` and `scripts/tests/test_downstream_release.py`.
