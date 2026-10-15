# comments

## c-da10bb444bcd

- At: 2026-10-15 17:07 HKT
- By: codex-task-tokens

Created in inbox.

## c-2cef7f6086bb

- At: 2026-10-15 17:07 HKT
- By: codex-task-tokens

triage: inbox -> ready.

Owner requested this current tooling port. Checked the board: earlier task ports are in review and do not cover tags or repository anchors; no duplicate active work.

## c-710e122646cd

- At: 2026-10-15 17:07 HKT
- By: codex-task-tokens

claim: ready -> active.

## c-87cdc47165ab

- At: 2026-10-15 17:12 HKT
- By: codex-task-tokens

tags: add @tag:tooling.

## c-8906b489253a

- At: 2026-10-15 17:12 HKT
- By: codex-task-tokens

Port complete; affected checks pass

Implementation: 4ef684e. Read locally from XH1B scripts/tasks.py at e66c9db272cf3645a28873cdf89ec5dcaa9f186b (canonical tags landed in 03e0fcd03), and scripts/refcheck.py at adc41dcfc2f9d29cef5e7ea1fe68ee935488ff7c. Imported the tag helpers, commands and tests; ported the tracked-text anchor/link checker and its tests. Added token instructions and quality-workflow checks.

- `.venv/bin/python -m pytest -q tests/test_tasks_board.py tests/test_tasks_workflow.py tests/test_refcheck.py`: 53 passed. Covers normalization, tag add/remove/filtering, duplicate/invalid metadata, unrelated staging, dirty-card refusal, mixed legacy/canonical links, replies, resolutions and moves, duplicate/dangling anchors, fenced examples and malformed token shapes.
- `.venv/bin/python -m ruff check src scripts`: passed.
- `.venv/bin/python -m vulture`: passed.
- `python3 scripts/refcheck.py check`: 4 anchors, 7 links, 0 failures after the implementation commit.
- `python3 scripts/tasks.py validate`: 0 errors and 0 warnings. The existing 45 historical evidence gaps across 30 tasks remain frozen; 4 tasks have 5 unsatisfied dependency references.
- `git diff --check`: passed. Existing task card bodies, comments and LEGACY_CHECKLISTS.json were not rewritten. All board changes are confined to this new card.

Downstream retains HKT timestamps, commit-first directory moves, title-based board commit summaries and legacy task-reference compatibility. New task output and reply/resolution metadata use the canonical prefix. Tag commands also refuse dirty cards. The anchor scanner validates the entire name, including mixed-case suffixes, and accepts the same tag shape as the task CLI.

Usage: [token guide](../../README.md), [task CLI](../../../scripts/tasks.py), [reference checker](../../../scripts/refcheck.py), [workflow tests](../../../tests/test_tasks_workflow.py), [reference tests](../../../tests/test_refcheck.py). Local commits only; XH1B was read without changes.

## c-1252fa3790dc

- At: 2026-10-15 17:12 HKT
- By: codex-task-tokens

done: active -> review.
