# Calculator browser review — 2026-10-15

<!-- @ref:audit-calculator-browser; @tag:calculator -->

Review receipt retained from the calculator guide. Current software instructions:
[calculator](../calculator.md) (@link:doc-calculator).

The local HTTP app was inspected in the in-app browser at 320, 390, 600 and
1440 px widths. Page width matched viewport width in all four cases.
Inputs aligned within each row. The risk table scrolled inside its container.
At 390 px, controls measured 44 px high. At 600 px, all three top inputs
shared the same vertical position despite the wrapped rate label.

Live checks retained the exact 0.125 exposure label and displayed 0.00359
expected excess deaths. The tail-null control displayed 20.52; reset restored
28.76. No browser console errors were reported. See the
[390 px screenshot](../images/calculator-mobile-390.jpg).

Earlier `file://` preview access was denied. The dedicated local HTTP server
now supplies the application through a supported URL. Physical phone testing,
200% zoom, screen-reader review and participant testing remain open.
Viewport emulation does not establish those results.

After the functional JavaScript refactor, the local server was restarted and
the page reloaded. Browser checks confirmed fractional exposure (0.125 →
0.00359 excess deaths), invalid-edit retention, tail-null (20.52), Q3 signed
child earnings and reset (28.76). No console errors were reported.

Human testing remains on task:2026-10-14-calculator-design. Test 6–8 intended
users. Ask them to identify units, source versus custom inputs, D₀/D₁/ΔD,
the lifetime child conversion, removal effects and unsupported target transport.
Record unaided errors and needed assistance. Revise recurring errors and repeat.
No participant results are claimed.
