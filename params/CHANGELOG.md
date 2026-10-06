## v1.49 — 2026-10-07 — enforce mortality baseline compatibility

- Add structured sex, age, time window, cause and geography to the national mortality baseline. County builders and consumers verify observation scope and posterior arithmetic; audits include optional mortality registries. Numeric baseline and parameter estimates are unchanged.

## v1.48 — 2026-09-16 — the receiving-community crime stream lands through the independence gate

- THE CRIME GATE IS EXECUTED AND PASSES. The channel the model's owner
  contested (owner objection: the leading meta-analysis's co-author
  reads as advocacy-adjacent) was closed until three quasi-experimental
  teams with zero UC Irvine ties corroborated the aggregate null, at
  least one with no pro-immigration incentive. Full texts of all four
  panel papers were acquired, hash-pinned into evidence_corpus.csv, and
  table-extracted: Light & Miller (Criminology 56(2):370-401, US state
  FE + IV), Bell/Fasani/Machin (REStat 95(4):1278-1290 PUBLISHED
  version via LSE Research Online; the scan's ReStud venue claim was
  wrong and is corrected), Bianchi/Buonanno/Pinotti (JEEA 10(6):
  1318-1347 via HAL), plus Light/He/Robey (PNAS 117(51)) as descriptive
  context. The panel is not a null-choir: BFM publish the positive
  where identification finds it.
- TWO ROWS LANDED (work-access margin): immigrant_influx->
  receiving_violent_crime_rate -0.12 [-0.18,-0.06] GAP_LOG
  (Light-Miller Table 2 Model 4; IV -0.46 recorded beside; the
  conservative weighted spec -0.05 recorded beside), and
  immigrant_influx->receiving_total_crime_rate +0.105 [-0.262,+0.472]
  GAP_LOG (BBP Table 4 col 3; the band deliberately includes zero —
  the aggregate NULL; OLS +0.156*** collapses under the supply-push
  instrument, so the raw correlation is selection). Both dist normal,
  evidence_role conditional, causal role
  direct_receiving_community_estimate (new — these are NOT displacement
  effects). NEW NODES: immigrant_influx, receiving_violent_crime_rate,
  receiving_total_crime_rate (all gap_multiplier).
- THE STRUCTURAL FINDING the gate surfaced: property crime responds to
  LABOR-MARKET ACCESS, not to immigration as such. BFM's work-banned
  asylum wave RAISES property crime (+1.14 OLS / +1.09 IV per 100
  adults per pp of share; dispersal instrument F=1522) while their
  free-labor-access A8 wave LOWERS it (-0.061** OLS / -0.386*** IV) —
  p(Asylum=A8)=0.001. The banned branch is recorded as findings rows
  (composable_after_baseline_and_time_alignment, fulltext_table) that
  must NEVER merge with the work-access rows; the engine's rows model
  the replacement-scenario margin (workers), not banned populations.
  Light/He/Robey's 2x-4x arrest-rate ratios are recorded as
  context_only_not_a_causal_edge (who-commits rates, not inflow
  effects).
- WHAT A REPLACEMENT SCENARIO NOW ANSWERS: a +10% immigrant influx
  composes to violent crime x1.10^-0.12 = 0.988 (-1.2%) and total
  crime x1.10^0.105 = 1.010 with a band through 1.0 — silence replaced
  by an extracted, independence-gated near-null. Five findings rows
  added; corpus 102 -> 106 verified PDFs (findings 75 -> 80).

## v1.47 — 2026-09-16 — the divorce walk goes live: a conditional-mixture transmission over the entry row's own counterfactual share

- NEW LEDGER KIND `conditional_mixture`: a parent hazard multiplier m
  dissolves share s(m) = 1 − (1−s)^m of marriages over the parent
  step's follow-up window (proportional hazards); the counterfactual
  share s cancels against itself, so the child multiplier is
  1 + (s(m) − s)(t − 1) — only the EXTRA dissolutions transmit. The
  share arrives as a declared aux parameter on the walk step; guards
  refuse a missing aux, an out-of-range share, or a negative parent
  multiplier, and corner min/max keeps bands ordered for protective
  hazards (t < 1).
