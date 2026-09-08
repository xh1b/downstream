# TODO — downstream model (nested repo, LOCAL-ONLY)

Model-side work lives here. XH1B-side integration tasks (entity_analysis
migration, runner script, phased backfill, incremental mode + scheduler,
website surfaces) live in the parent repo's `internal/TODO.md` under
"Downstream integration". Design for that side:
`internal/docs/ENTITY_ANALYSIS.md` (parent repo).

Plan of record: owner-approved top 10 (2026-09-06). Every number cites
(CITING.md); misses publish; website work gated.

## Engine

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

- **[P2] Remaining** — the extraction queue is EMPTY (all three owner downloads landed: #15 v1.26 colantone2018, #20 v1.25 paul2009, #22 v1.24 schneider2016).
  Remaining work is engine-level: #5 distributions + correlations, #6 back-tests, #7 place-resolved layer, #8 paper prose, employer scenario shape, P3s.
- Also: remarriage-margin candidate from the V1 divorce row.
