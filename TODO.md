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
See `docs/MODEL_CARD.md` for model limits and remaining assumptions.

## Next version — review follow-through (2026-10-14)

Acceptance standard: improve estimates symmetrically when evidence supports
smaller, larger, null, or beneficial effects. Better presentation and more
simulation draws do not establish causal validity or transportability.

- **[DONE / engine 0.4.0] Mortality persistence robustness:** publish
  the source-profile result beside a declared no-sustained-excess alternative
  (offset +6 onward at OR=1), motivated by the Eliason–Storrie long-run
  divergence already recorded in the evidence. Preserve the early profile,
  actual selected baseline, exposure and horizon. Show parameter intervals
  within each structure separately from the unweighted structural spread.
  Do not treat a nonsignificant HR as proof of zero, substitute an HR for an
  OR, reproduce the Swedish study with a hybrid profile, average unlike
  studies, or promote the alternative to a validated headline.
- **[P1] Define the target displaced cohort:** pin survey release, weighted
  inclusion rules, age, sex, tenure, industry, earnings and family structure;
  distinguish generic displacement from any H-1B-specific exposure bridge.
  Reproduce weighted cohort summaries before individual simulation. The
  review's 31.8 deaths per 1,000 remains unverified without its data/code.
- **[P1] Admit effects by stratum before heterogeneous mortality:** separate
  baseline-risk variation from evidence of effect modification; source
  age/sex-compatible response profiles before expanding admissible cohorts.
  Reconcile original study inclusion ages and tenure with the engine's
  reference-baseline age band; they must not be conflated as one restriction.
  Evaluate annual aging baselines against fixed-baseline sensitivity.
  Compare exact weighted-stratum aggregation with any sampled implementation.
- **[P1] Child eligibility and heterogeneity:** record age at displacement,
  child sex and family-income scope; refuse or explicitly flag unsupported
  extrapolations. Extract age/income contrasts from primary sources before
  introducing response curves. A childhood estimate does not establish
  the same effect for a fetus, adult child, or every family-income group.
- **[P1] Populate the coefficient synthesis library:** predeclare search and
  inclusion rules; retain nulls, protective effects and conflicts. Extract
  compatible treatment/comparison, population, scale, horizon, uncertainty,
  and sample-overlap records. Existing synthesis code is not a pooled
  evidence library; study-level heterogeneity is not a target transport model.
- **[P1] Matched independent evaluation:** freeze event bridges and scored
  endpoints; compare direct-effect and stratified baselines with the expanded
  model; report every preregistered result, subgroup miss and interval scope.
  Existing China-shock diagnostics and SIPP baseline checks remain visible;
  they do not establish H-1B-specific causal validation.
- **[P2] Household dynamics and displacement duration:** build on R2 SIPP
  transitions, linked households, recovery, partner resources and child ages.
  Distinguish baseline transitions from causal event responses and prevent
  double counting. Joint outcomes need evidenced/declared dependence;
  microsimulation alone does not identify it.
- **[P2] Child-dollar valuation:** retain undiscounted lifetime totals and add
  separately labeled present values with explicit real discount rate,
  valuation date, child age and annual earnings profile. Test zero-rate
  equivalence and supported timing; do not relabel an adult annual effect
  as an identified constant effect across the whole career.
- **[P2] Uncertainty coverage:** extend beyond existing parameter Monte Carlo
  and declared correlations to exposure, baseline, transport, structural and
  process uncertainty where a defensible joint model exists. Keep unknown
  components named; do not call parameter intervals full prediction intervals.

## Forward milestones

- **[R0-R1] Correct and classify:** resolve current review findings; distinguish
  baseline transitions, causal effects, and structural assumptions in evidence records.
