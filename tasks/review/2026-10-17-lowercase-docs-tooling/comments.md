# comments

## c-fee8e88bf1bf

- At: 2026-10-17 21:01 HKT
- By: codex-doc-cleanup

Created in inbox.

## c-8cc147816560

- At: 2026-10-17 21:01 HKT
- By: codex-doc-cleanup

triage: inbox -> ready.

User requested lowercase documentation and a development-tooling documentation check.

## c-d09b2c0652b6

- At: 2026-10-17 21:01 HKT
- By: codex-doc-cleanup

claim: ready -> active.

## c-8b02b460d6ca

- At: 2026-10-17 21:05 HKT
- By: codex-doc-cleanup

Lowercase docs and development-tooling coverage are implemented

All 34 Markdown files under docs/ now have lowercase filenames, including the main guides, audit/research records and their indexes. Case-only moves were committed through an intermediate spelling to keep path-scoped commits reliable on the case-insensitive checkout; no temporary filenames remain. Live Markdown paths, task-card evidence paths, generator defaults/templates, code strings and paper references use the new spelling. Stable refs remain unchanged. Existing historical task comments, frozen acceptance exemptions, evaluation JSON and the SIPP source manifest were preserved.

The development guide now includes the task-system quickstart and lifecycle, automatic local commits/ownership safeguards, evidence receipts, a development-tool matrix, focused/full test commands, CI jobs and scheduled mutation/benchmark runs. Detailed task rules remain authoritative in tasks/AGENTS.md. It also identifies the existing Markdown-format configuration and accurately states that the current quality workflow has no separate Markdown-lint job.

Verification: 102 affected generator/consumer/paper/ref/task tests passed. All four freshness checks pass (classification, pool readiness, consumer fixtures and calculator), and make -C paper succeeds. Exact-case checks pass for 514 relative file/heading links and all docs filenames. Refcheck passes with 329 anchors and 1442 links. Task validation, Ruff, Vulture, evidence audit (0 errors/warnings) and git diff --check pass. Engine executable AST differs only in documentation paths; no mathematical method or parameter changed.
