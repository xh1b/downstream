# tasks — the agent board

A task board in Markdown. Folders are columns. Each task has `card.md` and
`comments.md`. Git records changes. Use `show <id>` to read a card and find its comments.
Use `rg` to search the files.

## Columns

| Column | Meaning |
|:---|:---|
| `inbox/` | Proposed; not triaged. |
| `ready/` | Triaged and claimable. |
| `active/` | Claimed and in progress. |
| `review/` | Work finished; awaiting review. |
| `done/` | Accepted. |
| `cancelled/` | Closed without completion. Created on first use. |

## Card format

The directory name is the permanent task id: `YYYY-MM-DD-<short-slug>`.
Do not rename it. Change `title:` when the name needs to change.
Moving between columns keeps the id and every `task:` reference valid.

```yaml
---
title: One line
area: scripts
priority: P2
assignee:
due: 2026-10-21
blocked-by: [2026-10-14-source-repair]
related-to: [2026-10-14-parser-review]
parent: 2026-10-14-source-program
duplicate-of:
expected-paths: [scripts/]
---
```

Only `title`, `area`, `priority`, and `assignee` are required.
List fields use inline `[a, b]` syntax. Other fields hold one line.
The existing `title:` is the task's one-line summary. Put optional Markdown
details in the body, along with the existing acceptance checklist.
No additional message fields or fixed sections are required.

- `blocked-by`: these tasks must reach `done/` first. `next` omits blocked tasks.
  `claim` needs a reason with `-m` or `--file` to override an open blocker.
- `related-to`: context links. Add each link on one task; `refs` shows both directions.
- `parent`: the containing task. `refs` shows its children through incoming links.
  A parent link does not block work or complete children.
- `duplicate-of`: the task that covers this work. Cancel the duplicate with a reason.
- `expected-paths`: an advisory scope hint. It does not lock files.

Validation rejects missing targets, self relationships, and cycles in dependencies,
parents, and duplicate chains. A cancelled blocker stays unresolved. Update the
blocked task's plan before removing that dependency.

## References and backlinks

Use `task:<id>` for a task and `task:<id>#c-<comment-id>` for a comment.
These references work as plain text or Markdown link targets.

```markdown
See [source repair](task:2026-10-14-source-repair).
Evidence: [test receipt](task:2026-10-14-source-repair#c-0123456789ab).
```

`task:` is a board reference, not a browser URL. Resolve it with:

```sh
python3 scripts/tasks.py refs 2026-10-14-source-repair
python3 scripts/tasks.py refs task:2026-10-14-source-repair#c-0123456789ab
```

`refs` prints the current file and line, outgoing references, and incoming references.
It includes relationships and mentions from card bodies and comments.
Each entry includes its source task or comment, file, line, and source text.
Backlinks are computed from the files. Do not keep a second backlink list.
References in fenced code examples are ignored. Real references must resolve.

## Comments

Write new messages like Git messages: a one-line summary, then a blank line
and optional Markdown details. This applies to comments, replies, resolutions
and transition reasons. `-m` and `--message` accept multiline text. `--file`
reads the full message; `--file -` reads stdin. Existing messages stay valid
and unchanged. No headings or sections are mandatory. For creation, `--title`
supplies the task summary and the message input supplies its card body.

Use `comment` to append Markdown. Use `--file` for paragraphs, lists, code, and links.
`--file -` reads stdin. The command prints the new permanent comment reference.
Existing timestamped comments stay intact. They have no comment ids.
Link to their task, or cite a git revision when the exact old entry matters.

```sh
python3 scripts/tasks.py comment <id> -m 'The parser check passes.' --as codex
python3 scripts/tasks.py comment <id> --file /tmp/findings.md --as codex
python3 scripts/tasks.py comment <id> --reply-to task:<other-id>#c-0123456789ab -m 'This fixes the same input.'
python3 scripts/tasks.py resolve <id> task:<other-id>#c-0123456789ab -m 'The rerun confirms the fix.'
python3 scripts/tasks.py comment <id> --as codex-task-tooling --file - <<'EOF'
The parser check passes

- Source values remain unchanged.
- The failure case has a regression check.
EOF
```

New comments have this form:

```markdown
## c-0123456789ab

- At: 2026-10-14 20:00 HKT
- By: codex
- Reply-to: task:2026-10-14-source-repair#c-fedcba987654

The rerun passes.
```

Use `###` or deeper headings within a comment. `## c-<12 hex digits>` is reserved
for comment boundaries. `Reply-to` and `Resolves` are reserved metadata entries.
Replies and resolutions can reference a comment on any task.
`resolve` appends a comment with `Resolves:` metadata. It preserves the question
and all replies. `refs` shows the resolution and marks its target as resolved.
Resolution does not change the task's column.

Keep comments brief: state the finding, decision, question, or handoff, then link to the evidence. Put long reports in the relevant subsystem and link to them. There is no hard character or line-length limit.

Never delete or rewrite another agent's comments. Correct a mistake with a new comment.
Timestamps use Asia/Hong_Kong (HKT). The displayed age in `list` is time since the latest task commit.

## Acceptance evidence

Each checked criterion must include a Markdown evidence link on the same line.
The link can point to a comment with receipts, a report, a test file, or a commit.
Use relative file paths from the card directory. `task:` references survive moves.

```markdown
- [x] Source values are preserved. [receipt](task:2026-10-14-source-repair#c-0123456789ab)
- [x] Regression checks pass. [tests](../../../tests/test_tasks_workflow.py)
```

Both `done` and `accept` require a nonempty, complete checklist with evidence links.
Validation checks link syntax and resolves `task:` targets. It does not run tests or
prove the content of reports, external links, or commits. The reviewer checks those.

