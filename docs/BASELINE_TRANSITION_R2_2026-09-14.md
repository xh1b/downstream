# R2 artifact 1: ordinary December-to-December employment and earnings transitions (SIPP 2021→2022)

Status: **built and held-out validated, 2026-09-14.** This is the first
baseline-trajectory artifact under the R2 milestone of
`docs/LIFE_COURSE_RESEARCH_PLAN.md`. It estimates the *ordinary*
(no-displacement-event) year-over-year employment-state transitions and
earnings changes that any event scenario in this repo must be compared
against. It is a validation artifact, **not** a parameter landing: no
model parameter, chain, or scenario changed.

## What was estimated

- **Employment-state transitions**, December 2021 → December 2022, in a
  three-state definition: **E** (with a job all or part of the month),
  **U** (no job, on layoff or looking), **N** (no job, no layoff, no
  looking). Cells: sex × age band (25–34, 35–44, 45–54) × origin state,
  plus the three marginals of each cell, weighted shares of `to_E`,
  `to_U`, `to_N`.
- **Earnings among continuously employed (E|E) workers**: weighted
  median December TPEARN in each December, the weighted median of the
  person-level 2022/2021 ratio, and the weighted share with any nominal
  gain. Medians use E|E persons with **positive reported earnings in
  both months** (a December with zero reported earnings excludes a
  person from the earnings table but not from the employment table).
- **Held-out calibration**: persons are split by a stable hash of their
  key; cell shares estimated on half A are compared with observed
  shares on half B.

Outputs: `validation/sipp/r2_transitions/` —
`employment_transitions_2021_2022.csv`,
`earnings_transitions_2021_2022.csv`, `coverage_and_calibration.json`.

## Data and design (all choices declared)

- **Files** (provenance in `validation/sipp/MANIFEST.json`): content
  files `data/sipp/2021/pu2021.csv.gz` and `data/sipp/2022/pu2022.csv.gz`
  (person-month records, pooled across the overlapping active panels),
  and the calendar-2023 plain longitudinal weight
  `data/sipp/2023/lgtwgt2023yr2.csv`, whose **FINYR2** covers exactly
  the January 2021 – December 2022 span: 23,878 persons, all positive,
  summing to 328.6M ≈ the US resident population (the overlapping
  panels each carry a slice of the control total).
- **Sample**: RIN_UNIV = 1 at December 2021; age 25–54 at December 2021
  (TAGE_EHC); FINYR2 > 0; a December-2022 record matched on
  SSUID+PNUM+SPANEL with RIN_UNIV = 1 and a valid RMESR at both dates.
  Flow: 19,045 prime-age in-universe persons at December 2021 → 3,206
  in the weighted span → **3,206 linked transitions, 0 dropped**. The
  zero drops are structural, not luck: a positive full-span weight
  requires presence and response through the end of the span, so every
  weighted person is by construction in the December-2022 file.
- **State definition**: RMESR recode, read from the committed
  2021 data dictionary (`validation/sipp/2021/2021_SIPP_Data_Dictionary_AUG22.pdf`):
  E = codes 1–5 (job all month worked all weeks; job all month absent;
  absent on layoff; part-month job with/without layoff or looking),
  U = codes 6–7 (no job, layoff/looking all or some weeks), N = code 8.
- **Estimator**: FINYR2-weighted shares; single streaming passes over
  the content files (column-selected, Census-advised; stdlib only;
  deterministic; ~25 minutes).

## Headline results (marginal cells; full grids in the CSVs)

Employment, December 2021 → December 2022, weighted shares, all
prime-age linked persons (n = 3,206; weights sum 61.9M):

| origin | n | to_E | to_U | to_N |
|---|---|---|---|---|
| E | 2,530 | 0.960 | 0.007 | 0.033 |
| U | 95 | 0.678 | 0.132 | 0.190 |
| N | 581 | 0.212 | 0.028 | 0.760 |

