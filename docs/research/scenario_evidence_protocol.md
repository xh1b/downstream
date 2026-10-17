# Evidence selection and independent evaluation

<!-- @ref:doc-scenario-evidence-protocol; @tag:validation -->
<!--
Connections: @link:code-validate; @link:code-scoring; @link:code-forecast-registry; @link:doc-data-sources; @link:doc-evidence-classification-0-4; @link:docs-index; @link:paper-validation;
@link:script-acquire-followthrough-sources; @link:script-build-displaced-cohort; @link:script-evaluate-followthrough; @link:test-validate; @link:test-v2-backtest; @link:test-forecast-fsm.
-->

Related: [Documentation map](../README.md) · [data sources](../audits/DATA_SOURCES.md) · [evidence classification 0 4](../audits/EVIDENCE_CLASSIFICATION_0_4.md).
Implementation: [validate](../../src/downstream/validate.py), [scoring](../../src/downstream/scoring.py), [forecast_registry](../../src/downstream/forecast_registry.py). Checks: [validate](../../tests/test_validate.py), [v2_backtest](../../tests/test_v2_backtest.py), [forecast_fsm](../../tests/test_forecast_fsm.py).

Protocol fixed on 2026-10-14 for the next acquisition/evaluation round.
The existing anchors, source tables and China-shock diagnostics were already
known when this was written. This is not retrospective preregistration of
those results or an independently timestamped prospective forecast.

## Source selection

Search involuntary displacement, plant/firm closure and mass-layoff studies
for worker earnings/employment, child earnings, family outcomes and all-cause
mortality. Record population, treatment/comparison, design, calendar period,
follow-up, effect scale, uncertainty and sample overlap before deciding whether
an estimate is usable. Do not select by sign, statistical significance or
agreement with the current model. Preserve harmful, protective, null and
conflicting estimates. Record exclusions and unread candidates explicitly.

The first machine-readable library contains the re-extracted Sullivan–von
Wachter Table 5/7 and Oreopoulos Table 2/8 contrasts. These are two study
samples, not fourteen independent studies. The subgroups and phases share
their respective sample-overlap identifiers. Pool only estimates with
compatible treatment, outcome definition, scale, population and horizon,
with an explicit dependence model where needed. Never equate HR, OR,
cumulative hazard ratio, risk difference and a log-earnings coefficient.

Priority independent comparisons already identified in the literature are
Eliason–Storrie (Swedish long-run mortality divergence), Browning–Heinesen
(Danish cumulative mortality effects), Huttunen (Finnish child earnings),
and other displacement/closure replications in the existing bibliography.
An acquired PDF, approximate percentage, or cross-check note is not a
standard-error-bearing study row. Full-text uncertainty and exact source
version must be pinned before admission. Do not infer missing SEs from
statistical significance or treat a nonsignificant estimate as zero.

## Target population

The reproducible CPS January-2024 reference describes known-year 2021–2023
displacements with lost-job tenure >=3 years, with a separate >=6-year subset.
Weights are PWSUPWGT/10,000. Unknown loss years are excluded from the known-year
benchmark, and the total reproduces the independent BLS rounded publication.
Age and household variables are measured at interview. A hypothetical future
event can use that composition explicitly; a historical retrodiction cannot
silently relabel interview age as age at displacement. Neither reference
identifies H-1B-specific displacement or its target composition.

## Frozen independent-event requirements

Use an external event/cohort not used to select coefficients or structures.
Freeze its exposure bridge, age/sex/tenure composition, event date, geography,
reference group, outcomes and scoring rules before reading its scored outcomes.
Record hashes and independently verifiable dates where available. Local Git
history supplies reproducibility, not independent prospective timestamping.

For mortality, compare five-year all-cause cumulative risk differences in a
matched male, high-tenure closure/layoff cohort, using a common population for
all eligible comparators. Compare a direct source-profile reference, exact
age-baseline aggregation, and sourced age-response aggregation only where
their estimands and projection assumptions are compatible. Report coverage
gaps rather than silently shrinking the target to modeled strata.

For household resources, compare five-year gross real earnings under a
supplied duration with the stated reference. A constant-loss accounting
baseline and the SIPP transition scenario are conditional comparators;
neither automatically identifies a displacement treatment effect. Timing,
annual earnings paths, taxes/transfers and partner responses must be aligned
or excluded explicitly before comparing measured outcomes.

Report every frozen endpoint: signed/absolute point error, benchmark error,
subgroup errors, missingness and interval scope. Score CRPS/coverage only for
a compatible predictive distribution; a parameter-support envelope is not a
prediction interval. Do not tune on a held-out failure and keep calling the
same event held out. Retain misses and publish amendments as new versions.

## Current execution status

### Acquisition amendment — 2026-10-14

The 2026-10-14 acquisition round expands the initial fourteen contrasts from two
samples to twenty-three contrasts from three samples. Browning–Heinesen's
2011 AKF working-paper Table 6.1 contributes seven all-cause cumulative
hazard ratios and two cancer contrasts, including null-compatible estimates.
Standard errors are explicitly approximate, reconstructed from rounded
published 95% limits on the log scale. These cumulative hazard ratios are
incompatible with the annual odds-ratio phases and remain separate.
The Eliason–Storrie full-text acquisition returned HTTP 429; its previously
recorded long-run null finding remains visible, without inventing a new SE
or treating it as zero. The screening log records this missing extraction.
This amendment records results already inspected, not a prospective forecast.
The original evaluation is retained; the expanded-library execution is saved
as `validation/followthrough_evaluation_expanded_20261014.json` with this protocol's hash.
The pending update remains in the 0.4 development cycle. Correcting the
premature 0.5 label changes version metadata and filenames, not the evaluation
results; the expanded snapshot's protocol hash reflects this amendment.

The published-cohort reproduction and SIPP held-out baseline checks are
executed software/data checks. China-shock comparisons remain diagnostic,
including misses. The repository's V2 registry still has no external source
providing both an aligned displacement bridge and independently estimated
outcomes for a newly scored event. The new household and age-stratum paths
have **not** passed independent causal event validation. This is an empirical
dependency, not a reason to manufacture a score or pool incompatible studies.
