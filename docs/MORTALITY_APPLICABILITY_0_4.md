# Mortality applicability in 0.4

<!-- @ref:doc-mortality-applicability-0-4; @tag:mortality -->
<!--
Connections: @link:code-mortality-profiles; @link:code-mortality-strata; @link:doc-mortality-source-reconciliation-2026-09-10; @link:doc-mortality-covariance-0-4; @link:docs-index; @link:script-build-age-mortality; @link:script-build-cohort-projection; @link:test-mortality-admission-0-4; @link:test-mortality-profiles; @link:test-mortality-strata.
-->

Related: [Documentation map](README.md) · [mortality source reconciliation 2026-09-10](MORTALITY_SOURCE_RECONCILIATION_2026-09-10.md) · [mortality covariance 0 4](MORTALITY_COVARIANCE_0_4.md).
Implementation: [mortality_profiles](../src/downstream/mortality_profiles.py), [mortality_strata](../src/downstream/mortality_strata.py). Checks: [mortality_admission_0_4](../tests/test_mortality_admission_0_4.py), [mortality_profiles](../tests/test_mortality_profiles.py), [mortality_strata](../tests/test_mortality_strata.py).

Mortality baseline coverage and causal-response coverage are different. A
verified mortality rate for a demographic group never admits the default
displacement response for that group.

| Path | Response admission | Baseline handling | Interpretation |
|:---|:---|:---|:---|
| Standard scenario/profile | Male, ages 45–54, all causes; high-tenure mass-layoff response | Fixed compatible annual rate, or a declared compatible profile mixture | Conditional reference; target transport needs review |
| `mortality-cohort` | Separate Table 7 source contrasts for men displaced ages 30–39, 40–49, 50–59 or 60–69; tenure at least six years | Compare attained-age band rates against a fixed baseline | Conditional constant source-window projection |

The stratum path does not reuse the default response outside its admitted
age band. It selects the separately recorded age-at-displacement coefficient
from `study_estimates.csv`. Each record must match the annual all-cause logit
scale, sex, exact source age band, tenure, treatment, comparator, follow-up
window and projection status. Missing or incompatible source rows fail rather
than falling back to another age or to the standard scenario.

This review found and fixed a contract omission: the stratum consumer checked
scale and demographic/window metadata but did not check the treatment and
comparator. A custom row describing voluntary quits or a comparison among
displaced workers could otherwise pass. Both fields are now enforced.

The source also restricts the sample to stable employment in 1974–1979 and
employers with more than 50 employees. Tenure alone does not establish that
employment history. Supported output now carries these restrictions and the
remaining geography, calendar-time, recession and event-design assumptions.
The employer-size condition and its measurement timing have not been verified
for the target; no new size-based eligibility rule is inferred from that
incomplete metadata. Firm closure remains conditional transport
of a mass-layoff response, not a separately identified closure coefficient.

Every stratum projection stays ineligible for a public headline. Its
`constant_source_window_log_odds` assumption holds a window-averaged response
constant through follow-up. Aging changes baseline rates; it does not identify
how the displacement response itself changes as survivors age. Protective and
null-compatible source estimates remain signed. Marginal coefficient ranges
form a Cartesian envelope, not a simultaneous cohort confidence interval.

Women, unknown sex, unsupported event ages, short tenure and incompatible
events remain unmodeled even though baseline rates may exist. Positive
unmodeled exposure withholds the whole-cohort total; it is never assigned a
zero response. Expanding eligibility requires a separately admitted compatible
effect estimate and an explicit projection/transport contract.

This is a code and existing-source-contract review, not a fresh extraction or
new evidence admission. Sources and numerical defaults are unchanged.

Implementation: [mortality_strata.py](../src/downstream/mortality_strata.py).
Admission/refusal checks: [test_mortality_admission_0_4.py](../tests/test_mortality_admission_0_4.py).
Existing baseline profile gate: [mortality_profiles.py](../src/downstream/mortality_profiles.py).
