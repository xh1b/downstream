# Probabilistic extension roadmap

This document distinguishes implemented probability machinery from research
work that requires new data. It prevents a convenient sampler from being
mistaken for evidence about a causal bridge.

## Landed in the current engine

- **Incomplete mortality timing (`source_aligned` option).** The peak is
  applied in follow-up year 1; years 2--5 stay at baseline despite available
  unextracted source estimates. Offset +6 starts in year 6, one year early.
  See `REVIEW_2026-09-10.md` for the required source/profile correction.
  `immediate_sustained` is a named sensitivity assumption, never the default.
- **Expected versus realized counts.** Scenario output retains parameter-only
  intervals for expected effects. For integer worker cohorts it additionally
  reports a posterior-predictive binomial simulation for observed mortality in
  newly sampled exposed and counterfactual reference cohorts. The latter is
  not an individual-level paired causal-outcome distribution.
- **Dependence-aware sensitivity.** Classical Sobol remains available for
  independent inputs. `sensitivity --dependent-blocks` instead treats each
  connected component of the declared correlation graph as one joint input,
  preserving the production copula without fabricating individual dependent
  Sobol indices.
- **Structural robustness.** The ensemble publishes an unweighted credal
  statement: which directional conclusions hold under every listed structural
  variant and every listed support endpoint. Variants receive no subjective
  posterior weights.
- **County count-likelihood foundation.** `county-posterior` accepts only
  event counts plus compatible person-years and produces a Beta-binomial
  posterior against a declared national-strength prior. It deliberately does
  not reinterpret the current generic county precision field as a denominator.
- **Evidence-admission gate.** `synthesize --compare-params` can compare a
  compatible log-ratio synthesis to a shipped parameter, but produces a
  manual-review report only. Templates live in `params/study_estimates.template.csv`
  and `params/county_rates.template.csv`.

## Deliberately not claimed yet

Reported study confidence intervals are used as bounded working sampling
distributions (normal or lognormal rows are currently clamped at their stated
bounds). This is a transparent propagation convention, **not** a Bayesian
posterior and not a claim that a frequentist CI is a probability distribution.
Changing it needs row-level likelihood, parameter constraints, and a stated
prior; a global conversion would create a more polished but less defensible
number.

County mobility and baseline measurements are currently fixed within the
parameter interval. A spatial measurement model cannot be honestly fitted
until the input includes compatible county standard errors / denominators and
a documented adjacency or distance structure.

## Next evidence-gated methods

1. **Hierarchical transport meta-analysis.** Store study-level estimates and
   standard errors, then fit target-population predictions by sex, age,
   tenure, country, period, recession severity, and identification design.
   This replaces broad scope caveats with an explicit transport distribution.
2. **Discrete-time competing-risk mortality model.** Land age/sex/year
   baseline hazards plus evidence for years 2--5; use a monotone/smooth
   partial-identification family until the missing bridge is extracted.
3. **Conditional Shapley effects.** Add only after a citable conditional
   dependence model exists. The current block method is intentionally more
   conservative than allocating a joint recession-severity effect between
   correlated coefficients by convention.
4. **Spatial Bayesian baseline layer.** Add county denominators/SEs, temporal
   windows, and a prespecified spatial prior; publish posterior predictive
   checks and leave the fixed-input path available as a comparison.
5. **Decision-aware value of information.** The present knob score measures
   band-width reduction. Expected value of sample information needs a stated
   decision, loss function, acquisition cost, and prospective validation
   target; it must not be inferred from uncertainty width alone.
