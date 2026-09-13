# SIPP baseline-data assessment — 2026-09-13

## Scope and verdict

This is the R2 dataset assessment that
[PSID_BASELINE_DATA_ASSESSMENT_2026-09-13.md](PSID_BASELINE_DATA_ASSESSMENT_2026-09-13.md)
pointed to after PSID was ruled out on the ICPSR LLM policy. Same
checklist — data suitability, geography access, attrition, survey
weights, subgroup coverage, and now terms compatibility with this
repository's LLM-driven workflow — applied to the Census Bureau's Survey
of Income and Program Participation (SIPP). Every factual claim carries
its source. As with the PSID document, **no transition estimates exist
yet**; this is the selection step only.

**Verdict: adopt SIPP as the R2 baseline dataset.** It is the only major
US household panel whose terms are compatible with an open-source,
LLM-built repository: public-use files are free to download with no
registration and may be freely redistributed. Its limitations are real
and declared below — coarse public geography, short panel windows,
higher attrition than PSID, and no child/intergenerational supplements —
but every one of them bounds scope rather than blocking the R2 exit
criteria.

## Terms and workflow compatibility (the decisive criterion)

"Anyone may download SIPP public-use data from the SIPP data website. No
registration is required to download the data"
([National Academies, The 2014 SIPP Redesign, ch. 4](https://www.nationalacademies.org/read/27169/chapter/4)).
Public-use files are US-government works published for unrestricted use —
no click-through license, no redistribution ban, no third-party-transfer
clause, and no platform-level AI policy: the ICPSR LLM restriction that
ruled out PSID attaches to ICPSR-distributed data, and SIPP is not
distributed under it. The microdata can therefore live in this
repository, be read and processed by the LLM agents that build it, ship
inside reproducibility bundles, and be redistributed by anyone. This
inverts PSID's fatal property, and it outweighs every scientific
difference below. (Title 13 confidentiality governs what Census releases
in public files, not how released files are processed.)

## Assessment by criterion

### Design and cadence

SIPP is a continuous series of national panels of noninstitutionalized
households beginning in 1984
([Urban Institute](https://www.urban.org/sites/default/files/publication/99987/adding_historical_earnings_to_the_sipp.pdf)).
Through the 2008 panel, interviews came every 4 months with income
reported monthly and labor-force status weekly for the intervening period
([FRBSF working paper](https://www.frbsf.org/wp-content/uploads/wp2014-06.pdf));
the 2008 panel was the longest, exceeding five years
([National Academies, ch. 1](https://www.nationalacademies.org/read/24864/chapter/3)).
The 2014 redesign moved to annual interviews that reconstruct monthly
detail within each wave, and since 2021 panels overlap annually: the 2021
panel's Wave 1 (about 24,000 interviewed households) referenced calendar
2020, with a fresh panel launched each year
([Census, organizing principles](https://www.census.gov/programs-surveys/sipp/methodology/organizing-principles.html);
[Pew methodological notes](https://www.pewresearch.org/) on recent panel
sizes).

Consequence: SIPP offers *both* fine-grained transitions (2008 panel:
monthly income, weekly employment, 2008–2013) and current annual
transitions (2021+ panels). The cadence problem PSID forced — biennial
data, annual ambitions — has two honest solutions here: estimate annual
transitions on the current panels, or sub-annual transitions on the 2008
panel with its recency limitation declared. Either is better matched to
the plan's annual-step candidate than PSID's grid.

### Household representation

Each household has a reference person, with every member's relationship
to that person recorded (32 categories after the 2014 relationship
redesign) plus parent pointers
([Census, SIPP content](https://www.census.gov/programs-surveys/sipp/about/sipp-content-information.html);
[Statistical Policy Working Paper on household relationships](https://s3.amazonaws.com/sitesusa/wp-content/uploads/sites/242/2014/04/MRFHS_StatisticalPolicyWorkingPaper201408.pdf)).
Persons are followed across waves via stable identifiers (SUID + PNUM),
with the 2008 Users' Guide documenting the match mechanics and nonmatch
causes
([Users' Guide ch. 13](https://www2.census.gov/programs-surveys/sipp/guidance/SIPP_2008_USERS_Guide_Chapter13.pdf)).

Consequence: linked members, children's ages, membership change, and
shared-resource accounting — the plan §4 requirements — are all
representable. Reference-person changes across waves are a known trap the
estimation code must handle explicitly.

### Earnings and employment content

The core collects income at monthly frequency and labor-force status at
weekly level ([FRBSF](https://www.frbsf.org/wp-content/uploads/wp2014-06.pdf)),
with program participation a defining strength
([NACDA/ICPSR series](https://www.icpsr.umich.edu/sites/nacda/view/collections/135)).
Quality signals are mixed and must be recorded, not ignored: redesigned
SIPP's self-employment income estimate reaches 91% of the NIPA total
versus CPS ASEC's 35% ([National Academies, ch. 9](https://www.nationalacademies.org/read/24864/chapter/9)),
but aggregate income reporting relative to NIPA fell from 86% (1990) to
73% (2012) ([National Academies, ch. 7](https://www.nationalacademies.org/read/24864/chapter/9)).

Consequence: employment and earnings transitions for both partners are
directly measurable at the resolution the baseline model needs. The
declining income-capture ratio is a declared data-quality boundary and a
reason to validate against administrative-benchmarked estimates.

### Geography

Public-use files carry only coarse geography — the FCSM survey-profile
description states SIPP's public geography is effectively national-level
([NCES/FCSM](https://nces.ed.gov/fCSM/sipp.asp)); state and below require
restricted-access Census facilities ([Census
SIPP](https://www.census.gov/programs-surveys/sipp.html)), with the
[SIPP Synthetic Beta](https://www.census.gov/programs-surveys/sipp/guidance/sipp-synthetic-beta-data-product.html)
as an approved synthetic alternative. This is *weaker* than PSID, whose
public files include state of residence.

Consequence: the R2 baseline is national and census-region geography.
The engine's county places layer was already out of reach under PSID's
restricted geocodes; under SIPP it is equally out of reach, and the
state level is lost. Declared limitation, not a blocker for the R2 exit
criteria — which never required county resolution.

### Attrition

Initial nonresponse runs about 9–13% across panels, with cumulative
attrition usually over 20% by a panel's end
([Carr, Maestas, Mgmt — NBER w27672](https://www.nber.org/system/files/working_papers/w27672/w27672.pdf));
attrition has risen across recent panels
([Census/AAPOR working paper](https://s3.amazonaws.com/sitesusa/wp-content/uploads/sites/242/2014/05/IHSNG-aapor2004proceedingsrev2.pdf)).
This is worse than PSID's ~94% wave-to-wave retention.

Consequence: attrition is bounded by short panels and must travel as a
declared selection caveat on every baseline estimate, with longitudinal
weights applied. The two-wave transition artifact must report
wave-1-to-wave-2 retention for its estimation cells.

### Survey weights

Census publishes person weights, cross-sectional weights (WPFINWGT), a
separate Longitudinal Weights File for multi-wave person analysis, and
replicate weights for variance estimation
([Census weighting methodology](https://www.census.gov/programs-surveys/sipp/methodology/weighting.html);
[2023 weights overview handout](https://www2.census.gov/programs-surveys/sipp/2023/2023_SIPP_Weights_Overview_Handout_SEP23.pdf)).

Consequence: both transition estimation and held-out distribution checks
are supported from published files, with replicate-variance machinery
available for honest uncertainty on the baseline estimates.

### Subgroup coverage and intergenerational depth

Panels range from roughly 14,000 to 52,000 interviewed households
historically, with the redesigned panels sized around tens of thousands
of households
([National Academies, ch. 1](https://www.nationalacademies.org/read/24864/chapter/3)).
There is no CDS/TAS equivalent and no multigenerational tracking beyond
within-household parent pointers.

Consequence: prime-age worker transitions are well powered; the
intergenerational structural layer simply cannot be re-estimated here —
which the model already handles by sourcing persistence from published
studies through the citation pipeline, a route unaffected by any of
this.

## Declared limitations

1. **Short windows.** Panels last roughly three years (2008 panel the
   exception at 5+). Long-run baseline dynamics need chained or
   synthetic-cohort treatments, declared per use.
2. **Coarse public geography.** National/region only; state and county
   are restricted-facility territory.
3. **Attrition.** >20% cumulative per panel, rising across recent
   panels; longitudinal weights and cell-level retention reporting are
   mandatory, not optional.
4. **Income capture drift.** Aggregate income reporting fell to 73% of
   NIPA by 2012; earnings-based transitions must carry this caveat.
5. **No child/intergenerational supplements.** Structural persistence
   stays sourced from published literature, as it already is.

## Decision and next steps

**Adopt SIPP as the R2 dataset** for employment, earnings, and
household-resource baselines, with the five limitations above declared in
every derived artifact.

1. **Acquire:** download the 2008 panel (fine-grained transitions) and
   the current 2021+ panels (recency), the longitudinal weights files,
   and the Users' Guide — all free, all redistributable into this
   repository.
2. **Verify at extraction:** public geography fields actually present,
   monthly-detail structure in the redesigned panels, reference-person
   change handling, income variable naming across panels.
3. **First R2 artifact (unchanged in shape):** a weighted two-wave
   employment/earnings transition for prime-age workers with a
   held-out-wave validation report, reviewed before any household
   simulation builds on it.

## Source register

- [Census SIPP main page](https://www.census.gov/programs-surveys/sipp.html).
- [National Academies, The 2014 SIPP Redesign](https://www.nationalacademies.org/read/24864/chapter/4) — access terms, panel history, NIPA comparisons.
- [Census, organizing principles](https://www.census.gov/programs-surveys/sipp/methodology/organizing-principles.html) — waves, reference person.
- [Census, SIPP content](https://www.census.gov/programs-surveys/sipp/about/sipp-content-information.html) — relationships, parent pointers.
- [SIPP 2008 Users' Guide ch. 13](https://www2.census.gov/programs-surveys/sipp/guidance/SIPP_2008_USERS_Guide_Chapter13.pdf) — SUID/PNUM linking.
- [Census weighting methodology](https://www.census.gov/programs-surveys/sipp/methodology/weighting.html); [2023 weights handout](https://www2.census.gov/programs-surveys/sipp/2023/2023_SIPP_Weights_Overview_Handout_SEP23.pdf).
- [NBER w27672](https://www.nber.org/system/files/working_papers/w27672/w27672.pdf) — attrition magnitudes.
- [FRBSF WP 2014-06](https://www.frbsf.org/wp-content/uploads/wp2014-06.pdf) — monthly income, weekly employment status.
- [NCES/FCSM SIPP profile](https://nces.ed.gov/fCSM/sipp.asp) — public geography scope.
- [SIPP Synthetic Beta](https://www.census.gov/programs-surveys/sipp/guidance/sipp-synthetic-beta-data-product.html).
- [Urban Institute, adding historical earnings to SIPP](https://www.urban.org/sites/default/files/publication/99987/adding_historical_earnings_to_the_sipp.pdf) — panel series since 1984.
