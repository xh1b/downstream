---
title: Make documentation concise, executable and continuously checked
area: docs
priority: P2
assignee: codex-doc-reliability
tags: [@tag:tooling]
blocked-by: []
---

Implement the five approved documentation improvements: automated exact-case links/headings/lowercase/freshness checks in CI, reduce README/SPEC duplication, execute documented examples, complete the integration calling/result/error/version/cache reference, and add troubleshooting and section navigation inside the five maintained guides.

Code/data remain authoritative, mathematical explanation belongs in the paper, and historical audit/task records remain intact. Preserve existing stable anchor IDs when moving their canonical content. Related cleanup: @task:2026-10-17-documentation-consolidation and @task:2026-10-17-lowercase-docs-tooling.

- [ ] Reduce README/SPEC duplication while preserving useful information and all stable anchors.
- [ ] Provide executable documented examples for successful, blocked and refused results.
- [ ] Complete integration input/output/error/compatibility/cache guidance and troubleshooting/navigation.
- [ ] Add tested documentation checks and wire exact-case paths/headings, naming, examples and freshness into CI.
- [ ] Pass affected tests, refs, task validation and artifact checks without overwriting concurrent work.
