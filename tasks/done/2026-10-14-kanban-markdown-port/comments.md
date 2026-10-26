# comments

- 2026-10-14 21:10 kanban-port: Owner requested this port; ready for implementation.
- 2026-10-14 23:57 kanban-port: claimed (ready -> active)

## c-2d647cade4e4

- At: 2026-10-15 00:01 HKT
- By: kanban-port

### Port and verification receipts

Ported XH1B commit `e1b851ec28c75bc14f368f8655911e6d51f991e5`:
task/comment references and backlinks, Markdown comments via files or stdin,
replies and resolutions, relationships and cycle checks, and the complete
create/triage/claim/review/accept/request-changes/drop/cancel/reopen workflow.

Downstream retains commit-first moves, chained path-scoped add/commit,
master preflight, dirty-card refusals and Asia/Hong_Kong timestamps.
The frozen legacy checklist ledger preserves only exact historical criteria;
completion and acceptance always require evidence. Existing cards/comments
were not rewritten.

- `.venv/bin/pytest -q tests/test_tasks_board.py tests/test_tasks_workflow.py`: 23 passed.
- Ruff on the CLI and both task test files: passed.
- `python3 scripts/tasks.py validate`: zero errors; five existing blocker warnings.
- `git diff --check`: passed.
- Markdown lint on the updated guide and this task: zero issues.
- Full-board Markdown lint found six existing issues after disabling the false
  YAML-title/H1 conflict: four legacy comment threads without initial headings,
  and two list-spacing reports in the historical county-likelihood card.
  Those historical files were preserved.

Implementation: `396e6e5` (see git log for the definitive port revision).

## c-d48efa01d5b8

- At: 2026-10-15 00:02 HKT
- By: kanban-port

Correction to the preceding receipt: the implementation commit is `66658d1`. The earlier revision was a transcription error.

## c-f132a08c6e3e

- At: 2026-10-15 00:02 HKT
- By: kanban-port

done: active -> review.

## c-1311bde10e06

- At: 2026-10-27 06:42 HKT
- By: codex-review

accept: review -> done.

Verified references, relationships, append-only comments, workflow transitions, dirty-card refusal, explicit-path commits and commit-first moves against current task tests and CLI.

Verification receipt: @task:2026-10-27-review-acceptance#c-845b5298b984. Accepted under the owner's request to verify and complete review tasks.
