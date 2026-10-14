---
title: Audit 0.4 calculations, sources and release documentation
area: release
priority: P1
assignee:
due:
blocked-by: []
expected-paths: [src/downstream/, params/study_estimates.csv, paper/, docs/]
---

# Audit 0.4 calculations, sources and release documentation

Owner selected release-readiness items 1, 4 and 5 on 2026-10-14.
Audit the newly introduced numerical paths and their source inputs, fix
confirmed defects, and independently review the completed paper synchronization.
Preserve signed, null and conflicting effects, conditional applicability,
source versions and unresolved empirical dependencies. Keep engine 0.4.0.

## Acceptance

- [ ] Audit mortality timing, subgroup selection, discounting, custom parameters and shared uncertainty draws.
- [ ] Verify zero/beneficial/unsupported cases and add regression coverage for confirmed defects.
- [ ] Recheck source coefficients, SEs, effect scales, windows and sample overlap used by the new paths.
- [ ] Confirm agreement among paper, HTML, model card, saved outputs and current code after repairs.
- [ ] Record findings, exact audit scope, outstanding scientific limits and verification receipts.
