# Consumer acceptance fixtures for Downstream 0.4

<!-- @ref:doc-consumer-fixtures-0-4; @tag:consumer -->
<!--
Connections: @link:code-consumer; @link:code-bundle; @link:code-snapshot; @link:doc-exposure-semantics-0-4; @link:doc-version-comparison; @link:doc-xh1b-usage-plan-0-4; @link:docs-index;
@link:script-build-consumer-fixtures; @link:test-consumer-fixtures; @link:test-consumer-api;
@link:test-bundle.
-->

Related: [Documentation map](README.md) · [exposure semantics 0 4](EXPOSURE_SEMANTICS_0_4.md) · [version comparison](VERSION_COMPARISON.md).
Implementation: [consumer](../src/downstream/consumer.py), [bundle](../src/downstream/bundle.py), [snapshot](../src/downstream/snapshot.py). Checks: [consumer_fixtures](../tests/test_consumer_fixtures.py), [consumer_api](../tests/test_consumer_api.py), [bundle](../tests/test_bundle.py).

The fixture pack is model-side preparation for the pending XH1B handoff.
It does not change the companion pin, cache, website or deployed state.

## Build and check

```sh
.venv/bin/python scripts/build_consumer_fixtures.py
.venv/bin/python scripts/build_consumer_fixtures.py --check
.venv/bin/python -m pytest -q tests/test_consumer_fixtures.py
```

[The pack](../validation/consumer_fixtures_0_4.json) includes national,
county 17043, unsupported-county fallback, zero and fractional exposure,
a signed beneficial child subgroup, explicit valuation, a synthetic reviewed
transport decision and incompatible demographics. Synthetic reviewer fields
are test data, never real transport evidence. Default child profiles remain
unknown. Local service jobs remain blocked without their independent input.

The national fixture has 128 parameter draws and variance base 128, seed 1901.
These small designs test contracts; they are not precision-qualified research
intervals. Keep parameter intervals separate from support envelopes, structural
alternatives and broader uncertainty budgets.

## Package API

```python
from downstream.consumer import scale_outcome, mix_expected

# A row is one outcome from result["modeled"]. The caller supplies its factor.
displayed = scale_outcome(row, displayed_workers / source_workers)
combined = mix_expected([county_result, national_result], [0.6, 0.4], "excess_deaths")
```

The fixture builder uses these package functions. They return independent copies;
they do not modify the source result. Each mixture records the active component
weights, source indices, model/input identity, baseline, applicability and source
steps separately. A first-component baseline or eligibility is never inherited.
Missing identity metadata remains unknown. Headline eligibility must be Boolean.
Factors and weights must be finite and
nonnegative. Weights must sum to one. Scaling overflow produces an explicit error.
The source denominator must be declared and positive. A zero-source scenario
cannot identify a per-worker coefficient by division.

The mixture contract requires a common declared displaced-worker denominator.
Mortality also requires the same follow-up duration, method and phase timing.
Mismatched bases fail; missing bases stay unavailable. Refit components at the
same declared worker basis before mixing. A row-only display transform retains
its original source basis and must not be relabeled as a native refit. Scaling a mixture is supported;
all alternatives and sensitivity comparisons scale together, while original
component provenance retains its input basis.

The mixture contract needs outcome points, support endpoints, units and
applicability from each active component. Missing sensitivity reports keep the
point calculation available but withhold sensitivity comparisons. Positive-weight
blocked outcomes remain unavailable. Joint quantiles and variance attribution
remain unavailable. These transforms do not estimate exposure or target transport.

## Required result contract

Retain engine/parameter versions, source steps, units, baseline population,
target and child applicability, structural projection eligibility, blocked
reasons, source input-content hash, place provenance and declared exposure
provenance where supplied by the caller. Preserve optional child valuation,
parameter intervals, persistence comparisons and per-result sensitivity.

Fixtures use raw engine totals to retain small effects, paired with the public
result's provenance and reports. Do not normalize a rounded one-worker death
count and then multiply it back to a large exposure. The `precision` field
states this construction. Native engine calculation remains authoritative.

`normalization_workers` states the source scenario's worker denominator.
`expected_display_values` applies that declared denominator to five exposures:
0, 0.125, 250, 1,000 and 1,000,000. Do not infer that a worker-equivalent exposure
is a count of unique displaced people. Exposures and cohort/event-time bridges
remain caller-owned, as described in the XH1B usage plan.

For a display factor `s`, result-valued points, intervals, signed changes,
removal experiments and endpoint spans scale by `s`. Parameter values, source
endpoints, baseline rates, per-family schedules, source metadata and variance
indices do not scale. Output variance scales by `s²`. At zero display exposure,
variance indices are undefined and the report is marked unavailable.
Retain the original input basis separately from the displayed exposure.

## Place mixtures

Three expected mixtures test county/national weights, partial review and
partial blockage. Positive-weight components all need the outcome; a blocked
component prevents a whole-mixture total, rather than adding a zero. A zero-weight
component does not affect the outcome. All active components must be eligible
before the mixture can claim reviewed applicability. There is no representative
first-county baseline.

Every persistence alternative and effect-removal comparison uses the same
component weights. Supported-endpoint experiments also combine component
refits when their input endpoints agree; differing input endpoints are explicitly
unavailable as a shared experiment. A coefficient absent from a component leaves
that component at its reference for the coefficient-removal experiment.

Point expectations and declared Cartesian support envelopes can be combined
under these rules. Quantiles are not averaged. Mixture parameter intervals and
variance attribution remain unavailable until a joint draw/dependence calculation
is implemented. These fixtures intentionally do not invent that joint model.

The pack's county/national case catches the previously reproduced integration
defect: main mortality can combine correctly while a nested alternative still
comes from the first county. Check all nested comparisons, not only headline totals.

## Identity and cache acceptance

The pack records file hashes for engine source, parameters and its builder,
plus a content digest for that collection. This fixture digest is **not** the
engine bundle's `sha256` or a companion adapter hash.

Before the handoff, freeze the intended candidate and regenerate the bundle
and fixtures together. The companion must verify its actual bundle manifest,
source revision, engine/parameter versions and adapter content hash. Cache keys
must cover model inputs, place shares, cohort/transport decisions, caller exposure
provenance when consumed, and requested analysis settings such as seed/base.
A valid-looking hash alone does not establish current input provenance.

Keep the source-input hash and consumer transformation separate. Changing a
display exposure without altering the normalized model need not rewrite a cache,
but changing a consumed scenario assumption or place mix requires recomputation.
Missing or stale entity results must disclose any national-reference fallback.

## Companion acceptance sequence

1. Run bundle/package verification on the fixed candidate.
2. Parse each native fixture without dropping applicability, blocked reasons,
   signed results, valuation, sensitivity or source identity.
3. Compare scaled values, nested experiments and mixtures with pack expectations.
4. Check HTML, Markdown, explorer links and exported receipts against the same
   parsed data. Preserve unavailable states and interval meanings in all formats.
5. Inspect cache identity, current row coverage, fallback use, queue/lease behavior
   and scheduled entity types. Worker support does not prove a qualified drain.
6. Collect fresh page and deployment receipts in the companion project before
   describing the new pin as deployed. This local pack supplies no such receipt.