- NEW ROW: `married_cohort->parental_dissolution_share` 0.069
  [0.069, 0.072] EXACT-results — rege2007 (SSB DP 514) Table 1 + prose,
  the ENTRY row's own source: stable plants 6.9% dissolved by 2003,
  closing plants 7.2%; band = the observed range across plant types.
  Coherence check: at m = 1.11 the kind yields +0.73pp extra
  dissolutions vs the paper's own adjusted +0.78pp (+11%).
- THE DIVORCE WALK IS LIVE (`downstream transmissions --walk divorce`):
  worker 1.11 [1.05, 1.25] → child 1.0064 [1.0019, 1.0213] — an honest
  +0.6% child divorce hazard, small BECAUSE it is a mixture. The walk
  labels its generations explicitly (worker, child): the entry lands on
  the displaced worker's own hazard, not a child outcome. McLanahan &
  Bumpass 1988 (1.88 [1.57, 2.24], landed v1.46) is the transmission
  hazard; gruber2004's churning findings (earlier marriage,
  separation-prone unions) travel beside as the mechanism the mixture
  deliberately does NOT double-count.

## v1.46 — 2026-09-15 — the divorce transmission row: parental disruption walks to child own-divorce (walk blocked on the mixture kind, by design)

- NEW TRANSMISSION ROW: `divorce_hazard->child_divorce_hazard` 1.88
  [1.57, 2.24] EXACT-results — McLanahan & Bumpass 1988 (AJS 94(1):130-152,
  DOI 10.1086/228954; read in full via IRP DP 805-86 with an OCR
  prose↔table cross-check: zero-order exp(.65)=1.92 matches the text's
  "92 percent more likely to experience a marital disruption"; the landed
  band is the background-controlled β 0.63 (SE 0.09) exponentiated).
  BESIDE on the row: education-adjusted 1.67, Black women 1.36,
  widowhood 1.35 — disruption carries the effect, not parent absence.
- EXTRACTION HONESTY: gruber2004 ELIMINATED as the divorce-transmission
  pin (full text via NBER w7968: a unilateral-divorce LAW-exposure ITT
  with "no rise in the odds of being divorced" — earlier marriage +
  churning that fades by middle age); bib VENUE CORRECTED to JOLE
  22(4):799-833, DOI 10.1086/423155 (was mislabeled JPE 112(5)).
- THE WALK STAYS BLOCKED BY DESIGN: the row composes only through a
  conditional/mixture composition kind (only the displaced marriages
  that actually dissolve transmit) — to be designed separately.
  `downstream transmissions` reports the registry state.
- EDUCATION-ENTRY HUNT RECORDED (no row): displacement → child
  educational level is a DOCUMENTED NULL in the best register designs
  (Huttunen & Riukula 2024 Table 2: −0.002 (0.008), N=182,697;
  Oreopoulos et al. 2008 report no education regression; Bratberg et
  al. 2008 regress child earnings only). The education_years walk goes
  live only via a declared probability→years bridge.

## v1.45 — 2026-09-14 — fetal dose-response chain: birth weight walks to adult earnings and disease hazards

- CHAIN ADMITTED: the in-utero cohort chain
  displacement_event -> infant_birth_weight (lindo2011, landed v1.x)
  -> child_earnings / adult_type2_diabetes_hazard /
  adult_cardiovascular_disease_hazard is now composable
  (`CHAIN_KINDS` + causal roles in ledger.py). `gap_log_elastic` is
  chainable for the first time: its dose-response slopes are log-log
  elasticities by construction, and its guard now requires a strictly
  positive BASE while allowing negative exponent bands (protective
  gradients flip the monotonicity; corner arithmetic already covered
  it).
- ROW LANDED: infant_birth_weight->child_earnings 0.10 [0.0216,
  0.1784] EXACT (black2007, QJE 122(1):409-439 via IZA DP 1864 Table 5,
  twin FE on ln(BW), SE 0.04; a ln-ln elasticity by construction:
  +10% BW -> ~+1% adult full-time earnings). Composed on the Lindo BW
  shift: 0.9541^0.10 = 0.9953 -> -0.47% adult earnings — an order of
  magnitude under the childhood-exposure channel (oreopoulos2008,
  -9.24%), and a DIFFERENT population (in-utero vs childhood
  exposure): the rows are never additive.
