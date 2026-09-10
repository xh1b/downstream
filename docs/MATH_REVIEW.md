# Math review — engine 0.2.0, parameters v1.34

The review checks implemented arithmetic and probability propagation. It
does not certify every paper extraction, causal bridge, or policy forecast.
The current suite passes 491 tests. The parameter audit reports zero errors
and 66 warnings, chiefly evidence and graph-boundary warnings.

| Finding | Correction | Verification |
| --- | --- | --- |
| Mortality coefficients are odds ratios, but counts treated them as risk ratios | Convert with `q = r*m/(1-m+r*m)` and compare exposed/unexposed survival | One-year identities, zero effect, zero horizon, and bounded cohort deaths |
| Peak and sustained contributions double-counted timing | Total follow-up includes the peak year; subsequent years use the sustained coefficient | Explicit legacy mode retains historical arithmetic |
| Place effects received additional applications on descendants | Adjust the initial child once, then transmit the adjusted gap | Descendant identity and a single place step in the ledger |
| Interval endpoints assumed positive values and gaps below one | Evaluate every endpoint corner for products and gap transmission | Bounds above the counterfactual and structural variant envelopes |
| Declared lognormal rows fell through to uniform moments; normal rows were refused | Compute the sampler's clamped first three moments, including endpoint atoms | Compare moments with deterministic quantile integration |
| Reusing a parameter violates independent-step moment propagation | Refuse reused uncertain links in that analytic interface | Regression test; Monte Carlo remains available |
| The additive structural variant had reversed bound combinations | Add lower endpoints together and upper endpoints together | Every reported variant contains its point |
| Count and policy outputs obscured uncertainty sources | Report parameter-support and exposure envelopes separately with exclusions | Identical cases cancel; exposure bands widen results; provenance is required |

The current pinned parameter file extracts a coherent Table 5 column 3 mortality profile,
including early offsets and the correct +6 boundary. It is still a
historical high-seniority male Pennsylvania mass-layoff estimand, not a
general displacement effect. Engine 0.2.0 changes the arithmetic.
Historical V1 scorecards retain their original additive mortality formula;
they are not presented as validation of the corrected survival model.

## Assumptions still needing evaluation

- The mortality profile has grouped offsets, not a full annual aging or
  competing-risk model. The +6 estimate is extrapolated beyond the observed
  horizon and the baseline stays constant.
- A county income-rank exposure effect scales a same-place displacement loss.
  This passes the null-displacement check but is still an unvalidated
  structural bridge, not an identified interaction.
- Independent analytic moments do not incorporate the two declared
  earnings/mortality correlations. Monte Carlo uses those pairs, whose
  magnitudes are judgment rather than extracted covariance estimates.
- Count envelopes hold baseline estimates, county measurements, and
  pooling weights fixed. They are not complete confidence intervals.
- Direct displacement, divorce, and family-size effects can overlap.
  The combined child view remains a named structural experiment. It is
  not a sum of independently identified causal contributions.
- Housing and remarriage pathways lack the upstream incidence or causal
  response estimates needed for end-to-end displacement predictions.
- Policy comparisons condition on supplied exposures. The model does
  not identify a law's effect on displacement or establish individual harm.
- BRAC now has a reconciled base-job inventory. Independent outcome
  alignment and scoring remain incomplete; prospective events remain
  unregistered. Passing code tests does not remove those gaps.

The next model work is to test these assumptions and strengthen independent
validation. XH1B integration is deferred by the owner's current direction.
