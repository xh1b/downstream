---
title: R3 - Complete the five-year comparison and receiving-community scope
area: scenarios
priority: P2
assignee:
due:
blocked-by: []
expected-paths: []
---

# R3 - Complete the five-year comparison and receiving-community scope

## Historical migration context

Migrated from TODO entry 12, section "Forward milestones", original line 131.

- **[R3] First full comparison:** a five-year involuntary-displacement scenario versus a stated reference, limited to
supported employment, earnings, and household-resource outcomes. Current long-run coefficients are not annual paths. The
2026-09-14 scenario review surfaced a second gap: the engine is silent on receiving-community effects of replacement
inflows (unmodeled, not estimated zero). Anchors for rents, native wages, host mental health, trust, crime, and voting
are verified in `docs/audits/IMMIGRATION_REPLACEMENT_EVIDENCE_SCAN_2026-09-14.md`; next: screen them through the admission
contract into queued extractions. Progress 2026-09-16 (v1.48): the CRIME channel screened and LANDED — the independence
gate passed (Light-Miller Criminology 2018; Bell-Fasani-Machin REStat 2013 published; Bianchi-Buonanno-Pinotti JEEA
2012), two `immigrant_influx->receiving_*_crime_rate` rows shipped, and the work-ban vs work-access property-crime split
is recorded as findings. Remaining receiving-community channels (rents, native wages, mental health, trust, voting)
still queued; scenario wiring for an `--immigrant-influx` exposure is not built yet.

## Current scope — 2026-10-17

The annual five-year prototype and receiving adapter now exist. The migrated
`immigrant_influx` rows were retired in v1.52; current source-specific share
units are documented in the [receiving contract](../../../docs/INTEGRATION.md#receiving-community-adapter).
Do not rebuild the retired generic exposure or infer arrivals from displaced workers.
The [five-year result](../../../validation/household_five_year_result.json) now
includes reconciled gross earnings and state-time summaries. Taxes, transfers,
monthly/joint outcomes and the remaining receiving channels are separate research.
Scope review: @task:2026-10-17-release-task-review.

## Acceptance

- [x] Compare annual employment probabilities and gross earnings against a stated reference for the five-year prototype. [comparison scope](../../../docs/INTEGRATION.md#annual-household-comparisons) [saved result](../../../validation/household_five_year_result.json)
- [x] Wire explicit source-specific receiving shares/counts with baseline and transport refusals. [adapter and units](../../../docs/INTEGRATION.md#receiving-community-adapter) [accepted implementation](@task:2026-10-15-receiving-community-adapter)
- [ ] Admit supported household-resource components beyond gross earnings, with monthly/joint dependence requirements retained.
- [ ] Screen remaining receiving channels through the existing extraction/admission process before exposing them.
