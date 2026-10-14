# Sensitivity attached to scenario results

Engine 0.4.0 / parameters v1.51. Each emitted scenario count now carries a
`sensitivity` report. Child present-value projections carry the same report.
Entity results and policy comparison arms inherit it through the scenario engine.
Blocked outcomes do not acquire a result through sensitivity calculations.

## What each report contains

- `reference_point`: the unrounded point used for every comparison.
- `effect_drivers`: current parameter values, units, citations, evidence roles
  and population scope, ordered by absolute effect-removal change.
- `effect_removed`: refit with that effect neutralized. Mortality odds and direct
  earnings ratios use 1; the place exposure coefficient and jobs multiplier use 0.
- `supported_range`: refits at that parameter's source endpoints, with other
  parameters fixed. Endpoint results, signed changes and the resulting span
  are separate from the overall parameter envelope.
- `fixed_inputs`: exposure, actual resolved baseline, horizon, family composition
  and relevant scenario choices. Missing ranges remain explicitly unavailable.
- `variance_attribution`: a separate optional parameter variance decomposition.

`change_from_reference` means variant minus reference.
`reference_minus_variant` means reference minus variant. Negative values stay
negative, including modeled beneficial child earnings contrasts.

These experiments rerun the engine with the same custom source directory,
selected subgroup, county inputs, demographic profile and applicability rules.
Changing a parameter cannot unblock an unsupported population. Local-job
endpoints remain within the declared job class; the manufacturing/high-tech
span is not treated as a within-class uncertainty interval.

## Default mortality example

The main point remains 28.76 expected excess deaths per 1,000 workers over
20 years. Removing each phase individually gives:

| Effect removed | New expected excess deaths | Reference minus variant |
|:---|---:|---:|
| Offset +6 onward, follow-up years 7–20 | 20.52 | 8.24 |
| Displacement year | 21.54 | 7.22 |
| Offsets +2–3, follow-up years 3–4 | 22.42 | 6.34 |
| Offset +1, follow-up year 2 | 24.50 | 4.26 |
| Offsets +4–5, follow-up years 5–6 | 26.41 | 2.35 |

These changes do not sum to the total. Survival compounds across phases, so
each experiment holds the other effects in place. Removal can also put an input
outside its observed support. It is a declared hypothetical comparison, not
a new study estimate, a causal attribution share or a confidence interval.
The existing persistence comparison remains available for compatibility.

## Parameter uncertainty drivers

Deterministic reports are automatic. To additionally estimate variance drivers:

```sh
downstream scenario --workers 1000 --draws 2000 --seed 1901 --sensitivity-base 512
```

The API equivalent is `sample_counts(..., sensitivity_base=512)`.
`--draws` controls the existing parameter interval; `--sensitivity-base`
controls the independent variance-analysis design. Neither replaces the other.
Both retain the same scenario inputs, parameter sources and declared dependence.

The existing correlation-aware block Sobol estimator groups all connected
correlated parameters. Peak mortality and sustained mortality share a block
with the earnings parameter through the declared correlations. The report
preserves that block rather than inventing separate variance shares. Unrelated
parameters are excluded from the design, while complete relevant correlation
components are retained. Every sampled subset is merged back into the full engine.

`S_first` estimates a block's main variance effect; `S_total` includes its
interactions. Total-order indices need not sum to one. Finite-design estimates
can be negative or exceed one; they are not clipped. Increase the base and
compare seeds before interpreting small ranking differences. A constant
outcome reports that no variance decomposition exists. Zero variance does not
imply the scenario has no uncertain unmodeled inputs.

Endpoint spans in the deterministic table are not variance shares. Neither
report estimates baseline, exposure, demographic or transport uncertainty.
No distribution or sensitivity range is inferred for a fixed input. Unknown
structural probabilities and dependence remain unknown.

## Scope and consumer contract

The current automatic report covers the scenario's emitted mortality,
child-dollar and local-job counts, plus optional child-dollar valuation
projections. It is inherited by entity results, policy-arm scenario records,
and the fixed-input reference inside the extended uncertainty budget. It does
not decompose policy deltas, realized process outcomes, household trajectories,
cohort-stratum tools or every study effect in the evidence graph.
Internal `_raw=True` evaluations omit reports to avoid recursive analysis and
Monte Carlo overhead. Consumers that deliberately request raw results must
obtain reports from the public calculation before normalizing the payload.

For a consumer normalization factor `s`, scale result-valued fields by `s`:
reference points, experiment points, signed changes, output endpoint bounds and
spans. Scale `output_variance` by `s²`. Parameter values, source endpoints,
units, citations and dimensionless variance indices do not scale. Retain and
label the cached input normalization separately from the displayed exposure.

A place mixture must refit the same input experiment in every component and
combine its expected outcomes under the declared weights. It cannot copy the
first component's sensitivity report or average variance indices. A mixture's
variance attribution requires a joint calculation under a declared dependence
model. Mark it unavailable if that calculation has not been made.

Preserve the report schema, experiment definitions, unavailable statuses and
source metadata in JSON, HTML and Markdown. Bundle hashes identify this code
change even though engine and parameter versions remain 0.4.0 / v1.51. Cache
identity must also include requested analysis settings, such as seed and
sensitivity base, when those reports are stored. XH1B integration remains pending.

## Reproduction

[The saved reference](../validation/result_sensitivity_reference_20261015.json)
uses the command above. Tests check direct survival refits, null and beneficial
estimates, source selection, place inputs, blocked outcomes, class-specific
jobs, valuation, entity/policy delivery, correlated blocks and CLI routing.
