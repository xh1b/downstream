# Inspect child source support in 0.4

The source-support report makes the existing Canadian father-son earnings
source and its income contrasts inspectable together. It admits no new effect,
age-response curve or country-specific evidence. The wider extraction work in
`2026-10-14-child-heterogeneity` remains open.

```python
from downstream.child_support import child_support_report

report = child_support_report()  # source rows remain visible; target is unknown
```

Pass a validated `ScenarioInput` to inspect target child profiles, parent/event
metadata, income-rank mapping and an existing transport decision. Optionally
pass `parent_tenure_years` to inspect the source's two-year minimum. A label
such as `high-tenure` does not establish a numeric tenure value. This extra
inspection does not alter the scenario engine's gates or numerical defaults.

The standalone command prints the same structured report:

```sh
python3 scripts/inspect_child_support.py
python3 scripts/inspect_child_support.py --input scenario.json --parent-tenure-years 6
```

`scenario.json` contains `ScenarioInput` fields, rather than a mortality-cohort
or warehouse-exposure payload. `--params-dir` reads that directory's source
library; missing custom files never fall back to bundled contrasts.

## Existing source conditions

| Dimension | Existing source scope |
|:---|:---|
| Child | Sons aged 10–14 at displacement |
| Parent | Father; minimum tenure two years as recorded in the source library |
| Event | Father's firm closure in 1980–1982 |
| Country | Canada |
| Income groups | Father's average pre-displacement income in 1978–1979 |
| Outcome | Log son earnings averaged 1995–1999, at ages 25–33 |
| Overall contrast | Table 2, column 3, with pre-displacement income controls |
| Income contrasts | Table 8, columns 1–4, retained separately |

Each contrast retains its citation, source URL, source SHA-256, locator,
design, treatment, comparator, outcome and population metadata. The consumer
checks the source scale, ages, sex, tenure minimum, income group, treatment,
comparator, outcome window and projection status before displaying it. Unknown
additional parent restrictions are not filled in from assumptions.

## Support states

- `refused`: known child, parent/child sex or event mismatch, or declared
  numeric parent tenure below two years. Source rows remain visible to explain
  the refusal; no scenario total is supplied.
- `unknown`: no known mismatch, but child profiles, parent/event metadata,
  numeric tenure or income-rank mapping remain undeclared.
- `conditional_transport`: inspected dimensions match, with the source
  response's transport and lifetime-path assumptions still explicit.
- `reviewed_conditional_transport`: the same inspected dimensions match and
  the scenario includes a reviewed child transport decision. That decision
  stays conditional; this inspection report itself is never a public headline.

Country and period differences produce explicit transport conditions rather
than fabricated local evidence. The source's Canadian estimate never changes
into a US estimate just because the target says `US`.

## Signed contrasts and uncertainty

The report returns beta and its reported standard error, the earnings
multiplier `exp(beta)` with `exp(beta +/- 1.96*SE)`, and the signed relative
gap `100*(1 - multiplier)`. Positive gaps mean earnings below reference;
negative gaps mean earnings above it. The third quartile's positive log
earnings estimate therefore remains a negative loss, and all four quartile
intervals cross zero. Nonsignificance is not replaced with a zero estimate.

These are approximate marginal 95% Wald intervals from the source coefficients,
not a joint band across groups, independent replications, or uncertainty about
transport. Exact transforms can differ slightly from the rounded support
endpoints used in the engine's default parameter row. No averaging or pooling
across income groups is performed, and no lifetime or descendant totals are
calculated here.

Implementation: [child_support.py](../src/downstream/child_support.py).
Contract tests: [test_child_support.py](../tests/test_child_support.py).
Current admitted records: [study_estimates.csv](../params/study_estimates.csv).
