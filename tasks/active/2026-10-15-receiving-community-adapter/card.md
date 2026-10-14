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

- [ ] Validate source-specific immigrant-share exposure, population margin, horizon and baseline units without converting displaced workers into arrivals.
- [ ] Preserve source signs, uncertainty support, null contrasts, exact null-input behavior and declared unknown transport.
- [ ] Keep violent and total-crime contrasts separate, with overlapping endpoints and incomplete channels explicit; do not sum them.
- [ ] Provide a CLI and meaningful regression checks, including malformed inputs and unsupported margins/horizons.
- [ ] Record primary-source unit checks, legacy-mapping discrepancy and any remaining source-version repair; do not invent an empirical bridge or change default coefficients.
