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
