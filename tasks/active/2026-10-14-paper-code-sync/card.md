---
title: Synchronize the methods paper with current code
area: docs
priority: P1
assignee: paper-sync
blocked-by: []
expected-paths: [paper/downstream.tex, paper/build_tables.py, tests/test_paper_tables.py, scripts/build_methods_html.py]
---

# Synchronize the methods paper with current code

User authorized fixing all seven findings from 2026-10-14-paper-code-review, plus missing cohort/baseline coverage.
Preserve experimental applicability and independent-validation limitations. Do not change model behavior.

## Acceptance

- [x] Correct mortality coverage and generate its interpretation from current scorecards, with regression checks.
- [x] Resolve all seven findings in prose and figures; include descriptive cohort and baseline evaluation receipts.
- [x] Reconcile HTML, regenerate data, compile and visually inspect the updated PDF.
- [x] Run focused verification, record receipts and commit only authored changes.

## Implementation receipts

- F1: paper/build_tables.py generates mortality_summary.tex from the live V1 rows; the manuscript consumes it.
- F2: the implemented log_elasticity_transmission alternative is documented with its structural interpretation.
- F3: household methods and the figure describe the implemented SIPP transition prototype and remaining gates.
- F4: default fixed-age mortality is distinguished from experimental age-stratum projections and incomplete coverage.
- F5: the separate national Gamma/Poisson baseline, declared exposure and binomial process budget is documented.
- F6: child applicability, signed subgroup contrasts, observed-age versus career valuation and uncertainty are documented.
- F7: generated persistence reference values and within-draw structural differences are documented.
- CPS reproduction, SIPP calibration and archived pooling refusals are reported without claiming new V2 validation.
- HTML now includes the live mortality scorecard, the archived evaluation receipts and the same experimental scope.
- Source changes: 672d1a1; figure-label polish: 324ed8e.
- Focused verification: 121 tests passed in 3.96s; Ruff and git diff --check passed.
- Post-layout paper-generator check: 2 tests passed; fresh generation matched all existing generated data byte-for-byte.
- Multi-file repository build passed with latexmk; 20 pages rendered and inspected, revised figures checked at full size.
- No overfull boxes, undefined references/citations or compilation errors; one harmless underfull paragraph warning remains.
- Source SHA-256: 8f058f6253d0cd81c7fa07138ebab4b6682b31a39707649596b9a24431370c7b.
- Verified updated PDF: build/paper-code-sync/downstream.pdf.
- Updated PDF SHA-256: c13f2c9f09237293fb163261e6d2d28eaa3f81591f4878932bc90694383e73bb.
- Pre-existing uncommitted PDF preserved byte-for-byte as build/paper-code-sync/preexisting-downstream.pdf.
- Canonical PDF replacement is pending the owner's answer to the shared-file permission question.

Verification command:

```sh
.venv/bin/python -m pytest -q tests/test_paper_tables.py tests/test_release_repairs.py \
  tests/test_variants.py tests/test_mortality_robustness.py tests/test_mortality_strata.py \
  tests/test_child_applicability.py tests/test_valuation.py tests/test_household.py \
  tests/test_uncertainty_budget.py tests/test_followthrough_cli.py
make -C paper LATEXMK='latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error -outdir=../build/paper-code-sync'
```
