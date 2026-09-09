# Deep mathematics and code audit — 2026-09-09

## Executive conclusion

The shipped scenario calculation has important strengths: its mortality
conversion is now mathematically coherent **conditional on the parameter
being an annual odds ratio**, child gaps propagate in gap space, and the
county modifier is applied once before transmission in the default path.
The new count intervals are also correctly labeled as parameter-only.

However, this review found two P1 issues that should be resolved before
using validation or arbitrary-chain commands as evidence-bearing outputs:

1. The apparent type system is not enforced at runtime for arbitrary
   chains. A caller can apply a mortality odds ratio as a level multiplier,
   or allow the CLI's default `level` kind to do so, and receives a plausible
   numerical answer rather than a refusal.
2. V1 retrodiction and the future-scoring branch of V2 still use the old
   additive mortality expression, not the production odds-to-risk survival
   model. They can therefore grade a different model from the one shipped to
   users.

Three further P1 issues make some uncertainty/diagnostic outputs internally
inconsistent: normal/lognormal parameters are centered differently outside
the production Monte Carlo; sensitivity deliberately/implicitly omits the
declared correlations without flagging that its Sobol estimand changed; and
validation's divorce simulation uses a uniform distribution despite the
parameter's effective log-space distribution.

This is a code and mathematics audit, not a new literature review. It does
not decide whether the cited causal estimates generalize. It checks whether
the repository computes and describes its own declared model consistently.

## Repair status — 2026-09-09

All actionable numerical/code findings in this report have now been repaired
and regression-tested.

- Arbitrary public chains now require explicit kinds and are restricted to
  links with a declared context-safe chain operation; boundary coefficients
  fail loudly.
- V1 and the scoreable V2 mortality branch use the production
  odds-to-risk/survival kernel. V2 additionally blocks if its bridge lacks a
  cited baseline mortality probability instead of reusing measured excess
  deaths as a baseline.
- All sampling paths now use one point-aware materialization helper. Sobol,
  analytic, and closure outputs explicitly stamp their independent-input
  estimand; correlation stress retains declared production correlations.
- Spearman inputs are converted to Gaussian-copula latent correlations before
  Cholesky; the regression test checks achieved sample rank correlation.
- "Exact" log-space shares now refuse normal/lognormal marginals rather than
  using a wrong uniform formula. Scenario quantiles use unrounded internal
  counts. Parameter, node, baseline, and place loaders reject duplicate or
  non-finite source rows. School-spending cut steps preserve ordered bounds.
- Boundary inputs are now declared as such and uncited cross-check
  bibliography is informational, leaving the static audit at 0 errors / 0
  warnings. New `tests/test_audit_repairs.py` locks the numerical repairs.

## Scope and method

Reviewed source modules, public CLI verbs, parameter/node/correlation data,
the mathematical test suite, and validation code. The review used four
independent checks:

1. **Symbolic trace.** Re-derived each active transformation: level, direct,
   gap, odds-to-risk, survival, exposure conversion, partial pooling, and
   interval corners.
2. **Cross-surface trace.** Followed the same parameter through `scenario`,
   `simulate`, `infer`, `sensitivity`, `validate`, `policy`, and the
   explanation path to identify semantic or sampling drift.
3. **Adversarial probes.** Ran intentionally invalid compositions and
   compared production sampling with inference sampling for an asymmetric
   normal row.
4. **Regression checks.** Ran the relevant scenario, CLI, mathematics, and
   place-sampling suites: `31 passed`. `downstream audit` returned zero
   errors and 66 warnings; its warning volume is discussed below.

The preceding sentence records the audit-time baseline. After remediation,
the expanded focused suite passed 119 tests and the static audit reports zero
errors, zero warnings, and 49 informational uncited cross-check entries.

No production parameter values were changed by this audit.

## What checks out

### Mortality formula in the scenario path