- ROWS LANDED (medical): infant_birth_weight->adult_type2_diabetes_hazard
  -0.9637 [-1.3834, -0.5401] and
  infant_birth_weight->adult_cardiovascular_disease_hazard -0.6994
  [-0.8173, -0.5850] EXACT (knop2018, JAHA 7(23):e008870, pooled
  random-effects ORs per +1 kg BW: 0.78 [0.70-0.87] and 0.835
  [0.81-0.86], converted to log elasticities on a DECLARED 3.4 kg mean
  BW anchor). Composed: +4.6% T2D odds, +3.3% CVD odds for the
  in-utero cohort. J-shape caveat travels on the rows (downward shifts
  stay on the inverse branch; the high-tail upturn never enters).
- FINDINGS RECORDED (not composable yet, honestly queued):
  bds2007 twin-FE HS completion (+0.95pp per +10% BW; needs a
  probability translation — hs_completion is a probability-LEVEL
  node), bds2007 twin-FE IQ (+0.06 stanine per +10% BW; needs an SD
  translation), bds2007 twin-FE one-year mortality (-41.15 per 1000
  per log BW, SE 7.64 — UNSTABLE across periods/sex-composition and
  needs a baseline node; recorded with the instability traveling
  beside it), royer2009 intergenerational BW (abstract-only: effects
  "generally small"; bounds the generational walk — no offspring-BW
  row may be fabricated without her tables).
- USER QUESTION THAT DROVE THIS: "arent lighter babies more likely to
  have a variety of diseases, earn less" — yes, and now the engine
  carries the identified part of that chain with the double-counting
  scope rule declared on every row.

## v1.44 — 2026-09-14 — generational transmission rows 32-33: achievement and education walk toward grandchildren

- REGISTRY LANDED (prior commit): `src/downstream/transmissions.py` —
  one admitted parent->child relationship per outcome, applied
  recursively; per-step evidence support; audit drift guard on unrolled
  copies; `downstream transmissions [--walk OUTCOME]` renders the map
  and the walks.
- ROW 32 LANDED: child_achievement_sd->grandchild_achievement_sd
  0.38 [0.38, 0.42] EXACT-results (blackdevereuxsalvanes2009, Economics
  Letters 105(1):138-140 via IZA DP 3651: the father-son IQ correlation
  .38; band = the single-measure replications to the Bowles-Gintis 2002
  lower bound; the authors' "no causal interpretation whatsoever"
  caveat travels on the row). New `linear_shift` ledger kind composes
  standardized shifts (unit rule sd_delta->sd_delta). The ACHIEVEMENT
  walk is live: displacement -0.021 SD -> grandchild -0.008 SD.
- ROW 33 TRANSMISSION LANDED: child_education_years->
  grandchild_education_years 0.296 [0.255, 0.337] EXACT-results dist
  normal (lindahl2015 Table 2, SE 0.021, N=1,823, read in full via IZA
  DP 6463; bib upgraded to fulltext). DANGLING UPSTREAM by design: no
  displacement->child_education_years entry yet, so no walk — reported
  as the outcome's remaining gap.
- DOI discipline: a search surface returned a WRONG DOI for BDS 2009
  (resolved to an unrelated paper); caught by Crossref verification and
  pinned as 10.1016/j.econlet.2009.06.022.
- ROWS 34-35 (depression, divorce transmission) stay queued: no
  primary-source-verifiable coefficient at landing time; the divorce
  walk additionally needs a conditional composition kind (only the
  dissolved marriages transmit).

## v1.43 — 2026-09-13 — the six second-sweep studies extracted and landed

