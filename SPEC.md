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

### Active parameter set v1.2

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

## 7. Uncertainty propagation

`mc.simulate` rebuilds the full module compute per draw, so nonlinear
gap composition propagates correctly. Outputs carry p05/p50/p95/mean,
the seed, the draw count, the sampler id, and a `-sampled` version
mark. Methodology (mckay1979; iman1982; hersbach2000 in references.bib):

1. **Latin Hypercube Sampling** over the parameter space — one draw
   per stratum per marginal, converging faster than IID.
2. **Log-space sampling for positive ratios** (rate ratios, odds
   ratios, level ratios): a ratio's uncertainty is multiplicative;
   linear sampling biases toward the top of the band.
3. **Declared normal** rows: SE from the band half-width / 1.96,
   truncated to the band.
4. **Rank correlation** between parameters via Iman-Conover —
   marginals preserved exactly. The declared matrix
   (`params/correlations.csv`) ships EMPTY; a correlation enters only
   with a citation (candidate queued: shock depth vs mortality
   response, from the Davis-von Wachter bad-case caveat).

## 7b. Analytic inference (the same algebra, done exactly)

`inference.py` propagates the first two moments of a chain in CLOSED
FORM. Every ledger step is a product (level), a replacement (direct),
or affine in each argument (gap) — so under parameter independence
the mean and variance propagate exactly (§7's identities are in the
module docstring). Three uses:

1. **Cross-check.** `analytic_vs_mc`: the MC mean must sit within ~3
   sampling SE of the exact mean. On the grandchild line they agree
   to 0.07 SE and the sds match to 4 decimals. A larger gap is a
   sampler bug, and the test suite traps it.
2. **Bands.** `analytic_chain` gives a normal-approximation p05/p95
   for free (no seed). The MC exists to price the skewness this
   misses — the normal-vs-MC quantile gap publishes as the output's
   non-Gaussianity, not as error.
3. **Exact decomposition.** `logspace_variance_shares`: for a purely
   multiplicative (level) chain, Var[log Y] = Σ Var[ln Xi] and the
   shares ARE the Sobol indices of log Y — first-order equals total,
   no estimator, no seed. Non-level chains are REFUSED (log Y ≠ Σ ln
   Xi for gap/direct steps — the level-ratio bug in analytic
   disguise).

