# TODO — downstream model (standalone repo, LOCAL-ONLY)

Model-side work lives here. XH1B-side integration tasks (entity_analysis
migration, runner script, phased backfill, incremental mode + scheduler,
website surfaces) live in the parent repo's `internal/TODO.md` under
"Downstream integration". Design for that side:
`internal/docs/ENTITY_ANALYSIS.md` (parent repo).

Plan of record: owner-approved top 10 (2026-09-06). Every number cites
(CITING.md); misses publish; website work gated.

## Current scope

Owner direction: improve this project first. XH1B implementation is deferred.
See `docs/MATH_REVIEW.md` for reviewed arithmetic and remaining assumptions.

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
# Review priorities — 2026-09-10

- **[P1] Mortality profile:** reconcile source versions and columns, extract
  early-year estimates, and index offset +6 correctly. Current
  `source_aligned` behavior is an incomplete approximation.
- **[P1] Place counterfactual:** resolve `1-M*g` versus a same-place exposure
  contrast; a null displacement effect currently produces a county effect.
- **[P1 before integration] County likelihood:** distinguish person-time rates
  from binomial trials and validate national-prior population/window metadata.
- **[P2] Synthesis and transmission:** enforce estimand/window/overlap checks;
  add small-study interval sensitivity and a log-elasticity structural variant.
- **[DONE 2026-09-10] Numerical review repairs:** independent copula designs,
  connected custom chains, chain starting values, county predictive baselines,
  and refusal of legacy additive predictive probabilities. Full findings and
  acceptance criteria: `docs/REVIEW_2026-09-10.md`.
