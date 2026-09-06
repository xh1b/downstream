# SPEC — the downstream model

Versioned with the parameter set (`params/VERSION`). This document is
the algorithm: what is computed, from what, with which citations, and
what is deliberately not computed. Everything here is public by
design. The companion research corpus is private; this repo carries
only the model, the numbers, and their sources.

## 1. What the model computes

An **exposure** (workers displaced from tradable jobs) propagates
through cited effect links into outcomes for four streams:

| Stream | Outcomes |
|:---|:---|
| worker | long-run earnings, excess mortality |
| children | child adult earnings, grandchild earnings, great-grandchild earnings |
| family | divorce hazard, family-size penalty, daughter adult-violence odds |
| community | local service jobs, school-spending effects, youth-crime response |

Every number carries: a point estimate, a band, a precision tier, at
least one bib key (`params/references.bib`), and a population scope.
The ledger records each step so any output can be audited back to its
studies.

**Honesty architecture** (non-negotiable):

1. Nothing is computed without a cited parameter. Missing inputs fail
   loudly (`blocked` with the exact missing baseline named).
2. Vignettes and scenarios report **ranges for populations**, never
   deterministic claims about a person.
3. Relative effects (rate ratios, odds ratios) convert to counts only
   against **cited baselines**.
4. Weakly identified layers (generation 3) carry an honesty statement
   in their output, not a footnote.
5. Validation misses are published. The model does not tune to pass.

## 2. Nodes and units

`params/nodes.csv` declares every node and its unit. The unit decides
how a parameter may be applied:

| Unit | Meaning | Applied as |
|:---|:---|:---|
| `persons`, `count` | exposure quantities | inputs |
| `gap_multiplier` | deviation from 1.0 vs a counterfactual (0.80 = −20%) | `level`, `gap`, or `direct` step |
| `rate_ratio` | relative rate vs counterfactual | recorded; applied to a baseline rate at the boundary |
| `odds_ratio` | relative odds vs counterfactual | recorded; applied to baseline odds |
| `level_ratio` | jobs-per-jobs, dollars-per-dollars — a LEVEL | multiplies a count; **never chained** |
| `percent_delta` | percent change | via an elasticity |

The v0 lesson, now enforced by `downstream audit`: Moretti's
"1 high-tech job supports ~5 local service jobs" is a
`level_ratio`. Multiplying it into an earnings chain (as v0 did) is a
shape error, and the audit rejects any `level_ratio` row with a point
below 1.0 as the tell for that bug class.

## 3. Parameters

`params/parameters.csv`, version `params/VERSION`. Columns:
`link, from_node, to_node, point, low, high, tier, citation,
population_scope, notes`. `citation` holds semicolon-separated bib
keys — free-text citations are not allowed anywhere.

### Active parameter set v1.1

| Link | Value [band] | Tier | Source keys |
|:---|:---|:---|:---|
| displacement→worker_earnings | 0.80 [0.75, 0.85] | EXACT-abstract | jacobson1993; oreopoulos2008; davis2011 |
| earnings_shock→mortality_sustained | 1.17 [1.15, 1.20] | EXACT-abstract | sullivan2009 |
| earnings_shock→mortality_peak | 1.75 [1.50, 2.00] | EXACT-abstract | sullivan2009 |
| displacement→divorce_hazard | 1.11 [1.05, 1.25] | canonical | rege2007; charles2004 |
| displacement→child_earnings (direct) | 0.91 [0.86, 0.96] | EXACT | oreopoulos2008 |
| divorce→child_earnings (parallel) | 0.95 [0.90, 0.99] | canonical | gruber2004 |
| family_size→child_earnings (parallel, per extra child) | 0.98 [0.95, 1.00] | canonical | black2005 |
| child_earnings→grandchild_earnings (IGE) | 0.55 [0.40, 0.60] | canonical | solon1992; corak2013; chetty2014 |
| grandchild_earnings→greatgrandchild_earnings (IGE) | 0.55 [0.40, 0.60] | canonical | lindahl2015; adermon2018 |
| ipv_exposure→daughter_violence_odds | 2.5 [2.0, 3.0] | canonical | widom1989; ehrensaft2003 |
| displacement→local_service_jobs | 5.0 [1.6, 5.0] | canonical | moretti2010 |
| school_spending→child_earnings (per +10% × 12y) | 1.07 [1.03, 1.10] | canonical | jackson2016 |
| youth_wages→youth_crime (elasticity) | −1.0 [−1.5, −0.5] | canonical | gould2002; grogger1998 |

Tiers mean what `CITING.md` says they mean. The audit cross-checks
each tier against the `xh1b-evidence` class recorded in the bib entry.

## 4. Composition semantics

A ledger tracks one quantity through cited steps. Step kinds:

**level** — plain multiplication on a level:
`v' = v × p`, band `v' ∈ [v·p_lo, v·p_hi]`.

**gap** — transmission gap propagation (the IGE links). A parent gap
`g` and transmission parameter `t` give:

```
g' = 1 − t·(1 − g)
band: g'_lo = 1 − t_hi·(1 − g_lo),  g'_hi = 1 − t_lo·(1 − g_hi)
```

Worked line (the standard family, father shocked to 0.80):

```
child gap        = 0.91                       (direct, oreopoulos2008)
grandchild gap   = 1 − 0.55·0.09 = 0.9505     [0.916, 0.984]
great-grandchild = 1 − 0.55·0.0495 = 0.9728   [0.9496, 0.9936]
```

