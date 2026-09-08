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

- **[P2] Remaining** — #15 Colantone-Stanig, #20 Paul & Moser, #22 Schneider et al. (all three need owner downloads). LANDED: #21 v1.23 (evans2008),
  #18 v1.22 (campbell2011 spillover, venue corrected to AER), #17 v1.21 (collinson2024), #12 v1.20.
- Also: remarriage-margin candidate from the V1 divorce row.