- **[R2] Baseline household trajectories:** SIPP adopted as the dataset
  (2026-09-13 assessment:
  `docs/SIPP_BASELINE_DATA_ASSESSMENT_2026-09-13.md` — free, public
  domain, redistributable, LLM-workflow compatible; limitations: short
  panels, coarse public geography, >20% panel attrition, no
  intergenerational supplements. PSID ruled out on the ICPSR LLM policy
  — `docs/PSID_BASELINE_DATA_ASSESSMENT_2026-09-13.md` — and stays
  citation-only). First R2 artifact built and held-out validated
  (2026-09-14): FINYR2-weighted December-to-December 2021→2022
  employment/earnings transitions for 3,206 prime-age span persons
  (`docs/BASELINE_TRANSITION_R2_2026-09-14.md`; E-origin cells
  calibrate to ~1pp, U-origin cells indicative-only at n≈14–19).
  Next: pool the 2020/2021/2022 panel releases to enlarge U-origin
  cells, add replicate-weight SEs (`lgtrw2023yr2`), then the 2008
  panel for fine-grained monthly transitions.
- **[R3] First full comparison:** a five-year involuntary-displacement scenario
  versus a stated reference, limited to supported employment, earnings, and
  household-resource outcomes. Current long-run coefficients are not annual paths.
  The 2026-09-14 scenario review surfaced a second gap: the engine is silent on
  receiving-community effects of replacement inflows (unmodeled, not estimated
  zero). Anchors for rents, native wages, host mental health, trust, crime, and
  voting are verified in
  `docs/IMMIGRATION_REPLACEMENT_EVIDENCE_SCAN_2026-09-14.md`; next: screen them
  through the admission contract into queued extractions.
  Progress 2026-09-16 (v1.48): the CRIME channel screened and LANDED — the
  independence gate passed (Light-Miller Criminology 2018; Bell-Fasani-Machin
  REStat 2013 published; Bianchi-Buonanno-Pinotti JEEA 2012), two
  `immigrant_influx->receiving_*_crime_rate` rows shipped, and the
  work-ban vs work-access property-crime split is recorded as findings.
  Remaining receiving-community channels (rents, native wages, mental
  health, trust, voting) still queued; scenario wiring for an
  `--immigrant-influx` exposure is not built yet.
- **[R4-R5] Independent validation and applicability:** freeze a matched event
  evaluation, compare with simple models, and report subgroup and uncertainty limits.
- **[W0-W3] Calculator design:** research useful questions, write the explanation
  first, compare two visual directions, and test comprehension with fictional
  or explicitly limited examples before scientific release readiness.
- **[R6 / W4-W5] Evaluated public experience:** expose only eligible scenarios
  after the scientific, comprehension, and accessibility criteria are met.
- **[R7-R8] Expand with evidence:** add protective interventions and supported
  combinations before longer horizons and descendants.
- **[DECIDED 2026-09-14] County-mortality prior strength:** the DECLARED
  k = 2000 prior person-years stays the shipped pooling strength. The
  method-of-moments empirical-Bayes yardstick (k ≈ 822 on the male 45-54
  export; Poisson noise ≈ 11% of the county spread; Gamma shape ≈ 4.1) is
  recorded and reproducible (`build_county_mortality.py --estimate-prior-k`,
  `tests/test_county_eb_prior.py`) but is NOT adopted: it is the less
  conservative direction, it assumes iid Gamma county effects (no spatial
  correlation), and it rests on one export over one window. Revisit: rerun
  the flag as more cause/sex/window exports land; adopting would rewrite
  all 2,748 posteriors and the v1.41 build-places places.csv columns that
  key off k = 2000, so it needs an explicit fresh decision.
  (`docs/DATA_SOURCES.md` county row.)
