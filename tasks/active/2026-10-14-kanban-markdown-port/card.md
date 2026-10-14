---
title: Port XH1B task references and Markdown workflow
area: tooling
priority: P2
assignee: kanban-port
blocked-by: []
expected-paths: [scripts/tasks.py, tests/test_tasks_board.py, tasks/AGENTS.md]
---

# Port XH1B task references and Markdown workflow

Owner requested the kanban update from XH1B commit e1b851ec28c75bc14f368f8655911e6d51f991e5.
Retain Downstream commit-first moves, chained path-scoped commits, Hong Kong timestamps,
and compatibility with existing cards and append-only comments.

## Acceptance

- [x] Port references, Markdown comments, relationships and workflow commands with regression coverage. [receipt](task:2026-10-14-kanban-markdown-port#c-2d647cade4e4)
- [x] Preserve shared-checkout safeguards and validate the existing board without rewriting other agents' cards. [receipt](task:2026-10-14-kanban-markdown-port#c-2d647cade4e4)
- [x] Document the new workflow and record test and validation receipts. [receipt](task:2026-10-14-kanban-markdown-port#c-2d647cade4e4)
