---
title: Remove obsolete task-board migration scaffolding
area: scripts
priority: P2
assignee: codex-board-cleanup
tags: [@tag:tooling]
blocked-by: []
---

Remove completed import artifacts and obsolete backlog references from maintained task documentation. Replace frozen evidence exemptions with direct, relevant links on completed criteria, preserve card/comment history, and apply one evidence rule to all completed tasks.

- [x] Remove the migration map and checklist-exemption manifest without losing task history. [current board](../../README.md)
- [x] Replace exempted checked criteria with relevant evidence links and remove validator exceptions. [uniform evidence tests](../../../tests/test_tasks_board.py)
- [x] Update maintained task instructions and pass task, documentation and regression checks. [workflow regressions](../../../tests/test_tasks_workflow.py)