`odds_risk(b, OR) = OR*b / (1-b+OR*b)` in
`src/downstream/mortality.py:6-11` is the correct conversion from a baseline
event probability and an odds ratio. The default count calculation then uses

```
S0 = (1 - b)^Y
S1 = (1 - q_peak)^min(Y,1) * (1 - q_sustained)^max(Y-1,0)
excess deaths = N * (S0 - S1)
```

in `src/downstream/mortality.py:14-36`. This avoids both common errors:
treating an odds ratio as a risk ratio and applying the acute peak to every
follow-up year. It has sensible boundary behavior (`Y=0`, `N=0`, null odds
ratios), accepts fractional years, and cannot produce more than `N` excess
deaths when the inputs are probabilities and positive odds ratios.

The formula remains conditional on a strong *model assumption*: the
year-6-and-later coefficient is used in every post-peak year. That is
declared in code and output, but it is extrapolation, not an identified
annual effect profile. The legacy additive option deliberately retains the
old approximation and should remain visibly non-default.

### Gap and interval algebra

For a transmission `t` and an inherited multiplier `x`, the ledger uses
`1 - t(1-x)`, correctly transmitting the **gap**, not multiplying levels.
`Ledger._step` evaluates all four endpoint corners for both level and gap
steps (`src/downstream/ledger.py:63-85`), which is the safe envelope method
when sign/direction might differ. The focused tests independently verify the
child-to-grandchild identity and the signed-envelope case.

`child_line` applies a place modifier to the initial child and then carries
that modified gap through both descendant transitions
(`src/downstream/children.py:32-56`). The old repeated descendant behavior is
available only as an explicitly named legacy setting. This is a material
improvement over compounding the same place effect per generation.

### Count uncertainty labeling

`sample_counts` jointly samples all headline counts on each draw
(`src/downstream/scenario.py:199-245`). It keeps the original `low`/`high`
support envelope separate from `parameter_interval_90`, and explicitly names
fixed/excluded uncertainty sources. This avoids labeling a parameter-support
range as a confidence interval or presenting a partial interval as total
uncertainty. The use of shared draws preserves dependence among the reported
headlines.

### Other safeguards that behave as intended

- Negative/non-finite scenario exposure inputs are rejected.
- Unknown/missing baselines block rather than fabricate count conversions.
- Employer warehouse aggregates validate component reconciliation and retain
  exposure provenance.
- The bundle checksum path checks both individual files and manifest digest.
- Prospective forecast registration refuses overwrite and checks that the
  outcome window has not begun.

## Findings

Severity meanings: **P1** should be fixed before a surface is presented as a
validated/diagnostic model output; **P2** is a meaningful correctness or
reproducibility issue with narrower reach; **P3** is robustness, usability,
or audit-signal debt.

### P1 — arbitrary chains bypass unit/composition safety

**Evidence.** `Ledger.apply` accepts any of `level`, `gap`, `direct`, and
`rate` without comparing the selected kind against the parameter's
`from_node`/`to_node` units (`src/downstream/ledger.py:87-99`). `chain` simply
passes the caller's choices through (`:106-113`). `simulate_chain` defaults
all omitted kinds to `level` (`src/downstream/mc.py:171-194`), and the CLI
does the same (`src/downstream/cli.py`, simulate branch).

**Reproduction.**

```
downstream simulate --links 'earnings_shock->mortality_peak' --draws 20
downstream infer --links 'earnings_shock->mortality_peak' --action shares
```

Both return a number. The first reports a `level` chain whose sole parameter
is an odds ratio; the second calls a log-space variance decomposition
"Exact." Neither is a valid mortality computation.

**Why it matters.** The repository claims typed ledger enforcement, but this
public route can silently create a valid-looking yet meaningless result. The
parameter-file audit only checks that a *possible* composition exists; it
does not constrain a caller's chosen composition.

