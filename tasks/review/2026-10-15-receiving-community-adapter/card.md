---
title: Add explicit receiving-community exposure adapter
area: scenarios
priority: P2
assignee: eli
parent: 2026-10-14-full-comparison
expected-paths: [src/downstream/receiving_community.py, src/downstream/cli.py, tests/test_receiving_adapter.py, docs/RECEIVING_COMMUNITY_0_4.md]
blocked-by: []
---

# Expose receiving-community scenarios through explicit immigrant-share inputs

The owner authorized a bounded adapter for the two existing receiving-crime
coefficients. Input must remain separate from displaced workers. Source-unit
review finds Light–Miller's exposure is a percentage-point population share
with a logged outcome, while Bianchi's exposure is a log population share.
Do not propagate the generic legacy stock-elasticity interpretation.

## Acceptance

- [x] Validate source-specific immigrant-share exposure, population margin, horizon and baseline units without converting displaced workers into arrivals. [contract](../../../docs/RECEIVING_COMMUNITY_0_4.md) [tests](../../../tests/test_receiving_adapter.py)
- [x] Preserve source signs, uncertainty support, null contrasts, exact null-input behavior and declared unknown transport. [contract](../../../docs/RECEIVING_COMMUNITY_0_4.md) [tests](../../../tests/test_receiving_adapter.py)
- [x] Keep violent and total-crime contrasts separate, with overlapping endpoints and incomplete channels explicit; do not sum them. [contract](../../../docs/RECEIVING_COMMUNITY_0_4.md) [tests](../../../tests/test_receiving_adapter.py)
- [x] Provide a CLI and meaningful regression checks, including malformed inputs and unsupported margins/horizons. [contract](../../../docs/RECEIVING_COMMUNITY_0_4.md) [tests](../../../tests/test_receiving_adapter.py)
- [x] Record primary-source unit checks, legacy-mapping discrepancy and any remaining source-version repair; do not invent an empirical bridge or change default coefficients. [contract](../../../docs/RECEIVING_COMMUNITY_0_4.md) [tests](../../../tests/test_receiving_adapter.py)

## Source correction disposition

The unit repair advances parameters v1.51→v1.52 while keeping engine0.4.0. Generic stock links are retired. Light–Miller is per percentage-point undocumented population share; Bianchi uses log valid-residence-permit population shares. Points and coefficient-support endpoints remain unchanged. [Source receipt](../../../validation/receiving_source_units_20261015.json). Published Bianchi reconciliation and the other receiving channels remain open; the full-comparison parent is not completed by this adapter.
