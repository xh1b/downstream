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
| 3 | displacement→household_ipv | Aizer 2010 AER 100:1847 | elasticity of violence w.r.t. gender wage gap (Table ~4/5); gives household_ipv its producer | pending (full text queued) |
| 4 | displacement→marriage_rate | Autor, Dorn & Hanson 2019 AEA P&P 109 | marriage-rate coefficient per shock SD | pending |
| 5 | displacement→nonmarital_fertility | same | nonmarital fertility coefficient | pending |
| 6 | earnings→mortality full-text anchor | Sullivan & von Wachter 2009 QJE 124:1265 | sustained + peak-year hazards from the tables; upgrades tier to EXACT | pending (magnitudes CONFIRMED via Davis & von Wachter 2011 full-text synthesis 2026-09-06: near-term up to +100%, sustained for 20y, 1-1.5y life expectancy; QJE tables still needed for table-level pinning) |

## P2 — complete streams

| # | Link | Study | Extraction target | Status |
|:--|:--|:--|:--|:--|
| 7 | wage→fertility (converse) | Kearney & Wilson 2020 REStat | fertility elasticity to male income from fracking boom | pending |
| 8 | income→child achievement | Dahl & Lochner 2012 AER 102:1719 | SD achievement per $1k family income | pending |
| 9 | early-poverty→adult attainment | Duncan, Ziol-Guest & Kalil 2010 | adult earnings effect of ages 0-5 poverty | pending |
| 10 | unemployment→property crime | Raphael & Winter-Ebmer 2001; Lin 2008 | property-crime elasticity per pp unemployment | pending |
| 11 | parental displacement→college | Hilger 2016 AEJ:Applied 8:787 | college-attendance effect of father layoff | pending |
| 12 | displacement→test scores | Stevens & Schaller 2011 | math/reading effect sizes | pending |
| 13 | displacement→infant health | Lindo 2011 J Health Econ 30:229 | low-birth-weight / fetal-loss effect | pending |
| 14 | local decline→child maltreatment | Lindo, Schaller & Hansen 2018 | maltreatment effect per local shock | pending |
| 15 | import competition→radical vote | Colantone & Stanig 2018 AJPS 62 | vote-share effect per import shock SD | pending |
| 16 | import exposure→polarization | Autor et al. 2020 AER 110 | GOP-margin effect per shock | pending |
| 17 | eviction→hardship chain | Desmond & Gershenson 2016; Collinson & Reed 2018 | job-loss effect of eviction (structural link into homelessness) | pending |
| 18 | foreclosure→neighborhood prices | Immergluck & Smith 2006; Campbell et al. 2011 QJE 126 | price spillover per foreclosure within radius | pending |
| 19 | income→life expectancy slope | Chetty et al. 2016 JAMA 315:1750 | local slope of life-expectancy gradient at median income (for the earnings→life-years conversion) | pending |
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
| V1-a | CZ import-exposure shock values | ADH published instrument files | pending |
| V1-b | measured CZ outcome deltas 1990-2014 | Autor, Dorn & Hanson 2019 tables (+ Autor et al. 2020) | pending |
| V1-c | CZ demographic baselines | Census/ACS | pending |

## Honesty in both directions (excluded from parameterization)

- Immigration→crime: pooled null-to-negative (ousey2018; butcher1998).
  No positive link will be encoded; refusal documented in SPEC §10.
- Native-wage effects: contested (borjas2003 vs ottaviano2012; the
  Mariel re-analysis war). Not a parameter; alternate-band policy in
  SPEC §10 applies if a surface needs it.
