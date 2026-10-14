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

## Context

Migrated from TODO entry 12, section "Forward milestones", original line 131.

- **[R3] First full comparison:** a five-year involuntary-displacement scenario versus a stated reference, limited to
supported employment, earnings, and household-resource outcomes. Current long-run coefficients are not annual paths. The
2026-09-14 scenario review surfaced a second gap: the engine is silent on receiving-community effects of replacement
inflows (unmodeled, not estimated zero). Anchors for rents, native wages, host mental health, trust, crime, and voting
are verified in `docs/IMMIGRATION_REPLACEMENT_EVIDENCE_SCAN_2026-09-14.md`; next: screen them through the admission
contract into queued extractions. Progress 2026-09-16 (v1.48): the CRIME channel screened and LANDED — the independence
gate passed (Light-Miller Criminology 2018; Bell-Fasani-Machin REStat 2013 published; Bianchi-Buonanno-Pinotti JEEA
2012), two `immigrant_influx->receiving_*_crime_rate` rows shipped, and the work-ban vs work-access property-crime split
is recorded as findings. Remaining receiving-community channels (rents, native wages, mental health, trust, voting)
still queued; scenario wiring for an `--immigrant-influx` exposure is not built yet.

## Acceptance

- [ ] Compare supported employment, earnings and household resources against a stated reference.
- [ ] Screen remaining receiving-community channels and wire an explicit immigrant-influx exposure.
