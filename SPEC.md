# Implementation and methods map

<!-- @ref:specification; @tag:model @tag:methods -->
<!-- @link:docs-index; @link:paper-methods; @link:code-scenario. -->

The implementation and admitted data define behavior. The
[paper](paper/downstream.tex) explains mathematics and scientific rationale;
the [software guides](docs/readme.md) describe calling and maintenance contracts.
This file preserves historical SPEC section numbers and stable anchors as a
navigation map. It does not maintain a second set of formulas, parameter values
or verification claims. Historical versions remain available in Git.

## 1. Purpose and what the model computes

<!-- @ref:spec-purpose -->

[Model scope](docs/model_card.md). Rationale: @link:paper-model; implementation: @link:code-scenario.

## 2. Nodes and units

<!-- @ref:spec-nodes -->

[Nodes and admitted data](docs/evidence.md#know-which-record-you-are-editing). Rationale: @link:paper-composition; implementation: @link:code-units.

## 3. Parameters

<!-- @ref:spec-parameters -->

[Parameter custody](docs/evidence.md#citation-and-extraction-rules). Rationale: @link:paper-parameters; implementation: @link:code-params.

## 4. Composition semantics

<!-- @ref:spec-composition -->

[Typed composition and projections](docs/integration.md#child-and-descendant-outputs). Rationale: @link:paper-composition; implementation: @link:code-ledger.

## 5. Modeled pathways

<!-- @ref:spec-pathways -->

[Supported surfaces](docs/model_card.md#what-the-software-supports). Rationale: @link:paper-exposure; implementation: @link:code-worker.

## 6. Count conversion and baselines

<!-- @ref:spec-counts -->

[Count calling contracts](docs/integration.md#mortality-outputs). Rationale: @link:paper-counts; implementation: @link:code-mortality.

## 7. Uncertainty propagation

<!-- @ref:spec-uncertainty -->

[Uncertainty tools](docs/integration.md#uncertainty-and-experiment-tools). Rationale: @link:paper-uncertainty; implementation: @link:code-distributions.

## 7b. Analytic inference (the same algebra, done exactly)

<!-- @ref:spec-inference -->

[Analytic inference](docs/integration.md#uncertainty-and-experiment-tools). Rationale: @link:paper-inference; implementation: @link:code-inference.

## 8. Sensitivity analysis (what drives the range)

<!-- @ref:spec-sensitivity -->

[Sensitivity result contract](docs/integration.md#per-result-sensitivity). Rationale: @link:paper-sensitivity; implementation: @link:code-sensitivity.

## 8b. Knob experiments (how the model is explored)

<!-- @ref:spec-knobs -->

[Experiment tools](docs/integration.md#uncertainty-and-experiment-tools). Rationale: @link:paper-sensitivity; implementation: @link:code-knobs.

## 10. The explanation contract (how claims travel)

<!-- @ref:spec-explanation -->

[Result and explanation contracts](docs/integration.md#result-fields-and-units). Rationale: @link:paper-calculator; implementation: @link:code-explanation.

## 11. Scenario aggregation

<!-- @ref:spec-scenarios -->

[Scenario input contract](docs/integration.md#exposure-and-event-metadata). Rationale: @link:paper-exposure; implementation: @link:code-scenario.

## 12. Validation program

<!-- @ref:spec-validation -->

[Evaluation operations](docs/evidence.md#evaluation-records). Rationale: @link:paper-validation; implementation: @link:code-validate.

## 12b. Structural-variant ensemble (declared assumptions, priced)

<!-- @ref:spec-variants -->

[Structural alternatives](docs/integration.md#uncertainty-and-experiment-tools). Rationale: @link:paper-sensitivity; implementation: @link:code-variants.

## 13. Queued and excluded

<!-- @ref:spec-queued-evidence -->

[Acquisition/admission workflow](docs/evidence.md#add-or-revise-evidence). Rationale: @link:paper-parameters; implementation: @link:code-evidence.

## 14. Limitations (registered, not hidden)

<!-- @ref:spec-limitations -->

[Current model limits](docs/model_card.md#uncertainty-and-scientific-limits). Rationale: @link:paper-limitations; implementation: @link:code-scenario.

## 15. Layout

<!-- @ref:spec-layout -->

[Implementation navigation](docs/development.md#find-the-implementation). Rationale: @link:paper-reproducibility; implementation: @link:repository-overview.
