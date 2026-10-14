# Local calculator

Open [index.html](../examples/calculator/index.html). The page is self-contained.
No server, account or external assets are required.

## Calculation

Edit N, T, the annual baseline rate, five odds ratios, child count, child
multiplier and lifetime earnings. The browser recalculates survival and
child earnings. It also recalculates each mortality removal effect and
one-input source-endpoint experiment. The curve shows ΔD by follow-up year.

D₀ includes baseline deaths. D₁ applies the displacement response. ΔD is
their difference. The baseline rate stays fixed. The model does not age
the cohort. N is a reference scaling input, not an inferred unique cohort.

The equations match `downstream.mortality.excess_deaths_profile`. The
implementation uses `expm1` and `log1p` to retain small effects. Protective
coefficients can produce negative ΔD. Zero exposure and zero horizon
produce zero ΔD. Phase durations use source offsets 0, +1, +2–3, +4–5,
and +6+. Offset +6 starts in follow-up year seven.

The child result uses `N × c × (1 − g) × E`. Q1–Q4 load signed Table 8
source contrasts. The default uses the shipped overall parameter.
Income ranks refer to fathers' pre-displacement income. A target rank map
is not supplied. The Canada-to-US lifetime conversion is an assumption.
Child ages and sex remain unknown. The result is undiscounted.

Edits define custom assumptions. They do not establish target applicability.
Source endpoints remain fixed. Each displayed ΔD range changes one source
input, with all other current inputs fixed. These ranges are support
envelopes. They are not confidence intervals. Removal effects do not sum.
Variance attribution and full prediction intervals are not calculated.

The data panel separates current browser inputs/results from the immutable
source engine receipt. The browser calculation has its own schema and
math-source hash. The receipt's input hash identifies the source calculation.
It must not be used as the identity of edited browser results.

## Design and language

The page uses one layout. Numeric inputs, equations and tables occupy the
main surface. Method, source scope, unavailable paths and data are collapsed.
There is no hero, visual-direction selector, promotional text or card grid.

Necessary English uses short sentences, active verbs and consistent technical
names, based on [ASD-STE100](https://asd-ste100.org/). Symbols and units label
calculations. A formal controlled-dictionary compliance audit is not claimed.
The source receipt preserves original evidence text.

Input labels share the row height. Wrapped labels do not shift numeric controls.
Below 520 px, each input group uses two columns; its last field spans the row.
This gives the rate unit and lifetime earnings field more space. Mobile controls
have a 44 px minimum height and at least 16 px input text. The mortality table scrolls inside a named keyboard
focusable region. Large results use scientific notation; the data panel keeps
full numeric precision. Long source text can wrap within the page.

## Build and verify

```sh
.venv/bin/python scripts/build_calculator_prototype.py
.venv/bin/python scripts/build_calculator_prototype.py --check
.venv/bin/python -m pytest tests/test_calculator_prototype.py -q
node --check examples/calculator/math.js
node --check examples/calculator/app.js
```

The generated HTML embeds source parameters, signed child presets and the
complete engine receipt. Freshness checks cover HTML, CSS, both scripts and
engine inputs. The tests compare browser equations and all five removal
experiments with native engine refits at 22 input combinations. Cases include
phase boundaries, fractional exposure, small rates, protective effects, extreme protective odds,
null effects, zero counts and changed child assumptions. DOM tests check
edits, presets, invalid inputs, reset and source/current data separation.

Numeric limits are N ≤ 1,000,000; T ≤ 100 years; annual rate ≤ 1;
0 < odds ratio ≤ 1,000,000; integer c ≤ 100; 0.000001 ≤ g ≤ 10;
and E ≤ 1,000,000,000 USD 2024. All inputs must be finite. These are interface
limits, not source-support or transport claims. Invalid edits keep the last
valid calculation and mark the input.

## Remaining review

The browser tool rejected the previous `file://` preview under its URL policy.
No alternate route was used. Node tests verify equations and DOM behavior;
they do not verify rendered appearance, responsive layout or assistive technology.

Inspect at 1440 px and 390 px, at 200% zoom, with a keyboard and screen reader.
Check table scrolling, labels, focus, error recovery and the curve. Record
screenshots and defects before public use.

Human testing remains on task:2026-10-14-calculator-design. Test 6–8 intended
users. Ask them to identify units, source versus custom inputs, D₀/D₁/ΔD,
the lifetime child conversion, removal effects and unsupported target transport.
Record unaided errors and needed assistance. Revise recurring errors and repeat.
No participant results are claimed.
