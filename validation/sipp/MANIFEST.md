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

Pending: none — `validation/sipp/2022/pu2022_schema.json` had been
throttled on 2026-09-13 and was fetched 2026-09-14. The 2023-release
metadata (`lgtwgt2023_dictionary.txt`, `lgtrw2023yr2_schema.json`) and
the 2021 content schema + data-dictionary PDF were added to the
manifest on 2026-09-14.

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
- 2023 release (`datasets/2023/`) — ships files only inside
  `<name>_csv.zip` bundles; the plain `.csv.gz` paths 404.
  `lgtwgt2023yr2.csv` (unpacked from `lgtwgt2023yr2_csv.zip`) is the
  **span weight used by the R2 artifact**: 23,878 persons
  (SPANEL 2022: 13,016; 2020: 5,916; 2021: 4,946), all with FINYR2 > 0,
  a lowercase pipe-delimited header
  (`ssuid|pnum|spanel|finyr2`), covering the January 2021 – December
  2022 span; weights sum to 328.6M ≈ the US resident population, with
  the overlapping panels each carrying a slice of that control total.

## Structural finding recorded for the estimation phase

The redesigned SIPP is a set of **overlapping annual panels** (2014,
2018, 2020, 2021, 2022, ...), and the per-year `pu` files pool every
active panel's interviews for that calendar year. A year-to-year
baseline transition therefore links pu2021 to pu2022 on SSUID+PNUM
within SPANEL, applies the matching `lgtwgt`/`lgtrw` span weight, and
must restrict to each panel's in-survey universe (RIN_UNIV). Panel
attrition is measured as the person-level match rate between the two
files against the longitudinal weight population.
