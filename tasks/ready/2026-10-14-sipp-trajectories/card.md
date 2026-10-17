---
title: R2 - Pool SIPP trajectories and estimate survey-design uncertainty
area: households
priority: P2
assignee:
due:
blocked-by: []
expected-paths: []
---

# R2 - Pool SIPP trajectories and estimate survey-design uncertainty

## Context

Migrated from TODO entry 11, section "Forward milestones", original line 116.

- **[R2] Baseline household trajectories:** SIPP adopted as the dataset (2026-09-13 assessment:
`docs/audits/SIPP_BASELINE_DATA_ASSESSMENT_2026-09-13.md` — free, public domain, redistributable, LLM-workflow compatible;
limitations: short panels, coarse public geography, >20% panel attrition, no intergenerational supplements. PSID ruled
out on the ICPSR LLM policy — `docs/audits/PSID_BASELINE_DATA_ASSESSMENT_2026-09-13.md` — and stays citation-only). First R2
artifact built and held-out validated (2026-09-14): FINYR2-weighted December-to-December 2021→2022 employment/earnings
transitions for 3,206 prime-age span persons (`docs/audits/BASELINE_TRANSITION_R2_2026-09-14.md`; E-origin cells calibrate to
~1pp, U-origin cells indicative-only at n≈14–19). Next: pool the 2020/2021/2022 panel releases to enlarge U-origin
cells, add replicate-weight SEs (`lgtrw2023yr2`), then the 2008 panel for fine-grained monthly transitions.

## Acceptance

- [ ] Pool 2020/2021/2022 releases to improve sparse unemployed-origin transition cells.
- [ ] Add lgtrw2023yr2 replicate-weight standard errors and assess 2008 monthly transitions.
