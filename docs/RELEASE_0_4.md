# Downstream 0.4.0 — pending update and review follow-through

Engine 0.4.0 / parameters v1.51, 2026-10-14. This pending update implements the
review's scenario improvements and records unresolved empirical requirements
in the `tasks/` board. Software correctness and source reproduction do not establish
that the effects transport to a particular policy or population.

This work remains in the 0.4 development cycle and has not been applied to
XH1B. The initial 0.5 label was premature and has been corrected; implementation
and numerical results are retained. Future release numbering follows the
owner's release decision, rather than each batch of model changes.

## Source correction

Re-extraction of Sullivan–von Wachter's Table 5 found that the offset 4–5
standard error had been copied from a different column/phase: .077 becomes
the source column's .138. The coefficient point remains .240. The corrected
odds-ratio band is [0.9700, 1.6661], including the null. Source population
labels now distinguish the study cohort from the 45–54 reference baseline.
The mortality persistence alternative remains separately reported.

The release audit additionally re-executes all five Table 5 transformations
at four decimals (v1.51). The 1,000-worker, 20-year point changes from 28.73
to 28.76 expected deaths; the null-persistence alternative remains 20.52.
Working-paper rows now use canonical publication tier. Danish cumulative
hazard ratios retain their different scale/window and 2011 source version;
the MI-or-stroke 20-year cross-check is corrected to 1.09 [0.97, 1.23].
Source coefficients and baseline values are unchanged; the derived OR values
and some support endpoints are corrected, with prior values retained in Git.

The code audit fixes custom subgroup-source handling across all scenario
adapters, verifies consumed source scales/windows, preserves signed near-null
mortality calculations, and refuses incompatible child-dollar baseline units.
Marginal source ranges are not described as simultaneous confidence bands.

## Completed scenario capabilities

- Reproduce January-2024 CPS displaced-worker composition under explicit
  known-year and tenure restrictions. The >=3-year weighted total is
  2,578,128, matching the BLS rounded 2,578,000 publication. A separate
  >=6-year reference is available. Neither identifies an H-1B cohort.
- Compare exact age-stratum mortality with aging versus fixed age-band
  baselines, using sourced male age-at-event contrasts and an explicit
  constant-source-window-response projection. Unsupported strata stay
  unknown and prevent a whole-cohort mortality total.
- Apply sourced child age/sex eligibility and income-quartile contrasts.
  Preserve null-compatible estimates and the positive third-quartile earnings
  coefficient. Unknown child profiles cannot qualify for reviewed headlines.
- Add explicit real discount rates, event/valuation years and annual earnings
  schedules. Keep undiscounted totals, observed-adult-age-window projections
  and constant-career-gap extrapolations separately labeled.
- Compare annual household employment probabilities and gross earnings
  under a supplied unemployment duration and observed SIPP transitions.
  Sparse cells require explicit acceptance. Partner marginal earnings and
  children's ages are tracked; causal recovery and partner responses are
  not identified by these observational transitions.
- Propagate documented mortality-baseline counts, a declared integer exposure
  distribution, coefficients and independent-cohort binomial process variation.
  Keep fixed-input parameter intervals separate; transport error, structural
  model probabilities and unknown dependence remain outside this budget.

Reproducible inputs and results are committed in `validation/`. The new
`mortality-cohort`, `household` and `uncertainty` CLI commands accept those
inputs directly; `scenario` accepts the child eligibility and valuation flags.

## Evidence and evaluation

The source library retains 23 contrasts from three study samples. Repeated
horizons and subgroups are overlapping observations, not independent studies.
Danish cumulative hazard ratios cannot be pooled with annual odds ratios.
Their SEs are explicitly approximate, reconstructed from rounded 95% limits.
No compatible independent pool is claimed. A rate-limited Swedish full-text
request and the incomplete Finnish re-extraction remain in the screening log.
The previously recorded Swedish long-run null-compatible finding remains
visible; missing uncertainty is not invented.

`SCENARIO_EVIDENCE_PROTOCOL.md` freezes inclusion and scoring rules and records
the subsequent acquisition amendment. These are locally reproducible records,
not an independently timestamped prospective forecast. The original evaluation
is retained; `validation/followthrough_evaluation_expanded_20261014.json` executes the
expanded-library checks. Held-out SIPP transition discrepancies and existing
China-shock diagnostic misses remain visible.

Independent causal evaluation of the new paths still requires a matched
external displacement bridge and independently measured outcomes. Wider
age/sex admission, target-specific exposure/composition, monthly and joint
household dynamics, and a defensible transport-error model remain research
dependencies. The software refuses unsupported totals rather than filling
these gaps with zero or presenting conditional intervals as full certainty.

## Verification

Coverage: 96.8% statements and 93.2% branches, above the unchanged 95%/90%
gates. Focused checks cover source arithmetic, signed subgroup effects,
eligibility, unsupported strata, zero-rate valuation equivalence, zero-duration
household equivalence, uncertainty input compatibility and CLI routing.
The final full suite passes all **1,065 tests** after the saved examples and
methods refresh. Ruff and vulture pass; the evidence audit reports zero errors
and zero warnings. The built wheel passes an isolated-install check for all
three new commands plus audit, export, family, validate, scenario and bundle.

The final release audit rechecked 23 source-library contrasts and nine existing
parameter links against primary tables, alongside the 67-row mechanical audit
and existing extraction regressions. It does not claim a fresh primary-paper
re-extraction of the other 58 links. The current audit receipts are in
`tasks/review/2026-10-14-audit-04-release/card.md`.

## Per-result sensitivity - 2026-10-15

Scenario counts and child valuation projections now carry per-coefficient
removal experiments and supported-endpoint refits, with sources, units and
signed changes from the unrounded reference. Entity and policy-arm scenario
records inherit them. Reports retain fixed inputs and unavailable ranges;
they do not invent baseline, exposure or transport uncertainty. Optional
`scenario --sensitivity-base N` adds correlation-aware block variance
attribution separately from deterministic sensitivity and parameter intervals.
See `RESULT_SENSITIVITY.md` and the saved 2026-10-15 reference. Main estimates
and parameter versions are unchanged. Consumer rendering remains pending.