**Third moments and Cornish–Fisher bands.** The chain propagates
E, E², E³ exactly (level: products; gap: the bilinear identity in
`analytic_chain`'s docstring). Skewness γ₁ follows from raw moments;
the Cornish–Fisher expansion turns it into quantile corrections
`q_α ≈ μ + σ(z_α + (z_α²−1)γ₁/6)` that reduce exactly to the normal
band at γ₁ = 0. On a deliberately skewed two-step log-uniform product
chain, CF sits strictly closer to the MC quantile than the normal
band (trap-pinned) — the correction does work, and the MC remains
the referee.

**Correlation stress** (`correlation_stress`) — the bound on the
independence assumption. The declared correlation matrix ships EMPTY;
until a correlation is citable, every band assumes independence. The
stress test induces Spearman ρ among a chosen block via Iman-Conover
(marginals preserved; PSD violations refused at construction),
rebuilds the band, redraws truths under the SAME dependence, and
publishes the width move. Measured on the grandchild line at ρ = +0.5
between the direct child effect and IGE transmission: the band
NARROWS 18% — the gap step couples gradients of opposite sign
(∂g'/∂g = t > 0, ∂g'/∂t = −(1−g) < 0), so positive correlation is
cancellative. The independence assumption is therefore conservative
against positive correlation of this pair, and the number publishes
either way. Coverage stays nominal under declared dependence: the
machinery tracks whatever it is told; only a citation can make the
dependence real.

**Coverage closure test** (`closure_coverage`) — what "a 90% band"
means here and how it is earned: draw truths from the declared bands,
build the MC band from an independent sample, and count coverage. On
the grandchild line (600 trials): empirical 0.498/0.802/0.902/0.945
against nominal 0.50/0.80/0.90/0.95 — all within 2 binomial SE. This
validates the INTERVAL MACHINERY under the model's own assumptions.
It does not validate the economics; that is V1's job. A test that
sabotages the band fails the closure check — the test has teeth
(trap-pinned in the suite).

CLI: `downstream infer --outcome grandchild [--action chain|shares|
closure|agree]`.

**Property fuzz (test suite).** 24 randomly generated chains (mixed
units, mixed level/direct/gap sequences, random bands) demand the
exact moments agree with the MC sampler — mean within 4 sampling SE,
variance within 6%, skewness sign exact when identifiable. Declared-
`normal` sampling rows are REFUSED by the analytic layer (the sampler
truncates them; the algebra has no truncated-normal rule) — when one
is cited into the set, add the moment rule and unpin the trap.

## 8. Sensitivity analysis (what drives the range)

`sensitivity.sobol_indices` computes first-order and total Sobol
indices (sobol2001; saltelli2002) over the same parameter space:
`S_total` is the share of output variance driven by each parameter,
interactions included. It powers layer 3 of every explanation ("the
range is mostly driven by X — pinning X down helps most") and ranks
the extraction queue by precision value. Model evals =
base x (N+2); the model evaluates in microseconds, so base sizes of
a few hundred are cheap and seeded for reproducibility.

## 8b. Knob experiments (how the model is explored)

`knobs.py` is the experiment layer. Two tools, both fail-loud:

- **`sweep`** — pin one parameter at each of a list of values (band
  collapsed onto the value; the value must lie inside the parameter's
  cited band — the experiment door does not widen the evidence) and
  recompute the scenario. The table shows every modeled count plus the
  blocked list at each value, with deltas against the first row.
- **`value_of_information`** — narrow each parameter's band by a
  factor toward its point, re-run the Monte Carlo on a paired seed,
  and report the surviving output-band width. Ranked, this is the
  extraction queue in OUTPUT units: which knob, turned next, removes
  the most uncertainty. (For the grandchild line, halving the direct
  child-earnings band removes ~40% of the p05-p95 width; the youth-
  crime elasticity removes ~0 — it cannot reach that outcome.)
- **`sobol_ci`** (sensitivity.py) — re-run the Saltelli estimator on
  consecutive seeds and report the mean and sd of S_total across
  designs. The sd is design noise, not a confidence interval on a
  true index; it exists to check that a ranking separates by more
  than its noise.

Honesty rules, tested: every overridden parameter set carries a
`-knob` version marker (one experiment is never a published set);
unknown links and out-of-band pins raise; zero-width bands are
reported, not crashed on.

CLI: `downstream knobs --action sweep --link X --values a,b,c` and
`downstream knobs --action voi --outcome grandchild`; `downstream
sensitivity --ci N`. Shell note: link ids contain `->`, quote them.



`scoring.py` implements the verification layer for V1/V3
(gneiting2007): sample-based CRPS (hersbach2000), band coverage, and
PIT values with a calibration table. A published band that misses its
stated coverage is a wrong model, whatever its citations say.

## 10. The explanation contract (how claims travel)

`explanation.Explanation` is the data contract between the model and
every renderer (CLI, web, paper): claim with band, cited step list
with contribution shares, Sobol drivers, declared assumptions,
blocked outcomes with fixes, falsifiers, version + seed. Hard rules,
tested: no naked point estimates; every step cited; refusals named
with their missing input. Rendering rules live in
`docs/RENDERING.md`; the reference renderer is `render.py`.

## 11. Scenario aggregation

`scenario.compute_counts` takes an exposure (workers, family
structure, tradable share, window) and returns modeled counts +
multipliers + an explicit blocked list. Composition across units
(summing deaths over workers) is linear-in-N by construction; the
level (no-migration-dampener) caveat lives in the validation docs.

## 12. Validation program

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

## 12b. Structural-variant ensemble (declared assumptions, priced)

`variants.run_ensemble` runs the named composition-assumption
alternates side by side and publishes the spread (plan #9):
baseline; parallel_gap_additive (direct + divorce + family-size gaps
added in gap space — the additivity SPEC §4 refuses to assume
silently, priced here at −3.9pp of grandchild gap); ige_decay_half /
ige_decay_power (geometric re-parameterizations of the same cited
IGE band, 0.933 / 0.963 vs baseline 0.9505). The baseline row always
equals the shipped model (trap-pinned). No variant is silently
substituted — the spread IS the result. CLI: `downstream ensemble`.

## 13. Queued and excluded

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

## 14. Limitations (registered, not hidden)

1. Linear, deterministic propagation inside a draw; interactions
   between outcomes are not modeled.
2. Parameter correlations are mechanically supported
   (Iman-Conover) but the declared matrix is EMPTY: no correlation is
   yet citable. Sampling distributions are band-derived (uniform /
   log-uniform / truncated normal), not study-fitted.
3. US-centric parameters applied to US populations; scope mismatches
   are recorded per row.
4. Displacement is treated as exogenous; the model does not select
   who is displaced.
5. The great-grandchild layer is the weakest-identified number in the
   model (see the honesty statement shipped in its output).

## 15. Layout

```
params/            VERSION, parameters.csv, nodes.csv, baselines.csv,
                   correlations.csv, CHANGELOG.md, references.bib
src/downstream/    units, params, citations, ledger, worker, children,
                   family, community, vignette, scenario, mc,
                   distributions, sensitivity, scoring, explanation,
                   render, audit, validate, cli
docs/              CITING.md, QUEUED_EXTRACTIONS.md, PRIOR_ATTEMPTS.md,
                   RENDERING.md, MODEL_CARD.md
paper/             make -> downstream.pdf
```
