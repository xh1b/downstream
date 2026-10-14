---
title: Synchronize the methods paper with current code
area: docs
priority: P1
assignee:
blocked-by: []
expected-paths: [paper/downstream.tex, paper/build_tables.py, tests/test_paper_tables.py, scripts/build_methods_html.py]
---

# Synchronize the methods paper with current code

User authorized fixing all seven findings from 2026-10-14-paper-code-review, plus missing cohort/baseline coverage.
Preserve experimental applicability and independent-validation limitations. Do not change model behavior.

## Acceptance

- [ ] Correct mortality coverage and generate its interpretation from current scorecards, with regression checks.
- [ ] Resolve all seven findings in prose and figures; include descriptive cohort and baseline evaluation receipts.
- [ ] Reconcile HTML, regenerate data, compile and visually inspect the updated PDF.
- [ ] Run focused verification, record receipts and commit only authored changes.
