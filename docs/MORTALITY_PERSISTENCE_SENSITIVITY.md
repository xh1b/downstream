# Mortality persistence sensitivity — engine 0.4.0

The default source-profile scenario now reports two mortality structures
side by side in `modeled.excess_deaths.persistence_sensitivity`. This is
also available through entity calculations and the full scenario records
inside policy comparisons. Website consumers need to render the new field;
this repository does not implement the production website.

## Question and evidence

How much of the modeled mortality difference depends on excess annual
risk continuing beyond the early displacement years?

The shipped Sullivan–von Wachter working-paper profile estimates an odds
ratio above one from source offset +6 onward. The existing evidence review
also records Eliason–Storrie's Swedish establishment-closure study, which
does not find a lasting all-cause mortality increase. These studies have
different populations, designs, scales and follow-up windows. They are
not interchangeable estimates for a pooled coefficient.

Sources: [Sullivan–von Wachter working paper](https://www.nber.org/papers/w13626),
[Eliason–Storrie working-paper record](https://swopec.hhs.se/gunwpe/abs/gunwpe0153.htm),
and the existing [source reconciliation](MORTALITY_SOURCE_RECONCILIATION_2026-09-10.md).
The latter study's published record is *Does Job Loss Shorten Life?*,
Journal of Human Resources 44(2), 277–302 (2009), DOI 10.1353/jhr.2009.0020;
the parameter bibliography retains its working-paper extraction provenance.

## The two structures

| Structure | Early phases | Source offset +6 onward |
| --- | --- | --- |
| `source_profile` | Existing source odds ratios | Existing sustained odds ratio, point 1.1354 |
| `no_sustained_excess` | Identical source odds ratios | Declared OR=1 |

Displacement is follow-up year one, so the alternative first changes
follow-up year seven. Both structures use the same exposure, horizon,
resolved baseline, early coefficients and survival arithmetic. Selected
demographic mixtures are aggregated by stratum after calculating survival;
the engine does not replace them with an average hazard. County overrides
and explicit-profile precedence are inherited from the parent calculation.

The alternative is a hybrid structural assumption, **not a reproduction
of Eliason–Storrie**. A nonsignificant estimate is not proof of an exactly
zero response. No Swedish hazard ratio is substituted for a Pennsylvania
odds ratio. The cutoff follows the source profile's phase, not the Swedish
study's windows. Either persistence choice beyond that study's 12-year
follow-up is an extrapolation. Setting later annual excess risk to zero
does not erase the earlier cumulative mortality difference.

## Reproduce and interpret

```sh
downstream scenario --workers 1000 --draws 2000 --seed 1901
```

For parameters v1.51, the default two-children scenario and 20-year mortality
follow-up produce:

| Structure | Expected excess deaths | 90% parameter-only interval | Parameter support envelope |
| --- | ---: | ---: | ---: |
| `source_profile` | 28.76 | 22.04–36.68 | 11.26–50.10 |
| `no_sustained_excess` | 20.52 | 15.73–26.46 | 9.19–35.36 |

The point difference is 8.24 deaths. Its 90% parameter-only interval is
2.99–13.84. Each pair of results uses the same parameter draw, and the
difference is computed within the draw; it is not the subtraction of
separately calculated quantile endpoints. The alternative's late OR is
fixed at one, while uncertainty in its early phases is retained.

The 20.52–28.76 range across point estimates is a structural comparison,
not a confidence interval or a bound on the true effect. No probability
or averaging weight is assigned to either structure. A protective source
effect is preserved, so the null-persistence alternative is not guaranteed
to be the lower result for arbitrary parameters.

Adding this comparison leaves the default source estimate unchanged.
Parameter v1.50 separately corrects the offset +4–5 SE to 0.138, widening
its band and the scenario intervals; that correction did not change the source point.
Parameter v1.51 re-executes every phase transformation consistently and corrects
working-paper publication tiers and cross-study interpretation notes.
The new comparison stays separate from the original modeled
outcome list and parameter-uncertainty outcome map. Its report is explicitly
ineligible for a validated public headline. Both structures retain the
parent scenario's fixed inputs, excluded uncertainties and applicability
limits. Neither resolves baseline aging or target-population transport.

For incomplete or legacy mortality methods the comparison reports
`available: false`. Missing baselines or incompatible target demographics
cannot acquire a mortality result through this sensitivity.

## Validation in this release

Tests cover the phase boundary and fractional follow-up, analytic late-only
survival, protective and null effects, zero/fractional exposure, probability
versus rate baselines, mixture aggregation, paired-draw cancellation,
reproducibility, unsupported cohorts, missing baselines, and CLI/entity
delivery. Numerical verification does not establish external causal validity.
