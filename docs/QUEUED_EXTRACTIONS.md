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
| 1 | baseline: all-cause mortality | CDC WONDER / S&vW 2009 counterfactual | annual rate, men 45-54, US; the study's control-group rate is the cleanest match | pending |
| 2 | baseline: median male lifetime earnings | SSA Continuous Work History Sample | median lifetime earnings, men; pin cohort + year | pending |
| 3 | displacement→household_ipv | Aizer 2010 AER 100:1847 | LANDED v1.8: wage_ratio->household_ipv elasticity -0.813 (Table 2 col 3); remaining: incidence-weighted wiring into the daughter chain | done 2026-09-07 |
| 4 | trade_shock→marriage/fertility parameter links | Autor, Dorn & Hanson 2019 AER:I 1(2) | coefficients transcribed to validation/adh2019_measured_coefficients.csv (T6-T8, 11 rows); remaining: shock→displaced-workers conversion (ADH Table 2) to turn them into parameters | bridge pending 2026-09-07 |
| 5 | (merged into #4) | — | — | merged |
| 24 | displacement→non_displaced_wage_spillover | ADH 2019 panel (openICPSR 116320-V2) + local-labor-market lit | LANDED v1.12 via ADH 2013 AER (stronger than the queued candidates): Table 7 Panel B col 6 — nonmanufacturing (non-displaced) noncollege wage response −0.822 log pts per $1k/worker exposure [−1.304, −0.340] EXACT; pooled male TOTAL CZ response (Table 6 col 2, −0.892 SE 0.294) recorded in notes for the V1 cross-check | done 2026-09-07 |
| 6 | earnings→mortality full-text anchor | Sullivan & von Wachter 2009 QJE 124:1265 | LANDED v1.9: Table 5 col 2 sustained OR 1.135 [1.033,1.247], peak OR 2.672 [2.116,3.374], tier EXACT (read via NBER WP w13626) | done 2026-09-07 |

## P2 — complete streams

| # | Link | Study | Extraction target | Status |
|:--|:--|:--|:--|:--|
| 7 | wage→fertility (converse) | Kearney & Wilson 2020 REStat | fertility elasticity to male income from fracking boom | pending |
| 8 | income→child achievement | Dahl & Lochner 2012 AER 102(5):1927-1956 (queue page ref corrected) | LANDED v1.12: +0.0610 SD per $1,000 year-2000 $ [0.016, 0.106] EXACT — Table 3 col (i), SE 0.0231, N=8,608, EITC IV (read via NBER w14599) | done 2026-09-07 |
| 9 | early-poverty→adult attainment | Duncan, Ziol-Guest & Kalil 2010 | adult earnings effect of ages 0-5 poverty | pending |
| 10 | unemployment→property crime | Raphael & Winter-Ebmer 2001; Lin 2008 | property-crime elasticity per pp unemployment | pending |
| 11 | parental displacement→college | Hilger 2016 AEJ:Applied 8(3):247-283, DOI 10.1257/app.20150295 (queue citation CORRECTED; was 8:787) | pending — BLOCKED: AEA full text is viewer-gated (abstract only); headline from abstract: layoffs cut income dramatically but college enrollment/quality only SLIGHTLY, and firm-closure-based estimates suffer selection — expect a SMALL link, weaker than assumed; needs the published tables (replication package or library access) before an EXACT row | blocked 2026-09-07 |
| 12 | displacement→test scores | Stevens & Schaller 2011 | math/reading effect sizes | pending |
| 13 | displacement→infant health | Lindo 2011 J Health Econ 30:869-879 | LANDED v1.10: displacement->infant_birth_weight 0.954 [0.912,0.998] EXACT (Table 2 col 3 via IZA DP 5213) | done 2026-09-07 |
| 14 | local decline→child maltreatment | Lindo, Schaller & Hansen 2018 | maltreatment effect per local shock | pending |
| 15 | import competition→radical vote | Colantone & Stanig 2018 AJPS 62 | vote-share effect per import shock SD | pending |
| 16 | import exposure→polarization | Autor et al. 2020 AER 110 | GOP-margin effect per shock | pending |
| 17 | eviction→hardship chain | Desmond & Gershenson 2016; Collinson & Reed 2018 | job-loss effect of eviction (structural link into homelessness) | pending |
| 18 | foreclosure→neighborhood prices | Immergluck & Smith 2006; Campbell et al. 2011 QJE 126 | price spillover per foreclosure within radius | pending |
| 19 | income→life expectancy slope | Chetty et al. 2016 JAMA 315(16):1750-1766 | LANDED v1.12: 0.1333 y per $1k [0.117, 0.150] EXACT-derived — the paper's own concavity example $14k→$20k (P15→P20) carries +0.7-0.9y, slope 0.8/6; associational (authors' caveat) — row records it as a conversion factor, causal deaths stay anchored on sullivan2009 | done 2026-09-07 |
| 20 | unemployment→mental health | Paul & Moser 2009 JVB 74:264 | distress effect size (d ≈ 0.5) + re-employment reversal | pending |
| 21 | IPV exposure→child mental health | Evans, Davies & DiLillo 2008 | meta effect of exposure on internalizing/externalizing | pending |
| 22 | recessions→IPV | Schneider, Harknett & McLanahan 2016 | employment-status IPV effect (converges with Aizer) | pending |

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
