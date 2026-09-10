# Causal graph and life-course model plan

Updated September 10, 2026. This is the model-design companion to
[LIFE_COURSE_RESEARCH_PLAN.md](LIFE_COURSE_RESEARCH_PLAN.md), which defines the
research milestones and their order. The calculator experience is planned in
[WEBSITE_EXPERIENCE_PLAN.md](WEBSITE_EXPERIENCE_PLAN.md).

The revised sequence prioritizes corrected estimands, baseline household
trajectories, and independent validation before a distant multigenerational
chain. The previously proposed grandchild birth-weight chain is retained as
a later research candidate, not the next release target.

## Objective

Build an inspectable, versioned model that compares distributions of future
outcomes for a supplied person-and-place profile under specified events and
reference conditions. A time-indexed evidence graph describes supported
relationships; a state-transition model represents how lives evolve.
Graph reachability alone does not establish that a path can be evaluated.

The model retains harmful, beneficial, null, and conflicting findings. Every
reported consequence must be traceable to an appropriate evidential record
and an explicit scenario definition. Unknown pathways remain unknown.

## Non-negotiable rules

1. Separate baseline transitions, causal intervention estimates, and declared
   structural assumptions. Each has provenance appropriate to its role.
2. Predictive associations in baseline models do not become causal effects.
   A causal coefficient cannot be overlaid on a transition that already
   contains the same effect without an explicit reconciliation.
3. Require compatible treatment, comparison, outcome scale, population,
   dose, and timing before composing effects. Units alone are insufficient.
4. A total-effect estimate and its constituent mediator paths cannot both
   contribute to the same outcome in one structural variant.
5. Separate uncertainty about parameters and baselines from stochastic
   variation among lives and from alternative structural specifications.
6. An unsupported bridge or interaction blocks that claim rather than being
   supplied by narrative plausibility. Null evidence is not missing evidence.
7. Every exposed profile and scenario must have an applicability decision.
   Geography and personal detail do not automatically confer identification.

## Model records

### State and identity

A person has an identifier, age, supported economic and health states,
location, event history, and household membership. Households have linked
members and shared resource accounting. Children's ages and exposure windows
are explicit. Communities have a defined population and event scale rather
than being a universal multiplier attached to one person's trajectory.

A baseline state may be a distribution consistent with incomplete inputs.
Document data sources and initialization weights. Preserve missingness;
do not make a synthetic profile more precise than its inputs support.

### Baseline transitions

Record source dataset and version, population, predictors, time resolution,
outcome distribution, estimation method, validation, and uncertainty.
Transitions may be estimated from observational longitudinal data without
claiming intervention identification. Published causal-effect admission rules
continue to apply separately to the current parameter library.

### Causal edges

Record treatment and comparison; source and destination; effect scale;
estimand role (total, direct, or mediated); outcome window; onset and duration;
dose; studied population; causal design; assumptions; null or conflicting
findings; covariance and sample-overlap provenance; citation and extraction
receipt; and applicability to the target profile.

Time is measured explicitly relative to the initiating event. A coefficient
for offset +6 cannot be relabeled as follow-up year 6 when displacement is
follow-up year 1. Repeated events require a defined response model.

### Structural variants

A variant states which causal edges and transitions are used together and
why. Alternatives may change timing, effect transport, or the representation
of transmission. Do not assign probabilities to structural alternatives
without a defensible basis. Document shared populations and overlapping
outcomes before attributing additive contributions.

## Comparison semantics

Initialize compatible reference and event scenarios from the same profile.
The reference evolves under ordinary life transitions; it is not a frozen
state. The event changes specified mechanisms at a stated time and dose.
Background conditions remain matched unless they are part of the scenario.

Use coherent parameter draws across both arms. Separate model uncertainty
from simulated-life randomness. Common random numbers can reduce estimation
noise but do not identify the joint counterfactual outcomes of one individual.
Distinguish arm-specific distributions, expected contrasts, and any stronger
claims about the distribution of individual treatment effects.

For every result expose the comparison, unit, horizon, applicable population,
evidence path, uncertainty scope, alternatives, unsupported pathways, and
version. Produce an attribution breakdown only where its mathematics and
causal interpretation are defensible.

## Work sequence

| Stage | Model work | Research dependency and exit test |
|---|---|---|
| Correct | Repair mortality timing, place counterfactual, and county likelihood contracts | R0: independent mathematical checks and refreshed scorecards |
| Describe | Classify existing coefficients and baseline records; define composition contracts | R1: incompatible and overlapping paths refused; corrected current results remain reproducible |
| Initialize | Define linked household state and estimate narrow baseline transitions | R2: resource accounting and held-out baseline evaluation |
| Intervene | Implement one timed displacement scenario and explicit reference process | R3: five-year supported employment, earnings, and household-resource contrasts |
| Evaluate | Compare with independent event evidence and simple alternatives | R4-R5: frozen scorecard, applicability, interval scope, and sensitivity assessment |
| Explain | Make the validated comparison understandable in the calculator | R6: comprehension and product release criteria |
| Expand | Add supported protective events, interactions, and wider domains | R7: each new causal contract reviewed independently |
| Extend | Study longer horizons and descendants | R8: compatible bridges and endpoint evaluation justify the extension |

Testing and validation begin with the first stage and continue throughout;
they are not a final task after graph expansion.

## Later candidate pathways

Retain the proposed chain `job displacement -> child adult conditions ->
child pregnancy conditions -> grandchild birth weight` as an evidence question.
It requires compatible intermediate estimands, populations, timing, and an
independent endpoint check. A long sequence of citations is not sufficient.

Other domains include health shocks and disability; housing instability and
relocation; family formation and bereavement; childhood health and education;
crime and victimization; environment and disasters; and protective income,
health, school, and housing interventions. Prioritize additions by usefulness
for a defined scenario, evidence quality, evaluability, and reduction of
uncertainty in existing results, rather than graph size alone.

Extraction mechanics remain in
[LITERATURE_ACQUISITION_PLAN.md](LITERATURE_ACQUISITION_PLAN.md). Research status
and milestone completion belong in the life-course plan and the top-level
TODO, avoiding multiple conflicting schedules.
