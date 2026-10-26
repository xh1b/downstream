# comments

## c-def66708df0b

- At: 2026-10-15 02:06 HKT
- By: codex-task-tooling

Created in inbox.

## c-a599900b808f

- At: 2026-10-15 02:06 HKT
- By: codex-task-tooling

triage: inbox -> ready.

Owner-authorized tooling scope is ready.

## c-5959b351c2bf

- At: 2026-10-15 02:07 HKT
- By: codex-task-tooling

claim: ready -> active.

Implement the owner-approved convenience changes.

## c-adcf752daa00

- At: 2026-10-15 02:13 HKT
- By: codex-task-tooling

Tooling implementation passes verification

Implementation, tests and instructions are committed in `bf38e75`. Board status and evidence use separate commits.

- `.venv/bin/python -m pytest -q tests/test_tasks_board.py tests/test_tasks_workflow.py`: 29 tests pass in 43.93 seconds. Tests cover blocked status, frozen historical gaps, unchanged failure codes, structural and review evidence errors, task viewing after moves, multiline message inputs, append-only comments, unrelated staged files, deletion paths, dirty-card refusal and commit-first moves.
- `python3 scripts/tasks.py validate`: exit 0; zero errors and warnings. Historical evidence gaps are summarized separately: 45 missing links across 30 tasks.
- `validate --historical-details`: exit 0; all 45 frozen gaps remain visible. The exemption membership and frozen bytes do not change. Edited and new criteria still fail without evidence.
- Migration preservation: all 48 IDs in `tasks/MIGRATION.md` resolve uniquely across board columns. `tasks/LEGACY_CHECKLISTS.json` remains byte-for-byte equal to its committed source.
- Ruff passes for the tool and affected tests. Markdown lint passes for the board instructions, guide and this task. Local link, task-reference, final-newline and commit-example checks pass for the three changed documents. `git diff --check` passes.

The [tool](../../../scripts/tasks.py), [workflow tests](../../../tests/test_tasks_workflow.py), [board tests](../../../tests/test_tasks_board.py) and [instructions](../../AGENTS.md) contain the change. The runtime stays standard-library-only and uses installed Git. Existing cards and prior comments remain unchanged by this implementation. Other agents' changes remain outside these commits. No simulation tests or remote operation occur.

The implementation is ready for independent review. Commit the evidence checklist before `done`, as this board requires. Then send the task to `review/` without accepting it.

## c-851011612bb6

- At: 2026-10-15 02:14 HKT
- By: codex-task-tooling

done: active -> review.

Send the tooling change to independent review

Implementation and instructions: `bf38e75`.
Verification receipt: task:2026-10-15-task-tool-convenience#c-adcf752daa00.

All 29 affected tests pass. Board validation, migration preservation, Ruff and documentation checks pass. Review the historical summary, full messages, stable-ID view and explicit-path commit guidance. This handoff does not accept the task.

## c-1ca5e45848b0

- At: 2026-10-27 06:42 HKT
- By: codex-review

accept: review -> done.

Verified stable-ID show, multiline messages, title-based commit messages, blocked reporting, dirty-card/staging isolation and commit-first moves. The delivered historical-exemption feature was intentionally superseded by the owner-requested cleanup.

Verification receipt: @task:2026-10-27-review-acceptance#c-845b5298b984. Accepted under the owner's request to verify and complete review tasks.