- ALL SIX second-sweep candidates read from open full text and landed.
- THREE NEW EXACT rows: displacement_event->spouse_participation_
  elasticity -0.04 [-0.07, -0.03] (halla2020, AEJ:Applied 12(4):253-287
  via IZA DP 11752: the added-worker effect on Austrian registers, band
  = the paper's subgroup range with dist empty; an order below the AWE
  literature's -0.4; extensive-margin only), displacement_event->
  annual_birth_response -0.005 [-0.0089, -0.0011] (huttunenkellokumpi
  2016, JLE 34(2) via IZA DP 6707 Table 3: the displacement-year birth
  probability, ~5% relative; cumulative -4 births per 100 displaced
  women by year 11; career-concern channel, not income; MALE NULL
  declared beside and halla2020's husband null corroborates),
  displacement_event->child_depression_anxiety +0.008 [0.0002, 0.0158]
  (schallerzerpa2019, AJHE via NBER w21745: the CHILD'S own short-run
  mental health, paternal channel; spec sensitivity declared; maternal
  null declared).
- MORTALITY REPLICATIONS as cross-checks: the peak row gains a
  three-country year-1 convergence (eliasonstorrie2009 Swedish HR 1.44
  [1.19, 1.76]; bloemen2018 Dutch +85.8%); the sustained row gains
  Bloemen's declining 5y +33.5% AND the declared ES divergence (NO
  long-run all-cause effect: 5-8y 0.98, 9-12y 0.91) — positions never
  averaged; the B&H circulatory/external rows gain Bloemen's
  circulatory +52.8%/cerebrovascular +152.9% corroboration and the
  declared cause-pattern heterogeneity (Bloemen's external NEGATIVE);
  the rege2007 divorce row gains HSW's order-smaller register estimate
  with its precise-zero mass-layoff-firm control.
- HONESTY ANCHOR: mork2019 (IZA DP 12559, WP-only, canonical cap)
  recorded without a row — register-based child hospitalization/
  mortality NULLS over 10 years; paternal education NULLS; the
  maternal GPA/HS negatives are questioned by the authors' own
  pre-trend analysis.
- units.py: (PERSONS, LOG_ELASTICITY) boundary composition; new nodes
  spouse_participation_elasticity (log_elasticity), annual_birth_
  response and child_depression_anxiety (probability).
- Corrections at extraction: HK's venue is JLE 34(2) 2016 (not Labour
  Economics); ES's search-supplied NBER w12128 attribution was wrong
  (read via GUPEA WP 153 past the repository bot gate); Mörk authors
  corrected (Svaleryd, not Zhuravskaya).

## v1.42 — 2026-09-13 — Brand & Simon Thomas 2014 landed; EB prior-strength yardstick; second research sweep

- brand2014 (AJS 119(4):955-1001, read via PMC4372265 author manuscript
  of the published version; user-directed node design): FOUR EXACT
  conditional rows on new nodes, maternal displacement (US NLSY79
  children of single mothers, PSM kernel TT) —
  displacement_event->hs_completion -0.037 [-0.0801, 0.0061] (p<.10
  declared; the band honestly crosses zero), ->college_attendance
  -0.063 [-0.1081, -0.0179], ->college_completion -0.036 [-0.0674,
  -0.0046], ->adult_depression_cesd +0.025 [0.0034, 0.0466] on a new
  `scale01` unit (0-1 CESD symptom index, NOT a probability). Timing
  gradients travel in row notes: education effects concentrate in
  adolescence (HS 12-17 -0.115**), CESD in middle childhood (+0.047**).
  PSM is declared the weakest identification class in the set on every
  row — corroboration of the education streams, never an anchor.
- units.py: (PERSONS, PROB) and (PERSONS, SCALE01) boundary-applied
  compositions; college_attendance declared a stock, distinct from the
  hilger2016 college_enrollment annual flow — never merged.
- EB PRIOR-STRENGTH YARDSTICK: county_rates.empirical_bayes_prior_
  person_years (method-of-moments; Poisson-noise subtraction) +
  build_county_mortality.py --estimate-prior-k (writes nothing). On the
  committed male export: k ≈ 822 prior person-years (Gamma shape ≈ 4.1,
  noise ≈ 11% of the county spread) vs the DECLARED k = 2000 — the
  declared prior shrinks harder; kept as the shipped conservative
  choice, recorded in docs/DATA_SOURCES.md with the rerun-when-more-
  exports rule (tests/test_county_eb_prior.py pins the arithmetic).
- SECOND RESEARCH SWEEP queued (6 verified candidates): Eliason &
  Storrie 2009 (JHR 44(2) — venue corrected, Sweden), Bloemen,
  Stancanelli & van der Klaauw 2018 (JHE 59, Dutch, year-1 +84%),
  Halla-Schmieder-Weber 2020 (AEJ:Applied 12(4), spousal labor supply +
  divorce), Huttunen & Kellokumpi 2014 (Labour Economics,
  displacement-fertility), Schaller & Zerpa 2019 (AJHE, child health),
  Mörk et al. (Swedish child-health nulls). Open gap recorded: no
  displacement→spouse-MORTALITY study exists in the surfaced
  literature.

## v1.41 — 2026-09-13 — shrunk county mortality baselines in places.csv

- `downstream build-places` (new CLI verb) fills the generated places.csv
  mortality columns in the same pass as mobility, from the committed CDC
  WONDER county export (male 45-54, pooled 2015-2019) via
  county_mortality.parse_export + count_observations and the Gamma-Poisson
  posterior toward the verified national pin 0.004944 with 2000 prior
  person-years: 2,748 county rows at the closed-form posterior mean per
  person-year — the exact unit and population of
  baselines.csv:all_cause_mortality_annual, no conversion anywhere; draws
  are seed-fixed and unused by the plug.
- mortality_n = the county person-years: the precision label whose
  w = n/(n+k) with k = the 2000 prior person-years reproduces the
  posterior's pooling weight; explicitly NOT a binomial denominator (the
  header and every row citation record the choice). The national row
  carries the pin 0.004944 and the export Total person-years (104,024,440);
  the build refuses if the Total misses the pin at its 6-decimal precision.
