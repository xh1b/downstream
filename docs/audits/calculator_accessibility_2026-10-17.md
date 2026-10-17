# Calculator keyboard and reflow review — 2026-10-17

<!-- @ref:calculator-accessibility-review; @tag:calculator -->
<!-- @link:doc-calculator; @link:calculator-template; @link:calculator-app; @link:test-calculator. -->

Task: @task:2026-10-17-calculator-accessibility, under
@task:2026-10-14-calculator-design. This is a software/browser check, not a
screen-reader user study, physical-device test or participant result.

The app was served locally with `scripts/serve_calculator.py` and reviewed in
the Codex in-app browser on macOS. Native keyboard events and the browser's
accessibility tree were used. The source engine/parameters remained 0.4.0/v1.52.

## Checks and repairs

| Check | Observed result |
| --- | --- |
| Keyboard entry | Tab reaches the visible skip link; Enter focuses the mortality results section. |
| Complete tab path | All 19 stops are reachable: skip/reset, three main inputs, two scenario buttons, scroll region, five odds inputs, income selection, three child inputs and two disclosures. |
| Scenario controls | Keyboard activation of the all-one odds control gives zero excess deaths; reset restores 28.76. |
| Fractional exposure | Keyboard entry of 0.125 gives 0.00359 displayed excess deaths. |
| Invalid input | Exposure −1 marks the input `aria-invalid=true`, exposes the alert and retains the last valid result (0.00359). |
| Reflow equivalent to 200% at 1280 px | At a 640 CSS-pixel viewport, page width remains 640; the risk table fits its 608 px region. Controls have 44 px height. |
| Narrow layout | At 320 px, page width remains 320; the 500 px risk table scrolls inside its 288 px region. ArrowRight moves that region by 39 px. |
| Accessible names | Symbol-only mortality controls/headers now have English names; result tables are named, phase rows have row headers, and child output has polite live feedback. The names appear in the browser accessibility tree. |
| Runtime errors | No JavaScript errors were reported by the browser log. |

The compact visual labels and calculation functions are unchanged. Automated
calculator/server checks pass all 18 tests, including native-equation parity,
input behavior and the new accessible-name regression. Reproduce with:

```sh
.venv/bin/python -m pytest -q tests/test_calculator.py tests/test_calculator_server.py
.venv/bin/python scripts/build_calculator.py --check
node --check calculator/app.js
```

[The 640 px capture](../images/calculator-reflow-2026-10-17.jpg) shows the
reviewed layout and visible keyboard focus on reset.

## Remaining manual scope

The in-app browser did not change native zoom when the zoom shortcut was
sent. A 640 px viewport exercises the reflow layout corresponding to 200%
zoom from 1280 px; it is not a native zoom test. Actual browser zoom,
screen-reader operation/announcements, physical phones and the existing
6–8-user comprehension protocol remain on the parent task. Accessibility-tree
names and simulated input do not establish those results.
