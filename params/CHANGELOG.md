## v1.36 — 2026-09-13 — county mortality posteriors wired into the place layer

- Extraction #31 COMPLETE: params/county_mortality.csv — 2748 Gamma-Poisson
  county posteriors (male 45-54, All causes, 2015-2019) built by
  scripts/build_county_mortality.py from the validated WONDER county export,
  each row carrying the full provenance chain (events, person-years, declared
  scope/window/citation + the national prior's exact rate/unit/population/
  citation from baselines.csv).
- Prior strength: the repo's declared place.py PRIOR_N convention (2000
  equivalent person-years) — small counties shrink toward the national rate,
  large counties keep their own signal. Empirical-Bayes estimation of the
  prior strength remains open.
- place_baselines now applies county mortality ONLY under the strict
  contract: posterior row present AND prior chain matches the live national
  baseline exactly (rate, unit, population, citation). Any mismatch keeps
  mortality national with the precise refusal reason. The generic
  places.csv rate/precision path stays refused.
- scenario/entity --place FIPS now returns place-resolved excess deaths
  (e.g. Autauga 01001: posterior 0.005920, weight 0.905, excess deaths
  33.61 vs 28.73 national per 1000 workers over 20y).
- parse_export CSV dialect fix (csv.Sniffer mis-parsed quoted county names);
  genuine-export regression tests.

## v1.35 — 2026-09-13 — profile-specific verified mortality rates from a reproducible D76 pull

- ONE live CDC WONDER D76 XML-API pull (2026-09-13, request parameters
  identical to the live-validated 2026-09-06 warehouse query) saved as
  validation/cdc_wonder_d76_national_year_age_sex_1999_2020.xml +
  .provenance.json (sha256 24134d7f…). Reproduces the male 45-54 pooled
  2015-2019 pin EXACTLY (514314 / 104024440 = 494.4 per 100k).
- SEVEN new verified baseline-rate profile rows in
  params/mortality_profiles.csv: female 45-54 (0.003080) plus male/female
  25-34, 35-44, and 55-64 (0.001751/0.000781, 0.002453/0.001397,
  0.011119/0.006696), each with its exact deaths/person-years pool in the
  citation. These are RATE rows only: the shipped Sullivan-von Wachter
  response is admitted for Male 45-54 alone, so the applicability gate
  continues to refuse causal mortality contrasts on every other stratum
  until separately admitted effect profiles exist.
- The all-ages county export stays context_only: the D76 API cannot group
  by county (queued extraction #31 requires the public web export), and
  its unreproducible filters are still the reason it is never a baseline.

## v1.34 — 2026-09-09

Correct mortality node metadata from rate ratio to odds ratio, matching
Sullivan and von Wachter's extracted log-odds coefficients. No empirical
coefficient or band changes. Engine 0.2.0 performs exact odds-to-risk
conversion and finite-horizon survival; legacy counts remain selectable.

## v1.33 — 2026-09-09 — #24 Damm & Dustmann neighborhood conviction-share exposure landed

- #24 LANDED (damm2014, AER 104(6):1806-1832, read via the open Aarhus
  WP 2013-17 Sept-2013 draft; no NBER version exists). Queue target
  CORRECTED: the paper has NO clean exposure-duration elasticity (age
  at assignment is perfectly correlated with potential exposure
  years; the authors warn the age-cohort splits confound duration
  with age) - the landed number is the per-1pp conviction-SHARE
  exposure effect. TWO EXACT rows on the quasi-random refugee
  municipality assignment design (males, N=4,425, avg age at
  assignment 9): youth_crime_conviction_share ->
  youth_crime_convicted 0.061 [0.000, 0.123] per 1pp of the area
  15-25 conviction share (Table 3 spec 5 municipality-FE; conservative
  spec-4 0.033 SE 0.017 + count-of-convictions 0.241/1pp recorded
  beside; the band's lower edge rounds to 0.000, declared not
  massaged), youth_violent_crime_conviction_share ->
  youth_crime_convicted 0.366 [0.143, 0.589] per 1pp of the VIOLENT
  conviction share (Table 5 spec 5; mean 0.286% thin level; spec-4
  0.276 SE 0.089 beside).
- Operative-channel discipline declared: the COMMITTED-crime rate is
  a NULL (Table 6) - only the share of CONVICTED YOUTH moves
  children; property/drug shares null (Table 5); FEMALE NULL (panel
  B); co-national peer channel recorded (Table 7, social interaction
  via co-nationals). New PERCENT level unit token + (PERCENT, PROB)
  boundary 'rate' composition; both share nodes registered as entry
  nodes. damm2014 bib upgraded canonical -> fulltext-table.
