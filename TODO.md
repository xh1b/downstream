# TODO — downstream model (nested repo, LOCAL-ONLY)

Model-side work lives here. XH1B-side integration tasks (entity_analysis
migration, runner script, phased backfill, incremental mode + scheduler,
website surfaces) live in the parent repo's `internal/TODO.md` under
"Downstream integration". Design for that side:
`internal/docs/ENTITY_ANALYSIS.md` (parent repo).

Plan of record: owner-approved top 10 (2026-09-06). Every number cites
(CITING.md); misses publish; website work gated.

## Engine

- **[P1] Export verb** — export a version-stamped `parameter_set.json` snapshot. Prereq for the parent repo's `entity_analysis` runner (see internal/TODO.md,
  Downstream integration section).
- **[P1] Vector catalog v2 closeout.**
  - Live-smoke the 24 new functions (limit 3; scores 0..1).
  - Add the 6 signal MVs to `mv-catalog.md`.
- **[P2] #5: per-parameter distributions + first citable correlations.**
- **[P2] #6: V2 back-tests** — NAFTA, 2008-09 auto crisis, BRAC.
- **[P2] #7: place-resolved layer with shrinkage** — Chetty-Hendren modifier, WONDER county baselines, partial pooling.
- **[P2] #8: fill the paper prose** — methods, V1 scorecard, limitations; `make` builds clean.
- **[P3] #10: pre-registered prospective forecasts** — 2-3 events scored before outcomes.
- **[P2] Employer scenario shape** — documented-conduct inputs (LCA gap totals, WARN events) -> same `compute_counts` surface. Persons ARE included (owner
  decision 2026-09-08 — DOWNSTREAM_LEDGER_SPEC §8 revised; impact framing, never individual prediction).
- **[P3] Combined child-gap view; housing contagion chain; explanation surface design.**

## Extraction queue

Tracked in `docs/QUEUED_EXTRACTIONS.md` — the queue's status column is the
truth; do not duplicate rows here.

- **[P2] Remaining** — #15 Colantone-Stanig (owner download); #18; #20-#22 (#22 owner download). #17 LANDED v1.21 (version of record corrected to
  collinson2024 QJE; desmond2016 job-loss refusal in SPEC §10). #12 LANDED
  v1.20.
- Also: remarriage-margin candidate from the V1 divorce row.
