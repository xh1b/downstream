---
title: Synchronize pending 0.4 artifacts after receiving-unit repair
area: release
priority: P1
assignee: codex
blocked-by: []
---

Synchronize the pending 0.4 release with v1.52 receiving-source units and completed local tools. Keep dated historical receipts intact and state unresolved validation and visual-review limits.

Related: task:2026-10-15-receiving-community-adapter, task:2026-10-14-release-04-readiness.

## Acceptance

- [x] Update current release/model documentation for typed share exposures and new local calculation APIs. [current release](../../../docs/audits/release_0_4.md)
- [x] Regenerate calculator, evidence, pool, consumer and paper/method outputs from the fixed candidate. [candidate fixtures](../../../validation/consumer_fixtures_0_4.json)
- [x] Run relevant source/CLI/consumer checks and the full regression and coverage gates. [scoped qualification receipt](../../../docs/audits/release_0_4.md#final-local-qualification--2026-10-15)
- [x] Record local-only version, independent reviews and unresolved empirical/mobile-preview limits. [remaining limits](../../../docs/calculator.md)
