---
title: Synthesis and transmission contracts
area: evidence
priority: P2
assignee:
due:
blocked-by: []
expected-paths: []
---

# Synthesis and transmission contracts

## Context

Migrated from TODO entry 45, section "Review priorities — 2026-09-10", original line 245.

- **[DONE 2026-09-13] Synthesis and transmission:** estimand/window/overlap checks, REML and Hartung–Knapp
sensitivities, and the k>=3 / t(k-2) prediction-interval contract are in (`tests/test_synthesis.py`); the log-elasticity
transmission rule is a first-class, role-tagged ledger kind exposed through the declared variant ensemble, never
chainable (`tests/test_variants.py`); first-order Sobol estimators are centered with constant-shift invariance pinned
and dependent-block design-noise reporting (`tests/test_sensitivity_centering.py`). Sensitivity outputs remain
sensitivity outputs — none of this admits a synthesis result into parameters.csv.

## Acceptance

- [x] Preserve estimand/window/overlap, REML/Hartung-Knapp, transmission and Sobol contract receipts. [synthesis tests](../../../tests/test_synthesis.py) [transmission alternatives](../../../tests/test_variants.py) [Sobol centering](../../../tests/test_sensitivity_centering.py)
