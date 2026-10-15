# Annual household comparison summaries in 0.4

<!-- @ref:doc-household-comparison-0-4; @tag:household -->
<!--
Connections: @link:code-household; @link:doc-baseline-transition-r2-2026-09-14; @link:doc-life-course-research-plan; @link:docs-index; @link:paper-household; @link:test-household; @link:test-household-summary.
-->

Related: [Documentation map](README.md) · [baseline transition r2 2026-09-14](BASELINE_TRANSITION_R2_2026-09-14.md) · [life course research plan](LIFE_COURSE_RESEARCH_PLAN.md).
Implementation: [household](../src/downstream/household.py). Checks: [household](../tests/test_household.py), [household_summary](../tests/test_household_summary.py).

`household_comparison(payload, params_dir=None)` now returns cumulative paired
arm summaries for every adult and the household, in addition to existing
annual rows and the legacy cumulative difference field. This extends the
inspectability of the annual prototype; the broader household dynamics and
receiving-community comparison tasks remain open.

```python
import json
from pathlib import Path

from downstream.household import household_comparison

payload = json.loads(Path("validation/household_five_year_input.json").read_text())
payload["event"]["calendar_year"] = 2026  # optional whole-year scenario labels
result = household_comparison(payload)
print(json.dumps(result["summary"], indent=2, allow_nan=False))
```

The existing `downstream household --input ...` command returns these added
fields automatically. No new causal estimates, transition coefficients,
uncertainty distributions or model defaults are introduced.

## Summary contract

`summary.members` contains one row per supplied adult, preserving input order
and ID. `summary.household` sums those adult expectations. Both contain
`reference`, `displacement` and `displacement_minus_reference` blocks with:

- `gross_earnings_usd_2024`: cumulative expected gross earnings in the declared
  arm, or the signed paired difference across the follow-up window.
- `expected_state_person_years`: expected E (employed), U (unemployed) and N
  (not in labor force) years across that same window, or their signed changes.

These are **sums of annual marginal expectations**. No independence assumption
between members is needed to add expected earnings or expected state time.
This does not identify the probability of both adults being unemployed, the
distribution of household resources, partner responses to displacement or
other joint outcomes.

Annual state probabilities are treated as weights over one-year scenario
intervals. Expected state person-years are therefore an annual-model summary,
not observed spell lengths or a monthly employment model. Each adult's E/U/N
person-years sum to the follow-up length; household person-years sum to adult
count times follow-up length. State-time differences sum to zero. Cumulative
gross earnings and differences reconcile with the annual adult rows and the
household sum, up to floating-point precision.

The signed difference is always **displacement minus reference**: negative
earnings means less gross earnings, positive means more. Supplied beneficial
earnings paths are retained rather than clamped to losses. Differences are
computed from paired adult earnings before aggregation, preventing a small
worker loss from disappearing when an unaffected partner's earnings are very
large. Subtracting two separately rounded displayed arm totals can consequently
be less precise than the returned paired difference. The legacy
`cumulative_earnings_difference_usd_2024` equals the summary household difference.

All earnings are gross, undiscounted amounts in 2024 dollars. They do not
include taxes, transfers, savings, consumption, household economies of scale,
housing or children's future earnings.

## Follow-up and calendar windows

Annual `year_after_event` stays zero-based. The report also gives a one-based
`follow_up_year_number` and each row's `[start, end_exclusive)` follow-up
interval. Five years means intervals `[0,1)` through `[4,5)`, not six annual
observations.

If supplied, `event.calendar_year` must be an integer from 1900 through 2200.
It labels the first whole-year scenario interval; successive rows increment
that year. An event year of 2026 and five-year follow-up yield year labels
2026–2030 and an exclusive calendar end of 2031. These labels do not establish
the actual event month or date. If absent, annual calendar labels and calendar
window endpoints stay null. The source's December 2021–December 2022 transition
window is never substituted for a missing scenario calendar window.

## Validation and actual transition use

The source rows still require valid, normalized-for-rounding probabilities,
unique transition keys and explicit sparse-cell acceptance when used. Sample
counts must now be positive. Malformed payload/event/member objects fail with
clear contract errors; earnings-path assumptions must contain text.

During supplied forced unemployment, no transition lookup is performed for a
state that the supplied duration immediately overwrites. Such cells no longer
appear as used or trigger sparse/missing-cell refusals. Transitions needed in
the reference arm, partner arm or after the forced spell remain gated.
This fixes a provenance and validation defect without changing the forced
unemployment scenario itself.

Source transitions remain observational conditional shares, reused by a
stationary annual Markov assumption. They do not identify a causal recovery
response for displaced workers. Source cells can be sparse; no survey-design
or full household prediction interval is claimed. Input exposure, supplied
duration and earnings paths remain scenario assumptions.

Implementation: [household.py](../src/downstream/household.py).
Reconciliation and refusal tests: [test_household_summary.py](../tests/test_household_summary.py).
