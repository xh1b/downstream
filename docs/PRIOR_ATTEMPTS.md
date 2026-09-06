# PRIOR ATTEMPTS — models like this one, and what we take from each

The downstream model is not the first attempt to simulate population
consequences from economic shocks. Four traditions matter. Each is
summarized with what we adopt and what we refuse. Nothing here is
proprietary; these are all publicly documented modeling programs.

## 1. The Orcutt lineage — dynamic microsimulation

**What it is.** Guy Orcutt's 1957 "microanalytic model" idea: simulate
a synthetic population of persons forward year by year, applying
transition probabilities (marriage, birth, work, death), and aggregate
the micro ledger to answer policy questions. The US program family:

- **DYNASIM** (Urban Institute, 1970s-, DYNASIM3/DYNASIM4) — long-run
  Social Security and retirement-income projection.
- **CORSIM** (Cornell, Caldwell) — 1960-2050 US synthetic population,
  the longest-running dynamic model.
- **SSA's MINT** (Modeling Income in the Near Term) — Census SIPP
  panels projected to retirement; the Social Security
  Administration's workhorse for distributional solvency analysis.

**What we adopt.** The core ledger idea: consequences attach to
persons/families and aggregate to populations by summation, never by
re-scaling a national coefficient. Their alignment discipline
(calibrating transitions to known aggregates so the synthetic
population tracks history — Li & O'Donoghue 2013 survey the methods)
is the same instinct as our V1 retrodiction.

**What we refuse.** Decade-scale synthetic populations need hundreds
of unmeasured transition rates estimated by smoothing and judgment;
errors compound silently for 50 simulated years. Our scope is one
exposure propagating through ~30 cited links over 1-3 generations.
Every one of our numbers names a study; we refuse uncited transitions,
which is why the model stops where it stops.

## 2. Agent-based epidemic/behavior models — the CovidSim lesson

**What it is.** Individual-level simulation with behavioral rules and
interaction networks. The cautionary case: **CovidSim** (Ferguson et
al., Imperial College) drove March 2020 lockdown decisions on
parameters that were, in the team's own postmortem, "not estimated
from actual Covid data" — a codebase with 19 years of accretion and
no settled way to reproduce a run (the 2020 code audit, publicly
documented, found thousands of code paths and non-deterministic
output).

**What we adopt.** Nothing mechanically; we stay deterministic
inside a draw, seeded, versioned, and reproducible.

**What we refuse.** Policy-grade influence from a model whose
parameters outran its evidence. The CovidSim episode is the standing
argument for our honesty architecture: an uncited parameter is a bug,
a non-reproducible output is a bug, and influence must wait for the
validation program, not the other way around.

## 3. Regional input-output models — REMI / IMPLAN

**What it is.** Multiplier tables for local economies: a job lost in
industry i propagates through inter-industry flows to a total local
effect. REMI adds dynamics; IMPLAN is the standard commercial
implementation used in every "economic impact study."

**What we adopt.** The multiplier layer as ONE component: our
community stream (Moretti's local multipliers, school-spending
pass-through) is the honest version of this tradition.

**What we refuse.** Impact-study practice: pick a multiplier, multiply
by the press-release number, publish. Multipliers are the model's
least-cited numbers in practice — ours are cited (moretti2010, with
its own manufacturing-to-high-tech spread as the band), and they are
never the whole answer.

## 4. Forecast verification — the discipline we join

**What it is.** The weather/scoring tradition (Gneiting & Raftery
2007; Gneiting & Katzfuss 2014): probabilistic forecasts are scored
with proper scoring rules (CRPS), calibration is checked against
realized frequencies, and sharpness (narrow bands) only counts when
calibration holds.

**What we adopt.** The whole V3 stage: pre-registration, proper
scores, calibration curves, published misses. A modeled band that
misses 40% of the time is a wrong model no matter how plausible its
citations are.

**What we refuse.** The social-science habit of "validation by
citation" — treating published support for each link as validation of
the composition. Composed models fail in their own ways; that is why
V1/V2 exist and why the direct-vs-IGE cross-check (V0) runs on every
validate call.

## 5. Where this sits among them

| | DYNASIM/CORSIM/MINT | CovidSim-class ABM | REMI/IMPLAN | downstream |
|:--|:--|:--|:--|:--|
| unit of compute | synthetic person | agent | region | cited ledger step |
| parameter source | estimated + judgment | mixture | tables | citation-locked |
| uncertainty | some (stochastic sims) | rarely | none | bands + MC, mandatory |
| validation | alignment to aggregates | post-hoc | rarely | V0-V3 program |
| reproducibility | partial (code age) | failed publicly | proprietary | seeded + versioned |
| scope honesty | acknowledged drift | overreach | narrow but oversold | fail-loud on missing inputs |

The niche: nothing in the four traditions binds every simulated step
to a published effect size with a precision tier and publishes its
own misses. That is the experiment this repo runs.

## Key public sources

- Orcutt 1957, "A New Type of Socio-Economic System," REStat 39:108.
- Li & O'Donoghue 2013, "A survey of the microsimulation alignment
  method," IMA Journal of Management Mathematics 24:173.
- Zaidi & Rake 2001, "Dynamic microsimulation models: a review and
  some directions for further development," STICERD research note.
- Gneiting & Raftery 2007, "Strictly Proper Scoring Rules,
  Prediction, and Estimation," JASA 102:359.
- Imperial College CovidSim: the code went public on GitHub in 2020
  and an independent review documented its structure and
  non-determinism; the team's own published responses acknowledged the
  Covid parameters were judgment-based rather than estimated from
  Covid outcome data.
- Moretti 2010, "Local Multipliers," AER 100:373.
- Miller et al. (SSA), MINT documentation; Urban Institute DYNASIM3
  documentation; CORSIM documentation (Cornell).
