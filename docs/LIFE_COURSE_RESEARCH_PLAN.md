# Research plan: a person, their family, and their possible futures

Status: future direction agreed in conversation, September 10, 2026.
Capabilities below are goals unless explicitly described as current. This
plan supersedes the earlier sequence that prioritized a long multigenerational
chain before baseline life dynamics and independent validation.

## Vision and scientific promise

Allow someone to describe a person and where they live, specify an event or
intervention, and explore how the distribution of possible futures changes
for that person, their household, and relevant community outcomes.

The target statement is: “For people with these characteristics in this
context, how do modeled outcomes differ under this specified scenario?”
“All downstream effects” is a direction for evidence discovery, not a promise
of exhaustive coverage. An unsupported path stays visible as unknown. The
calculator never converts a population estimate into a claim about a known
individual's destiny.

The first research question is whether estimates from separate studies can
be composed into reliable scenario predictions under explicit compatibility
restrictions. A second is whether people can understand and use those
predictions without mistaking assumptions for personal facts.

## Current position

The engine has cited coefficients, typed ledger operations, conditional count
conversions, parameter sampling, analytic checks, sensitivity experiments, and
partial external comparisons. It does not yet simulate a household's ordinary
life course or establish arbitrary personalized treatment effects.

The [model card](MODEL_CARD.md) documents population applicability,
structural assumptions, and limits on independent validation. Public results
must retain those qualifications and each outcome's applicability decision.
The [related-work comparison](PRIOR_ATTEMPTS.md) identifies established models
to learn from; openness and multi-domain simulation alone are not novelty.

## The change in modeling approach

### 1. Model the reference life course

Start from a distribution of plausible states consistent with the supplied
profile. Advance age, employment, earnings, household membership, and other
supported variables through time. Retain relevant histories: duration of
unemployment, previous events, or accumulated resources can affect transitions.

The reference scenario means no specified initiating event, under stated
background conditions. It does not mean a frozen or perfect life. Specify
calendar year, geography, background labor-market conditions, and the
resolution at which time is simulated. Annual steps are a candidate starting
point; short-duration events need finer timing or a documented approximation.

