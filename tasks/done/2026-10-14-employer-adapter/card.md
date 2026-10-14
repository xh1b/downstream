---
title: Employer and person scenario adapter
area: integration
priority: P2
assignee:
due:
blocked-by: []
expected-paths: []
---

# Employer and person scenario adapter

## Context

Migrated from TODO entry 34, section "Engine", original line 213.

- **[DONE 2026-09-09] Employer scenario shape (engine)** — `DocumentedExposure.from_warehouse` validates existing
employer/person LCA and WARN aggregates, preserves the upstream total and method, and feeds `compute_entity_counts`.
CLI: `entity --input-format warehouse`. Synthetic integration fixtures cover both subjects, rounding, missing fields,
and invalid inputs. Production runner/cache wiring remains in XH1B.

## Acceptance

- [x] Preserve documented warehouse exposure validation and synthetic engine integration fixtures.
