# Same-place child-earnings counterfactual

<!-- @ref:doc-place-counterfactual; @tag:place -->
<!--
Connections: @link:code-place; @link:code-build-places; @link:code-county-rates; @link:doc-child-gap-view; @link:doc-cdc-wonder-profile-import; @link:docs-index; @link:test-place; @link:test-county-rates; @link:test-build-places-adversarial.
-->

Related: [Documentation map](../readme.md) · [child gap view](../integration.md#child-and-descendant-outputs) · [cdc wonder profile import](../evidence.md#mortality-baseline-import).
Implementation: [place](../../src/downstream/place.py), [build_places](../../src/downstream/build_places.py), [county_rates](../../src/downstream/county_rates.py). Checks: [place](../../tests/test_place.py), [county_rates](../../tests/test_county_rates.py), [build_places_adversarial](../../tests/test_build_places_adversarial.py).

Verified 2026-10-15 for engine 0.4.0, parameter set v1.51.

The contrast is displacement versus no displacement **in the same place**.
Let `g` be the direct child adult-earnings multiplier after parental displacement,
and `M` the place multiplier. The model uses:

```
child multiplier = 1 - M * (1 - g)
child loss       = M * (1 - g)
```

The previous task description concerned `1 - M*g`, which would create a loss
when `g=1`. That formula is not the current implementation. With the current
rule, null displacement (`g=1`) gives a multiplier of exactly one at every
place. At the national reference (`M=1`), the original direct effect is recovered.
A hypothetical `g=0.90, M=1.20` gives a 12% loss, not a 108% loss.

The place multiplier is derived as
`M = 1 + 18 * gamma * (county_percentile - national_percentile)/100`.
The gamma estimate and permanent-resident income ranks supply inputs; the
18-year exposure dose and the use of this multiplier to scale a displacement
loss are declared structural assumptions. Chetty–Hendren does not identify a
displacement-by-place interaction. A null-safe formula does not validate that
interaction or establish transport to a target displaced cohort.

The default `initial_only` applies the place modifier to the direct child loss
once; subsequent generations propagate that modified gap through the
intergenerational transmission registry. `legacy_repeated` additionally applies
the modifier to descendant ledgers and is an explicit alternative. Neither
should be interpreted as additional independent causal evidence.

Missing place data or an unavailable modifier reports a blocked modifier;
unknown place keys fail. Generic county mortality precision is not a binomial
denominator and cannot replace the compatible mortality baseline. The child
place interaction and mortality-baseline selection are separate operations.

## Implementation and verification

- [Place derivation and structural designation](../../src/downstream/place.py)
  (`mobility_modifier`, `modifier_parameter`).
- [Child composition](../../src/downstream/children.py) (`child_line`) and
  [ledger gap scaling](../../src/downstream/ledger.py) (`GAP_SCALE`).
- [Place tests](../../tests/test_place.py) include the null-displacement invariant,
  national-reference identity, default scenario/vignette use, missing-data
  blocking, generic county-mortality rejection and explicit legacy repetition.
- [Transmission tests](../../tests/test_transmissions.py) and
  [ledger tests](../../tests/test_ledger.py) cover downstream composition.

Receipt: `.venv/bin/python -m pytest tests/test_place.py tests/test_ledger.py
 tests/test_transmissions.py -q` — **83 passed in 4.58 seconds**.
No core code or parameter values changed in this verification.
