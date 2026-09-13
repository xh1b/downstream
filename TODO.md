# TODO — downstream model (standalone repo, LOCAL-ONLY)

Model-side work lives here. XH1B-side integration tasks (entity_analysis
migration, runner script, phased backfill, incremental mode + scheduler,
website surfaces) live in the parent repo's `internal/TODO.md` under
"Downstream integration". Design for that side:
`internal/docs/ENTITY_ANALYSIS.md` (parent repo).

Research plan of record: `docs/LIFE_COURSE_RESEARCH_PLAN.md` (2026-09-10),
with model design in `docs/CAUSAL_GRAPH_PLAN.md`. The earlier top-10 work
remains recorded below. Every numerical claim retains provenance; misses publish.

## Current scope

Owner direction: improve this project and plan an eventual public calculator.
The experience plan is `docs/WEBSITE_EXPERIENCE_PLAN.md`; website implementation
and XH1B integration remain future work.
See `docs/MATH_REVIEW.md` for reviewed arithmetic and remaining assumptions.

## Forward goals

- **[R0-R1] Correct and classify:** resolve current review findings; distinguish
  baseline transitions, causal effects, and structural assumptions in evidence records.
- **[R2] Baseline household trajectories:** select suitable longitudinal data,
  represent linked members/resources, and evaluate held-out ordinary transitions.
- **[R3] First full comparison:** a five-year involuntary-displacement scenario
  versus a stated reference, limited to supported employment, earnings, and
  household-resource outcomes. Current long-run coefficients are not annual paths.
- **[R4-R5] Independent validation and applicability:** freeze a matched event
  evaluation, compare with simple models, and report subgroup and uncertainty limits.
- **[W0-W3] Calculator design:** research useful questions, write the explanation
  first, compare two visual directions, and test comprehension with fictional
  or explicitly limited examples before scientific release readiness.
- **[R6 / W4-W5] Evaluated public experience:** expose only eligible scenarios
  after the scientific, comprehension, and accessibility criteria are met.
- **[R7-R8] Expand with evidence:** add protective interventions and supported
  combinations before longer horizons and descendants.
- **[DONE 2026-09-10] Research positioning and product plan:** cited related work
  added to the paper; prior-attempts comparison rewritten fairly; life-course
  and website experience plans documented. These are plans, not shipped capabilities.

## Engine

- **[DONE 2026-09-09] Math corrections, engine 0.2.0 / parameters v1.34** — odds-to-risk mortality and survival, one initial place adjustment, signed interval corners, clamped normal/lognormal moments, and refusal of reused uncertain parameters under independent-step inference. Legacy scenario methods remain selectable.
- **[DONE 2026-09-09] Deep mathematics/code audit remediation** — public chains now enforce declared context-safe composition; V1/V2 mortality scoring shares the production survival kernel; all parameter materialization is point-aware; rank correlations use the Spearman-to-copula mapping; count quantiles use raw values; and source loaders reject duplicate/non-finite rows. See `docs/DEEP_MATHEMATICS_CODE_AUDIT_2026-09-09.md`.
- **[DONE 2026-09-09] Property and coverage gate** — Hypothesis invariants cover ledger corners, mortality survival, and pooling convexity; Coverage.py records branches and `scripts/quality_gate.py` enforces 80% line / 70% branch floors. Full-suite baseline: 89.5% / 79.4%. See `docs/TESTING_QUALITY.md`.
- **[DONE 2026-09-09] Direct public-CLI contracts** — every verb has in-process routing/output coverage plus explicit invalid-contract behavior; subprocess tests retain installed-user smoke coverage.
- **[DONE 2026-09-09] Adversarial place-builder ingestion** — validates finite/ranged Atlas values, FIPS, and duplicate county keys; fixture tests pin territory filtering, weighted national aggregation, and byte-stable output.
- **[DONE 2026-09-09] Adversarial lifecycle and V2 branch tests** — Hypothesis state machines cover immutable forecast registration and transactional bundle export/verification/tampering. Synthetic V2 fixtures cover valid scorecard creation and malformed bridge/outcome refusals; count endpoints accept both signed-loss and positive-count conventions.
- **[DONE 2026-09-09] V2 external-source review** — reviewed independent BRAC, NAFTA, and auto-crisis candidate sources. None provides both a frozen-definition, event/geography/window-aligned displacement bridge and independently estimated scored outcome; V2 remains honestly blocked. See `docs/V2_SOURCE_REVIEW_2026-09-09.md`.
- **[DONE 2026-09-09] Conditional policy comparisons** — baseline/policy cases retain exposure provenance, exposure bounds, parameter envelopes, and conservative differences. This does not estimate policy-to-exposure effects.
- **[DONE 2026-09-09] Reproducible bundle export** — engine, data, place inputs, correlations, assumptions, and content hashes. Standalone execution and tampering checks pass.
- **[DONE 2026-09-09] BRAC exposure inventory** — 73 GAO Table 3 records reconcile to published totals. County/window alignment and the causal measured side remain pending.

