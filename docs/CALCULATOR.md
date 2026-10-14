# Local calculator

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

The app lives in [`calculator/`](../calculator/). `make calculator` rebuilds
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

Numeric limits are N ≤ 1,000,000; T ≤ 100 years; annual rate ≤ 1;
0 < odds ratio ≤ 1,000,000; integer c ≤ 100; 0.000001 ≤ g ≤ 10;
and E ≤ 1,000,000,000 USD 2024. All inputs must be finite. These are interface
limits, not source-support or transport claims. Invalid edits keep the last
valid calculation and mark the input.

## Browser review — 2026-10-15

The local HTTP app was inspected in the in-app browser at 320, 390, 600 and
1440 px widths. Page width matched viewport width in all four cases.
Inputs aligned within each row. The risk table scrolled inside its container.
At 390 px, controls measured 44 px high. At 600 px, all three top inputs
shared the same vertical position despite the wrapped rate label.

Live checks retained the exact 0.125 exposure label and displayed 0.00359
expected excess deaths. The tail-null control displayed 20.52; reset restored
28.76. No browser console errors were reported. See the
[390 px screenshot](images/calculator-mobile-390.jpg).

Earlier `file://` preview access was denied. The dedicated local HTTP server
now supplies the application through a supported URL. Physical phone testing,
200% zoom, screen-reader review and participant testing remain open.
Viewport emulation does not establish those results.

Human testing remains on task:2026-10-14-calculator-design. Test 6–8 intended
users. Ask them to identify units, source versus custom inputs, D₀/D₁/ΔD,
the lifetime child conversion, removal effects and unsupported target transport.
Record unaided errors and needed assistance. Revise recurring errors and repeat.
No participant results are claimed.
