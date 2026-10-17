---
title: Expose checked consumer scaling and mixture transforms
area: integration
priority: P2
assignee: codex
blocked-by: []
---

Make the checked normalization and mixture rules available to consumers as a native package API. Reuse the acceptance fixtures; preserve fixed source metadata and unavailable joint uncertainty.

Related: task:2026-10-14-consumer-contract-fixtures.

## Acceptance

- [x] Expose scaling and weighted-mixture helpers in the package and reuse them from the fixture builder. [package API](../../../src/downstream/consumer.py)
- [x] Preserve signed results, source/applicability metadata, nested alternatives and zero-exposure variance behavior. [native fixtures](../../../tests/test_consumer_fixtures.py)
- [x] Refuse malformed weights/units and preserve unavailable positive-weight components and joint uncertainty. [API guards](../../../tests/test_consumer_api.py)
- [x] Validate existing fixtures and record the API contract without repinning the companion. [contract](../../../docs/INTEGRATION.md#scaling-mixtures-and-acceptance-fixtures)
