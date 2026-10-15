# Analysis of mortality persistence: 28.76 versus 20.52

<!-- @ref:doc-mortality-persistence-analysis-2026-10-14; @tag:mortality -->
<!--
Connections: @link:code-mortality; @link:code-mortality-robustness; @link:doc-mortality-persistence-sensitivity; @link:doc-mortality-source-reconciliation-2026-09-10; @link:docs-index; @link:script-analyze-mortality-persistence; @link:test-mortality-robustness; @link:test-audit04-mortality-precision.
-->

Related: [Documentation map](README.md) · [mortality persistence sensitivity](MORTALITY_PERSISTENCE_SENSITIVITY.md) · [mortality source reconciliation 2026-09-10](MORTALITY_SOURCE_RECONCILIATION_2026-09-10.md).
Implementation: [mortality](../src/downstream/mortality.py), [mortality_robustness](../src/downstream/mortality_robustness.py). Checks: [mortality_robustness](../tests/test_mortality_robustness.py), [audit04_mortality_precision](../tests/test_audit04_mortality_precision.py).

2026-10-14. Engine 0.4.0 / parameters v1.51. No production default changes.

## What the comparison measures

Both numbers are modeled **additional deaths by the end of 20 years**, per
1,000 initially exposed workers, relative to the same reference scenario.
They are neither total deaths nor deaths per year. They are conditional
reference calculations, not validated estimates for XH1B's population.

Both use the same first six follow-up years. From year seven, the source
profile retains annual mortality odds ratio 1.1354. The alternative fixes it
at 1. This removes later excess annual risk, not the early exposure history.
The alternative is a declared hybrid assumption, not a second study estimate.

## Arithmetic and absolute scale

The fixed baseline is 0.004944 deaths per person-year. Conversion gives
annual probability `m = 1 - exp(-0.004944) = 0.00493179855`.
For an odds ratio `r`, annual exposed risk is `r*m / (1-m+r*m)`.
Survival compounds across the phase-specific annual risks.

| Follow-up years | Source OR | Annual death risk per 1,000 survivors | Alternative OR |
|:---|---:|---:|---:|
| 1, displacement year | 2.6698 | 13.059 | Same |
| 2 | 1.9838 | 9.736 | Same |
| 3–4 | 1.7315 | 8.509 | Same |
| 5–6 | 1.2712 | 6.261 | Same |
| 7–20 | 1.1354 | 5.596 | 1.0000, risk 4.932 |

These risks are conditional on survival into that year. The later increment
is about 0.664 deaths per 1,000 survivors per year. Applying it for fourteen
years produces an 8.235 difference after accounting for survival.
It is a 13.54% increase in odds, not a 13.54 percentage-point mortality increase.

| Scenario | Expected deaths by year 20 | Difference from reference |
|:---|---:|---:|
| Reference without the displacement response | 94.15 | 0 |
| Early response, then baseline annual odds | 114.67 | 20.52 |
| Full source response | 122.91 | 28.76 |

The persistence choice changes 20-year death probability by 0.824 percentage
points. It accounts for 28.64% of the source scenario's excess-death estimate;
the source excess is 40.13% larger than the alternative excess. These are two
ways to describe the same contrast, with different denominators.

## How the gap develops

| End of follow-up year | Source excess deaths | Alternative excess deaths | Difference |
|:---|---:|---:|---:|
| 1 | 8.13 | 8.13 | 0.00 |
| 4 | 19.65 | 19.65 | 0.00 |
| 6 | 21.99 | 21.99 | 0.00 |
| 10 | 24.04 | 21.56 | 2.48 |
| 12 | 25.03 | 21.35 | 3.68 |
| 15 | 26.47 | 21.04 | 5.44 |
| 20 | 28.76 | 20.52 | 8.24 |

The alternative's gap declines slightly after year six. Nobody comes back to
life. The reference group has more survivors left to die in subsequent years.
Equal annual risks among survivors therefore slowly narrow the difference
between cumulative death counts. Deaths brought forward by the early shock
still represent lost survival time even when cumulative count differences
later narrow. This analysis does not estimate lifetime years lost.

An elevated cumulative mortality measure at year 20, on its own, cannot establish
that the annual death risk remains elevated in year 20. Our alternative is a
numerical example: the cumulative difference remains positive with late OR=1.

## Evidence for and against generalizing persistence