- **[DONE 0.4.0] Sustained-mortality alternative:** Eliason & Storrie 2009 find
  no statistically significant long-run all-cause effect (5-8y HR 0.98, 9-12y 0.91, n.s., 12y
  follow-up) against the SvW 1.135 sustained anchor; v1.43 records the
  divergence as declared notes on `earnings_shock->mortality_sustained`
  and never averages (CITING 5). The robustness comparison
  exposes a named null-persistence assumption without changing that anchor
  or claiming the two studies share an estimand.
  See `docs/MORTALITY_PERSISTENCE_SENSITIVITY.md`; default scenario/entity
  results expose the two structures and scenario Monte Carlo uses shared
  draws for the contrast. Source parameters remain v1.49.
- **[OPEN] Promote the v1.43 streams to headline claims:** fertility
  (`annual_birth_response`), child mental health (`child_depression_
  anxiety`), and spousal labor supply (`spouse_participation_elasticity`)
  are wired as boundary-fenced parallel evidence — reachable, audited,
  exported, refused in arbitrary chains by the same guard as every other
  exposure contrast. Decide whether any should surface as explain-level
  claims (with their nulls and transport conditions), or stay
  consultable via export/citations/audit. User decision.
- **[OPEN/BLOCKED] V2 prospective validation:** still blocked on an external
  source providing BOTH a frozen-definition, event/geography/window-aligned
  displacement bridge AND independently estimated scored outcomes
  (BRAC/NAFTA/auto-crisis candidates were checked; none qualified). The SIPP
  adoption (R2) is the candidate path: if its panels clear the transition validation, re-evaluate SIPP
  as the bridge. Re-check after R2's first weighted two-wave transition
  reproduces with held-out validation.
- **[DONE 2026-09-10] Research positioning and product plan:** cited related work
  added to the paper; prior-attempts comparison rewritten fairly; life-course
  and website experience plans documented. These are plans, not shipped capabilities.

## Engine

- **[DONE 2026-09-09] Math corrections, engine 0.2.0 / parameters v1.34** — odds-to-risk mortality and survival, one initial place adjustment, signed interval corners, clamped normal/lognormal moments, and refusal of reused uncertain parameters under independent-step inference. Legacy scenario methods remain selectable.
- **[DONE 2026-09-09] Deep mathematics/code audit remediation** — public chains now enforce declared context-safe composition; V1/V2 mortality scoring shares the production survival kernel; all parameter materialization is point-aware; rank correlations use the Spearman-to-copula mapping; count quantiles use raw values; and source loaders reject duplicate/non-finite rows.
- **[DONE 2026-09-09] Property and coverage gate** — Hypothesis invariants cover ledger corners, mortality survival, and pooling convexity; Coverage.py records branches and `scripts/quality_gate.py` enforces 80% line / 70% branch floors. Full-suite baseline: 89.5% / 79.4%. See `docs/TESTING_QUALITY.md`.
- **[DONE 2026-09-09] Direct public-CLI contracts** — every verb has in-process routing/output coverage plus explicit invalid-contract behavior; subprocess tests retain installed-user smoke coverage.
- **[DONE 2026-09-09] Adversarial place-builder ingestion** — validates finite/ranged Atlas values, FIPS, and duplicate county keys; fixture tests pin territory filtering, weighted national aggregation, and byte-stable output.
- **[DONE 2026-09-09] Adversarial lifecycle and V2 branch tests** — Hypothesis state machines cover immutable forecast registration and transactional bundle export/verification/tampering. Synthetic V2 fixtures cover valid scorecard creation and malformed bridge/outcome refusals; count endpoints accept both signed-loss and positive-count conventions.
- **[DONE 2026-09-09] V2 external-source review** — reviewed independent BRAC, NAFTA, and auto-crisis candidate sources. None provides both a frozen-definition, event/geography/window-aligned displacement bridge and independently estimated scored outcome; V2 remains honestly blocked.
- **[DONE 2026-09-09] Conditional policy comparisons** — baseline/policy cases retain exposure provenance, exposure bounds, parameter envelopes, and conservative differences. This does not estimate policy-to-exposure effects.
- **[DONE 2026-09-09] Reproducible bundle export** — engine, data, place inputs, correlations, assumptions, and content hashes. Standalone execution and tampering checks pass.
- **[DONE 2026-09-09] BRAC exposure inventory** — 73 GAO Table 3 records reconcile to published totals. County/window alignment and the causal measured side remain pending.

