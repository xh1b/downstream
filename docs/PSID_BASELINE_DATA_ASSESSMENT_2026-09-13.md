# PSID baseline-data assessment — 2026-09-13

## Scope and verdict

R2 of the [research plan](LIFE_COURSE_RESEARCH_PLAN.md) requires a baseline
household model in which supported variables evolve plausibly, household
accounting reconciles, missingness is documented, and held-out baseline
predictions are assessed. Immediate goal 3 names the first step: "assess a
longitudinal dataset and reproduce a baseline transition example." This
document is the assessment half. It is a desk evaluation of the Panel Study
of Income Dynamics (PSID) against the plan's own checklist — data
suitability, geography access, attrition, survey weights, and coverage of
relevant subgroups — from the study's published documentation and
peer-reviewed descriptions. Every factual claim carries its source. It
makes **no** claims about transition estimates: none have been computed,
and the reproduction step remains open.

**Verdict: adopt PSID as the R2 candidate dataset, with three declared
limitations** — biennial interviewing since 1997 (annual simulation steps
need a documented cadence decision), public geography capped at
state/region (county context requires the restricted geocode enclave), and
a two-wave baseline panel that measures ordinary transitions at two-year
spacing. None of the three blocks the R2 exit criteria; all three shape
the design.

## What R2 needs from a dataset

- Household representation: linked members, children's ages, shared
  resources, membership-change rules (plan §4).
- Ordinary (non-event) employment and earnings transitions, plus enough
  history for duration-style state (plan §1).
- Intergenerational linkage, because the graph's structural layer is
  parent-to-child persistence (plan §1, §4).
- Geography compatible with the engine's place inputs, or an explicit
  coarse-geography decision.
- Attrition, weights, and subgroup coverage good enough for held-out
  baseline validation (plan "Evaluation program", Baseline bullet).

## Assessment by criterion

### Design and cadence

