# tasks — the agent board

A Trello-shaped task board in plain markdown. One directory per card; columns are
subdirectories; git history is the activity log. Agents read this file before using the board.

## Columns

| Column | Meaning |
|:---|:---|
| `inbox/` | Proposals, not triaged. Anyone may drop a card here. |
| `ready/` | Triaged and claimable. |
| `active/` | Claimed and in progress. |
| `review/` | Work finished; awaiting owner review. |
| `done/` | Accepted. |

## Card format

A card is a directory named `YYYY-MM-DD-<short-slug>`. The directory name is the card id.
A card holds:

- `card.md` — YAML front matter, then description, then the acceptance checklist.
- `comments.md` — the append-only thread.

Front matter:

```
---
title: <one line>
area: <subsystem tag>
priority: P1 | P2 | P3 | P4
assignee: <session or agent name; empty until claimed>
due: YYYY-MM-DD (optional)
blocked-by: [<card id>, ...] (optional)
expected-paths: [<repo path>, ...] (optional, advisory hint)
---
```

The body states context and approach, then acceptance criteria as `- [ ]` items.

## Process

1. Agents pull only from `ready/`. Never self-assign from `inbox/` — `inbox/` is for
   proposals (humans, audit agents, later Metrics).
2. Claim: `git mv ready/<id> active/<id>`, fill `assignee:`, leave a comment saying you
   started.
3. Narrate work in `comments.md`: findings, questions, handoffs, decisions. One line per
   entry: `- YYYY-MM-DD HH:MM <who>: text`. Append only; never delete or rewrite another
   agent's entries.
4. Done: check every `- [ ]` with its receipt referenced in comments, then
   `git mv active/<id> review/<id>`.
5. The owner (or a trusted agent) reviews and moves cards to `done/`.

## Verbs and commits

`scripts/tasks.py` mutating verbs edit the card AND commit it in one command, so board
state never sits uncommitted in the worktree:

- `tasks.py claim <id> --as <name>` — ready -> active, sets `assignee:`, comments, commits.
- `tasks.py comment <id> -m "..."` — appends a timestamped comment, commits it.
- `tasks.py done <id>` — requires every `- [ ]` ticked (with receipts); active -> review.
- `tasks.py drop <id>` — releases a claim: active -> ready, clears `assignee:`.

Use the verbs for claims, comments, completion and releases. Creating or
triaging cards and checking acceptance items use explicit path-scoped board
commits after validation. Initial migration is a bootstrap import.
A board change is always its own commit; never bundle it with a code-work commit.
Directory moves are committed immediately, before metadata/comment edits.
Move verbs therefore make a move commit, then a metadata/comment commit.
Commit your checklist and receipts before `done`; move verbs refuse dirty cards.
If a move succeeds but the metadata step fails, repair the card in its new
column and commit only that card; do not undo the committed move. Claim before starting work, not after. The
verbs refuse to run off `master`, mid-merge, or mid-rebase, and they commit with
card-directory pathspecs only, so they are safe beside other agents' staged work.
If a verb fails validation it leaves the changes uncommitted: fix them, then commit
the card directory with a pathspec yourself. `tasks.py list` shows claim ages and
flags uncommitted board state; a stale claim you did not make deserves a comment,
not a second claim.

## Rules

- `expected-paths` is a hint so an agent sees overlap before starting. It is advisory:
  bug reports often touch unexpected files. Overlap is resolved by the repo commit rules,
  not by this field.
- `blocked-by` lists card ids that should reach `done/` first. Advisory: claiming with an
  open blocker needs a comment saying why. `validate` fails on dangling ids.
- Renaming a card is a `git mv`; update `blocked-by` references in the same commit.
- Never edit another agent's card body or checklist while the card is `active/`;
  coordinate in comments.
- Every file: plain language, at most 160 characters per line, passes markdownlint.
- Repo rules always win: pathspec commits on `master`, no branches, no amend, no push,
  local-only development and the pending 0.4 update.

## Validation

- `python3 scripts/tasks.py validate` — checks columns, ids, front matter, references,
  checklists, and line lengths. Run it before committing any board change.
- `python3 scripts/tasks.py list` — the board view.
- `python3 scripts/tasks.py next` — claimable cards, ordered by priority then due date.

## Downstream migration

`tasks/MIGRATION.md` maps all 48 legacy entries to cards. The original TODO
was removed; Git history retains it. Legacy DONE entries in done/ preserve historical status;
this import does not assert fresh owner acceptance. Recent completed 0.4
implementation entries start in review/. Mixed completed/pending entries
retain checked achievements and unchecked remaining work in ready/.
Blocked external-data and owner-decision items start in inbox/.

`docs/QUEUED_EXTRACTIONS.md` remains authoritative for extraction-row status;
coordinate extraction work through cards without duplicating its table.
XH1B integration tasks belong to the companion repository. Local cards track
handoff and references; they do not authorize applying the pending update.
Comment timestamps use Asia/Hong_Kong. The CLI is adapted from XH1B's task
system, retaining its verbs and format with Downstream's commit-first moves
and chained, path-scoped add/commit rules.