- **[DONE 2026-09-13] #31: county WONDER mortality** — export landed via `scripts/fetch_wonder.py county` (web-UI session; the machine XML API is national-only); v1.36 wired the strict Gamma–Poisson posteriors into the place layer, and v1.41 fills the generated places.csv plug columns (shrunk posterior mean + person-years precision label) in the same build-places pass.
- **[DONE 2026-09-09] #8: methods paper** — prose, generated parameter inventory and current V1 scorecards, limitations, references; `make -C paper` builds the PDF. V2/V3 are explicitly incomplete.
- **[DONE 2026-09-09] Employer scenario shape (engine)** — `DocumentedExposure.from_warehouse` validates existing employer/person LCA and WARN aggregates, preserves the upstream total and method, and feeds `compute_entity_counts`. CLI: `entity --input-format warehouse`. Synthetic integration fixtures cover both subjects, rounding, missing fields, and invalid inputs. Production runner/cache wiring remains in XH1B.
- **[P3] #10: prospective validation** — registration and scoring tools are built. Select 2-3 real events, freeze forecasts before outcome windows, obtain independent timestamps, then score after outcomes.
- **[P3] Combined child-gap view; housing contagion chain; explanation surface design.**
- **[DONE 2026-09-09] Place layer into MC/knobs/sensitivity** — `simulate --outcome`, knob sweep/VOI, and Sobol/CI accept `--place`; gamma is recomputed per draw. Place measurements and pooling weights remain fixed.
- **[DONE 2026-09-09] Count-level parameter intervals** — `scenario` jointly samples local-job, mortality, and child-dollar counts on the same LHS/correlation draws and emits central 90% parameter-only intervals. Support envelopes remain separately labeled; exposure, baseline, county/pooling, structural, and unmodeled uncertainty are named rather than merged into a false total interval.

## Extraction queue

Tracked in `docs/QUEUED_EXTRACTIONS.md` — the queue's status column is the
truth; do not duplicate rows here.

- **[P2] Remaining** — remaining integration and research work: #7 production integration and P3s (county mortality completed v1.36 + v1.41). Paper prose and employer/person engine mapping are complete. (#7 engine + modifier plug LANDED v1.30; #5 distributions + correlations LANDED v1.27; #6 V2 framework pre-registered v1.28 — scoring blocked on per-event displacement bridges: BRAC needs county/window alignment + w6941 OCR; NAFTA needs a tariff-unit displacement bridge that no published source provides; auto crisis has no quasi-experimental measured side.)
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
  the posteriors into the place layer end to end; v1.41 also fills the
  generated places.csv mortality_rate/mortality_n columns (posterior mean +
  person-years precision label) in the same build-places pass, keeping
  suppressed/absent counties on the national fallback.
- **[DONE 2026-09-13] Synthesis and transmission:** estimand/window/overlap
  checks, REML and Hartung–Knapp sensitivities, and the k>=3 / t(k-2)
  prediction-interval contract are in (`tests/test_synthesis.py`); the
  log-elasticity transmission rule is a first-class, role-tagged ledger
  kind exposed through the declared variant ensemble, never chainable
  (`tests/test_variants.py`); first-order Sobol estimators are centered
  with constant-shift invariance pinned and dependent-block design-noise
  reporting (`tests/test_sensitivity_centering.py`). Sensitivity outputs
  remain sensitivity outputs — none of this admits a synthesis result
  into parameters.csv.
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
  conditions themselves remain explicit assumptions.
- **[DONE 2026-09-10] Numerical review repairs:** independent copula designs,
  connected custom chains, chain starting values, county predictive baselines,
  and refusal of legacy additive predictive probabilities.
