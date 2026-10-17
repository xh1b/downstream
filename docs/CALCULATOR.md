# Local calculator

<!-- @ref:doc-calculator; @tag:calculator -->
<!--
Connections: @link:code-mortality; @link:code-scenario; @link:paper-calculator; @link:paper-counts; @link:doc-exposure-semantics-0-4; @link:docs-index; @link:calculator-math; @link:calculator-app; @link:calculator-template; @link:calculator-style; @link:script-build-calculator; @link:script-serve-calculator;
@link:test-calculator; @link:test-calculator-server.
-->

[Documentation](README.md) · [Integration contracts](INTEGRATION.md) · [Development](DEVELOPMENT.md)

The calculator is a small browser implementation checked against the Python
engine. Code defines behavior; the [paper](../paper/downstream.tex) explains
survival and child conversion (@link:paper-counts, @link:paper-children).
This guide covers running, editing and checking the app.

Run from the repository root:

```sh
make serve
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/). Press `Ctrl+C` to stop.
Use `make serve PORT=8001` to select another port. Python 3.12 or later is
required; `make` uses `.venv/bin/python` when available.

Without `make`, run `python3 scripts/serve_calculator.py --port 8000`.
The server builds current source data at startup and serves only the calculator.
Restart it after changing source files. It listens on this computer's loopback
address. Repository files and directory listings are not served.

The app lives in [`calculator/`](../calculator). `make calculator` rebuilds
its self-contained [index.html](../calculator/index.html) for offline use or
static hosting. No account, Node packages or external assets are required.

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

## Code structure

`math.js` contains pure functions. `analyze(inputs, sources)` returns results,
one-input source ranges and a 101-point mortality curve. It does not read the
page, mutate inputs or retain state. Phase durations are intersections of the
follow-up horizon with source intervals [0, 1), [1, 2), [2, 4), [4, 6) and [6, ∞).
Changing one odds ratio creates a new input value for each sensitivity experiment.

For the survival equations and their rationale, see @link:paper-counts.
`math.js` uses log survival and cancellation-safe differences so small effects
and extreme protective inputs remain numerically stable. The independent
native parity tests below check that implementation choice.

`app.js` reads inputs, checks the shared validation rules, calls `analyze`,
then renders totals, phase rows, curve geometry and the receipt. Formatting and
chart geometry are separate from outcome calculations. The selected preset
comes from its control; there is no separate mutable preset or result cache.
An invalid edit marks each invalid field and keeps the last valid result on screen.

## Design and language

<!-- @ref:calculator-output; @tag:rendering -->
<!-- @link:code-explanation; @link:code-render; @link:paper-calculator; @link:test-guard-rails. -->

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
.venv/bin/python scripts/build_calculator.py
.venv/bin/python scripts/build_calculator.py --check
.venv/bin/python -m pytest tests/test_calculator.py tests/test_calculator_server.py -q
node --check calculator/math.js
node --check calculator/app.js
```

The generated HTML embeds source parameters, signed child presets and the
complete engine receipt. Freshness checks cover HTML, CSS, both scripts and
engine inputs. The tests compare browser equations and all five removal
experiments with native engine refits at 22 input combinations. Cases include
phase boundaries, fractional exposure, small rates, protective effects, extreme protective odds,
null effects, zero counts and changed child assumptions. DOM tests check
edits, presets, invalid inputs, reset and source/current data separation.
Additional mathematical checks cover constant-odds closed-form survival,
phase-duration sums, odds monotonicity, exposure scaling, curve endpoints,
repeatability and frozen-input immutability.

Numeric limits are N ≤ 1,000,000; T ≤ 100 years; annual rate ≤ 1;
0 < odds ratio ≤ 1,000,000; integer c ≤ 100; 0.000001 ≤ g ≤ 10;
and E ≤ 1,000,000,000 USD 2024. All inputs must be finite. These are interface
limits, not source-support or transport claims. Invalid edits keep the last
valid calculation and mark the input.

## Review status

The [browser review](audits/CALCULATOR_REVIEW_2026-10-15.md) records viewport,
interaction and refactor checks. Those receipts describe the tested revision.
Physical-device, zoom, screen-reader and participant testing remain open on
@task:2026-10-14-calculator-design. Record new results there and in a dated
audit; do not turn historical observations into a current verification claim.