**Remediation.** Make the chain API accept nodes (or start/end units) and
validate every requested transition with `units.composition_for`. The safest
public behavior is to require explicit kinds for arbitrary chains and reject
`rate` links except at named count-boundary adapters. Add CLI traps for every
invalid `(unit pair, kind)` and a test proving omitted kinds are refused (or
correctly inferred only when unambiguous).

### P1 — validation scores the retired mortality arithmetic

**Evidence.** The shipped scenario calls `excess_deaths`, but
`v1_retrodict` defines instead

```
n * mortality_rate * ((sustained - 1) * WINDOW + (peak - 1))
```

at `src/downstream/validate.py:423-435`. The future V2 scoring branch repeats
the same expression at `:803-824`.

This differs in two ways from production: it treats odds ratios as additive
risk increments and applies sustained excess to all `WINDOW` years in
addition to the acute peak. For `N=2,520`, `b=.003`, `peak=2.672`,
`sustained=1.135`, and ten years, the validation expression gives `22.8463`
and the shipped survival model gives `21.0561`: an 8.50% difference.

**Why it matters.** V1's pass/miss claims and any eventual V2 score are not
scores of the model exposed by `scenario`. That defeats the purpose of a
back-test even if the direction of the difference is modest for this baseline.

**Remediation.** Route all mortality scoring through one shared function,
preferably `excess_deaths`, with an explicit validated baseline, outcome
window, and method stamped into the scorecard. Recompute the current V1
scorecard under the shipped default; retain the old score only as a labeled
historical comparison. Add a test that V1/V2 and `scenario` agree exactly for
the same synthetic exposure/baseline/window.

### P1 — inference and sensitivity do not sample CI-shaped rows like production MC

**Evidence.** Production MC passes `point=p.point` to
`sample_unit_interval` (`src/downstream/mc.py:87` and `:146-147`). That is
required because normal/lognormal CI rows are centered on the reported
estimate, not necessarily the midpoint/geometric midpoint of rounded bounds.

Four inference paths omit it:

- `src/downstream/inference.py:347-348` (`_draw_samples`)
- `src/downstream/inference.py:404` (closure-test truths)
- `src/downstream/inference.py:504-505` (correlation stress)
- `src/downstream/sensitivity.py:52-57` (Sobol designs)

**Reproduction.** For the declared-normal
`unemployment_status->mental_health_sd` row, point `.510`, bounds
`[.470, .540]`, 5,000 draws yielded:

| Surface | Mean | 5th | 95th |
|---|---:|---:|---:|
| Production MC | .5097 | .4806 | .5394 |
| Inference raw sampler | .5050 | .4756 | .5344 |
| Analytic moments (correct center) | .5097 | .4812 | .5369 |

The `analytic_vs_mc` diagnostic reports a `19.621`-standard-error mean
disagreement in this one-link example—not evidence against the analytic
identity, but a sampler mismatch introduced by the diagnostic itself.

**Why it matters.** Generic `infer agree`, closure coverage, correlation
stress, and sensitivity results can be centered on a different model than
the published MC/count intervals. Existing child-line tests do not expose it
because their active rows are flat uniform.

**Remediation.** Centralize draw materialization in one helper used by MC,
inference, stress, and sensitivity; always pass the row point. Add an
asymmetric normal and asymmetric lognormal integration test that compares
all surfaces to the same expected moments and quantiles.

### P1 — sensitivity/analytic outputs silently change the correlation model

**Evidence.** Default production `simulate` loads the two declared
correlations from `params/correlations.csv`. `_draw_samples`,
`closure_coverage`, `analytic_vs_mc`, and `sobol_indices` construct plans
without those correlations. `analytic_chain` states independence but its CLI
does not say that declared correlations are being excluded. The correlation
stress function's prose still says the declared matrix is empty, although the
repository now has two declared pairs.

**Why it matters.** Classical Sobol indices assume independent inputs, so a
plain Sobol analysis can be legitimate—but it is a *different estimand* and
must not be presented as explaining the default correlated MC interval.
Likewise, an analytic-vs-MC agreement check must either compare two
independent samplers or explicitly reject correlated parameter sets.

