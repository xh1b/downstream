# Related work: life-course simulation and causal scenarios

Updated September 10, 2026. This is a selective comparison based on primary
project documentation and research papers, not a systematic review or a
ranking of scientific quality. “Prior attempts” includes active research
programs with substantial achievements.

The ambition to simulate consequences for people and families has close
predecessors. Useful search terms are **dynamic microsimulation**, **life-course
simulation**, **causal policy simulation**, and **population health
microsimulation**. Their existence gives downstream foundations to learn from
and a clearer standard against which to evaluate its contribution.

## Closest precedents

| Project | Documented focus | Relevance to downstream |
|---|---|---|
| SimPaths | Individual and household careers, relationships, health, and finances | Life-course state, feedback, modularity, and household context |
| LifeSim | Developmental, economic, social, and health outcomes across an English birth cohort's lifespan | Childhood-to-adulthood integration and long-horizon assumptions |
| DYNASIM | Demographic and economic transitions for individuals and families | Baseline trajectories, family structure, and population accounting |
| Future Elderly Model | Health and economic scenario analysis | Cross-domain consequences and an empirical research program |

### SimPaths

SimPaths is an open-source framework for individual and household life-course
analysis. Its methods paper describes interconnected domains and validation
against observed data. Its documented scope makes it a close architectural
reference; downstream should not claim that open, multi-domain life-course
modeling is new. [Bronka et al. (2025), methods paper](https://www.microsimulation.pub/articles/00318),
[project documentation](https://simpaths.org/).

**What to investigate:** how baseline transitions, household relationships,
scenario assumptions, and validation are separated. Compare the user-facing
interpretation of an event with the mechanisms actually being changed.

**Boundary of the comparison:** country-specific assumptions and data cannot
be transferred to a US displacement question simply by adopting the design.

### LifeSim

LifeSim models developmental, social, economic, and health outcomes from
birth to death for an English birth cohort. This is directly relevant to
the goal of following consequences across life domains and stages.
[Skarda, Asaria, and Cookson (2021), methods paper](https://microsimulation.pub/articles/00228).

**What to investigate:** how source estimates and baseline targets enter the
model, how timing is represented, and how simulated outcomes are checked
against external data. Inspect the assumptions that connect childhood
conditions with later outcomes before extending downstream's generations.

**Boundary of the comparison:** a birth-cohort policy model and a calculator
initialized at an arbitrary adult age solve different initialization problems.

### DYNASIM

Urban Institute's DYNASIM advances individuals and families through demographic
and economic events, including births, deaths, marriage, divorce, employment,
earnings, disability, and retirement. It provides a concrete precedent for
simulating lives within family context.
[Urban Institute, model summary (2015)](https://www.urban.org/sites/default/files/2022-04/dynasim_summary_march_23_2015_0.pdf).

**What to investigate:** household resource accounting, life histories, and
consistency between individual transitions and population totals. Separate
alignment to known totals from independent evaluation of event effects.

**Boundary of the comparison:** its retirement and aging applications do not
establish that arbitrary life shocks can be causally evaluated from any profile.

### Future Elderly Model

USC's Future Elderly Model connects health and economic outcomes to examine
alternative health and policy scenarios. It is an example of a sustained
research program built around a simulation model.
[USC Schaeffer, project documentation](https://schaeffer.usc.edu/data/future-elderly-model/).

**What to investigate:** how alternative scenarios alter trajectories and
how health consequences connect to economic and public-resource outcomes.

**Boundary of the comparison:** evidence and baseline dynamics for an older
population cannot be assumed to apply to working-age parents or children.

## Other relevant traditions

Dynamic microsimulation has a longer lineage, including Orcutt's work,
CORSIM, Statistics Canada's LifePaths, and SSA's MINT. A later systematic
comparison should examine their documented versions and applications rather
than assign blanket labels for openness, uncertainty, or validation. The
[SimPaths review](https://www.microsimulation.pub/articles/00318) is a useful
starting bibliography, not a substitute for reading each model's sources.

Agent-based models are relevant when consequences depend on interactions
between people, firms, or neighborhoods. Reproducibility, behavioral
assumptions, and calibration should be evaluated for each implementation.
The previous version of this document used broad, insufficiently sourced
claims about CovidSim; those claims are removed. There is no scientific gain
in presenting a different modeling tradition as uniformly unreliable.

Regional economic models address inter-industry and local spillovers. Their
scale differs from a person's life history. Downstream currently uses a
local-employment multiplier at a count boundary; it does not reproduce a
regional equilibrium model. A future comparison of REMI and IMPLAN should
examine their actual specifications, geography, and scenario definitions.

Forecast verification contributes proper scoring rules and calibration
checks. A cited path is not validated merely because each constituent study
exists. Likewise, matching a historical population total is not evidence
that an intervention effect transports correctly. Keep baseline validation,
causal event validation, and numerical verification separate.

## Positioning the contribution

Downstream currently propagates published response coefficients conditional
on an externally supplied exposure. It lacks a complete baseline life-course
model. Its prospective contribution is the combination of inspectable
provenance, evidence applicability, restrictions on causal composition,
explicit unknowns, and accessible scenario comparison.

Those are design goals to demonstrate empirically. No claim is made that
other models lack provenance, uncertainty analysis, or published validation.
No “first” or “only” claim follows from this selective review.

A useful research question is: **When can estimates from separate studies be
combined into reliable life-course scenario predictions, and when should the
model refuse that composition?** Evaluate whether the restrictions improve
out-of-sample performance or make unsupported extrapolation easier to detect.

## Comparative research tasks

1. Reproduce one documented example from SimPaths and LifeSim, subject to data
   access and licensing, and record the actual assumptions and outputs.
2. Compare a common narrow question across downstream, a simple direct-effect
   baseline, and an appropriate documented comparator where compatible inputs
   and estimands are available. Do not force unlike outputs into one score.
3. Record initialization data, transition estimation, causal identification,
   household links, place treatment, uncertainty, validation, and user-facing
   explanations in a versioned evidence matrix.
4. Identify reusable methods before building equivalents. Source access and
   integration feasibility are separate questions from conceptual usefulness.
5. Expand the comparison before making a novelty or superiority claim.

The forward research goals are in [LIFE_COURSE_RESEARCH_PLAN.md](LIFE_COURSE_RESEARCH_PLAN.md).
The calculator design is in [WEBSITE_EXPERIENCE_PLAN.md](WEBSITE_EXPERIENCE_PLAN.md).
