# Downstream task board

This board replaces the root TODO.md. Each task is a directory containing
`card.md` (scope and acceptance criteria) and `comments.md` (append-only history).
The folder is its current status, using the same system as `~/code/xh1b/tasks`.
Read [AGENTS.md](AGENTS.md) for the workflow.

```sh
python3 scripts/tasks.py list
python3 scripts/tasks.py next
python3 scripts/tasks.py show <card-id>
python3 scripts/tasks.py validate
python3 scripts/tasks.py validate --historical-details
python3 scripts/tasks.py claim <card-id> --as <agent-name>
python3 scripts/tasks.py comment <card-id> --as <agent-name> -m "Finding or receipt"
python3 scripts/tasks.py done <card-id>
python3 scripts/tasks.py drop <card-id>
```

The columns are inbox (proposals or blocked inputs), ready (triaged), active
(claimed), review (work complete), and done (accepted or imported legacy history).
The initial import has 48 cards. Partial scopes keep their remaining work open;
recent completed 0.4 work awaits owner review. No agent claims were invented.
See [the migration map](MIGRATION.md) for every original entry and its card.

## Scope

Model work lives here. XH1B-side entity-analysis migration, runner scripts,
backfills, incremental scheduling and website surfaces remain in the companion
repository's task system/backlog. Its design is `internal/docs/ENTITY_ANALYSIS.md`.
The 0.4 update remains pending XH1B integration; another release needs an owner decision.

The research plan is [LIFE_COURSE_RESEARCH_PLAN.md](../docs/LIFE_COURSE_RESEARCH_PLAN.md),
with [CAUSAL_GRAPH_PLAN.md](../docs/CAUSAL_GRAPH_PLAN.md) for model design and
[WEBSITE_EXPERIENCE_PLAN.md](../docs/WEBSITE_EXPERIENCE_PLAN.md) for the calculator.
The [model card](../docs/MODEL_CARD.md) records assumptions and limitations.
[QUEUED_EXTRACTIONS.md](../docs/QUEUED_EXTRACTIONS.md) remains authoritative for source-row status.

Improve estimates symmetrically when evidence supports smaller, larger, null or
beneficial effects. Every numerical claim retains provenance; misses publish.
Presentation and more simulation draws do not establish causal validity or transportability.
