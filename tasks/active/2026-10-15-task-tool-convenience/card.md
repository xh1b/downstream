---
title: Simplify cooperative task-board tooling
area: scripts
priority: P2
assignee: codex-task-tooling
blocked-by: []
---

Make the existing file board easier for cooperative agents to use. The owner authorizes this narrow tooling task, its triage and its implementation. Preserve stable IDs, existing cards, append-only comments, automatic commits, explicit dependency filtering and the standard-library-only runtime.

- [x] Separate blocked status and frozen historical evidence gaps from actionable validation output. Offer individual historical details and preserve error exit semantics. [verification](task:2026-10-15-task-tool-convenience#c-adcf752daa00)
- [x] Use task titles as Git summaries and preserve optional multiline Markdown details for message inputs. [verification](task:2026-10-15-task-tool-convenience#c-adcf752daa00)
- [x] Add a stable-ID task view that prints the card and its comments path. [verification](task:2026-10-15-task-tool-convenience#c-adcf752daa00)
- [x] Use explicit-path commits and document the same-file limit. Retain move-first behavior and test staged-file and dirty-card isolation. [verification](task:2026-10-15-task-tool-convenience#c-adcf752daa00)
- [x] Pass affected task tests, board validation, migration preservation and documentation checks. Send this task to review without self-acceptance. [verification](task:2026-10-15-task-tool-convenience#c-adcf752daa00)
