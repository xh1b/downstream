---
title: Port XH1B task references and Markdown workflow
area: tooling
priority: P2
assignee:
blocked-by: []
expected-paths: [scripts/tasks.py, tests/test_tasks_board.py, tasks/AGENTS.md]
---

# Port XH1B task references and Markdown workflow

Owner requested the kanban update from XH1B commit e1b851ec28c75bc14f368f8655911e6d51f991e5.
Retain Downstream commit-first moves, chained path-scoped commits, Hong Kong timestamps,
and compatibility with existing cards and append-only comments.

## Acceptance

- [ ] Port references, Markdown comments, relationships and workflow commands with regression coverage.
- [ ] Preserve shared-checkout safeguards and validate the existing board without rewriting other agents' cards.
- [ ] Document the new workflow and record test and validation receipts.
