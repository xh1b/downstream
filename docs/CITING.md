# CITING — citation and evidence rules

Binding for every parameter, baseline, and doc claim in this repo.
The audit (`downstream audit`) enforces the mechanical parts.

## 1. Source classes

| Class | Use |
|:---|:---|
| Peer-reviewed quasi-experimental studies (plant closures, lotteries, law reforms, shocks) | the ONLY class that sets parameter points |
| Meta-analyses | acceptable for points; band = reported CI plus between-study spread |
| Government compiled statistics (CDC WONDER, Census, BJS, SSA) | the ONLY class for baselines |
| Working papers | allowed with tier `canonical` max; upgrade or flag when published |
| Think-tank and advocacy reports | context only; NEVER a parameter source |
| Movement-produced "research" | same as above — context only |

## 2. Precision tiers

| Tier | Claim | Audit check |
|:---|:---|:---|
| `EXACT` | the number was read and pinned from the study's own table/figure this repo | bib `xh1b-evidence` ∈ {fulltext-table, fulltext} |
| `EXACT-abstract` | the number comes from the published abstract/summary, or is confirmed in the full text of a synthesis paper | bib evidence ∈ {abstract, results, fulltext-table, fulltext} |
| `EXACT-results` | extracted from a results section transcribed into the extraction log | bib evidence ∈ {results, fulltext-table, fulltext} |
| `canonical` | an established literature value; full-text pass queued | any bib entry; the queue entry must exist |

Lying upward here (claiming EXACT for a remembered number) is the
worst failure this repo can commit. When unsure, tier down.

## 3. Bands

A band is one of, and the `notes` column names which:

1. **Reported CI/SE interval** — best.
2. **Cross-study spread** — min/max of ≥2 credible designs of the same
   link; each study cited on the row.
3. **Rounding band** — the reported point ±25%, allowed ONLY for
   `canonical` with an extraction-queue entry, and phrased exactly so
   in notes (e.g. the youth-crime elasticity).

Bands never shrink when evidence is added. A tighter study narrows a
band only by replacing the row, with the old value preserved in git.

## 4. Citation mechanics

- Parameter rows cite **bib keys only** (`params/references.bib`),
  semicolon-separated. Free-text citations fail the audit.
- Every bib entry carries `xh1b-evidence` ∈ {fulltext-table, abstract,
  results, canonical} — how the number entered this repo.
- Uncited bib entries are a warning (staging area for queued work).
  Unresolvable keys are an error.
- Renaming a key requires updating every row that cites it (the audit
  catches strays).
- Corrections land as data edits with the correction recorded in the
  row `notes` (see rege2007: internal notes said +23%; the DP514
  abstract says +11%; the correction is dated in the row).

## 5. Honesty rows and refusals

- A literature that REFUTES one of our claims enters the bib and the
  docs (e.g. ousey2018 immigration-crime null). The model refuses to
  encode links the pooled literature does not support; the refusal is
  documented in SPEC §10.
- Contested literatures are never averaged into one number. Compute
  both positions as named alternate bands when a headline needs them.
- Duplicate findings across threads are collapsed to one row; the
  duplicate's citation joins the row.

## 6. Reproducibility

- Parameter set versions live in `params/VERSION`; every output stamps
  the version it used. Sampled (Monte Carlo) outputs mark `-sampled`.
- A published number must be regenerable from a tagged commit with a
  stated seed. No output cites "the model" without a version.
- Every correction is a new commit on top; history is never rewritten.
