# comments

## c-6dfeb92aa24a

- At: 2026-10-18 01:39 HKT
- By: board-message-fix

Created in inbox.

## c-870d33be205d

- At: 2026-10-18 01:39 HKT
- By: board-message-fix

triage: inbox -> ready.

Owner requested this formatter change. No existing active card covers it. Scope: formatter, regression checks and commit-format instructions.

## c-58af95ab2b89

- At: 2026-10-18 01:39 HKT
- By: board-message-fix

claim: ready -> active.

Add action prefixes to board subjects and remove redundant action/task-ID paragraphs.

## c-7315891da5e7

- At: 2026-10-18 01:40 HKT
- By: board-message-fix

Board subjects now use board(action): title without a repeated action/task-ID paragraph.

Implementation: b34ffbd. Supplied Markdown details remain in the body. The shared formatter covers all mutations, including separate directory-move commits. Root instructions now link to the updated board format contract.

Validation: .venv/bin/python -m pytest -q tests/test_tasks_board.py tests/test_tasks_workflow.py passed 37 tests. make check-docs passed reference checks, board validation, 48 document checks and 19 documentation tests. git diff --check passed. No remote operation or history rewrite.
