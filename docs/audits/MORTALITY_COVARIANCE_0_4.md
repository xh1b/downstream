# Published additive mortality coefficients: covariance diagnostic

<!-- @ref:doc-mortality-covariance-0-4; @tag:mortality -->
<!--
Connections: @link:code-mortality-covariance; @link:doc-mortality-applicability-0-4; @link:doc-pool-readiness-0-4; @link:docs-index; @link:script-analyze-mortality-covariance; @link:test-mortality-covariance.
-->

Related: [Documentation map](../README.md) · [mortality applicability 0 4](MORTALITY_APPLICABILITY_0_4.md) · [pool readiness 0 4](POOL_READINESS_0_4.md).
Implementation: [mortality_covariance](../../src/downstream/mortality_covariance.py). Checks: [mortality_covariance](../../tests/test_mortality_covariance.py).

The missing covariance does not prevent us from bounding each additive phase's
standard error. It still prevents reproducing the authors' ordinary phase-sum
intervals or joint draws. This diagnostic changes no admitted coefficient,
production profile, scenario output or CLI behavior.

## Source and additive parameterization

The [existing reconciliation](MORTALITY_SOURCE_RECONCILIATION_2026-09-10.md)
distinguishes the published article's additive parameterization from the directly
reported working-paper phases. On 2026-10-15, the available [2009 author-manuscript
copy](https://www.movingforwardnetwork.com/wp-content/uploads/2023/04/Sullivan_Job-Displacement-and-Mortality_2009.pdf)
was downloaded, rendered and visually checked: PDF page 35, Table 4, column 1.
Its SHA-256 is `1f31b9c02bc20d22fbdf5f2e86e655646ee3f5ae62b31f3b15549dffa0c4dd55`.
This is **not** a fresh verification of the publisher's version of record.

The marginal coefficient/error pairs are: main 16+ `.131 (.054)`; additions
for 1 year `.716 (.199)`, 2-3 years `.559 (.147)`, 4-5 years `.198 (.147)`,
6-10 years `.057 (.094)`, and 11-15 years `-.066 (.081)`. The printed model is
logistic: these coefficients add on the **log-odds** scale, not the probability
scale. The column covers male birth cohorts 1930-1959 and tenure of at least six
years. Totals below use its manufacturing reference category, excluding the
separate nonmanufacturing interaction. The script retains printed timing labels;
it does not map them onto production follow-up years.

## What can be established without covariance

For a linear total `T = sum(a_i beta_i)`, define `l_i = |a_i| SE_i`. Over every
positive-semidefinite (PSD) covariance matrix with the reported marginal variances:

```text
minimum SE(T) = max(0, largest(l_i) - sum(other l_i))
maximum SE(T) = sum(l_i)
```

These bounds are sharp for one contrast. To see why, write a PSD covariance matrix
as a Gram matrix of vectors with lengths `SE_i`. The weighted sum's standard error
is the length of the sum of the weighted vectors. Align them to attain the maximum;
oppose the longest with the others, or form a closed polygon, to attain the minimum.
This argument also handles signed weights and zero marginal errors. For two terms,
it is the familiar `[|s_1-s_2|, s_1+s_2]` result at correlation -1 and +1.

| Printed phase label | Additive log-odds total | Smallest compatible SE | Largest compatible SE |
| --- | ---: | ---: | ---: |
| 1 year after displacement year | 0.847 | 0.145 | 0.253 |
| 2-3 years after displacement year | 0.690 | 0.093 | 0.201 |
| 4-5 years after displacement year | 0.329 | 0.093 | 0.201 |
| 6-10 years after displacement year | 0.188 | 0.040 | 0.148 |
| 11-15 years after displacement year | 0.065 | 0.027 | 0.135 |
| 16+ years after displacement | 0.131 | 0.054 | 0.054 |

The last row needs no covariance because it is one coefficient. It illustrates
why treating each addition's own SE as the total's SE would be incorrect.

The implementation also reports `point +/- 1.96 * maximum_SE` as an **outer normal
approximation envelope**. This contains the marginal normal-approximation interval
for any compatible covariance, conditional on that approximation and the supplied
marginal errors. It is not a source-reported confidence interval or an exact
finite-sample coverage guarantee. No independence, correlation scenario or covariance
estimate is supplied.

Each phase is bounded separately. Their minimum-error covariances need not be
jointly attainable. These envelopes are not a simultaneous band and cannot simply
be propagated as independent phase draws. They do not bound nonlinear twenty-year
deaths, address baseline aging, identify target-cohort transport or resolve timing
and source-version admission. The parent published-profile task remains open.

## Implementation and reproduction

[The diagnostic module](../../src/downstream/mortality_covariance.py) validates finite
coefficients, nonnegative marginal errors, named weights and nonempty contrasts.
If an active component SE is missing, it returns the point but withholds uncertainty;
it never fills the gap. Overflow produces an explicit error rather than nonstandard
JSON. Every phase is marked ineligible for model admission.

```sh
.venv/bin/python scripts/analyze_mortality_covariance.py
.venv/bin/python scripts/analyze_mortality_covariance.py --output /tmp/downstream-covariance.json
.venv/bin/python -m pytest tests/test_mortality_covariance.py -q
.venv/bin/ruff check src/downstream/mortality_covariance.py scripts/analyze_mortality_covariance.py tests/test_mortality_covariance.py
```

The report includes source locator/hash, additive components, phase totals, sharp
SE bounds, normal approximation envelopes and implementation hashes. Source PDFs
are not bundled by this change. Tests use analytic PSD witnesses, a closed polygon,
signed weights, missing errors, malformed/overflowing inputs and the manuscript
transcription. A future admission decision still needs source-version reconciliation
and an explicit scientifically justified uncertainty/transport contract.
