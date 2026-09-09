# DATA SOURCES — everything the model needs, and the access path for each

Owner directive: use the APIs/pull tooling already in the xh1b
monorepo where they exist; new pulls follow the automation principle
(fully automated download path, no manual steps). Env vars live in
the root `.env`. Status as of 2026-09-06.

## Baseline tables (plan item #1 — unblocks absolute counts)

| # | Baseline (baselines.csv row) | Dataset | Access path | Key | Status |
|:--|:--|:--|:--|:--|:--|
| 1 | all_cause_mortality_annual (US prime-age, 45-54) | CDC WONDER "Underlying Cause of Death, 1999-2020" — deaths + population + crude rate by ten-year age group × gender | **WIRED 2026-09-06**: `scraper.cli wonder-mortality` (keyless machine API; POST `request_xml=` to `https://wonder.cdc.gov/controller/datarequest/D76`, `accept_datause_restrictions=true` as a form field; >=15 s between requests is server-enforced). Endpoint correction: the Underlying Cause database is controller **D76** — **D77 is the MULTIPLE Cause of Death database** (confirmed against CDC's own form pages: ucd-icd10.html links D76, mcd-icd10.html links D77; the earlier D77 probes were answered by the MCD form's validation). Confirmed query parameters: group-by `B_1=D76.V1-level1` (year), `B_2=D76.V5` (ten-year age groups; code `45-54`), `B_3=D76.V7` (gender, `F`/`M`); measures `M_1=D76.M1` deaths, `M_2=D76.M2` population, `M_3=D76.M3` crude rate per 100k; `O_age=D76.V5`, `O_aar=aar_none` + `O_aar_pop=0000` (D76 requires the pop even with adjustment off). First pull: 528 rows 1999-2020 in warehouse table `wonder_mortality` | none (keyless, polite) | table live; baseline pin next |
| 2 | median_male_lifetime_earnings | SSA Annual Statistical Supplement Table 4.B6 (CWHS/Master Earnings File 1% sample) — median earnings by sex × age band | **WIRED 2026-09-06**: `scraper.cli ssa-earnings-download` (Playwright fetch — ssa.gov 403s plain HTTP; editions newest-first, every edition kept). Pinned: male 2023 age profile, synthetic career ages 20-64 = 2,517,175 usd_2023 → **2,591,418 usd_2024** (CPI-U 304.702→313.689, BLS CUUR0000SA0) | none | **verified (v1.4)** |
| 3 | divorce_5y_cumulative | Census P70-125 Table 4 (Kreider & Glick 2012, SIPP 2008 panel) — NCFMR publishes annual rates, not 5-year cumulative probabilities, so the SIPP survival table is the source | **WIRED 2026-09-06**: `scraper.cli census-marriage-download` (keyless PDF). Pinned: 1 − 0.8955 (1995-99 cohort 5th-anniversary survival, men 89.6 / women 89.5) = **0.1045** | none | **verified (v1.5)** |
| 4 | ipv_annual_incidence | BJS Criminal Victimization bulletin (cv24) violent-crime trends table — NCVS intimate-partner-violence rates per 1,000 persons 12+ | **WIRED 2026-09-06**: `scraper.cli bjs-ipv-download` (keyless PDF). Pinned: **0.0027** per person-year (2024; window 1.7/1.7/3.4/2.2/2.7). UNIT CORRECTED: published semantics are per-person, not the placeholder per-household | none | **verified (v1.6)** |
| 5 | youth_crime_participation | OJJDP SBB arrest counts (api.ojp.gov dataset wwuj-iznp — the data behind the JS-rendered SBB FAQ; NCJJ estimates from FBI CIUS) joined with Census popest denominators | **WIRED 2026-09-06**: `scraper.cli ojjdp-arrests-download` + `census-popest-download` (both keyless). Pinned: male 18-24 arrests 908,880 / population 16,245,172 = **0.055948** per person-year (2023; 5,595 per 100k). BRACKET CORRECTED: published brackets give 18-24, not 16-24 | none | **verified (v1.7)** |

## Validation data (plan items #2/#6 — the retrodictions)

| # | Item | Dataset | Access path | Key | Status |
|:--|:--|:--|:--|:--|:--|
| V1-a | CZ import-exposure shock | ADH published instrument + replication files (Dorn's site: dornsife.usc.edu / daviddorn.net ADH data) | direct file fetch (zip of Stata/CSV tables) | none | pending |
| V1-b | measured CZ outcome deltas 1990-2014 | ADH 2019 AEA P&P tables + Autor et al. 2020 AER appendix | transcribe with citations per CITING.md (papers are paywalled; AEA appendices are open) | none | pending |
| V1-c | CZ/county demographic baselines | Census ACS 5-year (population, marriage %, poverty, employment by CZ/county) | Census Data API (`api.census.gov`); CZ crosswalk public (Dorn site / USDA ERS) | **CENSUS_API_KEY** (free, census.gov/developers) — the only NEW env var this subsystem needs | pending |
| V2 | NAFTA / auto-crisis / BRAC exposures | SPECIFIC sources identified 2026-09-09: NAFTA = Hakobyan & McLaren REStat 98(4):728-741 (open NBER w16535; measured wage-growth side, NO displacement bridge — the ADH import-penetration bridge does not transfer to tariff units); auto crisis = BLS national counts (no quasi-experimental local estimate found — honest refusal recorded); BRAC = Hooker & Knetter Economic Inquiry 39(4):583-598 (NBER w6941, scanned — needs GLM-OCR) + GAO-05-138 app. II (open HTML) + RAND MR-667 (open PDF) | fetch: w16535 done (laptop /tmp), w6941 downloaded (needs OCR), GAO HTML direct | none | scaffolded (pre-registered at v1.28; scoring blocked until bridges land) |

## Exposure construction (warehouse — ALREADY AVAILABLE)

| Item | Where it already lives | Notes |
|:--|:--|:--|
| Employer-level certified LCA filings + wage offers + worksite county | xh1b warehouse `lcas` (DOL OFLC, already ingested daily) | the H-1B-side exposure denominator |
| Displacement events (WARN layoffs) | xh1b warehouse `warns` + `displacement_events` (WARN↔LCA match engine already built) | the documented-layoff exposure |
| BLS OES medians by SOC | xh1b warehouse (BLS OES already ingested) | wage-gap inputs; also a fallback earnings baseline if SSA tables resist |
| County FIPS resolution | `lcas.worksite_county_fips` | joins place-level baselines |
| County mobility percentiles + county mortality baselines | place-resolved layer plugs (`params/places.csv`): mobility LANDED v1.30 (Opportunity Atlas `county_outcomes_simple.csv`, raw copy committed under `validation/`; derivation `build_places.py`); mortality from CDC WONDER D76 county query (parent-repo scraper task, queued as #31 — the wonder-mortality CLI is national-only today) | engine (shrinkage + modifier formula) LANDED v1.29; modifier LANDED v1.30 (gamma 0.037, Chetty & Hendren 2018 QJE, read via NBER w23001); county mortality values must be derived in the SAME unit/population as the national baseline rows (per person-year, prime-age) |
| Unconditional early income → child outcomes | Akee et al. 2010 AEJ:Applied 2(1):86-115 via PMC2891175 (author manuscript, open; tables 3/4/6/7/8 extracted) + Duncan et al. 2010 / Ziol-Guest et al. 2012 PNAS via PMC3477379 (observational cross-check only — CITING §1) | engine rows LANDED v1.32 (akee2010 x3); raw PDFs in /tmp (session scratch) |
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