## Process and commands

All mutating commands record a comment and commit explicit task paths.
They refuse to run off `master`, mid-merge, or mid-rebase.
Board changes are separate commits from implementation changes.
Each automatic commit uses the task title as its summary. A blank line separates
it from the board action and any supplied Markdown details.
Commits use `git commit --only`. Unrelated staged files stay outside the commit
and remain staged. Comments commit only `comments.md`.
Path selection cannot separate two agents' edits within the same file.
Inspect and coordinate those edits before committing that path.
Add and commit are chained, with explicit pathspecs. Moves refuse dirty cards and
commit the directory move immediately, before editing metadata or comments.
Commit your checklist and receipts before `done`. Comments also refuse dirty cards.
If metadata fails after a move commit, repair the task in its new column; do not undo the move.

```sh
python3 scripts/tasks.py create <id> --title 'One line' --area scripts --priority P2 --file /tmp/task-body.md
python3 scripts/tasks.py triage <id>
python3 scripts/tasks.py claim <id> --as codex
python3 scripts/tasks.py show <id>
python3 scripts/tasks.py done <id>
python3 scripts/tasks.py accept <id> --as reviewer
python3 scripts/tasks.py request-changes <id> -m 'Add the failure-case receipt.'
python3 scripts/tasks.py drop <id> -m 'Release the claim.'
python3 scripts/tasks.py cancel <id> -m 'Covered by the linked replacement task.'
python3 scripts/tasks.py reopen <id> -m 'The new input reproduces the fault.'
```

1. Create proposals in `inbox/`. An authorized reviewer uses `triage` to move them
   to `ready/`. Agents claim only from `ready/`, before starting implementation.
2. Record findings and decisions in comments. Edit your active task's checklist
   and add evidence links as work finishes.
3. `done` moves `active/` to `review/`. The owner or a trusted reviewer uses `accept`
   to move it to `done/`, or `request-changes` to return it to its assignee in `active/`.
4. `drop` moves `active/` to `ready/` and clears the assignee.
   `cancel` closes any open task in `cancelled/`.
   `reopen` moves a done or cancelled task to `ready/` and clears the assignee.
   Cancel, reopen, and request changes require a reason.

Commands accept `--as NAME`; the default is the git user. Claim requires `--as`.
Transition reasons accept `-m` or `--file`. Reasons can use Markdown and references.

Edit descriptions, relationships, priorities, and criteria directly in `card.md`.
Validate, then commit only that task directory. Never edit another agent's active
card body or checklist; coordinate in comments. Use the commands for comments and
state changes. Do not move cards by hand.

If a command fails after making changes, it leaves those changes uncommitted.
Fix the reported problem, validate, and commit only the paths the command prints.
Do not retry a move that already changed the directory.
Repo rules still apply: commits on `master`, pathspecs, no amend, no push, and
local-only development and the pending 0.4 update.

## Checks and navigation

Unmet explicit dependencies are ordinary blocked status, reported as a count.
Missing targets, cycles, invalid structure and completion evidence errors remain
visible. Validation exits with 1 when errors exist and 0 otherwise.
`next` keeps its explicit-dependency filtering. Check any phase prose yourself.
`show <id>` resolves the stable ID to its current column, prints the full card,
and shows the comments path. It does not change files or commit.

For direct card edits, inspect and validate the diff, then commit explicit paths:

```sh
git add -- tasks/active/<id>/card.md && git commit --only -m "<task title>" -- tasks/active/<id>/card.md
```

Historical evidence gaps covered by `LEGACY_CHECKLISTS.json` appear in a separate
summary. `validate --historical-details` shows each gap. These gaps do not count
as current warnings or errors. The exact frozen exemptions stay unchanged.
New or edited criteria, and every `done` or `accept` action, still require evidence.

```sh
python3 scripts/tasks.py validate
python3 scripts/tasks.py validate --historical-details
python3 scripts/tasks.py list
python3 scripts/tasks.py next
python3 scripts/tasks.py show <id>
rg -n 'source repair|task:2026-10-14-source-repair' tasks/
cat tasks/active/<id>/card.md tasks/active/<id>/comments.md
```

`validate` checks columns, ids, required fields, references, cycles, and acceptance
links. Markdown lint checks structure. Neither imposes a comment length limit.
`list` flags uncommitted board changes. A stale claim deserves a comment, not a
second claim. No database, generated index, or search service is needed.

## Downstream migration

`tasks/MIGRATION.md` maps all 48 legacy entries to cards. The original TODO
was removed; Git history retains it. Legacy DONE entries preserve historical status;
this import does not assert fresh owner acceptance. Recent completed 0.4
implementation entries start in review/. Mixed completed/pending entries
retain checked achievements and unchecked remaining work in ready/.
Blocked external-data and owner-decision items start in inbox/.

`tasks/LEGACY_CHECKLISTS.json` freezes only the checked criteria that lacked inline
links when the Markdown workflow was imported. Validation preserves those exact
historical entries; new or edited criteria need evidence links. `done` and `accept`
always enforce the complete evidence checklist, including on legacy tasks.
Existing comments remain byte-for-byte intact; only new entries get permanent ids.

`docs/QUEUED_EXTRACTIONS.md` remains authoritative for extraction-row status;
coordinate extraction work through cards without duplicating its table.
XH1B integration tasks belong to the companion repository. Local cards track
handoff and references; they do not authorize applying the pending update.
The CLI is adapted from XH1B commit `e1b851ec28c75bc14f368f8655911e6d51f991e5`,
retaining Downstream's commit-first moves, chained path-scoped commits and HKT timestamps.
