# DATA SOURCES — everything the model needs, and the access path for each

Owner directive: use the APIs/pull tooling already in the xh1b
monorepo where they exist; new pulls follow the automation principle
(fully automated download path, no manual steps). Env vars live in
the root `.env`. Status as of 2026-09-06.

## Baseline tables (plan item #1 — unblocks absolute counts)

| # | Baseline (baselines.csv row) | Dataset | Access path | Key | Status |
|:--|:--|:--|:--|:--|:--|
| 1 | all_cause_mortality_annual (US prime-age, 45-54) | CDC WONDER "Underlying Cause of Death, 1999-2020" (database D77) — deaths + population + crude rate by 10-year age group × gender | WONDER machine API: POST to `https://wonder.cdc.gov/controller/datarequest/D77` with `action=params&accept_datause_restrictions=true` + group codes; to become a `wonder-mortality` CLI verb in the monorepo | none (keyless, polite) | **routes tested 2026-09-06**: data.cdc.gov Socrata lacks sex×45-54 detail; cdc.gov PDFs bot-walled; PMC/Bookshelf versions strip tables. WONDER API is the road — build the verb, don't scrape |
| 2 | median_male_lifetime_earnings | SSA Continuous Work History Sample published tables ("Earnings Distribution of the Working Population") | ssa.gov published tables (file fetch + parser); restricted CWH microdata NOT required for a median | none | pending |
| 3 | divorce_5y_cumulative | NCFMR Family Profiles / Census SIPP divorce tables | ncfmr.bgsu.edu profiles (PDF/HTML fetch) or Census SIPP tables via Census API | none / CENSUS_API_KEY optional | pending |
| 4 | ipv_annual_incidence | BJS NCVS *Intimate Partner Violence* annual bullet tables | bjs.ojp.gov published tables (file fetch); NCVS microdata not needed for an incidence rate | none | pending |
| 5 | youth_crime_participation | BJS arrest tables / OJJDP Statistical Briefing Book (arrests per 100k by age) | ojjdp.ojp.gov + FBI CDE (file fetch) | none | pending |

## Validation data (plan items #2/#6 — the retrodictions)

| # | Item | Dataset | Access path | Key | Status |
|:--|:--|:--|:--|:--|:--|
| V1-a | CZ import-exposure shock | ADH published instrument + replication files (Dorn's site: dornsife.usc.edu / daviddorn.net ADH data) | direct file fetch (zip of Stata/CSV tables) | none | pending |
| V1-b | measured CZ outcome deltas 1990-2014 | ADH 2019 AEA P&P tables + Autor et al. 2020 AER appendix | transcribe with citations per CITING.md (papers are paywalled; AEA appendices are open) | none | pending |
| V1-c | CZ/county demographic baselines | Census ACS 5-year (population, marriage %, poverty, employment by CZ/county) | Census Data API (`api.census.gov`); CZ crosswalk public (Dorn site / USDA ERS) | **CENSUS_API_KEY** (free, census.gov/developers) — the only NEW env var this subsystem needs | pending |
| V2 | NAFTA / auto-crisis / BRAC exposures | published replication packages (Hakobyan-McLaren; Autor-Dorn-Hanson 2013 adjacent; GAO BRAC reports) | file fetch per package | none | pending |

## Exposure construction (warehouse — ALREADY AVAILABLE)

| Item | Where it already lives | Notes |
|:--|:--|:--|
| Employer-level certified LCA filings + wage offers + worksite county | xh1b warehouse `lcas` (DOL OFLC, already ingested daily) | the H-1B-side exposure denominator |
| Displacement events (WARN layoffs) | xh1b warehouse `warns` + `displacement_events` (WARN↔LCA match engine already built) | the documented-layoff exposure |
| BLS OES medians by SOC | xh1b warehouse (BLS OES already ingested) | wage-gap inputs; also a fallback earnings baseline if SSA tables resist |
| County FIPS resolution | `lcas.worksite_county_fips` | joins place-level baselines |
| Firm-size/lottery-era crowdout parameters | Doran-Gelber-Isen 2022 (already EXACT in evidence) | parameter-side, not a new pull |

## Access rules

1. New government pulls become monorepo CLI verbs (`<source>-download`
   pattern) with `run_source` provenance — never ad-hoc curl scripts,
   even when a one-off curl works.
2. CDC's surfaces are API-first: WONDER machine API (keyless) for
   mortality; data.cdc.gov Socrata (keyless) as secondary; PDFs are
   bot-walled and NOT the path.
3. The only new credential this subsystem needs is `CENSUS_API_KEY`
   (free registration) for ACS denominators; everything else here is
   keyless.
4. Every pinned baseline lands in `downstream/params/baselines.csv`
   with value + citation + access date, flips `status` to `verified`,
   and turns on its count conversion — the fail-loud gate does the
   bookkeeping.
