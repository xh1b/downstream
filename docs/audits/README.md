# Audits and review records

<!-- @ref:docs-audits; @tag:documentation -->
<!-- @link:docs-index; @link:doc-development. -->

These are reviews, diagnostics and qualification receipts. Read each record's
scope, version and date before using its conclusion. They preserve evidence of
what was inspected; current software contracts live in the [five guides](../README.md),
and mathematical explanation lives in the [paper](../../paper/downstream.tex).
Research proposals and design plans live separately in [research](../research/README.md).

An audit can be brief: state what was reviewed, the inputs/revision, findings,
reproduction commands and limitations. Link actionable findings to task cards.
Do not maintain a second API specification here or impose the core guides'
editorial standard on a review receipt. Preserve old findings when appending
a correction. Generated reports are updated through their builders.

## Sources and evidence

- [Evidence classification](EVIDENCE_CLASSIFICATION_0_4.md) — generated inventory of applicability and runtime roles.
- [Independent pool readiness](POOL_READINESS_0_4.md) — generated compatibility and sample-overlap screen.
- [Source acquisition inventory](DATA_SOURCES.md) — historical datasets, access paths and baseline decisions.
- [Mortality source reconciliation](MORTALITY_SOURCE_RECONCILIATION_2026-09-10.md) — source-version and scale review.
- [Mortality applicability](MORTALITY_APPLICABILITY_0_4.md) — admitted responses versus baseline coverage.
- [Additive mortality covariance](MORTALITY_COVARIANCE_0_4.md) — diagnostic without invented covariance.
- [Mortality persistence analysis](MORTALITY_PERSISTENCE_ANALYSIS_2026-10-14.md) — interpretation and robustness of the two structures.
- [Receiving-community evidence scan](IMMIGRATION_REPLACEMENT_EVIDENCE_SCAN_2026-09-14.md) — source margins, contested findings and unit correction.
- [Remarriage-margin screen](REMARRIAGE_MARGIN_SCREEN_0_4.md) — refusal of a bridge from divorce to remarriage.

## Baselines and implementation

- [PSID assessment](PSID_BASELINE_DATA_ASSESSMENT_2026-09-13.md) and [SIPP assessment](SIPP_BASELINE_DATA_ASSESSMENT_2026-09-13.md) — suitability and access constraints at review time.
- [SIPP baseline transitions](BASELINE_TRANSITION_R2_2026-09-14.md) — derivation and held-out descriptive calibration.
- [Same-place counterfactual review](PLACE_COUNTERFACTUAL.md) — null-safe implementation and interpretation check.
- [Testing quality review](TESTING_QUALITY.md) — historical coverage, mutation and performance receipts.
- [Calculator browser review](CALCULATOR_REVIEW_2026-10-15.md) — viewport and interaction checks, with remaining human review.

## Release and integration

- [0.4 candidate qualification](RELEASE_0_4.md) — source corrections, checks and pending acceptance.
- [XH1B integration review](XH1B_USAGE_PLAN_0_4.md) — inspected consumer behavior, integration gaps and priorities.

Task history remains on the [board](../../tasks/README.md). An audit's checklist
or passed software check does not establish independent scientific validation
or a deployed companion release.
