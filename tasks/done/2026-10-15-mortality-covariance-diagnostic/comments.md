# comments

## c-07ff824925a3

- At: 2026-10-15 01:23 HKT
- By: fenix

Created in inbox.

## c-90b55734f8c3

- At: 2026-10-15 01:23 HKT
- By: fenix

triage: inbox -> ready.

## c-af1e44c08200

- At: 2026-10-15 01:23 HKT
- By: fenix

claim: ready -> active.

## c-0255f6699b77

- At: 2026-10-15 01:28 HKT
- By: fenix

Implemented sharp marginal SE bounds over all PSD covariance matrices with supplied diagonal, weighted additive contrasts, missing-SE withholding and explicit normal-approximation outer envelopes. No correlation guessed and every result remains admission-ineligible. Available author-manuscript Table4 col1 was rendered and visually checked at PDFpage35; source hash/locator and manufacturing reference category recorded in docs/MORTALITY_COVARIANCE_0_4.md. 33 focused pytest checks pass; scoped Ruff passes. Reproduction: .venv/bin/python scripts/analyze_mortality_covariance.py --output /tmp/downstream-covariance.json. Report SHA256 1c88dbfd863d9909ca1d9017492015cb94d4aa77fedee8648c45de723b32702a. Implementation a3a4cc8. Parent remains open: no publisher-version reconciliation, source covariance, nonlinear death bounds, joint phase draws or profile admission claimed.

## c-15e0201f7944

- At: 2026-10-15 01:28 HKT
- By: fenix

done: active -> review.

## c-e8ef148bd66f

- At: 2026-10-15 01:34 HKT
- By: codex

accept: review -> done.

Reviewed sharp PSD-compatible bounds, signed-weight and missing-SE handling, additive log-odds parameterization and manuscript-version limits. Diagnostic and analytic witness tests pass. No published profile or nonlinear mortality total is admitted; parent remains open.