- Parameter set 42 rows; version pins bumped across the suite.

## v1.32 — 2026-09-09 — #25 Akee casino quasi-experiment landed + #9 Duncan refusal

- #25 LANDED (akee2010, AEJ:Applied 2(1):86-115, read via PMC2891175
  author manuscript): THREE EXACT rows on the casino-transfer
  quasi-experiment (Eastern Band of Cherokee, ~$4k/yr per adult,
  Great Smoky Mountains Study children) - education years at age 21
  +1.127 [0.247, 2.007] (T4 col 1, PREVIOUSLY-POOR households; the
  full-sample 0.379 ns and never-poor nulls recorded, so no surface
  quotes the pooled number), any-crime 16-17 -0.224 [-0.377, -0.071]
  (T6 col 1) and ever-minor by 21 -0.179 [-0.353, -0.005] (T6 col 4).
  Age-window discipline (minors-only; 18+ nulls), entry-not-count
  discipline (crime counts n.s.), mother-receipt driver, and the
  income-not-employment mechanism (parental labor participation
  null, supervision/activities significant) all declared on the rows.
- #9 REFUSED: Duncan, Ziol-Guest & Kalil 2010 is observational OLS on
  PSID - barred from a parameter point by CITING SS1 (the thornton1980
  precedent). Bib'd with the verified zg2012 companion magnitudes
  (Prenatal-2 income +$10k/y among <$25k families -> ln adult earnings
  +0.63 (SE 0.21), recorded as the cross-check note on the akee2010
  education row); SPEC SS13 carries the refusal. The causal slot is
  filled by akee2010.
- Units: EDU_YEARS token + (USD, EDU_YEARS)/(USD, PROB) boundary
  'rate' compositions; unconditional_income is an entry node.
- 419 tests green; audit 0 errors; export v1.32 = 40 params.

## v1.31 — 2026-09-09 — #7 integration: place layer wired into the vignette + scenario surfaces

- `vignette standard_family` and `scenario compute_counts` accept
  `places` + `place_key`: the baseline dict swaps for the SHRUNK
  county baselines (same unit/population — no conversion) and the
  Chetty-Hendren mobility modifier composes with the child-earnings
  chain as a derived, tier="derived" parameter built per place
  (never a new estimate).
- COMPOSITION SEMANTICS declared: the modifier applies at EACH
  generation's adult outcome (each generation grows up in the same
  county), so it composes AROUND the IGE steps, not once at the end.
- TRAP FIRED on the loss-share arithmetic: the scenario child-dollar
  count uses the LOSS share (1 - child_gap), so a below-mobility
  county SHRINKS the retained share and AMPLIFIES the dollar loss
  ((1 - m*gap)/(1 - gap) — 3.49x for the synthetic Philly trap; the
  naive "count x multiplier" expectation was wrong and is now pinned
  as the regression trap with the derivation in the comment).
- Blocked/absent modifiers leave every number unchanged (back-compat
  pinned); unknown place keys fail loudly; CLI `family`/`scenario`
  gained `--place KEY` (SystemExit when places.csv is absent).
- 401 tests green; audit 0 errors; export v1.31 = 37 params.

## v1.30 — 2026-09-09 — #23 + #30: Chetty-Hendren modifier landed + places.csv plug built

- #23 LANDED: `neighborhood_exposure->child_outcomes_modifier` =
  gamma 0.037 [0.031, 0.043] EXACT (Chetty & Hendren 2018 QJE 133(3),
  Appendix Table V col 1 — the COUNTY-level estimate, N=595,244;
  Table II col 1 CZ baseline 0.040 SE 0.002 recorded beside). Unit
  quoted verbatim: the increase in a child's adult income rank per
  ADDITIONAL YEAR of childhood in a county where children of
  permanent residents rank 1 percentile higher at a given parental
  income. dist=normal (reported CI = 1.96 SE). Robustness beside:
  family FE 0.033 (0.011), time-varying 0.032 (0.011), age-orthogonal
  0.036 (0.005); exposure linear to age 23, flat after.
