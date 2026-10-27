# comments

## c-8c229f76595d

- At: 2026-10-27 13:35 HKT
- By: codex-source-repair

Created in inbox.

## c-3293712b6877

- At: 2026-10-27 13:35 HKT
- By: codex-source-repair

triage: inbox -> ready.

## c-4512b23daad7

- At: 2026-10-27 13:35 HKT
- By: codex-source-repair

claim: ready -> active.

## c-1c55c39f412b

- At: 2026-10-27 13:40 HKT
- By: codex-source-repair

Original local PDFs were available and should have been checked before withdrawal

Located the owner's existing originals under /Users/jt/Downloads/papers. Initial table-text inspection finds the exact stored Hilger enrollment/income, Raphael property-crime, Bastian EITC, Evans internalizing/externalizing and Paul mental-health figures. That is seven inputs with directly available numerical evidence, rather than a demonstrated source-access failure. These findings still need visual table/version review and explicit admission before runtime restoration.

Additional primary material is available for the Autor exposure-unit, Colantone currency/window, Collinson denominator and Bingley risk-difference corrections. The original 0.4 withdrawal must not be counted as completed source repair. Local inspection artifacts are in build/source-repairs-20261027; no parameter or runtime restoration has yet been committed. Preserve the published 0.4.0 tag and assets while preparing a reviewed correction.

## c-546a3e88c723

- At: 2026-10-27 16:26 HKT
- By: codex-source-repair

Individual source repair implemented in v1.54

Commit 6d8d92f preserves all 67 original CSV records byte-for-byte, restores six source-verified original estimates and adds seven typed corrections. The 16 individual dispositions, source versions/tables, numeric extractions and artifact hashes are in [source_support.json](../../../params/source_support.json). There are now 64 available records and ten retired identifiers: seven superseded plus three unsupported relationships.

Restored: Hilger enrollment/income, Bastian EITC earnings, Evans internalizing/externalizing, Paul outlier-excluded mental-health association. Corrected: Raphael semi-log crime response; Aizer absolute wage-ratio/female-assault contrast; Autor penetration percentage points; Colantone two-year real-2006-euro exposure; Collinson matching quarterly denominator 4254; Bingley probability difference without a regression-constant denominator; Ehrensaft sex-adjusted pooled adult victimization OR 2.68 [1.49,4.82], replacing neither the meaning nor value of a daughters-only effect.

The three remaining original relationships are unsupported by their cited studies: Gruber estimates divorce-law exposure, not an individual parental-divorce effect; Black studies schooling, not a .98 earnings multiplier; Lindahl observes earnings for three generations, not an identified fourth-generation .55 gap rule. These remain unavailable rather than fabricating a repair.

The named [source-contrast adapter](../../../src/downstream/source_contrasts.py) and CLI require source-specific nodes/units; fixed study contrasts cannot be multiplied by population counts. Retired identifiers remain refused after sampling/overrides; custom data cannot relabel reviewed units or coefficients. Main mortality and direct-child point coefficients/baselines are unchanged. The published v0.4.0 tag/assets have not been replaced. Qualification is in progress: 90 source/export/audit checks and 124 focused checks pass; full suite and installed-wheel verification are running.

## c-b5bb4860a55e

- At: 2026-10-27 16:29 HKT
- By: codex-source-repair

All sixteen dispositions and the corrected implementation are qualified

Full local suite: 1,550 tests plus nine subtests pass in 638.64s. Coverage 96.7% lines / 93.8% branches exceeds unchanged 95%/90% gates. All twelve isolated installed-wheel CLI checks pass, including source-contrast. Audit has zero errors/warnings; Ruff/Vulture, documentation navigation/examples and generator freshness pass. Rebuilt 21-page methods paper and changed inventory/method pages visually checked; no LaTeX warnings/overfull boxes.

[Individual sixteen-row review](../../../docs/audits/source_repairs_2026-10-27.md) and [machine receipt](../../../docs/audits/source_repairs_2026-10-27.json) record primary-document versions/tables, available hashes, numeric extractions, 6/7/3 dispositions and code/data/artifact identities. For Ehrensaft the hash covers a numeric publisher-table extraction, not unavailable original PDF bytes; that access limit is explicit. All original 67 CSV records remain byte-identical in the first 82,447 bytes. Engine/default data now expose 64 available records, and every unsafe legacy alias stays refused.

Main implementation/data commit: 6d8d92f; installed-wheel check: 99bd37e. Corrected code/data, examples, exports, calculator, evidence reports, methods PDF/HTML and consumer fixtures are committed locally. No remote publication, v0.4.0 artifact replacement, companion repin/cache refresh or deployment is claimed. The three unsupported original earnings relationships require new supporting evidence; their absence is not a zero effect or a restored coefficient.

## c-fdb8528480a6

- At: 2026-10-27 16:37 HKT
- By: codex-source-repair

Preserve reviewed interpretation separately from original notes

Commit d9bbb05 makes active by_link lookups and snapshot exports expose the reviewed interpretation of the six restored rows. retained_by_link and the raw CSV continue to preserve historical notes, including the EITC income-bridge statement that must not be presented as an admitted source result. It also rejects unrepresentably large JSON integer doses cleanly and clarifies the Collinson manuscript cover/download dates.

Sixty-three focused source/export/parameter checks and documentation checks pass after this follow-up. Full coverage and isolated-wheel qualification are being rerun against the fixed final source. New-evidence follow-up for the three unsupported relationships is @task:2026-10-27-unsupported-earnings-bridges; they remain unavailable in the correction.

## c-d9311ba48a39

- At: 2026-10-27 16:44 HKT
- By: codex-source-repair

Final corrected source passes all qualification gates

Final runtime/data commit d9bbb05 passes 1,552 tests plus nine subtests (491.39s), coverage 96.7% lines / 93.8% branches, all twelve isolated installed-wheel CLI checks and a zero-error/zero-warning audit. Ruff, Vulture, documentation navigation/examples, generator freshness and artifact checks pass. The rebuilt methods PDF was reviewed after the final source/interpretation change.

[Final sixteen-row review](../../../docs/audits/source_repairs_2026-10-27.md) and [machine receipt](../../../docs/audits/source_repairs_2026-10-27.json) preserve both qualification runs and pin the final source tree, individual source decisions, dataset custody, bundle and distribution/artifact/log digests. Six original estimates restored; seven typed corrections available; three original earnings relationships remain unsupported. All 67 original records and historical notes are preserved. Current by_link and exports use reviewed interpretations.

All implementation, documentation, examples and receipts are committed locally on master. The published v0.4.0 tag/assets and companion operational state are unchanged. New-evidence follow-up for the three unsupported relationships is @task:2026-10-27-unsupported-earnings-bridges. This completion does not relabel their absence as zero effects, claim empirical transport calibration or invent replacement coefficients.
