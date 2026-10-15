# Documentation map

<!-- @ref:docs-index; @tag:documentation -->
<!-- Entry points: @link:repository-overview; @link:specification; @link:paper-methods; @link:documentation-workflow. -->

Start with [the model card](MODEL_CARD.md) for interpretation and limits,
[the algorithm specification](../SPEC.md) for computation rules, and
[the paper build and method map](PAPER.md) for the manuscript and its generated companions.
The [root README](../README.md) covers commands and installation.
The [task board](../tasks/README.md) records current work and review receipts.

Each guide links to related methods, implementation and representative checks.
Source comments provide stable refs and topic tags without adding navigation text
to paper or calculator output. See [the token contract](../tasks/README.md#reference-tokens)
for reference lookup. Original datasets and archived numerical evidence retain their
provenance; their source manifests and relevant guides provide navigation.

## Model, research and interpretation

| Guide | Implementation | Representative checks |
|:---|:---|:---|
| [Causal graph and life-course model plan](CAUSAL_GRAPH_PLAN.md) | [ledger](../src/downstream/ledger.py), [units](../src/downstream/units.py), [variants](../src/downstream/variants.py), [policy](../src/downstream/policy.py), [family](../src/downstream/family.py) |[ledger](../tests/test_ledger.py), [modules](../tests/test_modules.py), [variants](../tests/test_variants.py)|
| [Research plan: a person, their family, and their possible futures](LIFE_COURSE_RESEARCH_PLAN.md) | [scenario](../src/downstream/scenario.py), [household](../src/downstream/household.py), [policy](../src/downstream/policy.py) | [household](../tests/test_household.py), [policy](../tests/test_policy.py), [audit04_custom_inputs](../tests/test_audit04_custom_inputs.py) |
| [MODEL CARD — downstream engine 0.4.0 / parameters v1.52](MODEL_CARD.md) | [scenario](../src/downstream/scenario.py), [vignette](../src/downstream/vignette.py), [cli](../src/downstream/cli.py) |[vignette_scenario_mc](../tests/test_vignette_scenario_mc.py), [cli_direct_contracts](../tests/test_cli_direct_contracts.py), [exposure_semantics](../tests/test_exposure_semantics.py)|
| [Methods paper and generated companions](PAPER.md) | [scenario](../src/downstream/scenario.py), [ledger](../src/downstream/ledger.py), [mortality](../src/downstream/mortality.py), [validate](../src/downstream/validate.py) | [paper_tables](../tests/test_paper_tables.py) |
| [Related work: life-course simulation and causal scenarios](PRIOR_ATTEMPTS.md) | [household](../src/downstream/household.py), [scenario](../src/downstream/scenario.py) | [household](../tests/test_household.py), [audit04_custom_inputs](../tests/test_audit04_custom_inputs.py), [calculator](../tests/test_calculator.py) |
| [RENDERING — how to show the model's work to people who are not mathematicians](RENDERING.md) | [explanation](../src/downstream/explanation.py), [render](../src/downstream/render.py) |[explanation_properties](../tests/test_explanation_properties.py), [guard_rails](../tests/test_guard_rails.py)|

## Evidence, acquisition and source custody

| Guide | Implementation | Representative checks |
|:---|:---|:---|
| [ATTRIBUTION — how this model credits research](ATTRIBUTION.md) | [credits](../src/downstream/credits.py), [citations](../src/downstream/citations.py) |[credits](../tests/test_credits.py), [params](../tests/test_params.py)|
| [CITING — citation and evidence rules](CITING.md) | [params](../src/downstream/params.py), [citations](../src/downstream/citations.py), [audit](../src/downstream/audit.py) |[params](../tests/test_params.py), [audit](../tests/test_audit.py), [source_reextraction](../tests/test_source_reextraction.py)|
| [DATA SOURCES — everything the model needs, and the access path for each](DATA_SOURCES.md) | [brac](../src/downstream/brac.py), [build_places](../src/downstream/build_places.py), [county_mortality](../src/downstream/county_mortality.py) |[brac](../tests/test_brac.py), [build_places_adversarial](../tests/test_build_places_adversarial.py), [county_mortality](../tests/test_county_mortality.py)|
| [Evidence classification for 0.4](EVIDENCE_CLASSIFICATION_0_4.md) | [evidence](../src/downstream/evidence.py), [params](../src/downstream/params.py), [study_library](../src/downstream/study_library.py), [transmissions](../src/downstream/transmissions.py) |[evidence_classification](../tests/test_evidence_classification.py), [evidence](../tests/test_evidence.py)|
| [Literature Acquisition Plan](LITERATURE_ACQUISITION_PLAN.md) | [evidence](../src/downstream/evidence.py), [admission](../src/downstream/admission.py) |[evidence](../tests/test_evidence.py), [admission_provenance](../tests/test_admission_provenance.py)|
| [Independent coefficient pool readiness for 0.4](POOL_READINESS_0_4.md) | [study_library](../src/downstream/study_library.py), [synthesis](../src/downstream/synthesis.py), [admission](../src/downstream/admission.py) |[pool_readiness](../tests/test_pool_readiness.py), [synthesis](../tests/test_synthesis.py), [admission_provenance](../tests/test_admission_provenance.py)|
| [PSID baseline-data assessment — 2026-09-13](PSID_BASELINE_DATA_ASSESSMENT_2026-09-13.md) | [household](../src/downstream/household.py) | [household](../tests/test_household.py), [household_summary](../tests/test_household_summary.py) |
| [QUEUED EXTRACTIONS](QUEUED_EXTRACTIONS.md) | [params](../src/downstream/params.py), [evidence](../src/downstream/evidence.py), [admission](../src/downstream/admission.py) |[source_reextraction](../tests/test_source_reextraction.py), [admission_provenance](../tests/test_admission_provenance.py)|

## Exposure, consumer contracts and releases

| Guide | Implementation | Representative checks |
|:---|:---|:---|
| [Consumer acceptance fixtures for Downstream 0.4](CONSUMER_FIXTURES_0_4.md) | [consumer](../src/downstream/consumer.py), [bundle](../src/downstream/bundle.py), [snapshot](../src/downstream/snapshot.py) |[consumer_fixtures](../tests/test_consumer_fixtures.py), [consumer_api](../tests/test_consumer_api.py), [bundle](../tests/test_bundle.py)|
| [Entity exposure semantics in 0.4](EXPOSURE_SEMANTICS_0_4.md) | [employer](../src/downstream/employer.py), [scenario](../src/downstream/scenario.py), [community](../src/downstream/community.py) |[exposure_semantics](../tests/test_exposure_semantics.py), [employer](../tests/test_employer.py), [adapter_adversarial](../tests/test_adapter_adversarial.py)|
| [Open source release checklist](OPEN_SOURCE_RELEASE.md) | [bundle](../src/downstream/bundle.py), [credits](../src/downstream/credits.py), [audit](../src/downstream/audit.py) |[bundle](../tests/test_bundle.py), [export](../tests/test_export.py), [credits](../tests/test_credits.py)|
| [Downstream 0.4.0 — pending update and review follow-through](RELEASE_0_4.md) | [scenario](../src/downstream/scenario.py), [audit](../src/downstream/audit.py), [consumer](../src/downstream/consumer.py) |[release_repairs](../tests/test_release_repairs.py), [consumer_fixtures](../tests/test_consumer_fixtures.py), [exposure_semantics](../tests/test_exposure_semantics.py)|
| [Comparing versions](VERSION_COMPARISON.md) | [compare](../src/downstream/compare.py), [snapshot](../src/downstream/snapshot.py) | [compare](../tests/test_compare.py), [export](../tests/test_export.py), [release_repairs](../tests/test_release_repairs.py) |
| [Downstream 0.4 priorities informed by XH1B usage](XH1B_USAGE_PLAN_0_4.md) | [employer](../src/downstream/employer.py), [consumer](../src/downstream/consumer.py) |[consumer_fixtures](../tests/test_consumer_fixtures.py), [consumer_api](../tests/test_consumer_api.py), [exposure_semantics](../tests/test_exposure_semantics.py)|

## Mortality and place

| Guide | Implementation | Representative checks |
|:---|:---|:---|
| [CDC WONDER profile download and import](CDC_WONDER_PROFILE_IMPORT.md) | [county_mortality](../src/downstream/county_mortality.py), [mortality_profiles](../src/downstream/mortality_profiles.py) | [county_mortality](../tests/test_county_mortality.py), [mortality_profiles](../tests/test_mortality_profiles.py), [adapter_adversarial](../tests/test_adapter_adversarial.py) |
| [Mortality applicability in 0.4](MORTALITY_APPLICABILITY_0_4.md) | [mortality_profiles](../src/downstream/mortality_profiles.py), [mortality_strata](../src/downstream/mortality_strata.py) |[mortality_admission_0_4](../tests/test_mortality_admission_0_4.py), [mortality_profiles](../tests/test_mortality_profiles.py), [mortality_strata](../tests/test_mortality_strata.py)|
| [Published additive mortality coefficients: covariance diagnostic](MORTALITY_COVARIANCE_0_4.md) | [mortality_covariance](../src/downstream/mortality_covariance.py) | [mortality_covariance](../tests/test_mortality_covariance.py) |
| [Analysis of mortality persistence: 28.76 versus 20.52](MORTALITY_PERSISTENCE_ANALYSIS_2026-10-14.md) | [mortality](../src/downstream/mortality.py), [mortality_robustness](../src/downstream/mortality_robustness.py) |[mortality_robustness](../tests/test_mortality_robustness.py), [audit04_mortality_precision](../tests/test_audit04_mortality_precision.py)|
| [Mortality persistence sensitivity — engine 0.4.0](MORTALITY_PERSISTENCE_SENSITIVITY.md) | [mortality_robustness](../src/downstream/mortality_robustness.py), [scenario](../src/downstream/scenario.py) |[mortality_robustness](../tests/test_mortality_robustness.py), [result_sensitivity](../tests/test_result_sensitivity.py)|
| [Mortality source reconciliation — 2026-09-10](MORTALITY_SOURCE_RECONCILIATION_2026-09-10.md) | [mortality](../src/downstream/mortality.py), [worker](../src/downstream/worker.py) |[audit04_mortality_precision](../tests/test_audit04_mortality_precision.py), [mathematics_v02](../tests/test_mathematics_v02.py), [metamorphic](../tests/test_metamorphic.py)|
| [Same-place child-earnings counterfactual](PLACE_COUNTERFACTUAL.md) | [place](../src/downstream/place.py), [build_places](../src/downstream/build_places.py), [county_rates](../src/downstream/county_rates.py) | [place](../tests/test_place.py), [county_rates](../tests/test_county_rates.py), [build_places_adversarial](../tests/test_build_places_adversarial.py) |

## Children, households and receiving communities

| Guide | Implementation | Representative checks |
|:---|:---|:---|
| [R2 artifact 1: ordinary December-to-December employment and earnings transitions (SIPP 2021→2022)](BASELINE_TRANSITION_R2_2026-09-14.md) | [household](../src/downstream/household.py) | [household](../tests/test_household.py), [household_summary](../tests/test_household_summary.py) |
| [Child and descendant earnings gaps](CHILD_GAP_VIEW.md) | [child_gap_view](../src/downstream/child_gap_view.py), [children](../src/downstream/children.py), [transmissions](../src/downstream/transmissions.py), [valuation](../src/downstream/valuation.py) |[child_gap_view](../tests/test_child_gap_view.py), [child_gap_cli](../tests/test_child_gap_cli.py), [transmissions](../tests/test_transmissions.py)|
| [Inspect child source support in 0.4](CHILD_SUPPORT_0_4.md) | [child_support](../src/downstream/child_support.py), [child_applicability](../src/downstream/child_applicability.py), [study_library](../src/downstream/study_library.py) |[child_support](../tests/test_child_support.py), [child_applicability](../tests/test_child_applicability.py), [pool_readiness](../tests/test_pool_readiness.py)|
| [Annual household comparison summaries in 0.4](HOUSEHOLD_COMPARISON_0_4.md) | [household](../src/downstream/household.py) | [household](../tests/test_household.py), [household_summary](../tests/test_household_summary.py) |
| [Receiving-community channel: evidence scan and search protocol (2026-09-14)](IMMIGRATION_REPLACEMENT_EVIDENCE_SCAN_2026-09-14.md) | [receiving_community](../src/downstream/receiving_community.py) | [receiving_community](../tests/test_receiving_community.py), [receiving_adapter](../tests/test_receiving_adapter.py) |
| [Receiving-community scenarios in 0.4](RECEIVING_COMMUNITY_0_4.md) | [receiving_community](../src/downstream/receiving_community.py) | [receiving_community](../tests/test_receiving_community.py), [receiving_adapter](../tests/test_receiving_adapter.py) |
| [Remarriage-margin screen](REMARRIAGE_MARGIN_SCREEN_0_4.md) | [family](../src/downstream/family.py), [admission](../src/downstream/admission.py) |[remarriage_screen](../tests/test_remarriage_screen.py)|
| [SIPP baseline-data assessment — 2026-09-13](SIPP_BASELINE_DATA_ASSESSMENT_2026-09-13.md) | [household](../src/downstream/household.py) | [household](../tests/test_household.py), [household_summary](../tests/test_household_summary.py) |

## Uncertainty and verification

| Guide | Implementation | Representative checks |
|:---|:---|:---|
| [Probabilistic extension roadmap](PROBABILISTIC_ROADMAP.md) | [distributions](../src/downstream/distributions.py), [mc](../src/downstream/mc.py), [inference](../src/downstream/inference.py), [uncertainty_budget](../src/downstream/uncertainty_budget.py), [county_rates](../src/downstream/county_rates.py) | [distributions](../tests/test_distributions.py), [inference](../tests/test_inference.py), [uncertainty_budget](../tests/test_uncertainty_budget.py) |
| [Sensitivity attached to scenario results](RESULT_SENSITIVITY.md) | [result_sensitivity](../src/downstream/result_sensitivity.py), [sensitivity](../src/downstream/sensitivity.py), [knobs](../src/downstream/knobs.py) |[result_sensitivity](../tests/test_result_sensitivity.py), [sensitivity_scoring](../tests/test_sensitivity_scoring.py), [knobs](../tests/test_knobs.py)|
| [Testing quality review — 2026-09-09](TESTING_QUALITY.md) | [ledger](../src/downstream/ledger.py), [validate](../src/downstream/validate.py) |[properties_hypothesis](../tests/test_properties_hypothesis.py), [mathematics_v02](../tests/test_mathematics_v02.py)|

## Calculator

| Guide | Implementation | Representative checks |
|:---|:---|:---|
| [Local calculator](CALCULATOR.md) | [mortality](../src/downstream/mortality.py), [scenario](../src/downstream/scenario.py) |[calculator](../tests/test_calculator.py), [calculator_server](../tests/test_calculator_server.py)|
| [Website experience plan: explore possible futures](WEBSITE_EXPERIENCE_PLAN.md) | [explanation](../src/downstream/explanation.py), [render](../src/downstream/render.py) | [explanation_properties](../tests/test_explanation_properties.py), [guard_rails](../tests/test_guard_rails.py), [release_repairs](../tests/test_release_repairs.py) |

## Engine and verification navigation

Modules below link back to their primary guide and checks; each test file links
to the contract and implementation it exercises. The source comments preserve
public docstrings and executable behavior.

| Module | Primary guide |
|:---|:---|
| [__init__](../src/downstream/__init__.py) | [model card](MODEL_CARD.md) |
| [admission](../src/downstream/admission.py) | [pool readiness 0 4](POOL_READINESS_0_4.md) |
| [audit](../src/downstream/audit.py) | [citing](CITING.md) |
| [brac](../src/downstream/brac.py) | [data sources](DATA_SOURCES.md) |
| [build_places](../src/downstream/build_places.py) | [place counterfactual](PLACE_COUNTERFACTUAL.md) |
| [bundle](../src/downstream/bundle.py) | [consumer fixtures 0 4](CONSUMER_FIXTURES_0_4.md) |
| [child_applicability](../src/downstream/child_applicability.py) | [child support 0 4](CHILD_SUPPORT_0_4.md) |
| [child_gap_view](../src/downstream/child_gap_view.py) | [child gap view](CHILD_GAP_VIEW.md) |
| [child_support](../src/downstream/child_support.py) | [child support 0 4](CHILD_SUPPORT_0_4.md) |
| [children](../src/downstream/children.py) | [child gap view](CHILD_GAP_VIEW.md) |
| [citations](../src/downstream/citations.py) | [citing](CITING.md) |
| [cli](../src/downstream/cli.py) | [model card](MODEL_CARD.md) |
| [community](../src/downstream/community.py) | [exposure semantics 0 4](EXPOSURE_SEMANTICS_0_4.md) |
| [compare](../src/downstream/compare.py) | [version comparison](VERSION_COMPARISON.md) |
| [consumer](../src/downstream/consumer.py) | [consumer fixtures 0 4](CONSUMER_FIXTURES_0_4.md) |
| [county_mortality](../src/downstream/county_mortality.py) | [cdc wonder profile import](CDC_WONDER_PROFILE_IMPORT.md) |
| [county_rates](../src/downstream/county_rates.py) | [probabilistic roadmap](PROBABILISTIC_ROADMAP.md) |
| [credits](../src/downstream/credits.py) | [attribution](ATTRIBUTION.md) |
| [distributions](../src/downstream/distributions.py) | [probabilistic roadmap](PROBABILISTIC_ROADMAP.md) |
| [employer](../src/downstream/employer.py) | [exposure semantics 0 4](EXPOSURE_SEMANTICS_0_4.md) |
| [evidence](../src/downstream/evidence.py) | [literature acquisition plan](LITERATURE_ACQUISITION_PLAN.md) |
| [explanation](../src/downstream/explanation.py) | [rendering](RENDERING.md) |
| [family](../src/downstream/family.py) | [causal graph plan](CAUSAL_GRAPH_PLAN.md) |
| [forecast_registry](../src/downstream/forecast_registry.py) | [scenario evidence protocol](SCENARIO_EVIDENCE_PROTOCOL.md) |
| [household](../src/downstream/household.py) | [household comparison 0 4](HOUSEHOLD_COMPARISON_0_4.md) |
| [inference](../src/downstream/inference.py) | [probabilistic roadmap](PROBABILISTIC_ROADMAP.md) |
| [knobs](../src/downstream/knobs.py) | [result sensitivity](RESULT_SENSITIVITY.md) |
| [ledger](../src/downstream/ledger.py) | [causal graph plan](CAUSAL_GRAPH_PLAN.md) |
| [mc](../src/downstream/mc.py) | [probabilistic roadmap](PROBABILISTIC_ROADMAP.md) |
| [mortality](../src/downstream/mortality.py) | [mortality source reconciliation 2026-09-10](MORTALITY_SOURCE_RECONCILIATION_2026-09-10.md) |
| [mortality_covariance](../src/downstream/mortality_covariance.py) | [mortality covariance 0 4](MORTALITY_COVARIANCE_0_4.md) |
| [mortality_profiles](../src/downstream/mortality_profiles.py) | [mortality applicability 0 4](MORTALITY_APPLICABILITY_0_4.md) |
| [mortality_robustness](../src/downstream/mortality_robustness.py) | [mortality persistence sensitivity](MORTALITY_PERSISTENCE_SENSITIVITY.md) |
| [mortality_strata](../src/downstream/mortality_strata.py) | [mortality applicability 0 4](MORTALITY_APPLICABILITY_0_4.md) |
| [params](../src/downstream/params.py) | [citing](CITING.md) |
| [place](../src/downstream/place.py) | [place counterfactual](PLACE_COUNTERFACTUAL.md) |
| [policy](../src/downstream/policy.py) | [causal graph plan](CAUSAL_GRAPH_PLAN.md) |
| [receiving_community](../src/downstream/receiving_community.py) | [receiving community 0 4](RECEIVING_COMMUNITY_0_4.md) |
| [render](../src/downstream/render.py) | [rendering](RENDERING.md) |
| [result_sensitivity](../src/downstream/result_sensitivity.py) | [result sensitivity](RESULT_SENSITIVITY.md) |
| [scenario](../src/downstream/scenario.py) | [exposure semantics 0 4](EXPOSURE_SEMANTICS_0_4.md) |
| [scoring](../src/downstream/scoring.py) | [scenario evidence protocol](SCENARIO_EVIDENCE_PROTOCOL.md) |
| [sensitivity](../src/downstream/sensitivity.py) | [result sensitivity](RESULT_SENSITIVITY.md) |
| [snapshot](../src/downstream/snapshot.py) | [version comparison](VERSION_COMPARISON.md) |
| [study_library](../src/downstream/study_library.py) | [pool readiness 0 4](POOL_READINESS_0_4.md) |
| [synthesis](../src/downstream/synthesis.py) | [pool readiness 0 4](POOL_READINESS_0_4.md) |
| [transmissions](../src/downstream/transmissions.py) | [child gap view](CHILD_GAP_VIEW.md) |
| [uncertainty_budget](../src/downstream/uncertainty_budget.py) | [probabilistic roadmap](PROBABILISTIC_ROADMAP.md) |
| [units](../src/downstream/units.py) | [causal graph plan](CAUSAL_GRAPH_PLAN.md) |
| [validate](../src/downstream/validate.py) | [scenario evidence protocol](SCENARIO_EVIDENCE_PROTOCOL.md) |
| [valuation](../src/downstream/valuation.py) | [child gap view](CHILD_GAP_VIEW.md) |
| [variants](../src/downstream/variants.py) | [causal graph plan](CAUSAL_GRAPH_PLAN.md) |
| [vignette](../src/downstream/vignette.py) | [model card](MODEL_CARD.md) |
| [worker](../src/downstream/worker.py) | [mortality source reconciliation 2026-09-10](MORTALITY_SOURCE_RECONCILIATION_2026-09-10.md) |

## Reproduction and maintenance scripts

| Script | Guide |
|:---|:---|
| [acquire_followthrough_sources](../scripts/acquire_followthrough_sources.py) | [scenario evidence protocol](SCENARIO_EVIDENCE_PROTOCOL.md) |
| [analyze_mortality_covariance](../scripts/analyze_mortality_covariance.py) | [mortality covariance 0 4](MORTALITY_COVARIANCE_0_4.md) |
| [analyze_mortality_persistence](../scripts/analyze_mortality_persistence.py) | [mortality persistence analysis 2026-10-14](MORTALITY_PERSISTENCE_ANALYSIS_2026-10-14.md) |
| [benchmark](../scripts/benchmark.py) | [testing quality](TESTING_QUALITY.md) |
| [build_age_mortality](../scripts/build_age_mortality.py) | [mortality applicability 0 4](MORTALITY_APPLICABILITY_0_4.md) |
| [build_baseline_transitions](../scripts/build_baseline_transitions.py) | [baseline transition r2 2026-09-14](BASELINE_TRANSITION_R2_2026-09-14.md) |
| [build_calculator](../scripts/build_calculator.py) | [calculator](CALCULATOR.md) |
| [build_cohort_projection](../scripts/build_cohort_projection.py) | [mortality applicability 0 4](MORTALITY_APPLICABILITY_0_4.md) |
| [build_consumer_fixtures](../scripts/build_consumer_fixtures.py) | [consumer fixtures 0 4](CONSUMER_FIXTURES_0_4.md) |
| [build_county_mortality](../scripts/build_county_mortality.py) | [cdc wonder profile import](CDC_WONDER_PROFILE_IMPORT.md) |
| [build_displaced_cohort](../scripts/build_displaced_cohort.py) | [scenario evidence protocol](SCENARIO_EVIDENCE_PROTOCOL.md) |
| [build_evidence_classification](../scripts/build_evidence_classification.py) | [evidence classification 0 4](EVIDENCE_CLASSIFICATION_0_4.md) |
| [build_methods_html](../scripts/build_methods_html.py) | [paper](PAPER.md) |
| [build_pool_readiness](../scripts/build_pool_readiness.py) | [pool readiness 0 4](POOL_READINESS_0_4.md) |
| [check_distribution](../scripts/check_distribution.py) | [open source release](OPEN_SOURCE_RELEASE.md) |
| [evaluate_followthrough](../scripts/evaluate_followthrough.py) | [scenario evidence protocol](SCENARIO_EVIDENCE_PROTOCOL.md) |
| [fetch_dois](../scripts/fetch_dois.py) | [attribution](ATTRIBUTION.md) |
| [fetch_wonder](../scripts/fetch_wonder.py) | [cdc wonder profile import](CDC_WONDER_PROFILE_IMPORT.md) |
| [import_evidence_corpus](../scripts/import_evidence_corpus.py) | [literature acquisition plan](LITERATURE_ACQUISITION_PLAN.md) |
| [inspect_child_support](../scripts/inspect_child_support.py) | [child support 0 4](CHILD_SUPPORT_0_4.md) |
| [quality_gate](../scripts/quality_gate.py) | [testing quality](TESTING_QUALITY.md) |
| [refcheck](../scripts/refcheck.py) | [readme](README.md) |
| [serve_calculator](../scripts/serve_calculator.py) | [calculator](CALCULATOR.md) |
| [tasks](../scripts/tasks.py) | [readme](README.md) |
| [vulture_whitelist](../scripts/vulture_whitelist.py) | [testing quality](TESTING_QUALITY.md) |

## Entry points and source custody

- [Contributing](../CONTRIBUTING.md), [security reporting](../SECURITY.md) and [community conduct](../CODE_OF_CONDUCT.md).
- [Parameter change history](../params/CHANGELOG.md), [bibliography](../params/references.bib) and [computed attribution](../CREDITS.md).
- [SIPP data provenance](../validation/sipp/MANIFEST.md); original Census input examples and data dictionaries remain source artifacts.
- [Task workflow](../tasks/AGENTS.md) and [migration record](../tasks/MIGRATION.md); retained card bodies and comments remain historical records.
- [Package and quality configuration](../pyproject.toml), [quality workflow](../.github/workflows/quality.yml) and [paper publication workflow](../.github/workflows/publish-paper.yml).

## Finding a connection

```sh
python3 scripts/refcheck.py list
python3 scripts/refcheck.py show paper-counts
rg -n '@tag:mortality' src/ docs/ tests/ paper/
python3 scripts/tasks.py tags
python3 scripts/refcheck.py check
python3 scripts/tasks.py validate
```

Anchor IDs identify specific source locations. Tags identify related topics.
Ordinary Markdown links make files directly browsable. Backlinks are computed by
the reference tools; this guide groups maintained entry points rather than copying
a separate backlink database.
