# Child and descendant earnings gaps

<!-- @ref:doc-child-gap-view; @tag:children -->
<!--
Connections: @link:code-child-gap-view; @link:code-children; @link:code-transmissions; @link:code-valuation; @link:doc-child-support-0-4; @link:doc-place-counterfactual; @link:docs-index;
@link:paper-children; @link:test-child-gap-view; @link:test-child-gap-cli; @link:test-transmissions.
-->

Related: [Documentation map](README.md) · [child support 0 4](CHILD_SUPPORT_0_4.md) · [place counterfactual](PLACE_COUNTERFACTUAL.md).
Implementation: [child_gap_view](../src/downstream/child_gap_view.py), [children](../src/downstream/children.py), [transmissions](../src/downstream/transmissions.py), [valuation](../src/downstream/valuation.py). Checks: [child_gap_view](../tests/test_child_gap_view.py), [child_gap_cli](../tests/test_child_gap_cli.py), [transmissions](../tests/test_transmissions.py).

`downstream.child_gap_view.child_gap_view` provides one structured explanation
report containing the existing child, grandchild and great-grandchild earnings
paths. It combines views rather than adding effects. Engine and parameter
defaults are unchanged.

```python
import json

from downstream.child_gap_view import child_gap_view
from downstream.params import load_all
from downstream.scenario import ScenarioInput

bundle = load_all()
report = child_gap_view(
    bundle["params"], bundle["baselines"],
    ScenarioInput(displaced_workers=1000, n_children=2),
)
print(json.dumps(report, indent=2, allow_nan=False))
```

The keyword arguments `places`, `place_key`, `mortality_profiles`,
`county_mortality` and `params_dir` have the same meanings as in
`compute_counts`. A caller using a custom parameter directory must pass
`params_dir` for income-quartile contrasts; missing custom source files never
fall back to bundled contrasts.

## Reading the report

The current national reference produces these per-person relative earnings
gaps, displayed here rounded for readability:

| Generation | Earnings below reference | Support envelope | Evidence status |
|:---|---:|---:|:---|
| Child | 9.24% | 2.40%–15.60% | Direct estimate, conditional target transport |
| Grandchild | 5.082% | 0.96%–9.36% | Structural projection |
| Great-grandchild | 2.7951% | 0.384%–5.616% | Repeated structural projection |

The child entry is the Canadian father-son firm-closure estimate. Descendant
rows apply the existing intergenerational earnings persistence assumption in
gap space: `next_gap = persistence * preceding_gap`. They are not independently
identified effects of displacement on grandchildren or great-grandchildren.
The evidence status and each cited ledger step travel with every row.

`value` uses `100 * (1 - earnings_multiplier)`. Positive values mean earnings
below the no-displacement reference; negative values mean earnings above it.
The transformation reverses interval endpoints. Benefits and ranges crossing
zero are preserved, including the source income-quartile contrasts. A null
child response stays null throughout the transmission.

`uncertainty.band_kind` is a parameter-support envelope, **not a confidence
interval**. The report transforms existing ledger support ranges; it does not
estimate a joint sampling distribution, model probabilities, or transport
uncertainty. It keeps exposure, baseline values, county measurements and
pooling weights fixed, as declared by the underlying scenario calculation.

Only the child row can carry `dollar_conversion`, copied from the existing
scenario result with its baseline, source steps, sensitivity and applicability
metadata. It is an aggregate undiscounted lifetime difference in `usd_2024`,
not an annual earnings amount. No descendant population or compatible dollar
baseline is inferred, so descendant dollar conversions stay unavailable. The
relative gaps remain per-person reference responses even when exposure is
zero; the aggregate child dollar difference then equals zero.

No generation totals are added. Divorce, family-size and school-spending
effects are not added to the directly estimated child response: their margins
and populations differ and may already overlap with that estimate. A joint
causal estimand, incidence weights and overlap treatment would be necessary
before an additive scenario could be interpreted as a total.

## Scope and refusal rules

- Known-incompatible child ages/sexes or target parent/child sex and event type
  withhold the entire child-to-descendant path. Their numeric values are null,
  with the source steps retained for explaining the refusal.
- Unknown child demographics leave an illustrative reference and cannot gain
  public-headline eligibility. The source cohort contains sons aged 10–14 at
  their fathers' firm closure; the report invents no age-response curve.
- Missing or unverified lifetime-dollar baselines block dollar conversion,
  while preserving the supported relative path. They do not erase the reason
  for a demographic refusal.
- County modifiers retain the supplied place, fallback/provenance information
  and `initial_only` or `legacy_repeated` application. These rows are labeled
  exploratory place projections. They cannot become public-headline eligible,
  even when the national transport decision was reviewed.
- Reviewed child transport never promotes a structural descendant projection
  into a validated direct effect. `entry_evidence` describes the source-path
  status; `eligible_for_public_headline` describes this particular report row.

## Housing chain requirements

`housing_chain` always declares `available: false` and `total: null`.
`housing_chain_requirements(params)` also exposes this contract independently.
It carries the currently admitted `foreclosure_order->house_price_gap` row,
including its Campbell citation, population, tier, boundary role and notes.
If the caller's parameter set omits that row, `source_row` is null.

The row concerns a neighbor's relative property price conditional on a nearby
foreclosure. Its preferred estimate is about a 1% price reduction at the
0.05-mile reference distance. The shipped range is a rounding/support band,
not a statistical confidence interval. The source notes distinguish the
preferred estimate from hedonic associations and identify the working-paper
version used for table-level extraction. This boundary row is not a producer
of foreclosure counts from worker displacement.

An end-to-end chain needs four explicit bridges:

1. **Displacement to extra foreclosures:** mortgage/ownership-exposed
   households, counterfactual foreclosure incidence over a matching window,
   an identified displacement response and a target transport decision.
   Worker equivalents are not mortgage-exposed households.
2. **Extra foreclosures to neighboring prices:** geocoded foreclosures and
   properties, distance and sale timing, compatible property types and
   geography, and a rule for overlapping radii and repeated exposure.
3. **Relative prices to aggregate dollars:** unique affected properties and
   counterfactual values with a currency year and valuation date, plus a joint
   response rule. A stock-value difference is not an annual earnings loss.
4. **Housing to schools or children:** assessment/tax and school-finance
   pass-through, child exposure histories and a compatible spending response,
   with a joint model addressing overlap with the direct child estimate.

Until those bridges exist, neither housing totals nor housing-mediated child
earnings totals are supplied. This report specifies the missing inputs rather
than treating unavailable pathways as zero.

Implementation: [child_gap_view.py](../src/downstream/child_gap_view.py).
Contracts and refusal examples: [test_child_gap_view.py](../tests/test_child_gap_view.py).

## CLI

Run `downstream child-gaps --workers 1000` for the side-by-side report.
Optional `--child-profiles`, `--child-income-quartile`, `--income-rank-definition`,
`--place` and `--place-application` retain the scenario's input contracts.
`--real-discount-rate` and `--valuation-year` preserve the separate
`child_valuation` report when compatible child ages are supplied.
The view does not combine those projections with undiscounted child totals.