- place.py formula refined BEFORE the row landed (the freeze rule
  guards against post-data drift): multiplier = 1 + (DOSE_YEARS/100) *
  gamma * (place_pct - national_pct), reference = the places.csv
  NATIONAL row (count-weighted mean kfr = 40.7679), never a hard-coded
  50. DOSE_YEARS = 18 declared (the model's child window; the paper's
  window runs to age 23 — difference declared). Traps caught a
  double-counted gamma in the band arithmetic during the rewrite.
- #30 LANDED: build_places.py (CLI `downstream build-places`) derives
  params/places.csv from the Opportunity Atlas county_outcomes_simple
  (3,134 US counties + DC; skips missing-kfr/zero-count/territories,
  reported). Raw sources committed under validation/. mobility_
  percentile = kfr_pooled_pooled_p25 x 100 — the exposure effect's own
  treatment scale, NOT the county's rank among counties.
- #31 (county WONDER mortality) stays a parent-repo scraper task —
  handoff recorded.
- The modifier composes MULTIPLICATIVELY with the child-earnings
  chain (declared modeling assumption, on the row and in place.py);
  integration into vignette/scenario surfaces is the next slice.
- 393 tests green; audit 0 errors; export v1.30 = 37 params.

## v1.29 — 2026-09-09 — #7: place-resolved layer (shrinkage + mobility modifier, plugs pending)

- place.py: the engine's place-resolved layer. County baselines swap
  into the national values with empirical-Bayes shrinkage toward the
  national mean, w = n/(n+k) (declared prior n per outcome, module
  constant PRIOR_N; formula pinned, k is a modeling choice documented
  in the docstring). No silent unit conversions: a county value must
  be in the SAME unit and population as the national baseline it
  replaces (declared in the row's citation; the note in the swapped
  row says so).
- Missing anything (no file, no row, no precision n, no declared k)
  falls back to the national value with the exact reason stated —
  never a fabricated pool.
- Mobility modifier (Chetty & Hendren 2018, QJE 133(3):1163): formula
  frozen now — multiplier = 1 + (mobility_percentile - 50)/100 *
  param.point, band direction follows the gap sign, gap=0 -> exactly
  1. The parameter row `neighborhood_exposure->child_outcomes_modifier`
  is NOT extracted yet; the modifier reports `blocked` naming the
  link until it lands. Extraction queued.
- Audit: places.csv rows need citations; the national row is required
  when the file exists; a rate without its precision n is a WARN (the
  outcome stays national); the unextracted modifier link is a WARN.
- CLI verb `place --key <fips|national>` prints the CLI-ready shrunk
  baselines + modifier with provenance.
- traps caught: the CLI place path would have crashed on Baseline
  dataclass leakage into JSON (place_json fixes it); a loader crash on
  miscounted CSV columns fails loudly (correct behavior — the trap CSV
  was malformed).
- 375 tests green.

## v1.28 — 2026-09-09 — #6: V2 back-test framework, PRE-REGISTERED (sources pending)

- validate.py gains the V2 registry: three held-out events (NAFTA 1990-2000,
  2008-09 auto crisis, BRAC 1988-95 closures) with outcome definitions and
  scoring rules frozen in code BEFORE any event data lands (the
  clinical-trials rule); trap tests pin the registry so definitions cannot
  drift after a bridge arrives.
- Scored streams pre-registered: excess_deaths_per100k (S&vW sustained+peak),
  additional_divorces_per100k_women (rege2007/charles2004 + census baseline),
  local_service_jobs_per_displaced (Moretti-shape level ratio). Same verdicts
  as V1 (coverage both directions, no tuning, misses publish) with
  across-shock stability reported on the SAME frozen parameter set.
- v2_backtest(event) blocks BY DESIGN until both files exist per event
  (exposure bridge + measured coefficients, transcribed with citations);
  the blocked dict names the missing plugs. No fabrication.
