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
| 9 | early-poverty→adult attainment | Duncan, Ziol-Guest & Kalil 2010 | adult earnings effect of ages 0-5 poverty | pending |
| 10 | unemployment→property crime | Raphael & Winter-Ebmer 2001 JLE 44(1):259-283 (NOT JOLE — venue corrected); Lin 2008 | LANDED v1.13: +5.018% property crime per 1pp unemployment [2.795, 7.241] EXACT 2SLS (overID passes); OLS 1.6-2.4% recorded; violent-crime null deliberately not landed; Lin 2008 stays queued as the second band anchor | done 2026-09-07 |
| 11 | parental displacement→college | Hilger 2016 AEJ:Applied 8(3):247-283 | LANDED v1.13 (published copy provided by owner): enrollment multiplier 0.9894 [0.9848, 0.9939] EXACT (−0.432pp on 40.66% base) + companion income bridge 0.8640 [0.8568, 0.8712]. CLOSURE-SELECTION WARNING recorded: Hilger's own closure-DD is wrong-signed and his fn31 names oreopoulos2008 + sullivan2009 as exposed designs — V2 reconciliation item queued; child-earnings band NOT silently changed | done 2026-09-07 |
| 12 | displacement→test scores | Stevens & Schaller 2011 | math/reading effect sizes | pending |
| 13 | displacement→infant health | Lindo 2011 J Health Econ 30:869-879 | LANDED v1.10: displacement->infant_birth_weight 0.954 [0.912,0.998] EXACT (Table 2 col 3 via IZA DP 5213) | done 2026-09-07 |
| 14 | local decline→child maltreatment | Lindo, Schaller & Hansen 2018 JPubE 163:77-98 (DOI 10.1016/j.jpubeco.2018.04.007; read via NBER w18994 — the AEJ:Applied title in this queue row was wrong, the paper is the JPubE 'Caution! Men Not at Work' study) | LANDED v1.16: +6.0% maltreatment reports per 1pp male mass-layoff rate [3.65, 8.35] EXACT (Table 3 PA col 3); female-shock opposite-signed (scope-declared); unemployment-rate association negative/endogenous (declared) | done 2026-09-07 |
| 15 | import competition→radical vote | Colantone & Stanig 2018 AJPS 62(4):936-953 (Crossref-verified; bib record already correct) | pending — full text bot-walled (author site 403, Wiley 403, SSRN login); owner-download unblocks. Related landed: #16 Autor et al. 2020 gives the US win-probability row | pending 2026-09-07 |
| 16 | import exposure→polarization | Autor et al. 2020 AER 110(10):3139-3183 | LANDED v1.15: GOP House win probability +24.08pp per $1k/worker exposure [0.42, 47.74] EXACT (Table 4 col 6); vote-share columns NULL and declared (re-sorting, not uniform shift); effect emerges 2010+ | done 2026-09-07 |
| 17 | eviction→hardship chain | Desmond & Gershenson 2016; Collinson & Reed 2018 | job-loss effect of eviction (structural link into homelessness) | pending |
| 18 | foreclosure→neighborhood prices | Immergluck & Smith 2006; Campbell et al. 2011 QJE 126 | price spillover per foreclosure within radius | pending |
| 19 | income→life expectancy slope | Chetty et al. 2016 JAMA 315(16):1750-1766 | LANDED v1.12: 0.1333 y per $1k [0.117, 0.150] EXACT-derived — the paper's own concavity example $14k→$20k (P15→P20) carries +0.7-0.9y, slope 0.8/6; associational (authors' caveat) — row records it as a conversion factor, causal deaths stay anchored on sullivan2009 | done 2026-09-07 |
| 20 | unemployment→mental health | Paul & Moser 2009 JVB 74:264 | distress effect size (d ≈ 0.5) + re-employment reversal | pending |
| 21 | IPV exposure→child mental health | Evans, Davies & DiLillo 2008 | meta effect of exposure on internalizing/externalizing | pending |
| 22 | recessions→IPV | Schneider, Harknett & McLanahan 2016 Demography 53(2):471-505, DOI 10.1007/s13524-016-0462-1 (Crossref-verified 2026-09-07) | pending — Springer PDF blocked to scripts; Demography is open access so an owner download unblocks | pending 2026-09-07 |

## P3 — breadth and place resolution

| # | Link | Study | Extraction target | Status |
|:--|:--|:--|:--|:--|
| 23 | county mobility modifier | Chetty & Hendren 2018 AER 108; CHKS 2014 QJE 129 | per-county causal place effects file (public data) as a pluggable `place_modifier` | pending |
| 24 | neighborhood crime→child crime | Damm & Dustmann 2014 | exposure-duration elasticity | pending |
| 25 | casino income→child outcomes | Akee et al. 2010 AEJ:Applied 2:86 | education/crime effects per $4k unconditional income | pending |
| 26 | bankruptcy/default after job loss | Ganong & Noel 2022 QJE 137; Sullivan et al. 2000 | default hazard effect of income interruption | pending |
| 27 | austerity→extremist vote (context link) | Fetzer 2019 AER 109; Galofré-Vilà et al. 2021 JEH 81 | UKIP/Nazi vote effects — political-stream completeness | pending |
| 28 | multigenerational crime hazard | Farrington (Cambridge Study) | conviction-risk transmission across generations | pending |
| 29 | grandparent education→grandchild | Anderson, Sheppard & Monden 2018 Demography | conditional grandparent effect (cross-checks the IGE-decay layer) | pending |

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