**Remediation.** Stamp every analytic/sensitivity output with
`assumes_independent_parameters: true`; refuse an unqualified agreement or
closure claim when declared correlations are active. For correlated global
sensitivity, either use a documented dependent-input method or present a
separate correlation stress result. Correct the stale stress documentation.

### P2 — declared Spearman correlations are used as latent Pearson correlations

**Evidence.** `apply_rank_correlation` feeds the supplied matrix directly to
a normal-score Cholesky factor (`src/downstream/distributions.py:143-157`).
For a Gaussian copula, latent Pearson `r` produces rank Spearman
`rho_s = 6/pi * asin(r/2)`, not `r` itself. With the declared `-0.5`, a
100,000-draw probe achieved `-0.48345` rank correlation (the theoretical
value is `-0.48258`), not `-0.5`.

**Why it matters.** The deviation is modest for the currently declared pair,
but the output says the declared Spearman matrix was applied. Larger future
correlations would amplify the mismatch.

**Remediation.** Convert desired Spearman values to Gaussian-copula latent
correlations with `2*sin(pi*rho_s/6)`, then validate the transformed matrix
is positive definite. Rename/document the argument if the intended input is
instead latent Pearson correlation. Add a tolerance test on achieved sample
rank correlation.

### P2 — `logspace_variance_shares` overclaims exactness for normal/lognormal rows

**Evidence.** `logspace_variance_shares` selects the declared distribution,
but `_var_log` treats every non-loguniform distribution as a raw uniform
(`src/downstream/inference.py:244-268`). This is not the distribution used
for a `normal` or clamped `lognormal` row. The function nevertheless labels
its result "EXACT" at `:271-325`.

**Why it matters.** The output is exact for uniform/loguniform level chains
only. It is not exact for the CI-shaped rows the project deliberately added.
The arbitrary-chain bypass above makes this easy to invoke on semantically
invalid as well as statistically misdescribed chains.

**Remediation.** Either implement the corresponding clamped-normal/lognormal
log moments (using the same sampler semantics) or refuse those distributions.
Narrow the claim in code/output and require validated level transitions.

### P2 — validation has additional distribution and provenance drift

**Evidence.** `v1_panel` samples the divorce rate ratio with
`rng.uniform(divorce.low, divorce.high)` at
`src/downstream/validate.py:593-600`, while the effective model distribution
for that positive rate ratio is log-uniform. It also hard-codes divorce
baseline `.1045`, married share `.5305`, women share `.503`, and the
displacement bridge range rather than loading/stamping their source rows.

**Why it matters.** It weakens reproducibility and makes the validation
distribution differ from the declared engine distribution. Parameter or
baseline updates can silently change one surface but not the other.

**Remediation.** Materialize the scorecard draws through the shared sampler;
put bridge/demographic constants in a versioned, cited validation input file;
emit its content hash in the scorecard; and test that a changed source value
changes the scorecard through one named input.

### P2 — count-interval sampling quantizes the quantity before estimating quantiles

**Evidence.** `sample_counts` calls `compute_counts` on every draw and uses
the public `"point"` fields (`src/downstream/scenario.py:226-229`). Those
fields are rounded to two decimals for deaths and dollars before quantiles
are computed (`:146-181`).

**Why it matters.** At large exposures this is negligible, but at small
exposures it produces artificial ties and can move a reported percentile by
the rounding unit. Sampling should operate on full precision and only round
the final rendered summary.

**Remediation.** Separate numeric kernel results from serialization; retain
full-precision count values inside sampling and round only at the API output.
Add a one-worker/small-baseline regression test.

### P2 — input/data validation is deferred too late