- 2026-09-09 source sweep recorded: NONE of the three events carries a
  published displacement-count bridge (V1 had ADH's own Table 1). NAFTA
  (Hakobyan & McLaren, REStat 98(4):728-741; open NBER w16535) measures
  wage growth, not displacement counts, and the ADH import-penetration
  bridge does not transfer to tariff units. Auto crisis: BLS national
  counts only; no quasi-experimental local estimate surfaced (honest
  refusal recorded). BRAC: measured side identified — Hooker & Knetter
  (Economic Inquiry 39(4):583-598, 2001; NBER w6941, scanned -> needs OCR;
  RAND MR-667 open PDF as cross-checks); bridge = GAO-05-138 app. II
  transcription (open).
- 351 tests green; audit 0 errors.

## v1.27 — 2026-09-09 — #5: per-parameter distributions + first citable correlations

- parameters.csv gains a `dist` column. Twenty rows whose band is a reported
  95% CI now declare the shape that CI implies: `normal` (17 rows — band =
  point +/- 1.96 SE in linear space) and `lognormal` (3 rows — band =
  exp(beta +/- 1.96 SE)). Rows with DECLARED bands (rounding bands,
  cross-study spreads, evidence-widened bands) declare NOTHING: flat-in-band
  is the only honest shape when the paper reports no standard error.
- Sampling centers on the reported POINT, truncated at the band (a rounded
  CI like paul2009's [0.47, 0.54] has midpoint 0.505 != point 0.51; the
  point is the published estimate). Unknown dist tokens now FAIL LOUDLY
  (was: silent uniform fallback — caught by the v1.27 traps).
- New audit checks: declared-dist token validity, positive band edges for
  log shapes, point-vs-band asymmetry flagged as a WARN (assembled-band
  smell, with rounding epsilon).
- First citable rank correlations land via params/correlations.csv (the
  queued candidate: shock depth vs mortality response):
  displacement->worker_earnings <-> earnings_shock->mortality_peak/-sustained,
  spearman -0.5, direction citable (Sullivan & von Wachter 2009 bad-case
  calibration + the Davis & von Wachter 2011 smaller-in-normal-times caveat
  recorded in both rows' scope notes), magnitude DECLARED (no reported
  sampling covariance). mc.simulate loads correlations.csv by default,
  applies Iman-Conover (marginals preserved exactly), and stamps the
  sampler `lhs+iman-conover`; `use_declared_correlations=False` gives raw LHS.
- Stale v1.8-era pins updated: aizer row now samples `normal` (CI shape,
  still linear space — the never-log-space property stands), CSV field
  count 10 -> 11.
- 340 tests green; audit 0 errors; export v1.27 = 36 params.

## v1.26 — 2026-09-09 — queue #15 landed: import competition -> radical vote (colantone2018)

- One row (EXACT, 2SLS): import_shock->radical_right_vote_share 13.2 [3.2, 23.2] pp per $1k/worker
  exposure (IV Table 1 col 10: .132*** (SE .051) in vote-share fractions per 2-year $1k/worker
  shock; authors' 1-SD scaling = +1.7pp on a 5% mean RR share; IV > OLS .041 — demand-shock
  attenuation per the authors; first-stage F = 19.2, US-imports instrument).
- NO-LEFT-WING discipline on record: protectionist left NULL, protectionist left proper NULL,
  liberal right NULL — no polarization (declared contrast with the autor2020 US finding);
  pro-trade left negative significant (-.134**) — abandonment of social-democratic parties;
  protectionist right positive .278***.
- Individual-level (ESS waves 1-4): confirms; response is SOCIOTROPIC — no significant group
  heterogeneity (declared, cross-referenced against paul2009's person-level distress).
- Window discipline declared: 2-year-window coefficient stored per $1k cumulative exposure.
- New node: radical_right_vote_share (percent_delta, mirroring gop_win_probability).
- colantone2018 bib upgraded to fulltext-table; staging doi (SSRN preprint) replaced with the
  published AJPS doi 10.1111/ajps.12358.

## v1.25 — 2026-09-09 — queue #20 landed: unemployment -> mental health (paul2009)

- One row (EXACT, the CITING meta class): unemployment_status->mental_health_sd 0.51 [0.47, 0.54]
  (cross-sectional random-effects meta, outliers excluded, k=315, N=209,379; all-studies 0.54
  [0.50, 0.57] beside). Band = reported CI.
- Causality anchors recorded, never averaged: factory-closure natural experiments d=0.38 [0.25, 0.51]
  (k=27); longitudinal job loss 0.19 / reemployment 0.35, retest-corrected 0.25/0.29; selection effects
  small (0.23/0.15/0.08) and declared as running the other way.
- Moderators scope-declared: men and blue-collar stronger; duration peaks at 9 months (d=0.73), the
  post-29-month worsening UNSTABLE (k=5) — not landed; age U-shape unstable — not landed; country
  moderators recorded (low-GDP .62 vs .49, Gini .57 vs .48, weak protection .58 vs .46, Gini/protection
  confounded per the authors).
- New nodes: unemployment_status, mental_health_sd (sd_delta). PARALLEL stream, never chained.
- paul2009 bib entry upgraded to fulltext-table (owner-downloaded ScienceDirect PDF read in full).

## v1.24 — 2026-09-09 — queue #22 landed: recessions -> IPV (schneider2016)

- Three rows (EXACT-results, area-level shock + household-level distress) onto the household_ipv node:
  local_unemp_shock->household_ipv 1.58 [1.49, 1.58] per UR doubling (Table 3 logit .454*, LDV .401*, FE .406*;
  the band is the exp() spec range; the point is Model 1, the paper's headline spec);
  household_hardship->household_ipv 2.14 [1.61, 2.68] (Model 1 prevalence 15% vs 7%; +/-25% rounding band — the
  Table 1 coefficients are scrambled by text extraction and are recorded beside, NOT used for the band);
  couple_unemployment->household_ipv 1.30 [1.04, 1.63] (13% vs 10%; logit .404**, FE magnitude unchanged).
- LEVEL-NULL discipline on record: the UR LEVEL is null on all three outcomes — only the 12-month CHANGE moves
  abuse; violent-only is null for both unemployment measures; hardship->violent is the authors' reverse-causality
  concern.
- New nodes: local_unemp_shock, household_hardship, couple_unemployment (all rate_ratio); new boundary
  composition rule (RATE_RATIO, RATE_RATIO) = "rate" (per-unit shock multiplier, raphael-style, never chained).
- PARALLEL stream: all three rows are boundary-applied, declared never-chained.
- schneider2016 bib entry (Demography 53(2):471-505, owner-downloaded PDF read in full).

## v1.23 — 2026-09-09 — queue #21 landed: IPV exposure -> child mental health (evans2008)

- Two rows (EXACT, random-effects meta, CITING section 1 meta class): household_ipv->child_internalizing_sd
  0.48 [0.39, 0.57] (k=58, N=7,602, homogeneous) and household_ipv->child_externalizing_sd 0.47 [0.38, 0.56]
  (k=53, N=7,200, heterogeneous; boys .46 vs girls .23 declared).
- TRAUMA REFUSAL: d = 1.54 NOT landed (k=6, heterogeneous — the authors' own caution).
- Cross-checks recorded, never averaged: kitzmann2003 (-.50/-.43), wolfe2003 (.38/.42).
- New nodes: child_internalizing_sd, child_externalizing_sd (sd_delta); new composition rule
  (RATE_RATIO, SD_DELTA) = "rate" — boundary coefficient like dahl2012.
- evans2008 bib entry upgraded canonical -> fulltext-table (accepted manuscript read via the
  Nebraska DigitalCommons permission copy; Wayback mirror of the WAF-blocked PDF CGI).
- household_ipv node description de-staled (aizer2010 upstream landed v1.8).

## v1.22 — 2026-09-09 — queue #18 landed: foreclosure price spillover (campbell2011)

- New row: `foreclosure_order->house_price_gap` 0.99 [0.9875, 0.9925] EXACT-results — the
  authors' preferred estimate (each foreclosure ~0.05mi away lowers the price of a house by
  about 1%, lead-vs-lag DiD; zero distance -2%), stored as a gap multiplier; band = rounding
  band (no SE reported on the DiD) with the SE-carrying hedonic associates recorded beside,
  not averaged in (-1.8% / -1.1% per foreclosure within 0.25mi; 0.1mi zero-distance -9.1% /
  -7.3% clustering-inflated).
- New nodes: `foreclosure_order` (persons), `house_price_gap` (gap_multiplier) — PARALLEL
  stream, boundary-applied, never composed into the earnings/child chains (housing-contagion
  composition is a queued P3 item).
- QUEUE TARGET CORRECTED: venue is AER 101(5):2108-31, not QJE 126; Immergluck & Smith 2006
  (Housing Studies) is their crime paper — the price study is the 2005 Woodstock report /
  Housing Policy Debate (unread; recorded as a cross-check lead).
- IDENTIFICATION LIMIT declared (authors' own statement): no instrument; estimates are not
  structural — tier EXACT-results (read via NBER w14866 April 2009 draft; published AER
  abstract confirms the preferred estimate and the 27% discount).

## v1.21 — Collinson et al. 2024 eviction stream, queue #17 (2026-09-09)

- QUEUE TARGET CORRECTED: #17 named the Collinson & Reed 2018 WP; the
  version of record is Collinson, Humphries, Mader, Reed, Tannenbaum &
  van Dijk, "Eviction and Poverty in American Cities," QJE 139(1):57-120
  (doi 10.1093/qje/qjad042), which subsumes that WP. Read via NBER
  w30382 (rev. July 2023, post-acceptance). Crossref-verified.
- New rows (both EXACT, judge-leniency IV, Cook County + NYC):
  `eviction_order->emergency_shelter_use` 4.778 [1.076, 8.480] — year-1
  IV +3.4pp on the 0.9% base (Table V col 3); year-2 shelter null,
  homelessness-services contact persists (+3.6pp, SE 1.5).
  `eviction_order->eviction_earnings_response` -$613/quarter [-1,099,
  -127] 2016 USD — year-2 (Q5-8) IV on the $4,300 base; year-1 -$323
  (SE 175) ns recorded; female (-$767) / Black (-$931) concentration
  noted, equality not formally rejected.
- REFUSAL (SPEC §10): desmond2016 matched +11-22pp job-loss estimate is
  NOT encoded — matching-on-observables class (CITING §1) cannot set a
  point, and collinson2024 refutes the size (employment IV -1.5pp /
  -1.8pp, both ns). The eviction stream starts at three nodes
  (eviction_order, emergency_shelter_use, eviction_earnings_response);
  no rent-burden upstream producer yet (queued).

## v1.20 — Stevens & Schaller 2011, queue #12 (2026-09-08)

- New row `displacement->grade_retention_hazard` 1.1473 [1.012, 1.283]
  EXACT (stevens2011, Table 4 col 1 child-FE): head's involuntary job
  loss one or more years prior raises grade repetition by 0.8pp on the
  0.055 sample average (~15% relative); multiplier = 1 + 0.0081/0.055,
  band from 1.96SE scaled by the same base. Read via NBER w15480.
- QUEUE TARGET CORRECTED: #12 said "math/reading effect sizes" — the
  paper has no test scores; the outcome is grade retention, the
  authors' own proxy for academic difficulties. New node
  `grade_retention_hazard` (rate_ratio) is a PARALLEL stream: never
  composed with child_achievement_sd (dahl2012) or the earnings-gap
  multiplier.
- VENUE CORRECTED: version of record is Economics of Education Review
  30(2):289-299 (Crossref-verified); the queue and prior bib said
  Sociology of Education 84(3):201-223 — no such Crossref record
  exists. Bib evidence upgraded canonical -> fulltext-table.
- Bonus cross-check: Table 3 family income −10.9% (SE 2.8pp) 1+ years
  after loss recorded as a note on the hilger2016 short-run income row
  (values unchanged).
- BIB HYGIENE: three stale duplicate entries (dahl2012, hilger2016,
  raphael2001 — pre-upgrade canonical copies shadowed by the later
  fulltext-table entries under last-write-wins parsing) removed.
  Current behavior unchanged; the silent-downgrade trap is gone.

## v1.19 — closure-selection ensemble variant (2026-09-08)

- No parameter VALUES changed. The V2 item queued at v1.13 landed:
  `closure_selection_contrast` joins the structural-variant ensemble
  (variants.py). It sets the direct child anchor (oreopoulos2008, a
  firm-closure design) aside and stands the children line on the JLS
  father-shock path composed through the SAME cited IGE band — the
  design contrast Hilger 2016 fn31 forces. Full fn31 text read from
  the published copy: Hilger's closure-DD is wrong-signed and not
  significant (his Table 4), which he reads as assortative matching of
  workers and firms on unobservables correlated with children's
  outcomes; fn31 names Oreopoulos, Page & Stevens (2005, 2008) as
  "the most directly related example" of closure designs yielding
  "surprisingly large estimates" against cross-sectional benchmarks.
- Variant state: child gap 0.89 [0.85, 0.94] vs baseline 0.9076
  [0.844, 0.976]; grandchild 0.9395 [0.91, 0.976]. The composed band
  sits INSIDE the direct band (reconciliation within the evidence).
  Direction pinned: dropping the closure anchor moves the modeled
  child loss UP — the critique does not imply smaller losses under
  current evidence. Ensemble spread: child [0.8376, 0.9076],
  grandchild [0.9107, 0.9623].

## v1.18 — Thornton 1980 cross-check notes (2026-09-08)

- No parameter VALUES changed; no new row. Thornton 1980 (Population
  and Environment 3(1):51-72, DOI 10.1007/bf01253070, Crossref-verified;
  full text read, page-1 title confirmed) landed as CROSS-CHECK NOTES
  on the male_earnings->marital_fertility row, per the Behrman &
  Taubman precedent: PSID two-generation OLS is observational, and
  CITING §1 allows only quasi-experimental designs to set points.
- Findings recorded on the row: ACTUAL parental family size transmits
  near-null (siblings-of-husband -> total expected fertility: zero-
  order .070, standardized .058 with education controls, ns; parity
  sign-inconsistent across 1972/1974); IDEAL family size (preferences)
  transmits strongly (.282* zero-order, .237* controlled; text
  unstandardized: +1 parental ideal child -> child ideal +0.15,
  expected +0.08); parental economic status correlates negatively
  with child parity, attenuated by education controls.
- This note is the recorded reason the model carries NO cross-
  generation fertility multiplier.

## v1.17 — spillover wired into V1 (2026-09-08)

- No parameter VALUES changed. The v1.12 spillover row
  (import_shock->non_displaced_wage_spillover, adh2013) is now COMPOSED
  into the V1 panel earnings row (validate.v1_panel), the open wiring
  left by v1.12. Four tercile rows now publish:
  - direct-only p25 row RETAINED unchanged (miss −$73.59 [−91.99, −55.19]
    vs measured −$352.73) — misses publish, not overwritten;
  - composed row (direct + spillover, applied to the non-displaced
    share, exact exp conversion): −$165.31 [−237.03, −93.24] — closes
    32.9% of the point-gap, measured still outside the band (residual
    undershoot published);
  - new aggregate cross-check: implied TOTAL male wage response
    −1.408 [−2.019, −0.794] log pts per $1k/worker vs ADH 2013 T6 col 2
    −0.892 (SE 0.294) — model point inside the measured CI AND measured
    inside the model band. The residual p25 undershoot is therefore
    distributional (bottom-quartile concentration), not aggregate.
- Spillover units need no pp conversion: the coefficient is per
  $1k/worker, the panel exposure's native unit.

## v1.10 (2026-09-07)
- NEW displacement->infant_birth_weight (EXACT, lindo2011): queue #13 landed.
  Level multiplier 0.954 [0.912, 0.998] from Table 2 col 3 (log birth weight
  -0.047, SE 0.023, mother fixed effects; read via IZA DP 5213). Bib entry
  CORRECTED: it previously cited Lindo's unemployment-insurance paper (JHE
  30:1120-1131) instead of Parental Job Loss and Infant Health (JHE 30:869-879).

## v1.9 (2026-09-07)
- Sullivan & von Wachter 2009 mortality rows pinned from the tables (queue #6 /
  plan #4 head): full text read from the NBER WP version (w13626; tables of the
  QJE article). Table 5 col 2 (born 1930-59 main sample): sustained (year 6+)
  log-odds 0.127 (SE 0.048) -> OR 1.135 [1.033, 1.247]; peak (displacement
  year) log-odds 0.983 (SE 0.119) -> OR 2.672 [2.116, 3.374]. Both rows now
  tier EXACT. The table-fitted bands are WIDER than the prior abstract-derived
  ones (honest widening per CITING 3); the peak point is materially higher
  (the immediate spike at low baseline hazard). OR~RR conversion declared.
  V1 effect: the mortality model band widens so the measured ADH differential
  now sits INSIDE the band (evidence-driven verdict flip, documented); the
  point still overshoots.

## v1.8 (2026-09-07)
- NEW wage_ratio->household_ipv (EXACT-results, aizer2010): elasticity of ln(IPV)
  w.r.t. female/male wage ratio, -0.813 [CI -1.45, -0.18], AER Table 2 col 3 read
  from full text. First producer for household_ipv (queue #3 landed). Node
  wage_ratio added. Sign recorded honestly: male displacement lowers IPV against
  women via the relative-wage channel; daughter-chain composition deliberately
  deferred (needs incidence weights).
- autor2019 bib corrected (was miscited as AEA P&P 109; actually AER: Insights
  1(2):161-178) and upgraded to fulltext; Tables 4-8 transcribed to
  validation/adh2019_measured_coefficients.csv (11 V1 targets).
# Parameter set changelog

Semantics: a new parameter-set version is REQUIRED whenever a value,
band, tier, or sampling methodology changes. Old versions stay
queryable in git; published outputs stamp the version they used.

## v1.7 — all five baselines verified (2026-09-06)

- `youth_crime_participation` flipped pending -> **verified**:
  0.055948 arrests per person-year, US men 18-24, 2023 (OJJDP SBB
  arrest counts joined with Census population denominators, both via
  new keyless verbs `ojjdp-arrests-download` + `census-popest-download`;
  warehouse `ojjdp_arrests` 4,185 rows + `census_popest_agesex` 1,818
  rows). BRACKET CORRECTION documented: published brackets give 18-24,
  not the placeholder 16-24.
- **baselines.csv is now fully verified** — every count conversion the
  engine grows will land on cited absolute numbers.

## v1.6 — fourth baseline pinned (2026-09-06)

- `ipv_annual_incidence` flipped pending -> **verified**: 0.0027
  victimizations per person-year (BJS Criminal Victimization 2024
  bulletin, NCVS intimate-partner-violence rate 2.7 per 1,000 persons
  age 12+, 2024; warehouse `bjs_ncvs_victimization`, 10 rows via the
  new `bjs-ipv-download` verb). UNIT CORRECTION: the placeholder row
  declared a per-household rate; the pinned semantics follow the
  published per-person measure (documented in the row). No count
  conversion consumes it yet.
- One baseline remains pending: youth_crime_participation.

## v1.5 — third baseline pinned (2026-09-06)

- `divorce_5y_cumulative` flipped pending -> **verified**: 0.1045
  probability a first marriage ends within 5 years (Census P70-125
  Table 4, SIPP 2008 panel, 1995-1999 marriage cohort: 89.6/89.5
  percent of men's/women's first marriages reached the 5th anniversary;
  warehouse `census_marriage_survival`, 128 rows via the new
  `census-marriage-download` verb). No count conversion consumes it
  yet — the family-stream module stays a relative rate ratio until its
  absolute-count conversion is built.

## v1.4 — second baseline pinned (2026-09-06)

- `median_male_lifetime_earnings` flipped pending -> **verified**:
  2,591,418 usd_2024, US male median lifetime earnings (SSA Annual
  Statistical Supplement 2025 Table 4.B6, male 2023 medians by age,
  synthetic career ages 20-64 = 2,517,175 usd_2023, CPI-U-deflated to
  2024 dollars; warehouse `ssa_median_earnings`, 1,845 rows via the new
  `ssa-earnings-download` verb). Unlocks the child-earnings dollar
  conversion in `scenario.py`.
- Remaining pending baselines: divorce_5y_cumulative,
  ipv_annual_incidence, youth_crime_participation.
- No parameter bands or link values changed.

## v1.3 — first baseline pinned (2026-09-06)

- `all_cause_mortality_annual` flipped pending -> **verified**:
  0.004944 deaths per person-year, US prime-age men 45-54
  (CDC WONDER D76, Male 45-54 years, pooled 2015-2019 =
  514,314 / 104,024,440 = 494.4 per 100k; pulled via the new
  `wonder-mortality` warehouse verb, 528 rows 1999-2020).
  Unlocks the excess-deaths count conversion in `scenario.py`.
  The other four baselines stay pending (fail-loud gates hold).
- No parameter bands or link values changed.

## v1.2 — uncertainty methodology upgrade (2026-09-06)

- Monte Carlo switched from IID-uniform to **Latin Hypercube
  Sampling** (McKay, Beckman & Conover 1979).
- Positive ratio parameters (rate ratios, odds ratios, level ratios)
  now sample in **log space** by default — linear sampling of a ratio
  is biased toward the top of its band.
- **Rank-correlation induction** (Iman & Conover 1982) added; the
  declared correlation matrix ships EMPTY (params/correlations.csv).
  Correlations enter only with a citation.
- New layers: Sobol global sensitivity (`sensitivity.py`), proper
  scoring rules (`scoring.py`), the explanation/rendering contract
  (`explanation.py`, `render.py`).
- No parameter VALUES changed in this version; every output range
  shifts because the sampler changed.

## v1.1 — anchor read (2026-09-06)

- `displacement->worker_earnings` band widened to [0.75, 0.85] per
  the Davis & von Wachter 2011 full-text synthesis (15-20% below
  controls at 20 years; cross-study spread rule, CITING.md §3.2).
- Mortality rows carry full-text confirmation (near-term up to +100%,
  1-1.5 life-years) and the bad-case scope caveat.
- `davis2011` evidence class `results`.

## v1.0 — engine (2026-09-06)

- First full parameter set: 13 cited rows across worker / children /
  family / community streams.
- Gap-space composition for IGE links (fixes the v0 level-product
  bug), Moretti level-ratio corrected, divorce parameter corrected to
  Rege, Telle & Votruba 2007 DP514 (+11%).