- **[P2] #31: county WONDER mortality** — PARENT-REPO scraper task (handoff recorded; wonder-mortality CLI is national-only).
- **[DONE 2026-09-09] #8: methods paper** — prose, generated parameter inventory and current V1 scorecards, limitations, references; `make -C paper` builds the PDF. V2/V3 are explicitly incomplete.
- **[DONE 2026-09-09] Employer scenario shape (engine)** — `DocumentedExposure.from_warehouse` validates existing employer/person LCA and WARN aggregates, preserves the upstream total and method, and feeds `compute_entity_counts`. CLI: `entity --input-format warehouse`. Synthetic integration fixtures cover both subjects, rounding, missing fields, and invalid inputs. Production runner/cache wiring remains in XH1B.
- **[P3] #10: prospective validation** — registration and scoring tools are built. Select 2-3 real events, freeze forecasts before outcome windows, obtain independent timestamps, then score after outcomes.
- **[P3] Combined child-gap view; housing contagion chain; explanation surface design.**
- **[DONE 2026-09-09] Place layer into MC/knobs/sensitivity** — `simulate --outcome`, knob sweep/VOI, and Sobol/CI accept `--place`; gamma is recomputed per draw. Place measurements and pooling weights remain fixed.
- **[DONE 2026-09-09] Count-level parameter intervals** — `scenario` jointly samples local-job, mortality, and child-dollar counts on the same LHS/correlation draws and emits central 90% parameter-only intervals. Support envelopes remain separately labeled; exposure, baseline, county/pooling, structural, and unmodeled uncertainty are named rather than merged into a false total interval.

## Extraction queue

Tracked in `docs/QUEUED_EXTRACTIONS.md` — the queue's status column is the
truth; do not duplicate rows here.

- **[P2] Remaining** — remaining integration and research work: #7 production integration, county mortality, and P3s. Paper prose and employer/person engine mapping are complete. (#7 engine + modifier plug LANDED v1.30; #5 distributions + correlations LANDED v1.27; #6 V2 framework pre-registered v1.28 — scoring blocked on per-event displacement bridges: BRAC needs county/window alignment + w6941 OCR; NAFTA needs a tariff-unit displacement bridge that no published source provides; auto crisis has no quasi-experimental measured side.)
- Also: remarriage-margin candidate from the V1 divorce row.
## Review priorities — 2026-09-10

- **[P1] Mortality profile:** source offsets, early effects, and the +6
  boundary are fixed in the default working-paper profile. Published QJE
  Table 4 uses a different additive parameterization whose phase-total
  covariance is unavailable; a published-profile variant remains blocked.
  See `docs/MORTALITY_SOURCE_RECONCILIATION_2026-09-10.md`.
- **[P1] Mortality applicability:** demographic profile selection now refuses
  sex/age mismatch with the male 45--54 causal response. Adding other strata
  requires separately admitted effect estimates, not only new baseline rates.
- **[P1] Place counterfactual:** resolve `1-M*g` versus a same-place exposure
  contrast; a null displacement effect currently produces a county effect.
- **[DONE 2026-09-13] County likelihood:** Gamma--Poisson estimation and
  strict national-prior metadata; v1.36 completed extraction #31 (validated
  county export with matching outcome/population/window metadata) and wired
  the posteriors into the place layer end to end.
- **[P2] Synthesis and transmission:** enforce estimand/window/overlap checks;
  add small-study interval sensitivity and a log-elasticity structural variant.
- **[DONE 2026-09-13] Admission and provenance contract:** blank tier,
  citation, or population_scope is refused at parameter load, and every
  public ledger/scenario/community step publishes its studied population
  beside the citation (`tests/test_admission_provenance.py`). Synthesis
  loading and pooling also refuse blank population/design/horizon
  compatibility fields instead of pooling blank-to-blank as "identical"
  (`tests/test_synthesis.py`), and verified baseline rows must pin value,
  citation, and population at load, with unknown statuses refused. Code
  safeguards only — they do not
  discharge the transport assumptions in the applicability audit. Of the
  evidence blocks recorded this morning, county integration was lifted the
  same day by v1.36 (validated county export + matching metadata, wired
  end to end); the published-QJE mortality profile and V2/prospective
  validation remain unresolved.
- **[DONE 2026-09-13] Evidence-role and estimand contracts:** screening
  vocabularies frozen (unknown/blank composition or extraction status
  refused), Moretti conversion requires a declared job class (manufacturing
  or high_tech) instead of answering with the cross-class 1.6–5.0 span, and
  every parameter row now carries a machine-readable `evidence_role`
  (18 conditional / 3 structural / 28 boundary; `admitted` reserved) that
  load refuses when missing, chains refuse when boundary, and vignette
  streams visibly block with role-named reasons. Landing v1.39; applicability
  conditions themselves remain explicit assumptions. The audit document was
  revised the same day to fold in the post-audit rows (Browning–Heinesen
  cause-specific hazards, Marcus 2013 spouse mental health, Bingley–
  Cappellari–Ovidi 2026 child education) and to mark release gate 2 done.
- **[DONE 2026-09-10] Numerical review repairs:** independent copula designs,
  connected custom chains, chain starting values, county predictive baselines,
  and refusal of legacy additive predictive probabilities. Full findings and
  acceptance criteria: `docs/REVIEW_2026-09-10.md`.