- Honesty rules kept: the 388 Atlas counties absent from or suppressed in
  the export keep empty mortality columns and fall back to national — never
  reconstructed; the two 2015 FIPS renames outside the Atlas (Kusilvak
  02270, Oglala Lakota 46113) are reported, not forced in; the citation
  header names the WONDER export alongside the Opportunity Atlas; the
  female export stays out (the shipped displacement response is male
  45-54 only).
- The place layer's APPLY path is unchanged: mortality swaps in only via
  the strict params/county_mortality.csv posterior contract (v1.36);
  places.csv now carries the same posterior means as the plug's values.

## v1.40 — 2026-09-13 — Bingley–Cappellari–Ovidi (JEEA 2026) + Schaller–Stevens 2015 landed

- bingley2026 (Journal of the European Economic Association, advance
  article, DOI 10.1093/jeea/jvag048; read via IZA DP 16367, the August
  2023 WP draft of the version of record — marcus2013/damm2014 read-via
  precedent): two EXACT rows on Danish plant-closure children exposed at
  ages 0-16. displacement_event->child_achievement_sd -0.0206 [-0.0402,
  -0.0010] (grade-9 mathematics teacher grades, preferred spec, band =
  1.96 SE; exam test scores -0.0117 n.s. beside; infancy -0.0521
  [-0.0823, -0.0219], late childhood -0.0274 - the paper's timing
  structure travels in notes because the model has no age-at-exposure
  selector), and a new node exam_noncompletion_hazard:
  displacement_event->exam_noncompletion_hazard 1.0688 [1.0014, 1.1362]
  (derived relative on the 7.85% control mean, stevens2011 precedent;
  infancy 1.126 beside; exposure at age >= 18 jointly zero, p = 0.986).
  Both conditional: transport assumes Danish institutions/welfare and
  plant-closure identification.
- INCOME CHANNEL declared, never averaged: the achievement hit
  concentrates in below-median-income families and breadwinner
  displacements; the authors' mediation slope (+0.0008 SD math per
  +1,000 DKK/yr family income) is recorded as a dahl2012 cross-check.
- schallerstevens2015 (J Health Econ 43:190-203, read via the UC Davis
  open PDF of the version of record): cross-check notes on
  unemployment_status->mental_health_sd - fair/poor mental health
  +1.39pp on a 3.4% base (+40.9% relative), depression/anxiety +1.64pp
  on 7.3%; probability units, not SD-convertible. QUEUE CORRECTION: the
  paper is the MEPS health-conditions/insurance study, not a PSID
  mortality-timing paper - it estimates no mortality effects of its own.
- Queue author corrections: Bingley et al. is Bingley, Cappellari &
  Ovidi (not Lundborg), now peer-reviewed via the JEEA advance article.

## v1.39 — 2026-09-13 — machine-readable evidence_role on every parameter row

- parameters.csv gains an evidence_role column classifying all 49 rows per
  the four-status scheme in docs/STUDY_APPLICABILITY_AUDIT_2026-09-13.md:
  18 conditional (direct displacement/loss estimates with named transport
  conditions), 3 structural (IGE transmission x2, Chetty-Hendren same-place
  modifier), 28 boundary (separate input families or associational rows that
  must never start from generic worker displacement). `admitted` is reserved
  for future rows meeting the strict bar; no shipped row claims it yet. The
  four v1.38 rows (Browning & Heinesen cause-specific hazards, Marcus 2013
  spouse mental health) postdate the audit document and are classified
  conditional from their row metadata; fold them into the audit's pathway
  table at its next revision.
