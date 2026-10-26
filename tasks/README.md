# Downstream task board

Each task is a directory containing `card.md` (scope and acceptance criteria)
and `comments.md` (append-only history). Its folder records the current status.
Read [AGENTS.md](AGENTS.md) (@link:task-workflow) for the workflow.

```sh
python3 scripts/tasks.py list
python3 scripts/tasks.py next
python3 scripts/tasks.py show <card-id>
python3 scripts/tasks.py validate
python3 scripts/tasks.py claim <card-id> --as <agent-name>
python3 scripts/tasks.py comment <card-id> --as <agent-name> -m "Finding or receipt"
python3 scripts/tasks.py done <card-id>
python3 scripts/tasks.py drop <card-id>
```

The columns are inbox (proposed), ready (triaged), active (claimed), review
(work complete), done (accepted), and cancelled (closed without completion).
Claim ready work before implementation, record evidence in the task thread,
and submit completed work with `done`. An owner or trusted reviewer uses
`accept` to record acceptance. Every completed criterion needs an evidence link.

For the tooling/check map and a task-system quickstart, see the
[development guide](../docs/development.md#task-system-and-work-receipts).
For implementation and paper navigation, see [the documentation map](../docs/readme.md).

## Reference tokens

@ref:reference-token-contract

| Token | Meaning |
|:---|:---|
| `@task:<id>` | Permanent task ID; append `#c-<12 hex digits>` for a comment. |
| `@ref:<id>` | Defines one stable anchor across tracked text files. |
| `@link:<id>` | Cites an anchor without storing its current file path. |
| `@tag:<name>` | Task-type label in card metadata, docs and source comments. |

Anchor IDs use lowercase letters, digits, hyphens and underscores, starting
and ending with a letter or digit. Name anchors for their purpose and define
them beside the section they identify. Keep IDs stable when moving sections.
Retire a definition and all its links together. Fenced Markdown examples are
ignored; use angle-bracket placeholders such as `@ref:<id>` in prose.
Tags need no separate definition and may repeat freely.

`@task:` and `@link:` work as Markdown link targets. They are repository
references, resolved by the commands below. Legacy `task:` links still work;
retained cards and comments do not need rewriting. Backlinks are computed from
files; keep no second backlink list. Reuse existing tags before adding names.
See @link:task-card-format for fields and @link:task-command-reference for workflow commands.

```sh
python3 scripts/tasks.py tags
python3 scripts/tasks.py tags tooling
python3 scripts/tasks.py tag <id> add tooling --as <agent-name>
python3 scripts/tasks.py tag <id> remove tooling --as <agent-name>
python3 scripts/tasks.py refs @task:<id>
python3 scripts/tasks.py refs @task:<id>#c-0123456789ab
python3 scripts/refcheck.py check
python3 scripts/refcheck.py list
python3 scripts/refcheck.py show <anchor-id>
rg -n '@ref:anchor-id|@link:anchor-id' .
rg -n '@tag:tooling' tasks/ scripts/
```

`refcheck` scans tracked text for duplicate anchors, missing link targets and
malformed anchor/tag names. It ignores binaries, files over 1 MB and paths in
[scripts/refcheck-allowlist.txt](../scripts/refcheck-allowlist.txt), which exempts
intentional test fixtures. Task validation separately resolves task and comment
references. Both checks run in the quality workflow; neither proves evidence content.

## Scope

Model work lives here. XH1B-side entity-analysis migration, runner scripts,
backfills, incremental scheduling and website surfaces remain in the companion
repository's task system/backlog. Its design is `internal/docs/ENTITY_ANALYSIS.md`.
The 0.4 update remains pending XH1B integration; another release needs an owner decision.

The research plan is [life_course_research_plan.md](../docs/research/life_course_research_plan.md),
with [causal_graph_plan.md](../docs/research/causal_graph_plan.md) for model design and
[website_experience_plan.md](../docs/research/website_experience_plan.md) for the calculator.
The [model card](../docs/model_card.md) records assumptions and limitations.
[queued_extractions.md](../docs/research/queued_extractions.md) remains authoritative for source-row status.

Improve estimates symmetrically when evidence supports smaller, larger, null or
beneficial effects. Every numerical claim retains provenance; misses publish.
Presentation and more simulation draws do not establish causal validity or transportability.