The age gradients are the right way round: N→E falls from 0.332
(25–34) to 0.153 (45–54), E→E stability is flat-to-rising in age
(0.948 → 0.958), and U→E recovery is lower for women (0.616) than men
(0.728).

Earnings among continuously employed workers, December TPEARN, nominal:

| group | n | median 2021 | median 2022 | median ratio | share with gain |
|---|---|---|---|---|---|
| all | 2,321 | $4,429 | $4,769 | 1.053 | 0.616 |
| male | 1,235 | $5,110 | $5,536 | 1.058 | 0.619 |
| female | 1,086 | $3,897 | $4,088 | 1.044 | 0.613 |

Median nominal growth declines with age (1.087 at 25–34 → 1.028 at
45–54), the classic early-career profile.

## Held-out calibration (estimate on half A, evaluate on half B)

54 comparable cells (18 exact sex×age×origin cells × 3 destinations):

| origin | mean abs diff | max abs diff |
|---|---|---|
| E | 0.012 | 0.030 |
| N | 0.063 | 0.137 |
| U | 0.137 | 0.376 |

E-origin cells (the ones any scenario arithmetic will lean on)
calibrate to ~1 percentage point. The U-origin cells carry n = 14–19
persons per exact cell (halves of 7–10), and their error is
small-sample noise, not bias; **U-origin rows are indicative only**
until panels are pooled.

## Benchmarks checked

- Weighted in-sample E share at December 2021: **79.2%** (unweighted
  78.9%), against 77.65% for the full prime-age December-2021
  cross-section across all active panels (computed in the verification
  pass; BLS-consistent ~78%). The linked sample is slightly more
  employment-attached than the cross-section — expected for a
  full-span population and quantified below.
- Median December-2021 TPEARN among E|E: **$4,429** vs $4,258 for the
  RMESR==1 cross-section (verification pass). Consistent: E|E span
  survivors are a selected, slightly higher-earning set, and E here is
  broader than RMESR==1.
- Nominal median growth 5.3% vs CPI-U December-2021→December-2022 of
  ~6.5%: a small *real* decline for continuously employed workers —
  plausible for 2022 and exactly why the dollars stay nominal with a
  stated caveat.

## Declared limitations

1. **Span-survivor weighting.** The full-span FINYR2 restriction
   retains 3,206 of 19,045 (16.8%) prime-age December-2021 persons;
   most of the gap is panel rotation structure (later 2021 rotation
   groups cannot be in-universe for the whole 2021 calendar year), the
   rest is attrition and nonresponse. These transitions therefore
   describe the **span-stable population** — the population the
   Census-designed span weight represents — and mildly overstate
   stability relative to a full cross-section (79.2% vs 77.65% E
   share). Using the span weight is the price of Census's own
   longitudinal design; the alternative (cross-section December
   weights on matched pairs) has the same survivor logic with no
   designed weight.
2. **Population coverage.** Linked weights sum to 61.9M, roughly half
   the ~128M prime-age residents: the span-stable half, not the full
   prime-age population.
3. **Nominal dollars.** 2021→2022 comparisons carry the inflation
   caveat above; nothing is deflated to avoid implying a CPI series
   choice the artifact does not make.
4. **Small U-origin cells.** n = 14–19 per exact cell; see
   calibration. Pooling the 2020/2021/2022 panel releases (later R2
   work) roughly triples these cells.
5. **Point-in-time monthly state.** E = any job in the month; a person
   employed part of December counts as E. Coarser than weekly CPS
   measures; declared, and uniform across origins.
6. **Geography.** Public redesigned-SIPP files identify region only.
   National-level artifact.
7. **No separate attrition model.** Inter-wave attrition is absorbed
   by the Census weight construction, not re-modeled here.

## Role in the research plan and reproduction

This is the ordinary baseline that later R2 artifacts contrast
displacement-event cohorts against (same months, same state
definition, same weighting). It does not enter the parameter set.

Reproduce with:

```
uv run python scripts/build_baseline_transitions.py
```

Deterministic (hash-based split, no sampling); inputs and hashes in
`validation/sipp/MANIFEST.json`.