- params.load refuses rows with blank or unknown evidence_role: an
  unclassified row cannot state how it may be used, so it is not support.
- ledger.Step publishes evidence_role beside citation/population_scope;
  validate_chain refuses evidence_role=boundary links explicitly; the
  vignette visibly blocks the family-size and daughter-violence streams
  with role-named reasons (audit release gate 4); scenario mortality
  profile steps and the snapshot registry publish the role.

## v1.38 — 2026-09-13 — Browning & Heinesen 2012 + Marcus 2013 landed (full-text extractions)

- browningheinesen2012 (J Health Econ 31(4):599-616, read from the published
  version of record, VIVE-hosted PDF): three EXACT boundary-applied
  cause-specific mortality rows on new nodes —
  displacement->circulatory_mortality_hazard 1.54 [1.29, 1.83] (years 1-4;
  year-1 2.39 [1.62, 3.51]; MI/stroke 1.58 beside),
  displacement->alcohol_mortality_hazard 1.62 [1.09, 2.41] (the
  deaths-of-despair channel; year-1 2.82 wide; 1-20y n.s. — first-years
  concentration declared), displacement->external_cause_mortality_hazard
  1.53 [1.15, 2.04] (suicide year-1 4.31 wide; cancer NULL everywhere —
  cause-specific discipline declared). Population: Danish full-time males
  20-60, plant closures 1986-2002, PSW + duration analysis.
- ALL-CAUSE REPLICATION: B&H year-1 1.84 [1.44, 2.34] and 20-year 1.10
  [1.05, 1.16] (still significant; harvesting rebutted by the authors)
  recorded as cross-checks on the SvW peak (2.67) and sustained (1.135)
  rows — the long-run magnitude replicates nearly exactly across
  jurisdictions 25 years apart.
- marcus2013 (J Health Econ 32(3):546-558, read via SOEPpapers 488 WP
  draft — damm2014 read-via precedent): new node spouse_mental_health_sd;
  displacement_event->spouse_mental_health_sd = -0.194 SD [-0.327, -0.061]
  (spouse MCS -1.94, SE 0.68, ~11 months post-closure); own effect -0.272
  SD recorded as a paul2009 cross-check (inside the causal-clean
  factory-closure subset); own-vs-spouse difference p=0.38 (the spillover
  is as large as the displaced worker's own effect); placebo (closure
  without unemployment) clean.
- Queue corrections: Browning citation fixed (Heinesen's co-author is
  Browning alone on this paper — Danø is on the 2006 stress paper; the
  sweep's title/venue were wrong).

## v1.37 — 2026-09-13 — huttunen2019 cross-check landed; brand2014 numbers pinned

- READ (full text, both):
  - Huttunen & Riukula, IZA DP 12788 (Finland, plant closures 1991-2000):
    child age-30 earnings -575.476 EUR (SE 278.543) on mean 25883.871 =
    -2.2% (males -2.4%; females/mothers null; channel = career/study
    choice, no GPA/crime effects). LANDED as CROSS-CHECK NOTES beside the
    oreopoulos2008 -9.2% anchor on displacement->child_earnings (CITING 4:
    the reported-CI band never shrinks; a working paper is never a
    composed row).
  - Brand & Simon Thomas, AJS 119(4):955-1001 (US SIPP, single mothers,
    PSM): HS completion -0.037 (0.022), college attendance -0.063
    (0.023), college completion -0.036 (0.016), CESD 25-29 +0.025
    (0.011); adolescence timing stronger. Numbers PINNED in
    QUEUED_EXTRACTIONS; not yet a composed row (PSM identification class
    + new-node design are open decisions).
- Queue corrections: sweep author error fixed (the DP is Huttunen &
  Riukula, Finland); Schaller-Stevens and Browning-Dano-Heinesen venue
  details marked unverified until extraction.
- Place layer note: v1.36 county mortality posteriors verified end to end
  (scenario/entity --place, family mobility, audit clean).

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
