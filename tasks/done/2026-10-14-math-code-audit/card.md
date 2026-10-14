---
title: Deep mathematics and code audit remediation
area: engine
priority: P1
assignee:
due:
blocked-by: []
expected-paths: []
---

# Deep mathematics and code audit remediation

## Context

Migrated from TODO entry 23, section "Engine", original line 201.

- **[DONE 2026-09-09] Deep mathematics/code audit remediation** — public chains now enforce declared context-safe
composition; V1/V2 mortality scoring shares the production survival kernel; all parameter materialization is
point-aware; rank correlations use the Spearman-to-copula mapping; count quantiles use raw values; and source loaders
reject duplicate/non-finite rows.

## Acceptance

- [x] Preserve the documented composition, scoring, sampling, count-quantile and loader repairs.
