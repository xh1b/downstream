---
title: Review remaining tasks and reconcile the 0.4 release scope
area: release
priority: P1
assignee: codex-release-review
tags: [@tag:tooling]
blocked-by: []
---

Review every remaining task against current implementation and receipts; verify repository navigation coverage, repair confirmed gaps, and distinguish release work from research dependencies.

- [x] Review every inbox, ready and review task and record an evidence-backed 0.4 disposition. [receipt](@task:2026-10-17-release-task-review#c-58acce20734e)
- [x] Verify navigation coverage and fix confirmed link/ref gaps. [receipt](@task:2026-10-17-release-task-review#c-58acce20734e)
- [x] Reconcile stale release/task descriptions without losing historical evidence or accepting unreviewed work. [receipt](@task:2026-10-17-release-task-review#c-58acce20734e)
- [x] Record verification and a prioritized release recommendation. [receipt](@task:2026-10-17-release-task-review#c-58acce20734e)

## Review scope and recommendation — 2026-10-17

Reviewed all **35 pre-existing open cards** (inbox, ready and review), their
acceptance text, retained receipts and related code/contracts. This review
excludes its own tracking card. Existing source archives and accepted work
supply context; no new primary-source admission or causal validation is claimed.
No companion checkout, remote state, deployment or publication was changed or
freshly verified.

The release recommendation is to include the already implemented conditional
paths, the artifact/navigation repairs in `b4a9480`, and the reconciled scope
in `7953802` and `b7915fd`. Next, qualify a fixed candidate and verify the
companion against its fixtures. Keep human/public-readiness and empirical
expansion gates explicit. SIPP pooling/replicate uncertainty is the first
substantive household-data improvement if that scope is added to 0.4.

The following is a dated review of existing cards, not a second backlog.
Their cards retain ownership, checklists and history; no review task was
silently accepted or discarded.

| Existing task | 0.4 disposition | Evidence and remaining scope |
|:---|:---|:---|
| [W0-W3 - Design and comprehension-test the calculator](@task:2026-10-14-calculator-design) | Complete human/accessibility checks for public readiness | [Evidence](../../../docs/CALCULATOR.md). Visual directions, chosen calculator and viewport work are delivered. Test comprehension, keyboard, zoom, assistive technology and actual devices; no further redesign is required by this card. |
| [Decide whether boundary-fenced streams should become headline claims](@task:2026-10-14-headline-streams) | Defer expansion; owner decision | [Evidence](../../../docs/MODEL_CARD.md). Keep fertility, child mental health and partner labor supply consultable with their source boundaries; no new headline promotion is justified by this release review. |
| [Obtain matched external data and independently evaluate new paths](@task:2026-10-14-matched-event-evaluation) | External-data dependency | [Evidence](../../../docs/SCENARIO_EVIDENCE_PROTOCOL.md). No qualified matched exposure bridge plus independent outcomes is evidenced. Retain existing diagnostic misses and withhold causal validation claims. |
| [R7-R8 - Add supported protective interventions and combinations](@task:2026-10-14-protective-interventions) | Defer until supported source admission | [Evidence](../../../docs/LIFE_COURSE_RESEARCH_PLAN.md). Protective effects already present stay signed. New interventions and combinations require distinct estimands, overlap/dependence and evidence rather than summing coefficients. |
| [R6 / W4-W5 - Release an evaluated public experience](@task:2026-10-14-public-experience) | Retain scientific and human-testing gates | [Evidence](../../../docs/WEBSITE_EXPERIENCE_PLAN.md). This larger evaluated experience remains blocked by validation/applicability and comprehension. A conditional local scenario-tool release is a narrower scope. |
| [Coordinate the pending 0.4 update with XH1B integration](@task:2026-10-14-xh1b-handoff) | Required companion acceptance | [Evidence](../../../docs/CONSUMER_FIXTURES_0_4.md). Native contracts, fixtures and transforms exist. Link current companion tasks, verify nested fields, scaling, mixtures and caches, then collect fresh page/deployment receipts. The old inspection is not current deployment evidence. |
| [Expand child eligibility and heterogeneity evidence](@task:2026-10-14-child-heterogeneity) | Ship current eligibility; defer broader admission | [Evidence](../../../docs/CHILD_SUPPORT_0_4.md). Age/sex restrictions and signed quartile contrasts exist. Additional countries, ages and parent restrictions need primary-source extraction; do not invent an age curve. |
| [Populate compatible independent coefficient pools](@task:2026-10-14-coefficient-library) | Ship readiness diagnostic; defer new pooling | [Evidence](../../../docs/POOL_READINESS_0_4.md). 23 contrasts are three overlapping study samples. All 253 pairs are screened and no compatible independent pool is claimed. Independent source extraction remains substantive research. |
| [R3 - Complete the five-year comparison and receiving-community scope](@task:2026-10-14-full-comparison) | Partial implementation delivered; scope corrected | [Evidence](../../../docs/HOUSEHOLD_COMPARISON_0_4.md). Five-year gross earnings/state-time comparison and source-specific receiving adapter exist. Saved result refreshed. Broader household resources and remaining receiving channels stay open. |
| [Extend household dynamics beyond the annual prototype](@task:2026-10-14-household-dynamics) | Ship annual prototype; defer monthly/joint model | [Evidence](../../../docs/HOUSEHOLD_COMPARISON_0_4.md). Current marginal probabilities and gross earnings reconcile. Monthly recovery, taxes/transfers, membership changes and joint dependence need additional modeling and evidence. |
| [Expand supported mortality strata](@task:2026-10-14-mortality-strata) | Ship admitted male strata; defer wider response evidence | [Evidence](../../../docs/MORTALITY_APPLICABILITY_0_4.md). Male age-at-event strata and aging/fixed baselines are implemented. Observed female baseline hazards do not admit female treatment responses; uncovered strata must stay unknown. |
| [Select and freeze two or three real prospective events](@task:2026-10-14-prospective-events) | Defer until a qualified bridge exists | [Evidence](../../../docs/SCENARIO_EVIDENCE_PROTOCOL.md). Registration/scoring tools are implemented. Real event selection, independent timestamps and future outcomes cannot be replaced with retrospective software receipts. |
| [Resolve the published-QJE mortality profile covariance gap](@task:2026-10-14-published-mortality-profile) | Ship diagnostic only; keep production admission blocked | [Evidence](../../../docs/MORTALITY_COVARIANCE_0_4.md). Accepted marginal PSD covariance bounds are available. They do not provide joint draws, simultaneous coverage, nonlinear cumulative-death bounds or published-version reconciliation. |
| [Qualify Downstream 0.4 for the XH1B handoff](@task:2026-10-14-release-04-readiness) | Required next release unit; triaged ready | [Evidence](../../../docs/RELEASE_0_4.md). Freeze one candidate, rebuild artifacts, run the complete qualification/comparison and obtain release acceptance. Existing exposure, fixture and prototype-scope documentation is now checked with evidence. |
| [R2 - Pool SIPP trajectories and estimate survey-design uncertainty](@task:2026-10-14-sipp-trajectories) | First substantive household-data follow-up | [Evidence](../../../docs/BASELINE_TRANSITION_R2_2026-09-14.md). Pool compatible waves and use replicate weights before claiming better sparse-cell accuracy or survey uncertainty. Preserve current held-out misses. This is optional for the explicitly limited reference-count release. |
| [Define the target displaced cohort](@task:2026-10-14-target-displaced-cohort) | Ship reference/exposure contract; keep empirical bridge open | [Evidence](../../../docs/EXPOSURE_SEMANTICS_0_4.md). Generic CPS reproduction and unknown-target handling exist. H-1B-specific displacement, demographics, overlap and event timing require a sourced bridge; filing equivalents are not unique people. |
| [Extend uncertainty to transport and unknown dependence](@task:2026-10-14-transport-uncertainty) | Ship existing qualified budget; defer unsupported models | [Evidence](../../../docs/RESULT_SENSITIVITY.md). Existing baseline/exposure/process options and explicit exclusions are implemented. No invented transport errors, structural probabilities or cross-component correlations. |
| [Re-evaluate V2 validation eligibility after the SIPP baseline](@task:2026-10-14-v2-validation) | Retain external blocker; baseline scope clarified | [Evidence](../../../docs/SCENARIO_EVIDENCE_PROTOCOL.md). Held-out SIPP baseline calibration already exists. Repeating it cannot establish a causal displacement bridge or repair BRAC/NAFTA/auto alignment gaps. |
| [R4-R5 - Independent validation and applicability](@task:2026-10-14-validation-applicability) | External-data dependency | [Evidence](../../../docs/SCENARIO_EVIDENCE_PROTOCOL.md). A frozen matched evaluation and comparison with simpler baselines remain unperformed. Existing subgroup restrictions and diagnostic misses must continue to ship. |
| [Audit 0.4 calculations, sources and release documentation](@task:2026-10-14-audit-04-release) | Existing 0.4 work; final review/qualification | [Evidence](../../../tests/test_audit04_sources.py). Numerical/source audit and fixes are implemented. Its historical receipt is not the final current-candidate run, nor a fresh re-extraction of all 67 parameter links. |
| [Age-timed child-dollar present values](@task:2026-10-14-child-present-values) | Include existing conditional valuation | [Evidence](../../../src/downstream/valuation.py). Keep observed-age-window and career extrapolations, explicit timing/discounting, zero-rate equivalence and signed subgroup benefits separate. |
| [Port XH1B task references and Markdown workflow](@task:2026-10-14-kanban-markdown-port) | Existing tooling; review acceptance remains | [Evidence](../../../tests/test_tasks_board.py). References, relationship validation, append-only comments and explicit-path commits exist; focused task/reference regressions are rerun in this review. |
| [Mortality persistence robustness](@task:2026-10-14-mortality-persistence) | Include existing two-structure comparison | [Evidence](../../../tests/test_mortality_robustness.py). Source and no-sustained-excess alternatives share inputs and paired draws. Neither an unweighted spread nor a null-compatible study justifies model averaging or a zero true effect. |
| [Analyze the mortality persistence comparison](@task:2026-10-14-mortality-persistence-analysis) | Include existing analysis; no default change | [Evidence](../../../docs/MORTALITY_PERSISTENCE_ANALYSIS_2026-10-14.md). 28.76 versus 20.52 is documented with timing/baseline/transport limits; retain the paired calculation and source divergence. |
| [Attach input sensitivity reports to scenario results](@task:2026-10-14-result-sensitivity) | Include existing reports; verify companion delivery | [Evidence](../../../docs/RESULT_SENSITIVITY.md). Native removals, endpoints and optional variance attribution exist. Companion parsing, scaling and mixtures must preserve the complete metadata. |
| [Record the sustained-mortality alternative and source divergence](@task:2026-10-14-sustained-mortality-alternative) | Include existing named alternative | [Evidence](../../../docs/MORTALITY_PERSISTENCE_SENSITIVITY.md). The source-divergence record and named alternative overlap the persistence implementation; no second implementation is needed. Keep separate historical cards and owner review. |
| [Plan Downstream priorities from current XH1B usage](@task:2026-10-14-xh1b-usage-plan) | Use existing plan; refresh integration evidence at handoff | [Evidence](../../../docs/XH1B_USAGE_PLAN_0_4.md). The local October 14 source inspection is a compatibility plan, not a claim about the present companion pin, caches or deployed pages. |
| [Promote calculator app and add local web server](@task:2026-10-15-calculator-app-server) | Include existing application/server | [Evidence](../../../tests/test_calculator_server.py). Dedicated loopback server and narrow file serving are implemented; browser checks have receipts. No new hosting or deployment is needed for a local-tool release. |
| [Refactor calculator into pure calculation and focused rendering functions](@task:2026-10-15-calculator-functional) | Include existing refactor | [Evidence](../../../tests/test_calculator.py). Pure calculations, focused rendering and native parity tests exist. This does not establish comprehension or assistive-technology results. |
| [Apply follow-up Dependabot updates and repair CI failures](@task:2026-10-15-dependabot-followup) | Include landed dependency/portability repairs | [Evidence](../../../tests/test_paper_tables.py). Artifact actions, Hypothesis/Ruff and portable methods fingerprint are committed. Full-precision engine/export values remain unchanged. |
| [Apply open Dependabot dependency updates](@task:2026-10-15-dependabot-updates) | Include landed dependency updates | [Evidence](../../../pyproject.toml). All six original changes are present. Prior 1433-test and packaging receipts remain historical; use the final frozen candidate for release acceptance. |
| [Document linked Markdown, code and paper conventions](@task:2026-10-15-linked-documentation-guidance) | Include existing conventions | [Evidence](../../../AGENTS.md). Maintained Markdown placement, reciprocal refs and hidden paper metadata are documented; instructions alone are not the rollout evidence. |
| [Connect existing docs, code, tests and paper with repository references](@task:2026-10-15-repository-reference-rollout) | Broad coverage verified; generator gaps repaired | [Evidence](../../../docs/README.md). All maintained source/guide classes are covered with intentional reference-test/generated-copy exceptions. Two generated guide headers were not reproducible; their generators and freshness regressions are now repaired. |
| [Port XH1B task tags, refs and links](@task:2026-10-15-task-tags-refs-links) | Include existing token tooling | [Evidence](../../../tests/test_refcheck.py). Token uniqueness/resolution and canonical task links are implemented. Frozen historical evidence exemptions are preserved; checker success does not certify scientific correctness. |
| [Simplify cooperative task-board tooling](@task:2026-10-15-task-tool-convenience) | Include existing tooling; preserve separate owner acceptance | [Evidence](../../../tests/test_tasks_workflow.py). Stable-ID viewing, multiline receipts, historical summaries and shared-index safeguards exist. No review cards are silently self-accepted. |

## Navigation review

The initial scan resolves 314 anchors and 1335 links. Coverage includes all
54 engine modules, 25 Python scripts, 42 Markdown guides and seven authored
LaTeX manuscript/figure/style sources. Of 110 test files, 109 participate in
the token graph; [test_refcheck.py](../../../tests/test_refcheck.py) is the
documented deliberate-fixture exception in the
[allowlist](../../../scripts/refcheck-allowlist.txt). Its verification anchor
and ordinary file link live in the testing guide. All four authored calculator
sources have canonical definitions; generated index.html cites those definitions
instead of duplicating them. Imported source data and archived numerical records
are not blanket-annotated.

All 898 initially checked maintained Markdown file links resolve. Historical
task comments are preserved rather than rewritten for old relative paths.
Token validity checks spelling, uniqueness and resolution; it does not prove
every semantic relationship or scientific claim. The two confirmed propagation
gaps were generated guide headers: regeneration would remove their anchors and
links. The generators now own those headers, with freshness/navigation regressions.

## Confirmed fixes

- Evidence classification and pool-readiness reports regenerated with current
  source hashes and source-generated navigation; both previously failed `--check`.
- Consumer fixtures refreshed: 56 file hashes and the collection fingerprint
  were stale; fixture numerical results were unchanged. Added a committed-source
  identity regression.
- The saved five-year household report regenerated to include the current
  comparison summary and explicit window, paired earnings precision and current
  limitations. Added a saved-example regression and a reproducible guide link.
- Seven stale task descriptions/checklists reconciled without modifying the
  frozen legacy evidence ledger. Readiness is triaged to ready; the other open
  scientific tasks retain their unmet scope and existing dependencies.

Further publication, companion integration, research acquisition and human
participant work remain on the corresponding existing cards.

## Final verification

[The final receipt](@task:2026-10-17-release-task-review#c-58acce20734e)
records 393 passing focused tests, all four generator freshness checks, lint,
the zero-error/warning evidence audit, 314 resolved anchors/1357 links and
904 existing maintained Markdown file targets. Full-suite/coverage/distribution
qualification on one frozen candidate remains an explicit release task.

The [paper](../../../paper/downstream.pdf) was rebuilt after the validation
artifact refresh. Its manifest digest verifies, text changes only in the page-14
source fingerprint, and the changed page was rendered and inspected. Build and
render receipts are in `build/release-task-review-20261017/` (ignored, reproducible).
No manuscript source or scientific default changed.
