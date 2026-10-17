# comments

## c-cd07620d0537

- At: 2026-10-17 20:37 HKT
- By: codex-doc-cleanup

Created in inbox.

## c-e2e57f5fa462

- At: 2026-10-17 20:37 HKT
- By: codex-doc-cleanup

triage: inbox -> ready.

User requested documentation consolidation and an audit archive.

## c-9b3cee1f3ea2

- At: 2026-10-17 20:37 HKT
- By: codex-doc-cleanup

claim: ready -> active.

## c-4296cd89dde7

- At: 2026-10-17 20:40 HKT
- By: codex-doc-cleanup

Review establishes code, paper, software docs and audit responsibilities

The 42 top-level Markdown files mix API contracts, mathematical explanation, dated reviews, generated inventories, research plans and extraction status. Many code headers cite review reports or plans as their primary method reference. Two generators and their tests assume report files live at the top level; evaluation also hashes a protocol by path. The existing 208-line docs index duplicates a module/test directory.

Code and admitted data define actual behavior. The paper explains mathematical and scientific choices, with code comments pointing to the relevant passage. Five maintained software guides will cover model scope, integration contracts, evidence/data operations, the calculator and development. Reviews belong in docs/audits; research/design plans and the extraction register remain separate in docs/research. Contracts consolidated into the guides will be removed, with their stable anchors transferred to the corresponding sections. Historical task comments and frozen evidence records stay intact.

Pure moves were committed immediately per AGENTS.md (47704dc, e335af8). Follow-up tasks cover guide consolidation, source/paper navigation and generator/link verification. No model behavior or parameter change is intended.
