# Causal Graph Plan

## Objective

Build `downstream` into a versioned, evidence-locked causal consequence graph.
Starting from an event or state, it must discover every supported downstream
path, compose compatible effects over time, and report the result with a full
uncertainty and provenance trail.

The model is descriptive. It encodes published estimates, nulls, conflicting
results, scope limits, and uncertainty; it does not contain outcome-specific
or political conclusions.

The first executable target is one synthetic person and their family after a
job displacement. The first scientific target is one long, auditable chain
whose distant endpoint cannot be reached by a single paper alone.

## Non-negotiable rules

1. Every computed effect is graph-derived from cited evidence.
2. Every estimate has a distribution or a declared reason it cannot support a
   probabilistic result. Point estimates alone never become final outputs.
3. Every output separates parameter uncertainty, simulated-life randomness,
   baseline uncertainty, and structural uncertainty.
4. Effects, nulls, beneficial effects, and contradictory results are all
   represented. No path is selected because of its narrative appeal.
5. Total effects and mediated paths are mutually exclusive within a structural
   variant. The engine must not double-count a total-effect estimate and its
   constituent routes.
6. A missing bridge blocks that route visibly; it is never inferred from
   intuition.

## Graph primitives

### Nodes

Nodes are observable events, states, or outcomes, not moral labels. Examples:

`job_displacement`, `earnings`, `parental_divorce`, `childhood_place_exposure`,
`birth_weight`, `adult_earnings`, `incarceration`, and `mortality`.

Every node has a unit, time semantics, population scope, and an optional
baseline distribution.

### Edges

An edge is a study-backed change from one node to another. It records:

- treatment and comparison;
- outcome and unit;
- point estimate and uncertainty distribution;
- onset, duration, and persistence;
- studied population and transfer limits;
- causal design and evidence tier;
- estimand role: `total`, `direct`, `mediated`, `null`, or `context_only`;
- citations and extraction receipt.

### Structural variants

A variant is an explicit, testable view of a pathway where the literature does
not identify one unique composition. It can select a total-effect edge or a
set of mediator edges, but never both. Outputs report the variant spread.

## Computation

The graph is unrolled by time. A simulation draw first samples a coherent
scientific world (edge parameters and their declared dependencies), then a
stochastic life within that world. This separates what is unknown about an
effect from variation in what happens to a simulated person.

For every reported result, emit:

- point, interval, and distribution summary;
- all contributing paths and their signed contribution;
- error budget by edge, baseline, stochastic outcome, and structural variant;
- blocked paths and the missing scientific bridge;
- parameter-set and graph version.

## Work plan

### Phase 1 — Convert the existing library into a graph

1. Promote current nodes and parameter rows to graph nodes and edges without
   changing numerical behavior.
2. Add timing, estimand role, and uncertainty metadata to every active edge.
3. Encode existing parallel streams as graph branches rather than renderer
   folders.
4. Preserve current CLI output and tests as backward-compatibility fixtures.

**Exit test:** every current result can be produced by graph traversal and has
the same citations, point, and interval semantics as before.

### Phase 2 — Uncertainty-native engine

1. Replace generic low/high handling with unit-appropriate distributions.
2. Add baseline and outcome-process uncertainty alongside parameter sampling.
3. Add declared dependence groups and reject undeclared correlation claims.
4. Produce a per-result error budget and structural-variant spread.

**Exit test:** a one-edge result, a two-edge mediated result, and a competing
total-effect variant have analytically or simulation-verified uncertainty.

### Phase 3 — First long chain

Build and validate a first distant consequence chain:

`job displacement → child adult conditions → child pregnancy conditions →
grandchild birth weight`

This chain only ships when every bridge is supported by an extracted study,
timing is compatible, and its output identifies which bridge dominates error.

**Exit test:** `downstream` can explain the distant birth-weight result from
the initiating event through every cited edge, including uncertainty.

### Phase 4 — Systematic evidence expansion

Expand by graph bridges, not by topical anecdotes. Initial research domains:

1. health shock, disability, earnings, debt, and bankruptcy;
2. housing instability, eviction, relocation, and place exposure;
3. family formation, divorce, bereavement, parenting, and fertility;
4. childhood health, birth conditions, education, and adult outcomes;
5. crime, victimization, incarceration, and family spillovers;
6. mental health, substance use, work, and child outcomes;
7. environment, disaster, migration, health, and labor outcomes;
8. protective interventions: income supports, health care, schools, and
   neighborhood improvements.

Each new study is triaged by causal quality, composability, time resolution,
number of bridges unlocked, and expected reduction in output uncertainty.

### Phase 5 — Single-person causal trace

Model one synthetic person, their household, children, and marginal community
contribution as a time-indexed graph state. This is not person-level
prediction; repeated draws produce the population distribution conditional on
the specified initial state and event.

**Exit test:** a trace shows what happened in one draw, while the aggregate
result reports the distribution across draws and its evidence receipts.

### Phase 6 — Validation and falsification

1. Keep internal algebra and unit tests.
2. Add held-out event studies for graph subpaths and full chains.
3. Register prospective graph forecasts before outcome windows.
4. Publish misses, failed transfers, and blocked paths.

## Immediate next actions

1. Inventory every existing parameter as a graph edge and classify its role.
2. Define the graph edge and uncertainty data model in code.
3. Create a literature queue organized around missing bridges to the first
   long-chain target, beginning with adult socioeconomic conditions to
   pregnancy and birth outcomes.
4. Implement graph traversal for the existing displacement graph before
   adding new numerical claims.

The acquisition workflow and first DOI/open-access batch live in
`docs/LITERATURE_ACQUISITION_PLAN.md`.