The [2007 Pennsylvania paper](https://www.nber.org/system/files/working_papers/w13626/w13626.pdf)
reports pooled offset +6 log-odds 0.127, SE 0.048, in Table 5 column 3.
Its transformed marginal 95% interval, OR 1.0335–1.2474, excludes 1.
The study therefore supplies affirmative evidence of persistence in its sample.
[The Chicago Fed copy](https://www.chicagofed.org/-/media/publications/working-papers/2006/wp2006-21-pdf.pdf)
reports the same table coefficients. This is not independent evidence.

Table 5 column 2 separates offsets +6–10, +11–15 and +16 onward, with betas
0.179, 0.065 and 0.153. Applying that column's full point profile to the same
fixed model baseline gives **29.34**, close to 28.76. This checks the late pooling
choice within this study; it does not validate transport. No joint interval is
claimed for this diagnostic, and it is not admitted as a new production profile.

The [2009 manuscript](https://www.movingforwardnetwork.com/wp-content/uploads/2023/04/Sullivan_Job-Displacement-and-Mortality_2009.pdf)
also describes persistent effects and uses a different, additive Table 4
parameterization. This is a manuscript cross-check, not a new verified
published-version extraction. The covariance problem in the existing
[source reconciliation](MORTALITY_SOURCE_RECONCILIATION_2026-09-10.md) remains.
Missing covariance prevents ordinary phase-sum intervals; it does not prevent
an explicitly labeled point-profile check in future work.

The [Swedish study's working-paper Table 3](https://scispace.com/pdf/does-job-loss-shorten-life-1fllp9gb2i.pdf)
reports these male all-cause hazard ratios after establishment closures:

| Study window | HR | Marginal 95% interval |
|:---|---:|:---|
| First four years | 1.44 | 1.19–1.76 |
| Years 5–8 | 0.98 | 0.82–1.17 |
| Years 9–12 | 0.91 | 0.77–1.07 |

Its later point estimates are below one, and both intervals include one.
Retain that information; do not replace it with a known zero. The study has
another population, treatment definition, scale and window. It does not
supply a matched annual-OR replacement for the Pennsylvania profile or evidence
on years 13–20. The model alternative's year-seven cutoff comes from the
Pennsylvania phase boundary, not the Swedish four-year windows.
The [university series record](https://swopec.hhs.se/gunwpe/abs/gunwpe0153.htm)
confirms the study and version; the table above is a working-paper extraction.

These findings justify showing persistence sensitivity and researching target
fit. They do not justify a claim that either study is wrong, a universal zero
late effect, or equal-probability averaging of their results.

## Uncertainty beyond the two points

A rerun with 2,000 shared parameter draws and seed 1901 reproduces:

| Conditional structure | Point | Central 90% parameter-only interval |
|:---|---:|:---|
| Source profile | 28.76 | 22.04–36.68 |
| Fixed late OR=1 | 20.52 | 15.73–26.46 |
| Paired source minus alternative | 8.24 | 2.99–13.84 |

The paired difference uses the same early coefficients and baseline in each
draw. Its interval is not a subtraction of marginal interval endpoints.
The sampler and its declared dependence assumptions are not an identified
joint sampling distribution from the source papers. These intervals condition
on the chosen structure and fixed inputs; they do not decide whether persistence
transports or provide probabilities for the structures.

For illustration, retaining half the source late **log-odds** effect gives OR
1.0656 and 24.52 excess deaths. This is an unweighted diagnostic, not a preferred
estimate. Neither 20.52–28.76 nor the attenuation grid bounds the true effect.
An independently sourced protective or larger response could fall outside it.

Both structures also hold the male 45–54 baseline fixed for twenty years.
Neither ages the cohort or identifies the displaced workers behind XH1B's
filing-history worker equivalents. Family size does not affect these mortality
calculations. Target sex, age, tenure, recession conditions, geography and event
timing remain separate questions from persistence.

## Conclusion and next analysis

The current source result has a real empirical persistence basis. The within-study
late-period check does not explain away that basis. The null-persistence scenario
is useful because transport is uncertain and another setting has a different
pattern; it is not an equally established estimate for the same target cohort.

1. Preserve both structures and their assumptions in consumer output; fix the
   reproduced XH1B mixture/parser gaps before applying 0.4.
2. Extend source records with compatible annual late-period estimates, uncertainties,
   sample restrictions and overlap. Retain signed null-compatible findings.
3. Reconcile a verified published profile, including point-only checks where
   legitimate, and seek covariance or declare conservative interval construction.
4. Cross persistence with an admitted aging baseline and explicit cohort composition.
   Do not substitute baseline variation for evidence of response heterogeneity.
5. Establish the exposure-to-displacement and event-time bridge before making
   target-specific counts. Report unmodeled differences and validation limits.

No default is changed, no structural probabilities are assigned, and no source
coefficients are pooled in this analysis.

## Reproduction and verification

Run `.venv/bin/python scripts/analyze_mortality_persistence.py`.
[The saved result](../validation/mortality_persistence_analysis_20261014.json)
contains input hashes, all twenty annual survivor calculations, attenuation
probes, the same-study diagnostic and paired sampling results. Independent annual
survivor recurrence agrees with the production log-survival function within
2e-12 deaths at every horizon for both structures.

The 36 existing persistence and numerical-precision checks pass. Ruff passes for
the analysis script. These verify arithmetic and contracts, not external validity.
