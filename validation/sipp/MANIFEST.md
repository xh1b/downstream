# SIPP data manifest — downloaded 2026-09-13

Exact provenance lives in `MANIFEST.json` beside this file: for every
file, its source URL on
`www2.census.gov/programs-surveys/sipp/data/datasets/`, byte size,
sha256, and download date. Raw `.csv.gz` files sit in gitignored
`data/sipp/`; the Census-published metadata (schemas, validation
spreadsheets, dictionaries, input example) is committed here under
`validation/sipp/`, so the pipeline's inputs are reproducible from this
repository alone — anyone can re-download the raw files from the
recorded URLs and verify every hash. Terms: free download, no
registration, redistributable
(`docs/SIPP_BASELINE_DATA_ASSESSMENT_2026-09-13.md`).

Pending as of 2026-09-13: `validation/sipp/2022/pu2022_schema.json`
(the raw pu2022.csv.gz is downloaded and hashed; census.gov throttled
the small schema fetch — re-fetch and regenerate the manifest).

## What the files are (verified by inspection 2026-09-13)

- `pu<YEAR>.csv.gz` — the primary CONTENT file: pipe-delimited,
  **person-month** records (each row = one person in one month), all 12
  months of the calendar year, pooled across the active overlapping
  panels (pu2021 shows SPANEL = 2018, 2020, 2021). 5,214 columns.
  Identification: SSUID+PNUM (person), SSUID+ERESIDENCEID (household);
  ERELRPE (relationship to reference person); ESEX, TAGE, TAGE_EHC
  (monthly age), EEDUC; TPTOTINC (total personal income, monthly),
  TPEARN (earnings); RIN_UNIV (monthly in-survey universe); WPFINWGT
  (weight). Read with the Census schema JSON and the published Python
  example — Census advises column selection; the full file does not fit
  in memory.
- `lgtrw<YEAR>yr<N>.csv.gz` — longitudinal **replicate** weights
  (REPWGT0–240) for panel spans through year N: 31,726 persons
  (SPANEL 2018: 20,817; 2020: 10,909) in the yr2 file, with
  initial_year/final_year eligibility spans and LGTWTTYP.
- `lgtwgt<YEAR>yr<N>.csv.gz` — the plain longitudinal weight per person
  per span (SSUID, PNUM, SPANEL, finyr<N>): 31,726 rows.

## Structural finding recorded for the estimation phase

The redesigned SIPP is a set of **overlapping annual panels** (2014,
2018, 2020, 2021, 2022, ...), and the per-year `pu` files pool every
active panel's interviews for that calendar year. A year-to-year
baseline transition therefore links pu2021 to pu2022 on SSUID+PNUM
within SPANEL, applies the matching `lgtwgt`/`lgtrw` span weight, and
must restrict to each panel's in-survey universe (RIN_UNIV). Panel
attrition is measured as the person-level match rate between the two
files against the longitudinal weight population.
