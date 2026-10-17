# Audits and review records

<!-- @ref:docs-audits; @tag:documentation -->
<!-- @link:docs-index; @link:doc-development. -->

These are reviews, diagnostics and qualification receipts. Read each record's
scope, version and date before using its conclusion. They preserve evidence of
what was inspected; current software contracts live in the [five guides](../readme.md),
and mathematical explanation lives in the [paper](../../paper/downstream.tex).
Research proposals and design plans live separately in [research](../research/readme.md).

An audit can be brief: state what was reviewed, the inputs/revision, findings,
reproduction commands and limitations. Link actionable findings to task cards.
Do not maintain a second API specification here or impose the core guides'
editorial standard on a review receipt. Preserve old findings when appending
a correction. Generated reports are updated through their builders.

## Sources and evidence

- [Evidence classification](evidence_classification_0_4.md) — generated inventory of applicability and runtime roles.
- [Independent pool readiness](pool_readiness_0_4.md) — generated compatibility and sample-overlap screen.
- [Source acquisition inventory](data_sources.md) — historical datasets, access paths and baseline decisions.
- [Mortality source reconciliation](mortality_source_reconciliation_2026-09-10.md) — source-version and scale review.
- [Mortality applicability](mortality_applicability_0_4.md) — admitted responses versus baseline coverage.
- [Additive mortality covariance](mortality_covariance_0_4.md) — diagnostic without invented covariance.
- [Mortality persistence analysis](mortality_persistence_analysis_2026-10-14.md) — interpretation and robustness of the two structures.
- [Receiving-community evidence scan](immigration_replacement_evidence_scan_2026-09-14.md) — source margins, contested findings and unit correction.
- [Remarriage-margin screen](remarriage_margin_screen_0_4.md) — refusal of a bridge from divorce to remarriage.

## Baselines and implementation

- [PSID assessment](psid_baseline_data_assessment_2026-09-13.md) and [SIPP assessment](sipp_baseline_data_assessment_2026-09-13.md) — suitability and access constraints at review time.
- [SIPP baseline transitions](baseline_transition_r2_2026-09-14.md) — derivation and held-out descriptive calibration.
- [Same-place counterfactual review](place_counterfactual.md) — null-safe implementation and interpretation check.
- [Testing quality review](testing_quality.md) — historical coverage, mutation and performance receipts.
- [Calculator browser review](calculator_review_2026-10-15.md) — viewport and interaction checks, with remaining human review.

## Release and integration

- [0.4 candidate qualification](release_0_4.md) — source corrections, checks and pending acceptance.
- [XH1B integration review](xh1b_usage_plan_0_4.md) — inspected consumer behavior, integration gaps and priorities.

Task history remains on the [board](../../tasks/README.md). An audit's checklist
or passed software check does not establish independent scientific validation
or a deployed companion release.
