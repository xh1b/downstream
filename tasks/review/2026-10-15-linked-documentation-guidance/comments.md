# comments

## c-fa5095f996da

- At: 2026-10-15 17:13 HKT
- By: codex-doc-links

Created in inbox.

## c-1b08161b1fc2

- At: 2026-10-15 17:13 HKT
- By: codex-doc-links

triage: inbox -> ready.

Owner explicitly requested this follow-up. Checked the current board: token tooling is in review, and no active task covers documentation policy. Existing docs and root entry points are established.

## c-3eddb14f15d5

- At: 2026-10-15 17:13 HKT
- By: codex-doc-links

claim: ready -> active.

## c-e17ce0888c3b

- At: 2026-10-15 17:14 HKT
- By: codex-doc-links

Linked documentation guidance is complete

Updated the root [agent instructions](../../../AGENTS.md) with a documentation workflow: maintained Markdown in docs/, discoverable entry-point links, one authoritative explanation per topic, reciprocal refs between methods, implementations and verification, reusable topic tags, task provenance and ordinary file/source/artifact links. Paper sources stay in paper/; navigation tokens use LaTeX percent comments or Markdown/HTML comments so they stay out of rendered output. Scientific citations and attribution remain reader-facing. Examples are fenced and do not create live anchors.

Checks: `python3 scripts/refcheck.py check` reports 5 anchors, 8 links and 0 failures; `python3 scripts/tasks.py validate` reports 0 errors and 0 warnings; `git diff --check` passes. A direct scanner smoke check confirmed two anchors and reciprocal links in LaTeX percent comments and Markdown HTML comments resolve. Only guidance changed; no paper-source or rendered-output build was needed. Existing shared-checkout and task rules are preserved.

## c-d79b5bf6b466

- At: 2026-10-15 17:14 HKT
- By: codex-doc-links

done: active -> review.