PSID began in 1968 with a nationally representative sample and is the
longest-running longitudinal household survey in the world
([PSID main site](https://psidonline.isr.umich.edu/)). Interviews were
annual 1968–1997 and biennial thereafter
([ICPSR series 131](https://www.childandfamilydataarchive.org/cfda/cfda/series/131)).
The 2023 interviewing wave is released, with a 2025 user manual
([PSID-2023 Main Interview User Manual](https://psidonline.isr.umich.edu/data/Documentation/UserGuide2023.pdf)).

Consequence: the plan's candidate annual time step does not match the
modern wave spacing. R2 must either simulate biennial steps, interpolate
with a declared assumption, or estimate two-year transition probabilities.
The honest default is the third: estimate transitions on the wave grid and
declare the cadence, never silently resample biennial data into annual
paths.

### Household representation

One person per family is interviewed each wave, and families are followed
as they split and recombine
([ICPSR series description](https://www.childandfamilydataarchive.org/cfda/cfda/series/131)).
PSID's design follows descendants of original sample members — the "PSID
gene" — with seventh-generation members present by 2017, and the Family
Identification Mapping System (FIMS) generates custom files linking
relatives within and across generations; the 2015 wave contains 4,822
parent-child and 1,371 grandparent-grandchild pairs each heading their own
interviewed unit ([Johnson et al. 2018, "Fifty Years of the Panel Study of
Income Dynamics"](https://pmc.ncbi.nlm.nih.gov/articles/PMC6820672/)).
Child-focused content arrives through the Child Development Supplement —
1997 (ages 0–12, three waves through 2007–08) and the new CDS launched
2014 (ages 0–17, repeating every 5–6 years) — and the Transition to
Adulthood study, biennial from 2005 and expanded in 2017 to all young
adults in PSID families (Johnson et al. 2018).

Consequence: the household node structure the engine needs — members,
ages, membership change, intergenerational links — is representable from
public family/individual files plus FIMS maps. This is the strongest
suitability finding.

### Earnings and employment content

Income from all sources is core content; generated variables provide
taxable income, earnings, and weeks worked for primary respondents and
spouses/partners (Johnson et al. 2018, citing Duffy 2011). Aggregate PSID
income runs a few percentage points above CPS at each percentile and
within 3.7% of NIPA aggregates on average over 1968–2010 (Johnson et al.
2018, citing Cynamon & Fazzari 2015).

Consequence: earnings and employment state variables for the baseline
model exist for both partners, supporting the plan's requirement to track
partner resources rather than scaling children off one worker. Exact
variable naming and definition drift across waves is an at-acquisition
verification item.

### Geography

Public-release files carry generalized geography — census region, **state
of residence**, and a collapsed Beale rural-urban code
([PSID FAQ: obtaining the data](https://psidonline.isr.umich.edu/Guide/FAQ.aspx?Type=3);
[SIMBA restricted-data page](https://simba.isr.umich.edu/restricted/processreq.aspx),
which states state of residence is on the public-use file). County, tract,
block-group, and address-level geographies live in the restricted
Geospatial Match files, available only by data-use contract through the
PSID Virtual Data Enclave
([PSID Geospatial](https://simba.isr.umich.edu/restricted/Geospatial.aspx);
Johnson et al. 2018).

Consequence: the engine's county places layer (mobility percentiles,
Gamma–Poisson county mortality) **cannot** be matched to PSID households
from public data. The R2 baseline starts with state/region geography —
which is compatible with the model's national and regional framing — and
county resolution is a separately gated follow-up requiring an
application. This limitation is declared, not worked around.

### Attrition and retention

Wave-to-wave response rates have run about 94% since 1970, with overall
response rates near 91%; the 2017 wave met the 95% reinterview goal.
Attrition is steeper among lower-income families, but validation work
finds little-to-no evidence of biased intergenerational estimates
(Johnson et al. 2018, citing Fitzgerald et al. 1998 and Fitzgerald 2011).
Independent analyses report 94–98% wave-to-wave reinterview (Gouskova et
al. 2010, cited in the
[longitudinal weights documentation](https://psidonline.isr.umich.edu/data/weights/Long-weights-doc.pdf)),
and cumulative response rates for the original 1968 cohort are documented
in [Heeringa's 2018 technical series paper](https://psidonline.isr.umich.edu/publications/papers/tsp/2018-01_6815CRR_68SP.pdf).

Consequence: attrition is manageable and measurable — exactly what R2's
"missingness is documented" criterion needs. The low-income-skew and
survivorship composition must travel with every baseline estimate, and the
longitudinal weights (below) are the declared correction, not an optional
extra.

### Survey weights

Longitudinal individual and family weights exist for the core and
immigrant samples
([1993–2005 revision](https://psidonline.isr.umich.edu/data/weights/Long-weights-doc.pdf),
[2009](https://psidonline.isr.umich.edu/data/weights/long_weight_09.pdf),
[2017](https://psidonline.isr.umich.edu/data/weights/long_weight_17.pdf)),
and cross-sectional individual weights are calibrated to census population
totals from the longitudinal family weights
([2017–2021 series](https://psidonline.isr.umich.edu/data/weights/cross_sec_weights_21.pdf)).

Consequence: both transition estimation (longitudinal weights) and
held-out distribution checks against population margins (cross-sectional
weights) are supported without external data.

### Subgroup coverage

The 1968 baseline was 4,802 households — 2,930 nationally representative
(SRC) plus a 1,872 low-income oversample (SEO) — with about 18,000
individuals; cumulative participation over fifty years is 80,666
individuals, and the 2017 wave interviewed 9,607 families (Johnson et al.
2018). Immigrant refresher samples were added in 1997–1999 (511 families)
and 2017 (615 post-1997 immigrant families; 455 completed interviews at a
75.5% response rate)
([PSID technical paper 2000-04](https://psidonline.isr.umich.edu/publications/papers/tsp/2000-04_Imm_Sample_Addition.pdf);
[2017 user guide](https://psidonline.isr.umich.edu/data/Documentation/UserGuide2017.pdf);
Johnson et al. 2018).

Consequence: the working-age prime-age population the engine's causal
layer targets (e.g., the male 45–54 mortality scope) and the low-income
strata where displacement concentrates are both observable. Sample sizes
per cell still bound subgroup resolution — cell counts are an at-extraction
check, not an assumption.

### Access

Public-use data are free after registration and acceptance of the
conditions of use; no ICPSR membership is required
([PSID Getting Started](https://psidonline.isr.umich.edu/GettingStarted.aspx);
[conditions of use](https://simba.isr.umich.edu/u/conduse.aspx)).

Consequence: acquisition is not a blocker. An owner-registered account and
a Data Center extract (family + individual files, with weights and FIMS
maps) is the concrete next step.

## Declared limitations

1. **Biennial cadence since 1997.** Baseline transitions are two-year
   transitions. The plan's annual-step candidate requires a declared
   mapping; silent interpolation is refused.
2. **Public geography ends at state.** County-level baselines or
   validation would need the restricted geocode enclave — a separate
   application the owner would have to sponsor. The R2 baseline is
   state/region until then.
3. **Baseline panel ≠ causal layer.** PSID supplies ordinary transitions.
   The displacement effects already admitted stay separately sourced
   causal estimates; the plan's overlap rule (§2) forbids a transition
   model that embeds the same response the intervention layer adds.
4. **Unverified at desk distance:** exact variable names and definitions
   by wave; wave-by-wave state-variable availability; the 2023 user
   manual's response-rate and exit/death tracking tables (the manual's
   PDF was not machine-readable here). All are first-week verification
   items once the extract exists.

## Decision and next steps

1. **Adopt PSID as the R2 dataset** for employment, earnings, and
   household-resource baselines, with the four limitations above declared
   in every derived artifact.
2. **Acquire:** owner registers, downloads recent-wave family and
   individual files plus longitudinal/cross-sectional weights (Data
   Center), and the FIMS link files for intergenerational work.
3. **Verify at acquisition:** variable naming by wave, state-of-residence
   availability, exit/death recording, and per-cell sample sizes for the
   target populations.
4. **Reproduce one baseline transition** (immediate goal 3's second
   half): a two-wave employment/earnings transition for prime-age
   workers, weighted, with a held-out-wave validation report — the first
   R2 artifact, to be reviewed before any household simulation is built
   on it.

## Source register

- [PSID main site](https://psidonline.isr.umich.edu/) — study overview.
- [PSID Getting Started](https://psidonline.isr.umich.edu/GettingStarted.aspx) — free registration access.
- [PSID conditions of use](https://simba.isr.umich.edu/u/conduse.aspx) — no ICPSR membership required.
- [ICPSR/Child and Family Data Archive series 131](https://www.childandfamilydataarchive.org/cfda/cfda/series/131) — annual 1968–1997, biennial after; one respondent per family.
- [Johnson et al. (2018), Fifty Years of the PSID (PMC6820672)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6820672/) — sample sizes, retention, income content, CDS/TAS, PSID gene/FIMS, restricted geospatial scope.
- [PSID-2023 Main Interview User Manual (Release 2025)](https://psidonline.isr.umich.edu/data/Documentation/UserGuide2023.pdf) — current-wave response-rate tables (verify at acquisition).
- [PSID FAQ: obtaining the data](https://psidonline.isr.umich.edu/Guide/FAQ.aspx?Type=3) — public geography: region, state, Beale code.
- [SIMBA: obtaining restricted data](https://simba.isr.umich.edu/restricted/processreq.aspx) — state of residence on the public-use file.
- [SIMBA: PSID Geospatial](https://simba.isr.umich.edu/restricted/Geospatial.aspx) — county/tract restricted enclave access.
- [PSID technical paper 2000-04](https://psidonline.isr.umich.edu/publications/papers/tsp/2000-04_Imm_Sample_Addition.pdf) — 1997 sample reduction and immigrant addition.
- [PSID 2017 user guide](https://psidonline.isr.umich.edu/data/Documentation/UserGuide2017.pdf) — 2017 immigrant refresher.
- [Gouskova et al. (2008), longitudinal weights 1993–2005](https://psidonline.isr.umich.edu/data/weights/Long-weights-doc.pdf).
- [Heeringa (2018), cumulative response rates 1968–2015](https://psidonline.isr.umich.edu/publications/papers/tsp/2018-01_6815CRR_68SP.pdf).
- [2017 longitudinal weights](https://psidonline.isr.umich.edu/data/weights/long_weight_17.pdf); [2021 cross-sectional individual weights](https://psidonline.isr.umich.edu/data/weights/cross_sec_weights_21.pdf).