Longitudinal data such as [PSID](https://psidonline.isr.umich.edu/default.aspx)
were first assessed, then ruled out for this project's workflow: PSID is
distributed under ICPSR terms whose LLM policy forbids sharing the
microdata with cloud LLM agents — the way this repository is built and
operated ([2026-09-13 PSID assessment](PSID_BASELINE_DATA_ASSESSMENT_2026-09-13.md);
it remains citation-only). The Census Bureau's
[SIPP](https://www.census.gov/programs-surveys/sipp.html) was adopted in
its place ([2026-09-13 SIPP assessment](SIPP_BASELINE_DATA_ASSESSMENT_2026-09-13.md)):
public-domain, redistributable, LLM-compatible, with declared
limitations — short panels, coarse public geography, higher attrition.
No baseline transitions have been computed yet; the download, variable
verification, and one held-out transition reproduction are the next R2
steps.

### 2. Separate three evidential roles

| Role | Question answered | Required record |
|---|---|---|
| Baseline transition | How do similar lives ordinarily evolve? | Dataset, sample, estimation procedure, uncertainty, predictive validation |
| Causal intervention | What changes because this event or intervention occurs? | Treatment/comparison, identification assumptions, effect scale, population, timing |
| Structural assumption | How are incomplete pieces connected? | Explicit formula, rationale, alternatives, sensitivity, conditions for refusal |

Baseline transitions can be estimated from documented observational data.
They must not silently become causal effects. An intervention coefficient
cannot simply be added to a transition model that already embeds the same
response. Specify how each intervention modifies the reference process and
check for overlap. Longitudinal causal methods provide relevant foundations;
see [Hernán and Robins, Causal Inference: What If](https://miguelhernan.org/whatifbook).

The provenance rule becomes “every component has an appropriate evidential
record,” while causal claims retain stricter identification requirements.
This is a future design change, not permission to invent current coefficients.

### 3. Personalize within the evidence

Distinguish baseline-risk predictors from demonstrated effect modifiers.
Age can alter absolute risk without evidence of a different relative effect;
a county baseline does not establish a county-specific causal response.

For each result, record the studied population, supplied profile, unsupported
characteristics, and whether the estimate is directly applicable, pooled, or
extrapolated. Use partial pooling only with a declared model. Never assign a
fabricated precision percentage to “people like you.” Missing inputs should
be integrated over a documented distribution or requested when essential.
A person's details should influence results only through supported mechanisms.

### 4. Represent households and communities explicitly

Households need linked members, children's ages, shared resources, and rules
for membership changes. Track partner earnings and relevant buffers rather
than treating children as a multiplier on every worker.

Community outcomes require their own population, exposure scale, and response
model. A plant closure and an isolated job loss need not have proportional
spillovers. Avoid adding a person's loss, their household's inclusive total,
and an overlapping regional total into one “overall damage” number.

### 5. Define events and their combinations

Every event has onset, duration, dose, eligibility, and a counterfactual.
Distinguish involuntary displacement from leaving work voluntarily. Record
whether a scenario changes employment, earnings, or both.

Order matters for multiple events. Admit interactions only when justified,
otherwise report named alternatives or block the joint claim. Include
recovery and protective interventions in the acquisition queue. A sequence
editor on the website must not imply that arbitrary event composition works.

### 6. Compare distributions without claiming individual counterfactual truth

Draw uncertain parameters and baseline models separately from stochastic
life events. Use shared model draws across comparison arms where warranted.
Common random numbers can reduce Monte Carlo noise; their use does not
identify the cross-world dependence of one person's potential outcomes.

Report arm-specific distributions and expected contrasts. A distribution of
individual treatment effects requires additional identification assumptions.
Keep parameter, baseline, exposure, process, and structural uncertainty
separate where a joint model is unavailable. A full uncertainty decomposition
is itself a research task, not a set of numbers to fill by convention.

## Milestones and acceptance criteria

All unfinished milestones are **planned**. Each should produce a reviewable
artifact and evidence of meeting its exit criteria, not just more code.

| ID | Goal and deliverable | Completion criterion |
|---|---|---|
| R0 | Repair current headline estimands; source extraction and correction memo | Coherent mortality profile and phase boundaries; rate/risk distinction; null-event and same-place invariants; refreshed validation |
| R1 | Evidence and estimand registry; data dictionary and admission examples | Baseline, causal, and structural roles separated; incompatible scale/window/population and overlapping total/mediated paths refused |
| R2 | Baseline household model; initialized cohort and transition report | Supported variables evolve plausibly; household accounting reconciles; missingness is documented; held-out baseline predictions assessed |
| R3 | Five-year displacement comparison; reproducible scenario report | Reference and event arms share initial conditions; event timing is explicit; supported employment, earnings, and household resources have traceable contrasts |
| R4 | Independent event evaluation; frozen bridge and scorecard | Compatible exposure/outcome data withheld from fitting; all preregistered outputs reported; compared with simple alternatives; misses retained |
| R5 | Applicability and uncertainty report | Subgroup performance and evidence gaps visible; unsupported profiles refused or labeled; interval scope checked; sensitivity stable enough for intended use |
| R6 | Evaluated calculator study; comprehension report | Target users can explain the comparison, horizon, population meaning, and key limitations; website release criteria met |
| R7 | Wider supported scenarios and one protective intervention | Each new event has its own causal contract and evaluation; combinations do not assume unidentified interactions |
| R8 | Longer horizons and descendants | Additional transitions, timing, transport, and endpoint validation justify extending beyond the first household window |

R1 and design research for R6 can proceed alongside R0. The numerical claims
in R3 depend on R0-R2. R4 begins with an evaluation protocol before model
selection; independent outcomes are not used to choose the specification.
R8 follows evidence readiness, not the appeal of a long causal story.

## First substantial demonstration

Use a synthetic household with a working-age adult, optional partner, and
children whose ages are specified. Compare five years under no initiating
displacement and involuntary displacement at a stated date.

Start with employment, earnings, and household resources only where suitable
transitions and causal effects can be estimated. The current long-run
coefficients must not be relabeled as annual five-year trajectories. Add a
protective intervention only after its independent effect and eligibility
are justified. Other domains appear as coverage gaps rather than zero effects.

The report should contain the input profile, definition of both scenarios,
trajectories and cumulative measures, uncertainty scope, evidence applicability,
assumptions that change the answer, and the validation status. A small result
set meeting this contract is a stronger milestone than a large unvalidated graph.

## Evaluation program

- **Numerical:** null-event invariance, same-place cancellation, legal state
  transitions, resource accounting, death as an absorbing state, reproducible
  independent designs, and independent mathematical oracles.
- **Baseline:** held-out distributions and transition frequencies across time,
  place, and supported subgroups. Record where calibration targets were used.
- **Event effects:** independent compatible events or designs, measurement
  uncertainty, and comparison with direct-effect and simple baseline models.
- **Intervals:** assess probabilistic coverage only for intervals claiming it;
  distinguish support envelopes and structural alternatives.
- **Prospective:** independently timestamp one forecast before its outcome
  window and publish its eventual result, including failure.
- **Understanding:** evaluate interpretation and usefulness with the website
  tasks in [WEBSITE_EXPERIENCE_PLAN.md](WEBSITE_EXPERIENCE_PLAN.md).

Potential research outputs include a benchmark of compatible event studies,
a reproducible evidence registry, an evaluation of composition restrictions,
and a user study of communicating causal scenarios. None requires claiming
that the complete life simulator already exists.

## Immediate goals

1. Complete R0 and classify the current active parameters under R1.
2. Write the first household scenario's estimand, variables, and data needs.
3. Assess a longitudinal dataset and reproduce a baseline transition example.
4. Freeze the independent evaluation question and candidate data before fitting.
5. Prototype the result explanation with fictional or existing explicitly
   limited scenarios; conduct comprehension interviews before visual polish.

Scientific tasks are tracked through these milestone IDs. The graph work is
specified in [CAUSAL_GRAPH_PLAN.md](CAUSAL_GRAPH_PLAN.md); extraction mechanics
remain in [LITERATURE_ACQUISITION_PLAN.md](LITERATURE_ACQUISITION_PLAN.md).