**Evidence.** `load` parses parameters and only runs a cycle check
(`src/downstream/params.py:130-154`). Duplicate links, non-finite values,
invalid tiers, invalid units, and point-outside-band data are caught only by
the optional audit. Node and place loaders also silently overwrite duplicate
keys. `shrink` accepts non-finite precision/prior values without a direct
guard (`src/downstream/place.py:158-172`).

**Why it matters.** Normal CLI computation can consume an invalid edited CSV
before an export audit is run; `by_link` then silently takes the first
duplicate. This is particularly risky because parameters are source data,
not generated cache.

**Remediation.** Make loading enforce finite values, ordered bands, unique
links/nodes/place keys, known units/tiers/distributions, and non-negative
finite precision. Keep the audit for cross-file quality warnings, but make
invalid compute inputs impossible to load.

### P3 — school-spending step provenance stores inverted bounds for a cut

**Evidence.** For a `-10%` twelve-year spending exposure,
`school_spending_child_earnings` yields a ledger state of
`point=.93, low=.90, high=.97`, but its recorded `Step.value` is
`(.93, .97, .90)` because negative intensity reverses the scaled interval
before `Ledger.apply` fixes the ledger ordering
(`src/downstream/community.py:50-72`).

**Why it matters.** The user-facing final range is ordered, but the embedded
audit trail says `value_low > value_high`, contradicting its own invariant.

**Remediation.** Order scaled bounds before constructing the temporary
parameter, and validate finite spending intensity/duration. Add a negative-
exposure step-audit test.

### P3 — audit signal-to-noise and stale claims

The audit has zero errors but emits 66 warnings, many expected boundary
links and deliberately retained bibliography entries. A warning channel this
large makes a new meaningful warning easy to miss. Several comments/docs
also lag the current state, including the correlation-stress assertion that
the declared matrix is empty. Classify intentionally boundary-applied nodes
explicitly, distinguish pending references from cross-check bibliography,
and promote contradictory/stale claims to a small tracked documentation
check.

**Resolved.** Boundary-applied inputs are now declared entry nodes and
uncited cross-check bibliography is informational rather than warning-level.
The audit is now `0 errors / 0 warnings / 49 info`; an unexpected graph gap
again produces a warning.

## Recommended repair order

1. **Block invalid chain composition** and remove the CLI default that makes
   arbitrary links `level` chains. This prevents new false calculations.
2. **Unify mortality scoring with `excess_deaths`**; regenerate and publish
   the changed V1 scorecard before claiming an external back-test.
3. **Centralize materialization of parameter draws** (point-aware,
   distribution-aware, correlation-aware). Use it everywhere or explicitly
   state/refuse a different independence estimand.
4. Correct the Spearman-to-copula mapping and add achieved-rank tests.
5. Repair exact-share scope, validation input provenance, pre-quantile
   rounding, and loader validation.
6. Clean the P3 audit trail/documentation issues after the numerical paths
   are trustworthy.

## Regression tests required for closure

- Every illegal unit/kind pair raises from both Python and CLI APIs.
- Scenario, V1, and V2 mortality scores agree for identical synthetic input.
- Production MC, inference agreement, closure truth draws, correlation
  stress, and Sobol materialization agree on asymmetric normal/lognormal
  marginals where they claim the same distribution.
- A declared Spearman `rho` produces sample rank correlation within a
  prespecified Monte Carlo tolerance.
- `logspace_variance_shares` either matches a high-draw reference for every
  accepted distribution or refuses that distribution.
- Count intervals are invariant to display rounding at small exposures.
- CSV loaders reject duplicate/non-finite/out-of-band source rows.
- Negative school-spending exposures have ordered final and step ranges.

## Remaining epistemic limitations after code fixes

None of the repairs above resolves the substantive open items: county
mortality data, event-specific exposure bridges, independent outcome
measurements, prospective timestamped forecasts, common-cause correlation
evidence, the structural composition of parallel child pathways, or the
external validity gap between studied populations and an arbitrary
displacement event. Those must remain separately represented rather than
being converted into narrower-looking numerical bands.
