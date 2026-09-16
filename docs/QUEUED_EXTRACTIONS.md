# QUEUED EXTRACTIONS

Structure exists in the model; the NUMBER is pending a full-text
extraction pass. Each row names the study, the exact target, and the
priority. When a row lands: add the parameter row (tiered per
CITING.md), delete the queue entry, keep the bib entry.

Priority: P1 = blocks a shipped surface (counts, vignette streams);
P2 = completes a stream; P3 = breadth.

## P1 — unblock counts

| # | Link | Study | Extraction target | Status |
|:--|:--|:--|:--|:--|
| 1 | baseline: all-cause mortality | CDC WONDER D76 | LANDED 2026-09-06 (pre-dating this queue's last pass): baselines.csv all_cause_mortality_annual = 0.004944/person-yr verified (men 45-54, pooled 2015-2019, pre-pandemic window, population matched to the S&vW prime-age counterfactual) | done 2026-09-07 |
| 2 | baseline: median male lifetime earnings | SSA CWHS Table 4.B6 | LANDED 2026-09-06: baselines.csv median_male_lifetime_earnings = $2,591,418 (usd_2024) verified, synthetic-cohort derivation declared on the row | done 2026-09-07 |
| 3 | displacement→household_ipv | Aizer 2010 AER 100:1847 | LANDED v1.8: wage_ratio->household_ipv elasticity -0.813 (Table 2 col 3); remaining: incidence-weighted wiring into the daughter chain | done 2026-09-07 |
| 4 | trade_shock→marriage/fertility parameter links | Autor, Dorn & Hanson 2019 AER:I 1(2) | coefficients transcribed to validation/adh2019_measured_coefficients.csv (T6-T8, 11 rows); remaining: shock→displaced-workers conversion (ADH Table 2) to turn them into parameters | bridge pending 2026-09-07 |
| 5 | (merged into #4) | — | — | merged |
| 24 | displacement→non_displaced_wage_spillover | ADH 2019 panel (openICPSR 116320-V2) + local-labor-market lit | LANDED v1.12 via ADH 2013 AER (stronger than the queued candidates): Table 7 Panel B col 6 — nonmanufacturing (non-displaced) noncollege wage response −0.822 log pts per $1k/worker exposure [−1.304, −0.340] EXACT; pooled male TOTAL CZ response (Table 6 col 2, −0.892 SE 0.294) recorded in notes for the V1 cross-check. WIRED into the V1 panel earnings row v1.17: composed −$165 [−237, −93] closes 32.9% of the point-gap (direct-only miss retained beside it); implied total response −1.41 log pts/$1k inside the measured aggregate CI | done 2026-09-08 |
| 6 | earnings→mortality full-text anchor | Sullivan & von Wachter 2009 QJE 124:1265 | LANDED v1.9: Table 5 col 2 sustained OR 1.135 [1.033,1.247], peak OR 2.672 [2.116,3.374], tier EXACT (read via NBER WP w13626) | done 2026-09-07 |

## P2 — complete streams

| # | Link | Study | Extraction target | Status |
|:--|:--|:--|:--|:--|
| 7 | wage→fertility (converse) | Kearney & Wilson 2018 REStat 100(4):678-690 (queue said 2020 — corrected; the 2020 REStat paper is their DIFFERENT Pill study) | LANDED v1.14: marital-birth-rate elasticity to male earnings 1.24 [0.397, 2.083] EXACT (Table 8 PB col 2, IV, F=11.8 declared; nonmarital same elasticity, marriage null; coal-boom 0.75 recorded as cross-context anchor) | done 2026-09-07 |
| 8 | income→child achievement | Dahl & Lochner 2012 AER 102(5):1927-1956 (queue page ref corrected) | LANDED v1.12: +0.0610 SD per $1,000 year-2000 $ [0.016, 0.106] EXACT — Table 3 col (i), SE 0.0231, N=8,608, EITC IV (read via NBER w14599) | done 2026-09-07 |
| 9 | early-poverty→adult attainment | Duncan, Ziol-Guest & Kalil 2010 | adult earnings effect of ages 0-5 poverty | **REFUSED** 2026-09-09: observational OLS on PSID — barred from a point by CITING §1 (thornton1980 precedent); duncan2010 + zg2012 bib'd with the verified Table S5 magnitudes as the cross-check note on the akee2010 education row; the causal slot is filled by #25 Akee |
| 10 | unemployment→property crime | Raphael & Winter-Ebmer 2001 JLE 44(1):259-283 (NOT JOLE — venue corrected); Lin 2008 | LANDED v1.13: +5.018% property crime per 1pp unemployment [2.795, 7.241] EXACT 2SLS (overID passes); OLS 1.6-2.4% recorded; violent-crime null deliberately not landed; Lin 2008 stays queued as the second band anchor | done 2026-09-07 |
| 11 | parental displacement→college | Hilger 2016 AEJ:Applied 8(3):247-283 | LANDED v1.13 (published copy provided by owner): enrollment multiplier 0.9894 [0.9848, 0.9939] EXACT (−0.432pp on 40.66% base) + companion income bridge 0.8640 [0.8568, 0.8712]. CLOSURE-SELECTION WARNING recorded: Hilger's own closure-DD is wrong-signed and his fn31 names oreopoulos2008 + sullivan2009 as exposed designs — V2 reconciliation item queued; child-earnings band NOT silently changed | done 2026-09-07 |
| 12 | displacement→academic difficulty | Stevens & Schaller 2011 | LANDED v1.20 — queue target CORRECTED: the paper has NO math/reading test scores; the outcome is grade retention (the authors' own proxy for academic difficulties). displacement->grade_retention_hazard 1.1473 [1.012, 1.283] EXACT — Table 4 col 1 child-FE: +0.0081 (SE 0.0038) on the 0.055 base = +0.8pp ≈ +15% one-or-more years after the loss (current-year null = the timing identification); concentrated among HS-or-less heads. VENUE CORRECTED: Economics of Education Review 30(2):289-299, not Sociology of Education (no such Crossref record); read via NBER w15480. Bonus: Table 3 family-income −10.9% recorded as a cross-check note on the hilger2016 short-run income row | done 2026-09-08 |
| 13 | displacement→infant health | Lindo 2011 J Health Econ 30:869-879 | LANDED v1.10: displacement->infant_birth_weight 0.954 [0.912,0.998] EXACT (Table 2 col 3 via IZA DP 5213) | done 2026-09-07 |
| 14 | local decline→child maltreatment | Lindo, Schaller & Hansen 2018 JPubE 163:77-98 (DOI 10.1016/j.jpubeco.2018.04.007; read via NBER w18994 — the AEJ:Applied title in this queue row was wrong, the paper is the JPubE 'Caution! Men Not at Work' study) | LANDED v1.16: +6.0% maltreatment reports per 1pp male mass-layoff rate [3.65, 8.35] EXACT (Table 3 PA col 3); female-shock opposite-signed (scope-declared); unemployment-rate association negative/endogenous (declared) | done 2026-09-07 |
| 15 | import competition→radical vote | Colantone & Stanig 2018 AJPS 62(4):936-953, DOI 10.1111/ajps.12358 (owner-downloaded PDF read in full; staging bib's SSRN preprint doi replaced with the published AJPS doi) | LANDED v1.26: import_shock->radical_right_vote_share 13.2 [3.2, 23.2] pp per $1k/worker EXACT (IV Table 1 col 10, .132*** SE .051 in vote-share fractions per 2-yr $1k/worker shock; authors' 1-SD scaling +1.7pp on a 5% mean; IV > OLS .041 — demand-shock attenuation; F=19.2). NO-LEFT-WING discipline: protectionist left/liberal right NULL (no polarization, declared contrast with autor2020 US), pro-trade left -.134**, protectionist right +.278***. Individual-level ESS confirms, SOCIOTROPIC (no group heterogeneity). Window discipline declared. Boundary-applied, never chained | done 2026-09-09 |
| 16 | import exposure→polarization | Autor et al. 2020 AER 110(10):3139-3183 | LANDED v1.15: GOP House win probability +24.08pp per $1k/worker exposure [0.42, 47.74] EXACT (Table 4 col 6); vote-share columns NULL and declared (re-sorting, not uniform shift); effect emerges 2010+ | done 2026-09-07 |
| 17 | eviction→hardship chain | Desmond & Gershenson 2016; Collinson et al. 2024 QJE (queue's named C&R 2018 WP subsumed — version-of-record correction) | LANDED v1.21: queue CORRECTED to the version of record collinson2024 QJE 139(1):57-120 (read via NBER w30382). TWO rows: eviction_order->emergency_shelter_use 4.778 [1.076, 8.480] EXACT (year-1 IV +3.4pp on 0.9% base, Table V col 3; year-2 shelter null, services persist +3.6pp) and eviction_order->eviction_earnings_response −$613/qtr [−1099, −127] EXACT (Y2 Q5-8; Y1 −323 ns recorded; female/Black concentration). REFUSAL: desmond2016 matched +11-22pp JOB-LOSS estimate NOT encoded — matching class (CITING §1) + collinson2024 employment nulls (−1.5/−1.8pp ns) refute the size; SPEC §10 documents it | done 2026-09-09 |
| 18 | foreclosure→neighborhood prices | Campbell, Giglio & Pathak 2011 AER 101(5):2108-31 (venue CORRECTED — not QJE; read via NBER w14866 April 2009 draft; Immergluck & Smith 2006 Housing Studies is their crime paper, the price study is the 2005 Woodstock/Housing Policy Debate report — unread cross-check lead) | LANDED v1.22: foreclosure_order->house_price_gap 0.99 [0.9875, 0.9925] EXACT-results — preferred lead-vs-lag DiD −1% per foreclosure at 0.05mi (zero distance −2%), gap-multiplier storage; rounding band (no SE on the DiD) with SE-carrying hedonics recorded beside (−1.8%/−1.1% per foreclosure within 0.25mi; 0.1mi zero-distance −9.1%/−7.3% clustering-inflated); persistence (lag-1 comparable) + heterogeneity (single-family/condo, cheap neighborhoods; absent multifamily) declared; PARALLEL stream, not structural per the authors — no instrument | done 2026-09-09 |
| 19 | income→life expectancy slope | Chetty et al. 2016 JAMA 315(16):1750-1766 | LANDED v1.12: 0.1333 y per $1k [0.117, 0.150] EXACT-derived — the paper's own concavity example $14k→$20k (P15→P20) carries +0.7-0.9y, slope 0.8/6; associational (authors' caveat) — row records it as a conversion factor, causal deaths stay anchored on sullivan2009 | done 2026-09-07 |
| 20 | unemployment→mental health | Paul & Moser 2009 JVB 74(3):264-282, DOI 10.1016/j.jvb.2009.01.001 (owner-downloaded ScienceDirect PDF read in full) | LANDED v1.25: unemployment_status->mental_health_sd 0.51 [0.47, 0.54] EXACT (cross-sectional random-effects meta, outliers excluded, k=315, N=209,379; all-studies 0.54 beside). Factory-closure causal anchor d=0.38 [0.25, 0.51] k=27 recorded (never averaged); longitudinal 0.19/0.35 retest-corrected 0.25/0.29; selection effects weak (0.23/0.15) declared; moderators scope-declared (men/blue-collar stronger, duration peak 9mo d=0.73, post-29mo worsening UNSTABLE k=5 not landed; country moderators recorded). PARALLEL stream, never chained | done 2026-09-09 |
| 21 | IPV exposure→child mental health | Evans, Davies & DiLillo 2008, Aggression and Violent Behavior 13(2):131-140 (DOI 10.1016/j.avb.2008.02.005; read via the Nebraska DigitalCommons accepted manuscript — Wayback mirror of the WAF-blocked PDF CGI) | LANDED v1.23: household_ipv->child_internalizing_sd 0.48 [0.39, 0.57] EXACT (k=58, N=7,602, homogeneous) + household_ipv->child_externalizing_sd 0.47 [0.38, 0.56] EXACT (k=53, heterogeneous; boys .46 / girls .23 declared). Random-effects meta (CITING §1 meta class); kitzmann2003/wolfe2003 cross-checks recorded, not averaged; trauma d=1.54 refused (k=6, authors' own caution); PARALLEL stream — boundary coefficient, never chained into earnings/IGE/achievement | done 2026-09-09 |
| 22 | recessions→IPV | Schneider, Harknett & McLanahan 2016 Demography 53(2):471-505, DOI 10.1007/s13524-016-0462-1 (owner-downloaded PDF read in full) | LANDED v1.24: local_unemp_shock->household_ipv 1.58 [1.49, 1.58] per UR doubling (Table 3 logit .454*, LDV .401*, FE .406* — band = exp() spec range, point = Model 1 headline) + household_hardship->household_ipv 2.14 [1.61, 2.68] + couple_unemployment->household_ipv 1.30 [1.04, 1.63] (Model 1 prose predictions; +/-25% declared bands, coeffs recorded beside). LEVEL-NULL discipline: UR level null — only the 12-month CHANGE moves abuse; violent-only null for both unemployment measures. PARALLEL stream, never chained | done 2026-09-09 |

## P3 — breadth and place resolution

| # | Link | Study | Extraction target | Status |
|:--|:--|:--|:--|:--|
| 23 | county mobility modifier | Chetty & Hendren 2018 QJE 133(3):1163 (childhood exposure effects; AER 108 = the 2018 follow-on) | per-percentile exposure-effect parameter `neighborhood_exposure->child_outcomes_modifier` — the engine formula is FROZEN (v1.29, multiplier = 1 + (pct-50)/100 x point); the number lands as the parameter row with the unit conversion declared in notes | **LANDED v1.30**: gamma 0.037 [0.031,0.043] EXACT (App. Table V col 1, county level, N=595,244; CZ baseline 0.040 beside) — read via NBER w23001 |
| 30 | county mobility_percentile plug | Opportunity Atlas county outcomes (Chetty et al. 2018, public data) | per-county mobility T-rank percentile + n -> `params/places.csv` rows (the modifier's place input) | **LANDED v1.30**: build_places.py -> 3,134 US counties from county_outcomes_simple (raw committed under validation/); mobility_percentile = kfr x 100 (the effect's own treatment scale) |
| 31 | county mortality plug | CDC WONDER D76 public web export (FIPS-level deaths + population, 45-54 men, 2015-2019 pooled to match the national baseline pin) | `places.csv` mortality_rate (same unit as baselines.csv:all_cause_mortality_annual — per person-year prime-age) + mortality_n | **LANDED 2026-09-13** — validation/cdc_wonder_county_male_45_54_2015_2019.csv (+ .provenance.json, .metadata.json): 2748 counties, Total row 514314/104024440 reproduces the national pin exactly; downloadable via scripts/fetch_wonder.py county (web-UI session; the machine XML API is national-only by server policy — probed 2026-09-13). The earlier "REMAINING: derive shrunk baselines" clause is SUPERSEDED by v1.36: params/county_mortality.csv carries the 2748 Gamma–Poisson posteriors (matching national prior + metadata) and is wired into the place layer end to end; v1.41 completes the row's literal target — the generated places.csv plug columns (mortality_rate = posterior mean per person-year, mortality_n = county person-years precision label) fill in the same build-places pass; 388 suppressed/absent counties stay empty (national fallback), national row = pin 0.004944 + Total 104024440 person-years | done 2026-09-13 |
| 24 | neighborhood crime→child crime | Damm & Dustmann 2014 AER 104(6):1806-1832 (read via Aarhus WP 2013-17, Sept 2013 draft) | queue target CORRECTED: the paper has NO clean exposure-duration elasticity (age at assignment is perfectly correlated with potential exposure years; the age-cohort splits confound duration with age, authors' own caveat) | **LANDED v1.33**: TWO EXACT rows on quasi-random refugee municipality assignment (males, N=4,425, avg age at assignment 9) — youth_crime_conviction_share→youth_crime_convicted 0.061 [0.000, 0.123] per 1pp of the area 15-25 conviction share (T3 spec 5 municipality-FE; conservative spec-4 0.033 + the count row 0.241/1pp recorded beside; band lower edge rounds to 0.000, declared) and youth_violent_crime_conviction_share→youth_crime_convicted 0.366 [0.143, 0.589] per 1pp of the VIOLENT conviction share (T5 spec 5, mean 0.286%; spec-4 0.276 beside). Operative-channel discipline: the COMMITTED-crime rate is a NULL (T6) — only the share of CONVICTED YOUTH moves children; property/drug shares null (T5); FEMALE NULL (panel B); co-national peer channel recorded (T7). Boundary-applied, never chained | done 2026-09-09 |
| 25 | casino income→child outcomes | Akee et al. 2010 AEJ:Applied 2:86 | education/crime effects per $4k unconditional income | **LANDED v1.32**: THREE rows — education years at 21 +1.127 [0.247, 2.007] EXACT (T4 col 1, previously-poor households; full-sample null recorded, mother-receipt drives it), any-crime 16-17 −0.224 [−0.377, −0.071] EXACT (T6 col 1) and ever-minor by 21 −0.179 [−0.353, −0.005] EXACT (T6 col 4); age-window discipline (18+ null) + minor-only offense nulls declared; read via PMC2891175 author manuscript |
| 26 | bankruptcy/default after job loss | Ganong & Noel 2022 QJE 137; Sullivan et al. 2000 | default hazard effect of income interruption | pending |
| 27 | austerity→extremist vote (context link) | Fetzer 2019 AER 109; Galofré-Vilà et al. 2021 JEH 81 | UKIP/Nazi vote effects — political-stream completeness | pending |
| 28 | multigenerational crime hazard | Farrington (Cambridge Study) | conviction-risk transmission across generations | pending |
| 29 | grandparent education→grandchild | Anderson, Sheppard & Monden 2018 Demography | conditional grandparent effect (cross-checks the IGE-decay layer) | pending |

## Transmission rows — one edge per outcome walks all generations

Design landed 2026-09-13 (`src/downstream/transmissions.py`,
`downstream transmissions`): an intergenerational walk is ONE admitted
parent→child relationship applied recursively — never separately
extracted per-generation parameters. The earnings walk (ige_earnings:
US IGE literature anchors step 2, Lindahl 2015 / Adermon 2018 anchor
the repetition) is the template. Each row below makes ONE more outcome
walk to grandchildren; the audit fails if unrolled copies of a
relationship drift apart.

| # | Link | Study | Extraction target | Status |
|:--|:--|:--|:--|:--|
| 32 | parent achievement→child achievement | Black, Devereux & Salvanes 2009 Economics Letters 105(1):138-140 (read via IZA DP 3651; NBER w14274 beside) | `child_achievement_sd->grandchild_achievement_sd` | **LANDED v1.44**: 0.38 [0.38, 0.42] EXACT-results (father-son IQ correlation .38, p.8; band = single-measure replications to the Bowles-Gintis lower bound; the authors' no-causal-interpretation caveat travels on the row). New `linear_shift` ledger kind composes standardized shifts; DOI verified via Crossref after a search surface returned a WRONG one | done 2026-09-14 |
| 33 | education-years transmission | Lindahl et al. 2015 JHR 50(1) — read in full via IZA DP 6463 | `child_education_years->grandchild_education_years` — **LANDED v1.44**: 0.296 [0.255, 0.337] EXACT-results (Table 2 parent×child cell, SE 0.021, N=1,823; band = 95% CI, dist normal; the authors' own IV null on causal parental-education effects carried as the caveat). REMAINING: the gen-2 entry (`displacement->child_education_years`) — entry hunt READ + RECORDED 2026-09-15: a DOCUMENTED NULL, not a missing extraction (see below); the walk goes live only via a declared probability→years bridge | transmission done 2026-09-14; entry recorded 2026-09-15 |
| 35a | row 33 entry hunt — displacement→child educational level | three candidates, all read in full: Huttunen & Riukula, "Parental Job Loss and Children's Careers" (Labour Economics 2024, DOI 10.1016/j.labeco.2024.102578; read via IZA DP 12788); Oreopoulos, Page & Huff-Stevens 2008 JLE 26(3):455-483 (read via the published-version PDF on the author's UofT page); Bratberg, Nilsen & Vaage 2008 Labour Economics 15(4):591-603 (read via IZA DP 2895) | the `displacement->child_education_years` entry row | READ + RECORDED 2026-09-15 (no row, by design — the entry is a measured NULL): Huttunen & Riukula Table 2 col 1: tertiary ed −0.002 (SE 0.008), N=182,697 — "We find no evidence that the father's job loss affects the educational level of the child" (what DOES move: same-field study choice −1.3pp ≈ −8% relative, earnings −2.2%). Oreopoulos et al.: son's earnings −9% (−0.091, SE 0.037, Table 4) with NO education regression in the published version — the −9% holds at similar schooling levels. Bratberg et al.: child education in descriptives only (12.3 vs 12.6 years raw); regressions target child earnings, itself null (father displaced −0.004 [0.019], Table 5) — a declared contrast to Oreopoulos. Positive displacement effects on education live on probability scales (Hilger 2016 enrollment; Bingley et al. 2023 HS enrollment, IZA DP 16367; Coelli 2005 attendance) and cannot bridge to edu_years without a declared conversion — that bridge is the walk's actual remaining blocker | recorded 2026-09-15 |
| 34 | parent depression→child depression | Weissman et al. three-generation depression studies (JAMA 2006; 2016 follow-up) as candidates; mclanahan1994 beside for the family-process pathway | `adult_depression_cesd->grandchild depression` row (entry edges exist: displacement_event->adult_depression_cesd brand2014, displacement_event->child_depression_anxiety schallerzerpa2019); sd-scale composition kind needed | pending |
| 35 | parental divorce→child own-divorce | mclanahan1994 beside; the transmission pin: McLanahan & Bumpass 1988, "Intergenerational Consequences of Family Disruption", **AJS 94(1):130-152** (DOI 10.1086/228954; the queue had wrongly said Demography; read in full via IRP DP 805-86 with OCR prose↔table cross-check: exp(.65)=1.92 matches the stated 92%). gruber2004 ELIMINATED as the pin (full text read via NBER w7968): law-exposure ITT, "no rise in the odds of being divorced" — earlier marriage + separation/churning fading by middle ages; bib VENUE CORRECTED to JOLE 22(4):799-833 (was mislabeled JPE 112(5)) | **LANDED v1.46**: `divorce_hazard->child_divorce_hazard` 1.88 [1.57, 2.24] EXACT-results (Appendix Table A1 background-controlled β 0.63, SE 0.09; band = exp(β±1.96 SE); education-adjusted 1.67, Black women 1.36, widowhood 1.35 all beside; dist withheld — asymmetric exponentiated CI). THE WALK IS LIVE: the conditional composition kind LANDED v1.47 (see row 35b) | done 2026-09-15: row v1.46, walk v1.47 |
| 35b | conditional-mixture composition kind + dissolution share | rege2007 SSB DP 514 (Statistics Norway; the ENTRY row's own source — same population and window): Table 1 + prose, 'About 7.0 percent of the couples got divorced from 1995 to 2003', stable plants 6.9%, closing 7.2%; read in full from the SSB PDF | NEW KIND `conditional_mixture`: child multiplier = 1 + (s(m) − s)(t − 1), s(m) = 1−(1−s)^m (proportional hazards over the parent window); the infra-marginal dissolutions carry t in both worlds and cancel. NEW ROW `married_cohort->parental_dissolution_share` 0.069 [0.069, 0.072] (stable-plant share; band = the paper's observed range across plant types). Coherence: at m=1.11 the kind yields +0.73pp extra dissolutions vs the paper's own adjusted +0.78pp (+11%). WALK LIVE: worker 1.11 [1.05, 1.25] → child 1.0064 [1.0019, 1.0213] — small BECAUSE it is a mixture; walk labels generations explicitly (worker, child) since the entry lands on the displaced worker's own hazard | LANDED v1.47 |

## Validation data plugs

| # | Item | Source | Status |
|:--|:--|:--|:--|
| V1-a | CZ import-exposure shock values | ADH published instrument files | LANDED 2026-09-07: openICPSR 116320-V2 extract (validation/adh_cz_panel.csv) |
| V1-b | measured CZ outcome deltas 1990-2014 | Autor, Dorn & Hanson 2019 tables (+ Autor et al. 2020) | LANDED 2026-09-07: T4-T8 transcribed (validation/adh2019_measured_coefficients.csv) + panel outcome columns |
| V1-c | CZ demographic baselines | Census/ACS | pending |

## Honesty in both directions (excluded from parameterization)

- Immigration→crime: pooled null-to-negative (ousey2018; butcher1998).
  No positive link will be encoded; refusal documented in SPEC §10.
- Native-wage effects: contested (borjas2003 vs ottaviano2012; the
  Mariel re-analysis war). Not a parameter; alternate-band policy in
  SPEC §10 applies if a surface needs it.

## Downloaded full texts available (owner, 2026-09-07 — ~/Downloads/papers)

Landed: hilger2016, raphael2001, dahl2012 (published AER — v1.12 row verified
identical coefficient/SE, N corrected 8608→8609). Also available, not yet landed:

| Study | What it could anchor |
|:--|:--|
| Bastian & Michelmore 2018 (JLE 36(4):1127-1163) | LANDED v1.14: eitc_exposure->adult_earnings_early 564.0 [84.0, 1044.0] EXACT (reduced form, ages 13-18; IV-scaled 10%-significant number recorded in notes); TIMING finding recorded: exposure before 13 ~ null — adolescent income is the operative window | done 2026-09-07 |
| Behrman & Taubman 1990 (Review of Income and Wealth 36(2)) | LANDED v1.14 as CROSS-CHECK NOTES on both IGE rows (not a composed row — it is a correlation/attenuation result, not an elasticity): one-year measures R=0.20 (elasticity ~0.07) vs >0.5 long-run; brackets our [0.40,0.60] band honestly | done 2026-09-07 |
| Carneiro et al. 2021 (DOI 10.1086/712443) | TIMING of parental income — which child ages matter; supports/bounds the sustained-exposure framing |
| Michelmore & Pilkauskas 2021 (DOI 10.1086/711383) | EITC response by child age (maternal labor supply/childcare) — side stream, low priority |
| Thornton 1980 (Population and Environment 3(1):51-72, DOI 10.1007/bf01253070 — Crossref-verified) | LANDED v1.18 as CROSS-CHECK NOTES on the fertility row (not a composed row — PSID two-generation OLS correlations, observational; CITING §1 bars non-quasi-experimental points): ACTUAL family size transmits near-null (.070 zero-order / .058 controlled, ns; parity sign-inconsistent), IDEAL family size transmits strongly (.282*/.237*) — the recorded reason the model carries no cross-generation fertility multiplier | done 2026-09-08 |

## Research sweep 2026-09-13 — candidates (NOT numbered, NOT extracted)

Web sweep for quasi-experimental (plant-closure / mass-layoff identified)
studies beyond the landed corpus. These are CANDIDATES ONLY: no estimate
lands until a full-text table extraction follows the standard process
(exact point/band/SE, tier, scope, CITING §1 admissibility). Search terms:
job displacement mortality long-run quasi-experimental; parental job
displacement children outcomes; plant closure spouse mental health.

| Candidate | Design | What it could anchor | Status |
|:--|:--|:--|:--|
| Browning & Heinesen 2012 (J Health Econ 31(4):599-616) — CITATION CORRECTED 2026-09-13 via the references of a read full text: the sweep's 'Browning, Dano & Heinesen 31(5)' and its title were wrong (Danø is on the 2006 stress-hospitalization paper, not this one) | Danish plant closures, males 20-60, PSW + duration analysis | CAUSE-SPECIFIC mortality responses | READ + LANDED v1.38: three EXACT boundary-applied rows (circulatory 1-4y 1.54 [1.29,1.83]; alcohol-related 1-4y 1.62 [1.09,2.41] — the deaths-of-despair channel; external causes 1-4y 1.53 [1.15,2.04], suicide year-1 4.31 [1.64,11.37] beside) + all-cause replication cross-checks on the SvW peak/sustained rows (year-1 1.84 [1.44,2.34]; 20y 1.10 [1.05,1.16]). Read from the published JHE version of record (VIVE-hosted PDF) |
| Schaller & Stevens 2015 (J Health Econ 43:190-203, DOI 10.1016/j.jhealeco.2015.07.003; NBER w19884 is its WP) — CONTENT CORRECTION 2026-09-13 from the read full text: this is the MEPS health-conditions/insurance/utilization study, NOT a PSID mortality-timing paper — it estimates NO mortality effects of its own | US MEPS involuntary job losses, individual-FE panel | Own mental-health corroboration (probability units) + the null that conditions the mortality pathway (no short-run chronic-condition onset) | READ + LANDED v1.40 as CROSS-CHECK NOTES on unemployment_status->mental_health_sd (preferred spec: fair/poor mental health +1.39pp on 3.4% base = +40.9% relative; depression/anxiety +1.64pp on 7.3%; units not SD-convertible — directional corroboration; arthritis/diabetes positives not robust to baseline-trend controls). Read via the UC Davis open PDF of the version of record |
| Marcus 2013 (J Health Econ 32(3):546-558; read via SOEPpapers 488 WP draft) | German SOEP plant closures, entropy-balancing DiD | SPOUSE mental-health spillover | READ + LANDED v1.38: new node spouse_mental_health_sd, row displacement_event->spouse_mental_health_sd = -0.194 SD [(-0.327), (-0.061)] (spouse MCS -1.94, SE 0.68); own-effect -0.272 SD recorded as a paul2009 cross-check (inside the causal-clean factory-closure subset); own-vs-spouse difference p=0.38; placebo (closure without unemployment) clean on the spouse side |
| Huttunen & Riukula 2019 (IZA DP 12788) — AUTHOR CORRECTION 2026-09-13: the sweep first mislabeled the co-authors (Møen/Salvanes are a different parental-job-loss paper); the DP is Huttunen & Riukula, and it is FINLAND not Norway | Finnish plant closures 1991-2000 | CHILD earnings — cross-jurisdiction check beside oreopoulos2008 | READ 2026-09-13 — LANDED v1.37 as CROSS-CHECK NOTES on displacement->child_earnings (age-30 earnings -575.476 EUR SE 278.543 on mean 25883.871 = -2.2%; males -2.4%; females/mothers null; channel = career choice, no GPA/crime effects); working paper -> notes only, never a composed row |
| Brand & Simon Thomas 2014 (AJS 119(4):955-1001; PMC4372265 author manuscript) | US SIPP displacement events, propensity matching (TT kernel) | MATERNAL displacement → child outcomes | READ + LANDED v1.42 (user-directed node design): FOUR EXACT conditional rows on new nodes — displacement_event->hs_completion -0.037 [(-0.0801), 0.0061] (p<.10 declared; band honestly crosses zero), ->college_attendance -0.063 [(-0.1081), (-0.0179)], ->college_completion -0.036 [(-0.0674), (-0.0046)], ->adult_depression_cesd +0.025 [0.0034, 0.0466] on a new scale01 unit (0-1 CESD index, not a probability); timing gradients in row notes (education = adolescence 12-17 concentration, HS 12-17 -0.115**; CESD = middle-childhood +0.047**); PSM declared the weakest identification class on every row — corroboration, never an anchor; college_attendance is a stock, distinct from the hilger2016 enrollment flow |
| Bingley, Cappellari & Ovidi — AUTHOR CORRECTION 2026-09-13 (not Lundborg): IZA DP 16367 "When It Hurts the Most: Timing of Parental Job Loss and a Child's Education"; PEER-REVIEWED as of the JEEA advance article 2026, DOI 10.1093/jeea/jvag048 | Danish admin registers, plant closures matched to controls, children 0-16 at closure | Education TIMING structure (infancy < age 5 concentration) + math achievement in SD units | READ + LANDED v1.40: EXACT rows displacement_event->child_achievement_sd (-0.0206 [-0.0402,-0.0010] avg 0-16, math teacher grades; infancy -0.0521 beside) + new node exam_noncompletion_hazard (1.0688 [1.0014,1.1362] avg; infancy 1.126 beside), both conditional; income-channel mediation recorded as dahl2012 cross-check (+0.0008 SD per +1,000 DKK/yr). Read via IZA DP 16367 (WP draft of the version of record; read-via precedent) |

Excluded from candidacy: Brand 2015 (Annual Review of Sociology) — narrative
review, not an identified estimate; Oreopoulos et al. 2008 — already LANDED
(oreopoulos2008); Sullivan & von Wachter 2009 — the shipped response source.

## Research sweep 2026-09-13 (second pass) — READ + LANDED v1.43

Targets were the coverage gaps left by the first pass: third-country
mortality replication, fertility, spousal labor supply, child mental
health. All six extracted from open full text and landed. Corrections
made at extraction: no displacement→SPOUSE-MORTALITY study exists (the
widowhood literature is the reverse direction) — open gap, not a row;
the remembered "Kuka/Shenhav/Shumway" paper does not exist; the ES NBER
number a search result supplied (w12128) was WRONG (an unrelated
Glaeser paper) — ES was read via GUPEA WP 153 through the repository's
bot gate; HK's venue is the Journal of Labor Economics 34(2) 2016, not
Labour Economics, and its regression tables live in IZA DP 6707 (the
SOLE PDF's tables are images).

| Study | Design | Anchors | Status |
|:--|:--|:--|:--|
| Eliason & Storrie 2009, J Human Resources 44(2):277-302, DOI 10.1353/jhr.2009.0020 | Swedish PSW establishment closures 1983-92, men 20-60 | mortality timing + causes | READ + LANDED v1.43 as CROSS-CHECKS: men ≤4y all-cause HR 1.44 [1.19,1.76] on the peak row; external 2.07 [1.42,3.02], suicide 2.15 [1.28,3.59], alcohol 2.21 [1.14,4.31] on the B&H external row; DECLARED DIVERGENCE on the sustained row — NO long-run effect (5-8y 0.98, 9-12y 0.91 n.s.); women null declared. Read via GUPEA WP 153 (2007 revision) through the bot gate |
| Bloemen, Stancanelli & van der Klaauw 2018, J Health Econ 59:78-90 | Dutch registers, men 45-59, ≥5y tenure, firm-closure job loss, LPM | mortality timing + causes | READ + LANDED v1.43 as CROSS-CHECKS: year-1 +0.2229pp (SE 0.0812) = +85.8%; 5y +0.5968pp (SE 0.1763) = +33.5% (2y 60.9→declining); circulatory +0.2453pp (+52.8%), cerebrovascular +152.9% on the B&H circulatory row; DIVERGES on external (−0.0389pp) and suicide (n.s.) — heterogeneity declared. Read via IZA DP 9483 |
| Halla, Schmieder & Weber 2020, AEJ:Applied 12(4):253-287, DOI 10.1257/app.20180671 | Austrian ASOS registers, husbands displaced, event studies | spousal labor supply + divorce | READ + LANDED v1.43: NEW EXACT row displacement_event->spouse_participation_elasticity −0.04 [−0.07,−0.03] (band = the paper's subgroup range, dist empty; AWE an order below the literature's −0.4; extensive-margin only); DIVORCE cross-check on the rege2007 row: +0.004pp/quarter (SE 0.001), ~0.5pp/5y, PRECISE ZERO vs mass-layoff-firm controls — order smaller than the shipped multiplier, divergence declared; births null beside. Read via IZA DP 11752 |
| Huttunen & Kellokumpi 2016, Journal of Labor Economics 34(2), DOI 10.1086/683645 — VENUE CORRECTED (not Labour Economics 2014) | Finnish FLEED, plant closures 1991-93, couples | displacement→fertility | READ + LANDED v1.43: NEW EXACT row displacement_event->annual_birth_response −0.005 [−0.0089,−0.0011] (displacement-year P(birth), Table 3; year-3 recurrence; cumulative −4 births/100 women by year 11, Figure 6; high-education −0.05, career-concern channel not income); MALE NULL declared (Table 4) + halla2020 husband-null beside; never merged with the kearney local-shock row. Read via IZA DP 6707 (tables; the SOLE/Helda PDFs carry image tables) |
| Schaller & Zerpa 2019, American Journal of Health Economics 5(2):247-279 (NBER w21745) | US MEPS, individual-FE LPM, parental job loss, children | child mental/physical health | READ + LANDED v1.43: NEW EXACT row displacement_event->child_depression_anxiety +0.008 [0.0002,0.0158] (paternal, tenured spec; closure +0.006*, all +0.002 n.s. — spec sensitivity declared); mental-health-excellent falls (father closure −0.044**, mother −0.038**/−0.058**); MATERNAL depression/anxiety NULL declared; MÖRK honesty beside. Read via NBER w21745 |
| Mörk, Sjögren & Svaleryd 2019, IZA DP 12559 — AUTHOR CORRECTION at extraction (Svaleryd, not Zhuravskaya); WP-only, canonical cap holds | Swedish workplace closures, registers, 10y child follow-up | HONESTY anchor | READ + RECORDED v1.43 (no row, by design): child hospitalization/mortality NULLS (only significant result: paternal mental/behavior admissions −2.8/1000 = −8.3%, a DECLINE); paternal education NULLS; maternal GPA/HS negatives carry similar pre-trends and are questioned by the authors. Cited from the child_depression_anxiety honesty note; never promoted past the cap |

## Research sweep 2026-09-14 (third pass) — candidates (NOT extracted)

Pass-three targets: the timing/mechanism refinements of the newly landed
streams, the cross-jurisdiction fertility checks, and the first sweep of
the DISPLACED-WORKER-OWN-CRIME gap (the shipped crime rows are area-share
based — a personal displacement effect would be a new stream). Venues
verified via search at queueing; numbers NOT yet pinned — every landing
still requires the standard full-text table extraction.

| Candidate | Design | What it could anchor | Access |
|:--|:--|:--|:--|
| Del Bono, Weber & Winter-Ebmer 2012, "Clash of Career and Family: Fertility Decisions after Job Displacement", JEEA 10(4) — VENUE VERIFIED (JEEA, not Labour Economics) | Austrian social-security registers, plant closures, event study | Fertility TIMING beside huttunenkellokumpi2016: displacement reduces average fertility 5-10% at both 3 and 6 years (short AND medium run — tests the Finnish cumulative pattern) | IZA DP 3272 open PDF |
| Del Bono, Weber & Winter-Ebmer 2015, "Fertility and Economic Instability: The Role of Unemployment and Job Displacement", J Pop Econ 28(2):463-478 | Austrian white-collar women; separates unemployment per se from displacement | MECHANISM disambiguation beside the fertility row: displacement effect vs unemployment-status effect (the model carries both nodes — this is the row that says which channel moves fertility) | RePEc/EconStor open |
| Högberg & Baranowska-Rataj 2024, Advances in Life Course Research (PMID 38569249) | Swedish registers, workplace closures, child psychotropic DISPENSED PRESCRIPTIONS; timing + cumulative exposure | Child mental-health corroboration beside schallerzerpa2019 in a THIRD outcome type (medication fills, not survey reports or hospitalization) — the direct complement to the mork2019 null | open via DiVA (Umeå) |
| Rege, Skardhamar, Telle & Votruba 2019, "Job displacement and crime: Evidence from Norwegian mass layoffs", Labour Economics | Norwegian registers, mass layoffs, young adult men, charge records | NEW STREAM: displaced worker's OWN crime (the shipped crime rows are AREA conviction-share based — damm2014 — and casino-income based — akee2010; a personal-displacement effect is a distinct estimand, never merged). DP version headline: +14% crime charges; pin the published-table numbers at extraction | ScienceDirect S0927537119300879; IZA DP 593 open |
| Black, Devereux & Salvanes, "Losing Heart? The Effect of Job Displacement on Health" (NBER w18660; verify published venue/pages at extraction — Bloemen 2018 cites it as 2015 on smoking-related disease) | Norwegian registers (verify at extraction), plant closures | Health-BEHAVIOR mechanism beside the mortality cause rows (ES attributes long-run mortality to smoking; this is the morbidity-side evidence) | NBER w18660 open PDF |
| Tyagi 2026, Social Science Research (S0049089X26000517) | Norwegian plant closures, couples | Cross-jurisdiction fertility check beside huttunenkellokumpi2016 (Finland) and delbono2012 (Austria) | ScienceDirect; verify open access at extraction |
| Hofmann 2017, "Job Displacement and First Birth Over the Business Cycle" (PMC5486876; journal to verify at extraction) | Register data, first births, business-cycle interaction (verify design at extraction) | Fertility timing x macro-state (recession vs expansion displacement) — extends the v1.43 fertility row's context-dependence | PMC open |

## Fetal-channel queue (opened v1.45, 2026-09-14)

The v1.45 chain landed the earnings and disease-hazard dose-response
rows. These four extractions complete the channel; none may land
without its stated precondition.

| Extraction | What it needs before landing | Numbers already recorded |
|:--|:--|:--|
| BDS 2007 HS completion (bds2007 twin FE: +0.95pp per +10% BW, SE 0.04) | a (GAP, PROB) dose-response composition decision — hs_completion is a probability-LEVEL node and boundary-applied; a RR-per-log-BW translation must be declared first | evidence_findings: bds2007_twinfe_hs_completion_pp |
| BDS 2007 IQ (twin FE: +0.06 stanine per +10% BW, SE 0.18) | an SD translation row (stanine SD = 2) and a consumer node | evidence_findings: bds2007_twinfe_iq_stanine |
| BDS 2007 one-year mortality (FE -41.15 per 1000 per log BW, SE 7.64) | a baseline infant-mortality node, a functional-form choice (logit marginals ~6x smaller), and a transport declaration (Norway 1967-88 -> US); the FE gradient flips sign across periods — the instability travels with any future row | evidence_findings: bds2007_twinfe_1yr_mortality |
| Royer 2009 intergenerational BW (abstract reports effects "generally small" incl. offspring birth weight; the full PDF is paywalled and the evidence corpus is PDF-hash-pinned, so no finding row exists for it yet) | acquire the AEJ:Applied full-text PDF, then extract her Table 4/5 coefficients; until then NO offspring-birth-weight row may be fabricated | bib key royer2009 (xh1b-evidence: abstract); full text NOT yet in corpus |

## Receiving-community channel queue (opened 2026-09-14)

From `docs/IMMIGRATION_REPLACEMENT_EVIDENCE_SCAN_2026-09-14.md`: screen
the six verified anchor channels through the admission contract. The
crime channel carries one extra gate — an INDEPENDENCE CHECK (below)
because the leading meta-analysis (Ousey & Kubrin 2018) is contested
by the model's owner.

- Independence check (crime): the near-null must be corroborated by at
  least three quasi-experimental teams with no co-authorship or
  shared-institution ties to Ousey/Kubrin, including at least one
  team with no pro-immigration publication record — candidate
  independent anchors already surfaced by the scan: Light & Miller
  (AJPH 2018), Light/He/Robey (AJPH 2020), Bell, Fasani & Machin
  (REStat/JEEA UK), plus European register studies. If independence
  fails, the crime channel stays UNMODELED (silence, not a borrowed
  null).
- Mental-health anchor: Shin 2026 (IZA DP 18586, Jeju Island
  quasi-experiment) — working-paper tier; re-check for journal
  publication before screening.
