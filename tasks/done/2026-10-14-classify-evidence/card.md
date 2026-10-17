---
title: R0-R1 - Correct and classify evidence
area: evidence
priority: P1
assignee: eli
due:
blocked-by: []
expected-paths: []
---

# R0-R1 - Correct and classify evidence

## Context

Migrated from TODO entry 10, section "Forward milestones", original line 114.

- **[R0-R1] Correct and classify:** resolve current review findings; distinguish baseline transitions, causal effects,
and structural assumptions in evidence records.

## Acceptance

- [x] Resolve classification ambiguities and classify baseline transitions, direct/conditional effects, structural assumptions and boundary evidence. [generated inventory](../../../docs/audits/evidence_classification_0_4.md) [admission/use checks](../../../tests/test_evidence_classification.py)

## Scope disposition

The existing calculation/source corrections are recorded in task:2026-10-14-audit-04-release. This unit makes current evidence roles and runtime use inspectable without claiming a new primary-source review or closing the separate applicability, published-profile, SIPP and external-validation tasks. The generated report names those remaining scientific questions.
