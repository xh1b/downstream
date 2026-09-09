# MODEL CARD — downstream engine 0.2.0 / parameters v1.34

Model card practice per Mitchell et al. 2019, "Model Cards for Model
Reporting". This card travels with the model.

## Model details

- Current implementation: deterministic, citation-locked microsimulation of
  downstream consequences of worker displacement, with Monte Carlo uncertainty
  propagation (LHS + log-space ratio sampling + optional declared rank
  correlation).
- Project direction: a versioned, evidence-locked causal consequence graph.
  Worker displacement is the first seed event. The graph will represent
  published causal links between life events and states across people, families,
  and communities, including null, beneficial, harmful, and conflicting
  evidence. See `docs/CAUSAL_GRAPH_PLAN.md`.
- Scenario headline counts (local jobs, excess deaths, and child-dollar
  loss) additionally carry jointly sampled central 90% intervals for
  **parameter uncertainty only**. Their support envelopes are retained
  and explicitly not presented as confidence intervals.
- Parameter set v1.34: 42 parameter rows, each with point, band,
  precision tier, bib keys, and population scope.
- Version stamping: params/VERSION; every output carries the version
  it used; sampled outputs mark `-sampled`.

## Intended use

- Present: population-level, place-resolved modeling of displacement
  consequences for transparent public reporting: workers, children (three
  generations), family stability, and local economies.
- Intended direction: graph-based simulation of downstream consequences from
  a documented initiating event or altered state. Results must be distributions
  with scientific receipts and an error budget, not asserted personal futures.
- Explanation-first surfaces: every claim ships with its derivation,
  drivers, falsifiers, and receipts.

## Out-of-scope use

- NOT a person-level predictor. Vignettes describe modeled ranges for
  family TYPES; the model never assigns outcomes to an individual.
- NOT an agenda engine. The evidence graph must preserve nulls, benefits,
  harms, and disagreements; an unsupported or incompatible path is refused.
- NOT a forecasting system until V3 prospective validation runs.
- NOT an immigration effects model per se: it models DISPLACEMENT
  events and their documented consequences. It refuses links the
  pooled literature does not support (SPEC §10), including the
  immigration-crime link.

## Factors

- Exposure: displaced workers (count, tradable share, family
  structure). Populations in evidence are US-centric; scope is
  recorded per parameter row.

## Metrics and evaluation

- V0 internal consistency: direct vs IGE-composed child effect
  (0.91 vs 0.89, bands overlap) — runs on every `validate`.
- V1 China-shock retrodiction: scaffolded, data plugs pending.
- V2 out-of-sample back-tests (NAFTA, 2008-09 auto crisis, BRAC):
  PRE-REGISTERED (outcome definitions + scoring rules frozen in code
  at v1.28, trap tests pin them); scoring blocks until each event's
  displacement bridge and measured coefficients land — recorded
  honestly, never fabricated.
- Place-resolved layer (v1.29-v1.30): county baselines with empirical-Bayes
  shrinkage toward national (w = n/(n+k), declared prior n) + the
  Chetty-Hendren mobility modifier LANDED (gamma 0.037 [0.031,0.043]
  EXACT, county level; declared 18-year dose) over 3,134 county
  mobility rows from the Opportunity Atlas. County mortality + divorce
  plugs still pending.
- V3: immutable local registration and scoring tools built; no real event registered.
- Unit tests cover the known bug classes
  (level-vs-gap composition, level-ratio misuse, naked estimates,
  band inversion, pre-registration drift, fabricated scorecards,
  place-swap unit bugs, pooling-weight fabrication).

## Ethical considerations

- The subject is harm to identifiable communities. The honesty
  architecture (fail-loud missing inputs, published misses, refused
  links, weakest-layer caveats) exists because overclaiming here can
  hurt real people twice: first by the documented harm, then by
  exploits of exaggerated evidence.
- All parameter sources are public academic research; no confidential
  material enters this repo.

## Caveats

- Nonlinear gap and survival propagation inside a draw. Per-parameter distributions: rows
  whose band is a reported 95% CI declare the CI shape (normal, or
  lognormal for exp-CI multiplier rows); rows with declared bands
  (rounding bands, cross-study spreads, evidence-widened bands) sample
  flat — no shape is invented.
- Parameter correlations: two declared pairs (shock depth <-> mortality
  response, spearman -0.5, direction citable, magnitude declared) applied
  via Iman-Conover with marginals preserved; the sampler stamp
  `lhs+iman-conover` declares when they apply.
- The great-grandchild layer is the weakest-identified number in the
  model; its output carries that statement.
- Pending baselines block absolute counts on purpose: no baseline, no
  counts, no exceptions.
- Count intervals hold documented exposure, baseline estimates, county
  measurements/pooling weights, and structural assumptions fixed. Those
  sources of uncertainty are not yet quantified jointly, and are listed
  as excluded rather than claimed to be covered by the parameter band.
