# Model scope and supported use

<!-- @ref:doc-model-card; @tag:model -->
<!-- @link:code-scenario; @link:code-vignette; @link:code-cli; @link:paper-model; @link:paper-limitations; @link:docs-index. -->

Downstream is a citation-calibrated scenario engine for consequences of worker
displacement, with separate source-specific adapters and experimental comparison
tools. The code and admitted data define its behavior. The
[methods paper](../paper/downstream.tex) explains the math and scientific
limitations; [integration](integration.md) describes the calling contracts.

Engine **0.4.0**, parameters **v1.54**. These labels identify the development
candidate, not a deployed companion release or scientific acceptance. Output
content hashes and source receipts are required in addition to version labels.

## What the software supports

| Surface | Computation | Interpretation boundary |
| --- | --- | --- |
| Scenario/entity counts | Expected mortality, child lifetime dollars and separately supplied net tradable-job consequences where qualified | Conditional reference calculations; worker equivalents are not an identified cohort. |
| Child/descendant views | Direct child source contrasts and structural gap propagation | Source child applicability is separate from descendant assumptions. |
| Mortality profiles/strata | Compatible baseline selection and separately admitted age-response projections | Baseline availability does not admit a response for a new group. |
| Household comparison | Paired annual expected gross earnings and E/U/N state-years | Observational transitions plus supplied event assumptions; no causal recovery claim. |
| Receiving-community adapter | Named source-specific population-share contrasts | Requires separate exposure units; no generic displacement-to-arrivals bridge. |
| Uncertainty/sensitivity tools | Parameter draws, explicit removal/endpoint refits and qualified extended budgets | Each report declares what varies and what remains fixed. |
| Browser calculator | Editable source-offset survival and child lifetime conversion | Custom assumptions do not establish target applicability. |

All outcomes carry sources, units and applicability or an explicit unavailable
state. A missing baseline blocks absolute conversion. Unsupported positive
exposure is not assigned a zero response. Known incompatibilities refuse the
relevant path; unknown target information must remain unknown.

## Intended use

Use the engine for transparent population/reference comparisons under declared
inputs. Preserve harmful, beneficial, null and conflicting evidence, along with
source version, population, timing and structural assumptions. Review target
transport independently of whether a number can be calculated.

Defaults are illustrative and ineligible for public headlines. Reviewed
conditional transport needs a reviewer, rationale and citations; it is not
established by a precise input, a county identifier, a successful audit or a
synthetic test fixture. Outputs are not predictions about an identified person.
The software is not an independently validated prospective forecasting system.

The default mortality response uses working-paper phases for high-seniority
male Pennsylvania mass layoffs, with a compatible US male 45–54 baseline.
The child earnings source is Canadian father-son firm closure evidence,
converted to a US synthetic lifetime earnings baseline in 2024 dollars.
Neither source automatically transports to mixed/unknown target populations.
See [mortality](integration.md#mortality-outputs) and
[child contracts](integration.md#child-and-descendant-outputs).

## Uncertainty and scientific limits

Parameter intervals are conditional on the selected structure and declared
fixed inputs. Support envelopes, parameter intervals, process distributions
and structural alternatives have different meanings; preserve those labels.
Removal experiments do not add to causal shares. Unknown dependence or
structural probabilities are not filled in by convenience.

Repeated relationship records share one exact draw. The available grandchild
result is a structural projection; the later great-grandchild earnings branch
is unavailable following source withdrawal. Same-place child modifiers are exploratory interactions;
null-safe arithmetic does not establish a causal displacement-by-place effect.
Mortality persistence alternatives retain early risk and vary later risk;
their spread is not a confidence interval or a replication of another study.

The source library retains overlapping contrasts from a small number of study
samples. Its [compatibility review](audits/pool_readiness_0_4.md) does not establish
a pool of independent estimates. Age-stratum mortality holds a source-window
response constant as baselines age. Household gross earnings omit taxes,
transfers, savings, housing and joint-resource distributions. Receiving outputs
retain their fixed-effects/IV roles, source windows and version limits.

## Evaluation status

V0 checks internal consistency. V1 China-shock diagnostics retain known misses,
including mortality overprediction and earnings underprediction. Software tests
and published-cohort reproductions do not erase them. V2 real event scoring
remains gated on aligned exposure bridges and independently measured outcomes;
synthetic fixtures verify the scorer only. V3 has local registration tools but
no completed real prospective event validation.

The new household and age-stratum paths have not passed independent causal
event validation. Baseline held-out calibration is descriptive evidence about
that baseline. Read the paper's validation sections (@link:paper-validation,
@link:paper-independent-validation) and the [evaluation workflow](evidence.md#evaluation-records).
Human calculator comprehension and physical-device/accessibility review remain
open; browser viewport checks are recorded separately in audits.

Model-card practice follows Mitchell et al., “Model Cards for Model Reporting”
(2019). Source contributions are credited in [CREDITS.md](../CREDITS.md).


## Declared transport and dependence experiments

The national uncertainty command can additionally report
[explicit mortality assumption cases](integration.md#declared-uncertainty-assumption-cases).
Each caller-supplied case fixes a log-odds transport scale and retains independent
input ranks or aligns/opposes baseline/exposure ranks with the signed source
mortality response. These cases preserve marginal draws and study correlations.
They are separate conditional sensitivity results, without inferred probabilities,
model averaging, a full uncertainty interval or new population admission.
Calibrated target transport error and actual cross-component dependence remain
unknown. The published source profile and its persistence alternative remain
separate in every case.


## Withdrawn historical inputs

The [source-support contract](evidence.md#source-withdrawals-and-retained-records)
records individual review of all sixteen former withdrawals: six original
estimates restored, seven corrected typed replacements, three unsupported
relationships. Sixty-four records are available; ten legacy identifiers remain
retired (seven superseded and three unsupported). Original values and every
disposition remain inspectable. Great-grandchild earnings, daughters-only
partner violence and the additive divorce/family-size variant remain unavailable.
Corrected source contrasts do not establish target transport or new headline
eligibility. Supported mortality and direct-child point coefficients and
baselines are unchanged.
