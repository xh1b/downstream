# Local calculator prototype

Two selectable visual directions use the same engine output:

- **Comparison first:** warm editorial hierarchy; comparison precedes effect sensitivity.
- **Sensitivity first:** cool analytical hierarchy; effect removal experiments precede comparison.

Open [the self-contained HTML](../examples/calculator/index.html) locally in a browser.
No web server, account, dependencies, remote assets or deployment are needed. External
study links are ordinary links, loaded only if the visitor follows them.

## Build and check

From the repository root:

```sh
.venv/bin/python scripts/build_calculator_prototype.py
.venv/bin/python scripts/build_calculator_prototype.py --check
.venv/bin/python -m pytest tests/test_calculator_prototype.py -q
node --check examples/calculator/app.js
```

`index.html` is generated from `template.html`, `style.css`, `app.js` and a fresh
`compute_counts` result. The complete 1,000-worker-equivalent engine receipt,
including the input-content digest, is embedded and inspectable. A stale HTML
fails `--check`. The generator uses the current local `src/` and `params/`.

The editable exposure scales engine-generated count/dollar differences and their
sensitivity values linearly. This is valid for this fixed reference only. JavaScript
does not implement survival, draw new coefficients, infer demographics, combine
county mixtures or create annual earnings trajectories. Exposure is a nonnegative
finite scaling input, allowed from zero to one million, including fractional values.
Invalid edits keep the previous result and display an error. Reset restores 1,000.
Scenario labels retain the exact exposure entered. Nonzero results below 0.01 use
three significant digits, with scientific notation below 0.000001, so small
fractional expected counts and driver impacts do not appear as zero.

## Scope and interpretation

The displayed reference arm has zero **displacement-attributed difference**, not
zero total deaths or zero lifetime earnings. Mortality displays additional expected
deaths over twenty years. The national male 45–54 baseline stays fixed throughout;
cohort aging is not modeled. Child dollars are undiscounted lifetime totals in USD
2024, assuming two children per worker equivalent; their ages and sex remain unknown.
The reference calculation does not establish target-population applicability.

Per-effect details preserve source input, endpoints, null experiment, population,
evidence role and tier. They show engine refits with other inputs fixed. Removal
impacts are hypothetical, nonadditive and not intervention recommendations. The
combined support envelope is not a confidence interval. Variance attribution is
not requested; exposure, baseline, timing and transport uncertainty remain excluded.
Blocked pathways are listed with their engine reasons, separately from zero effects.

Controls have native labels, visible focus, an invalid-input alert, a concise live
result announcement and a skip link. Actual DOM order changes with the chosen
direction so keyboard/screen-reader reading order follows visual order. The layout
stacks below 760px and has no required motion. These are implementation provisions,
not a claim of WCAG conformance or completed accessibility research.

## Verification receipt and remaining checks

Automated tests check generated-data freshness, preserved applicability/sensitivity,
absence of remote dependencies, labels, numeric edits, zero and fractional exposure,
invalid values, reset, outcome selection, direction/DOM order and blocked paths.
The interaction test uses a minimal DOM double in Node; it does not prove browser
rendering, responsive appearance, contrast or assistive-technology behavior.

On 2026-10-15 the browser tool rejected a `file://` preview under its URL security
policy. No alternate route was attempted. Visual/browser verification is therefore
pending: inspect both directions at 1440px and 390px, at 200% zoom, using keyboard
only, then a screen reader. Verify no clipped content, comparison meaning, focus
visibility/order, announced changes and error recovery. Record screenshots and any
issues before treating this as a reviewed public experience.

## Human comprehension test protocol — pending

Recruit 6–8 formative participants from the intended audience, including mobile
users, different numeracy levels and people with access needs. Counterbalance which
direction appears first; use the same reference and tasks for each. Do not explain
the intended interpretation before their first attempt.

1. Describe what is compared and what the zero reference means.
2. Identify units and horizon for mortality, then for child dollars.
3. Change exposure to 500; explain what changed and what stayed fixed.
4. Locate a supported-range experiment and an effect-removal experiment. Explain
   whether either is a prediction for an individual, another study's result or
   a confidence interval.
5. Find an unavailable pathway and explain why it is not a zero effect.
6. Find the population, source and version; assess whether a supplied mixed-age
   workforce or household has established applicability.
7. Complete the same tasks with keyboard controls; inspect small-screen reading order.

Record unaided interpretation, errors, assistance, completion time and usefulness;
ask which direction helped most and why. Flag confusion about personal certainty,
lifelong versus annual dollars, worker equivalents versus unique people, and
sensitivity versus uncertainty. Revise recurring critical misunderstandings and
repeat the round. No participants have been recruited or tested by this implementation.
The parent calculator-design task's human-test criterion remains pending.
