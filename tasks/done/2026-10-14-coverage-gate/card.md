---
title: Property tests and branch-aware coverage gate
area: quality
priority: P2
assignee:
due:
blocked-by: []
expected-paths: []
---

# Property tests and branch-aware coverage gate

## Context

Migrated from TODO entry 24, section "Engine", original line 202.

- **[DONE 2026-09-09] Property and coverage gate** — Hypothesis invariants cover ledger corners, mortality survival, and
pooling convexity; Coverage.py records branches and `scripts/quality_gate.py` enforces 80% line / 70% branch floors.
Full-suite baseline: 89.5% / 79.4%. See `docs/TESTING_QUALITY.md`.

## Acceptance

- [x] Preserve property-test and coverage-gate receipts; historical baseline figures remain dated.