v0 multiplied levels straight through (0.91 × 0.55 = 0.50) — that
overstated the grandchild loss ~9×. The `gap` kind exists so that bug
class cannot recurse.

**direct** — a directly estimated effect on the outcome: `v' = p`
(with its band). Used where the literature estimates the outcome
itself, not a transmission step.

**rate** — a rate ratio, recorded on the ledger and held there.
Counts happen only at the boundary (§6).

**level_ratio** — `n × p`. Additive in n. Never enters a ledger chain.

**elasticity** — `%Δoutcome = e × %Δinput`, sign carried through.

Parallel streams (divorce→child_earnings, family_size→child_earnings)
are reported **side by side** with the displacement path. There is no
silent composition: combining independent causes needs incidence
weights and an additivity assumption the literature does not license.
`combine_parallel` exists (gap-additive, floored at 0) for a future
combined view, behind its own cited derivation.

## 5. Modeled pathways

- **Worker stream** (`worker.py`): earnings gap (direct), mortality
  sustained ratio, mortality peak ratio — separate outcomes of one
  shock, never multiplied together.
- **Children line** (`children.py`): direct child gap, then gap-space
  IGE to grandchild, then to great-grandchild with the honesty marker.
- **Family streams** (`family.py`): divorce hazard (rate ratio),
  family-size penalty (level-compounded per extra child), daughter
  violence odds (odds ratio; upstream IPV incidence is queued — the
  vignette reports it `blocked`).
- **Community** (`community.py`): service jobs lost (level ratio),
  school-spending effect normalized linearly in
  `(spend_pct/10) × (years/12)` — both normalizations are declared
  assumptions — and youth-crime percent delta via the wage elasticity.

## 6. Count conversion and baselines

Relative effects become counts only against cited baselines
(`params/baselines.csv`), each of which must reach `status=verified`
with a value and a source before use:

```
excess_deaths = N · m · (r_sust − 1) · Y  +  N · m · (r_peak − 1)
child_earnings_lost_$ = N · children · (1 − g_child) · L
```

where `m` is the cited baseline mortality rate, `Y` the exposure
window, and `L` cited median lifetime earnings. Pending baselines
block their outcome (`blocked`, with the fix named); `strict=True`
raises instead. **No baseline value is ever guessed.**

## 7. Monte Carlo

`mc.simulate` redraws every parameter uniformly in `[low, high]` and
rebuilds the full module compute per draw, so nonlinear gap
composition propagates correctly. Outputs carry p05/p50/p95/mean, the
seed, the draw count, and a `-sampled` version mark. Uniform is the
declared v1 default; distributions upgrade per-parameter as full-text
passes pin them (see `docs/QUEUED_EXTRACTIONS.md`).

## 8. Scenario aggregation

`scenario.compute_counts` takes an exposure (workers, family
structure, tradable share, window) and returns modeled counts +
multipliers + an explicit blocked list. Composition across units
(summing deaths over workers) is linear-in-N by construction; the
level (no-migration-dampener) caveat lives in the validation docs.

## 9. Validation program

- **V0 — internal consistency (running):** the direct child estimate
  (oreopoulos2008) must overlap the IGE-composed path
  (jacobson1993 × IGE band). `downstream validate` runs it; a
  divergence means one of the two literatures is misread.
- **V1 — retrodiction (scaffolded):** China-shock commuting zones;
  reproduce measured marriage / fertility / child-poverty / mortality
  deltas without tuning. Spec: `validate.v1_backtest_spec()`.
- **V2 — back-tests (designed):** NAFTA, 2008-09 auto crisis, BRAC.
- **V3 — prospective (designed):** pre-registered forecasts scored
  with proper rules; misses published.

## 10. Queued and excluded

- Queued (structure known, number pending full-text extraction):
  `docs/QUEUED_EXTRACTIONS.md`. Each row names the study, the exact
  table/figure to extract, and the priority.
- Excluded by honesty rule: the immigration-crime link. The pooled
  literature (ousey2018; butcher1998) is null-to-negative — the model
  refuses to encode a positive link, and this refusal is itself a
  published result.
- Contested literature (native-wage effects: borjas2003 vs
  ottaviano2012; Mariel: card1990 vs the re-analysis war) is not
  encoded as a parameter. When a headline needs it, both positions are
  computed as named alternate bands, never averaged silently.

## 11. Limitations (registered, not hidden)

1. Linear, deterministic propagation inside a draw; interactions
   between outcomes are not modeled.
2. Uniform parameter distributions; correlation between parameters
   (e.g. earnings and mortality both worsening with shock depth) is
   not yet modeled.
3. US-centric parameters applied to US populations; scope mismatches
   are recorded per row.
4. Displacement is treated as exogenous; the model does not select
   who is displaced.
5. The great-grandchild layer is the weakest-identified number in the
   model (see the honesty statement shipped in its output).

## 12. Layout

```
params/            VERSION, parameters.csv, nodes.csv, baselines.csv, references.bib
src/downstream/    units, params, citations, ledger, worker, children,
                   family, community, vignette, scenario, mc, audit,
                   validate, cli
docs/              CITING.md, QUEUED_EXTRACTIONS.md, PRIOR_ATTEMPTS.md
paper/             make -> downstream.pdf
```
