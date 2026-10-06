# MODEL CARD — downstream engine 0.3.0 / parameters v1.49

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
- Parameter set v1.49: 67 parameter rows, each with point, band,
  precision tier, bib keys, and population scope.
- Version stamping: params/VERSION; every output carries the version
  it used; sampled outputs mark `-sampled`.

- Public scenario results carry per-outcome applicability decisions and target metadata. Defaults are illustrative reference calculations and explicitly ineligible for public headlines; reviewed conditional transport requires a reviewer, rationale and citations. Structural projections remain distinct from direct effects.
- Repeated intergenerational relationship rows share one exact uncertainty draw. Sensitivity groups them and analytic independent-step inference rejects repeated aliases.
- Scenario results carry input content hashes. Bundles additionally hash engine code and exported files; engine and parameter version labels alone are insufficient cache keys.

## Intended use

- Present: population-level, place-resolved modeling of displacement
  consequences for transparent public reporting: workers, children (three
  generations), family stability, and local economies.
- Intended direction: graph-based simulation of downstream consequences from
  a stated initiating event or altered state. Results must be distributions
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
  pooled literature does not support (SPEC §10). Receiving-community crime paths require a separately defined influx input; they never start from generic worker displacement.

## Factors

- Exposure: displaced workers (count, tradable share, family
  structure). Populations in evidence are US-centric; scope is
  recorded per parameter row.

## Metrics and evaluation

- V0 internal consistency: direct vs IGE-composed child effect
  (0.91 vs 0.89, bands overlap) — runs on every `validate`.
- V1 China-shock retrodiction: unit and commuting-zone panel checks run.
  Family-status contrasts are covered. Male mortality variants overpredict,
  and the lower-quartile earnings loss remains underpredicted after the
  wage-spillover term is added. These misses are part of the scorecard.
- V2 out-of-sample back-tests (NAFTA, 2008-09 auto crisis, BRAC):
  PRE-REGISTERED (outcome definitions + scoring rules frozen in code
  at v1.28, trap tests pin them); scoring blocks until each event's
  displacement bridge and measured coefficients land — recorded
  honestly, never fabricated.
- Place-resolved layer: the Chetty-Hendren mobility modifier uses gamma
  0.037 [0.031, 0.043] and a declared 18-year dose. County mortality uses
  CDC WONDER male ages 45–54 counts and Gamma-Poisson posterior baselines
  where the matched county row is available. Suppressed or absent rows use
  the named national baseline. A county divorce baseline is still pending.
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
- Count intervals hold stated exposure, baseline estimates, county
  measurements/pooling weights, and structural assumptions fixed. Those
  sources of uncertainty are not yet quantified jointly, and are listed
  as excluded rather than claimed to be covered by the parameter band.
- The mortality count uses a US male age 45–54 baseline and a displacement
  effect from high-seniority men. Child earnings transport a Canadian
  father-son firm-closure finding to a US male lifetime-earnings baseline
  in 2024 dollars. A mixed or unknown population needs a separately
  reviewed transport rule before these counts can be read as its expected
  outcomes.
