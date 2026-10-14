---
title: Qualify Downstream 0.4 for the XH1B handoff
area: release
priority: P1
assignee:
due:
blocked-by: []
expected-paths: [docs/RELEASE_0_4.md, scripts/check_distribution.py, tests/]
---

# Qualify Downstream 0.4 for the XH1B handoff

Proposed scope following the owner's request for a very good 0.4 release.
Keep engine 0.4.0 until the owner chooses another release. This card records
release acceptance; it does not authorize deployment or remote operations.

## Recommended work order

1. Audit new numerical paths and evidence/admission contracts, including custom
   parameter directories, draw preservation, signed benefits, zero exposure,
   zero duration/discounting, timing boundaries and unsupported populations.
2. Improve the SIPP baseline through pooled releases and survey-design uncertainty
   where compatible. Compare held-out cells with the current baseline and retain
   misses. Specify a supported experimental scope if sparse cells remain unresolved.
3. Review the target-cohort/exposure contract and prepare XH1B-compatible fixtures.
   Missing demographics stay unknown; generic CPS composition does not identify
   an H-1B displacement bridge. Upstream exposure remains caller-owned.
4. Complete the current methods-paper synchronization, inspect its receipts and
   confirm that paper, HTML, model card and JSON tell the same scientific story.
5. Execute release comparisons and distribution checks on a fixed candidate.
   XH1B must preserve applicability, structural sensitivities, interval scope,
   source versions and content hashes, and recompute stale cached results.

## Acceptance

- [x] Audit new calculation paths; fix confirmed defects and retain numerical/source receipts.
- [ ] Record SIPP held-out accuracy, survey uncertainty and the supported household prototype scope.
- [ ] Document admitted cohort and exposure requirements, including how missing target information is handled.
- [x] Recheck source coefficients, scales, windows, overlap and null/beneficial estimates used by the release.
- [x] Resolve the paper-review findings and check agreement among paper, HTML, model card and saved examples.
- [ ] Prepare consumer fixtures and a version/hash/cache handoff checklist for the companion project.
- [ ] Run full tests, coverage, audit, lint, wheel/sdist installation and previous-version comparisons.
- [ ] Publish changed results, known validation misses, unmodeled uncertainty and unresolved research dependencies.

## Related cards

- `2026-10-14-classify-evidence` - evidence and calculation contracts.
- `2026-10-14-sipp-trajectories` - sparse cells, pooled releases and replicate weights.
- `2026-10-14-target-displaced-cohort` - target composition and exposure provenance.
- `2026-10-14-coefficient-library` - source uncertainty, compatibility and overlap.
- `2026-10-14-paper-code-sync` - narrative and generated-paper corrections already in progress.
- `2026-10-14-xh1b-handoff` - coordination with companion integration work.

## Research dependencies

Continue seeking matched independent event data, compatible independent pools
and wider response evidence. A conditional scenario-tool release must explicitly
state what remains unvalidated; it cannot claim complete causal validation.
The published-QJE covariance gap does not justify inventing a profile or covariance.
Broader household dynamics, new headline streams and calculator development need
separate scope decisions; they are not implicit acceptance requirements here.

## Board accuracy

The migrated place-counterfactual card appears implemented: current code scales
the displacement gap, and tests/test_place.py includes a null-effect regression.
Verify its current receipts and move it through review before calling it open work.

## Selected work completed - 2026-10-14

Owner-selected items 1, 4 and 5 are implemented and verified in
`2026-10-14-audit-04-release`. Its card records defects, primary-table audit
coverage and remaining scientific limits. Engine stays 0.4.0; corrected
source transforms/provenance are parameters v1.51. Full suite: 1,065 tests;
coverage 96.8% statements / 93.2% branches. This is not a release decision
or completion of the remaining SIPP, cohort and XH1B handoff scope.

## Integration-informed sequencing - 2026-10-14

The owner requested a current XH1B usage review. Follow
`docs/XH1B_USAGE_PLAN_0_4.md` for the next implementation order: exposure
semantics, then consumer fixtures and preservation of structural comparisons.
The current companion adapter uses reference counts and does not consume the
household prototype. Retain SIPP scope and held-out misses in release acceptance,
but qualify that prototype separately from the count consumer. A repin alone
loses persistence metadata and miscombines nested alternatives in employer mixes.
The local inspection does not establish deployed state or authorize integration.
