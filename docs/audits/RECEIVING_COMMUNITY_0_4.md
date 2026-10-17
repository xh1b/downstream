# Receiving-community scenarios in 0.4

<!-- @ref:doc-receiving-community-0-4; @tag:receiving -->
<!--
Connections: @link:code-receiving-community; @link:doc-immigration-replacement-evidence-scan-2026-09-14; @link:doc-exposure-semantics-0-4; @link:docs-index; @link:test-receiving-community;
@link:test-receiving-adapter.
-->

Related: [Documentation map](README.md) · [immigration replacement evidence scan 2026-09-14](IMMIGRATION_REPLACEMENT_EVIDENCE_SCAN_2026-09-14.md) · [exposure semantics 0 4](EXPOSURE_SEMANTICS_0_4.md).
Implementation: [receiving_community](../src/downstream/receiving_community.py). Checks: [receiving_community](../tests/test_receiving_community.py), [receiving_adapter](../tests/test_receiving_adapter.py).

Engine **0.4.0**, parameter set **v1.52**. The `receiving-community` command
applies one explicitly selected source contrast to supplied immigrant population
shares. It does not convert displaced workers, requested positions or wages
into arrivals. Rates and annual endpoint incidents are separate from cumulative
counts. Unsupported receiving channels remain unmodeled, not zero.

## Necessary source correction

The earlier generic `immigrant_influx` links conflated distinct input units.
They are retired in v1.52, with a migration refusal for generic chains.
Coefficient points and stored support endpoints are unchanged.

| Source path | Required exposure | Response | Source scope |
| --- | --- | --- | --- |
| `light_miller_2018` | Change in undocumented residents / total population, in percentage points | `exp(beta * delta_pp)` | Annual state panel, predictor lagged one year; fixed-effects association |
| `bianchi_2010` | Post/reference ratio of valid residence-permit residents / total population | `exp(beta * log(post_share/reference_share))` | Italian province endpoint differences, 1991–2001; IV source contrast |

Light–Miller's published Table 1 defines the unlogged share; Table 2 Model 4
reports **−0.12 (SE 0.03)**. The modeled change is per percentage point, not
per percent immigrant-stock growth. The downloaded PDF matches the original
corpus hash. [Published paper, Tables 1/2 and focal-measure definition](https://www.antoniocasella.eu/nume/LIGHT_Miller_2018.pdf).

Bianchi's Equation 3 and Table 5 column 3 in the newly pinned 2010 mirror define
log shares and report **0.105 (SE 0.187)**. Valid residence permits supply the
immigrant numerator. The earlier HAL draft has a different Table 4 locator;
published JEEA reconciliation remains queued. The coefficient is now canonical
under the working-paper rule. The mirror recheck is a duplicate version, not
another independent study. [2010 working-paper mirror](https://www.antoniocasella.eu/nume/Bianchi_Buonanno_Pinotti_2010.PDF).

The [source-unit receipt](../validation/receiving_source_units_20261015.json)
records both hashes, locators, version distinctions and unchanged coefficients.
The [extraction queue](QUEUED_EXTRACTIONS.md) retains published reconciliation.

## CLI and inputs

```sh
downstream receiving-community --input receiving.json
```

```json
{
  "model": "light_miller_2018",
  "exposure": {
    "margin": "undocumented_residents",
    "response_window": "annual_one_year_lag",
    "unit": "population_share_fraction",
    "reference_share": 0.02,
    "post_share": 0.022,
    "post_population_for_counts": 10000,
    "population": "synthetic receiving population",
    "source": "supplied share scenario"
  },
  "baseline": {
    "outcome": "violent_crime",
    "rate": 300,
    "unit": "incidents_per_100000_residents",
    "window": "annual_endpoint_rate",
    "population": "synthetic receiving population",
    "source": "synthetic fixed annual baseline"
  }
}
```

Shares are fractions between zero and one: **0.02 means 2%**. Their difference
is multiplied by 100 for the undocumented-share path. The synthetic example's
0.2 percentage-point increase gives `exp(-0.12*0.2) ≈ 0.97629` for the rate
ratio. It does not give `1.10^-0.12`. A logarithmic source requires both shares
strictly positive; the semi-log source can represent a zero share.

For the regular-resident path, select `bianchi_2010`, set margin to
`valid_residence_permit_residents`, response window to
`ten_year_endpoint_difference` and baseline outcome to `total_crime`.
These inputs cannot be relabeled as all migrants, undocumented residents,
asylum seekers or H-1B arrivals. Other horizons/margins are refused.

Alternatively, use `unit: resident_counts` and supply
`reference_immigrants`, `post_immigrants`, `reference_total_population` and
`post_total_population` instead of shares. Each immigrant count must not exceed
its total population. The adapter derives **both shares**, including changing
denominators. If immigrant stock is unchanged but total population doubles,
the share halves; stock growth alone would wrongly imply no change.

Source and population descriptions are required. Unknown fields, including
displaced-worker counts, are refused. An optional `transport_assumption` is
preserved as caller rationale; it does not establish reviewed applicability.

## Returned results and limits

The result preserves input and coefficient fingerprints, engine/parameter
versions, source metadata and the source-specific causal role. Public-headline
eligibility remains false: correct units are necessary but do not establish
transport to a new receiving population.

`rate_ratio` and signed `percent_rate_change` are available without a baseline.
The coefficient endpoints transform through the same function; endpoint order
reverses appropriately for a negative exposure change. The total-crime support
retains the null and both signs. Tiny signed changes use `expm1`, avoiding
cancellation even when the displayed ratio rounds to one.

A supplied baseline must match the outcome, population and annual endpoint
window in incidents per 100,000 residents. It enables a rate projection.
A supplied post population additionally enables annual endpoint incident
changes. Both rate scenarios use that **same post population**; the difference
isolates the modeled rate response rather than adding population growth itself.
Missing baselines or populations produce unavailable counts, not zeros.
No ten-year multiplier turns an endpoint rate contrast into cumulative crimes.

Exponentiating predicted log-rate differences yields the stated arithmetic
rate/count ratio only under an **unchanged residual retransformation factor**
between scenarios. That assumption travels with the result; the adapter does
not estimate residual distributions or a smearing factor. Finite-change mapping
also assumes the source slope applies over the supplied shift; target exposure
support and transport are unestablished.

The transformed support is conditional on fixed shares and baseline. It is
not future incident-count uncertainty, target transport uncertainty, or a
whole-community confidence band. Violent crime overlaps total crime, and the
two sources cover different populations: **do not add their results**.
Rents, wages, health, trust, voting and other receiving channels remain open
under the full-comparison task.

[Adapter tests](../tests/test_receiving_adapter.py) cover source units, changing
population denominators, signs/nulls, tiny effects, baselines, missingness,
unsupported margins/horizons, source metadata, caller preservation and CLI
migration. [Source/chain tests](../tests/test_receiving_community.py) refuse the
retired stock links and generic semi-log composition.
