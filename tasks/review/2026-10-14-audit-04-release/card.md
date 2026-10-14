---
title: Audit 0.4 calculations, sources and release documentation
area: release
priority: P1
assignee: codex
due:
blocked-by: []
expected-paths: [src/downstream/, params/study_estimates.csv, paper/, docs/]
---

# Audit 0.4 calculations, sources and release documentation

Owner selected release-readiness items 1, 4 and 5 on 2026-10-14.
Audit the newly introduced numerical paths and their source inputs, fix
confirmed defects, and independently review the completed paper synchronization.
Preserve signed, null and conflicting effects, conditional applicability,
source versions and unresolved empirical dependencies. Keep engine 0.4.0.

## Acceptance

- [x] Audit mortality timing, subgroup selection, discounting, custom parameters and shared uncertainty draws.
- [x] Verify zero/beneficial/unsupported cases and add regression coverage for confirmed defects.
- [x] Recheck source coefficients, SEs, effect scales, windows and sample overlap used by the new paths.
- [x] Confirm agreement among paper, HTML, model card, saved outputs and current code after repairs.
- [x] Record findings, exact audit scope, outstanding scientific limits and verification receipts.

## Audit findings and resolution

1. Custom income-quartile selection read the bundled library even with a custom
   parameter directory. Fixed propagation through scenario, entity, policy and
   extended-uncertainty APIs/CLI; absent custom sources fail instead of falling back.
   A selected contrast now carries its own citation, preserving source provenance.
2. Subgroup/stratum consumers checked numeric SEs but did not verify the consumed
   scale/window/population metadata. Added explicit admission checks, including
   rejection of cumulative hazard ratios used as annual odds ratios.
3. Direct subtraction of survival probabilities lost tiny signed effects.
   A 1e12-worker, 1e-8-risk, OR=1.00000001 fixture returned -0.000111 deaths
   instead of the independent 70-digit result +0.001999999588. Log-survival
   ratios and expm1 now preserve signs and exact null cancellation. Hazard-to-risk
   conversion also preserves tiny rates; extreme protective horizons stay bounded.
4. Child-dollar conversion accepted wrong-currency/year or negative baselines.
   These now block the outcome (or raise in strict mode). Valuation output names
   the fixed SSA annual shape separately from a caller-supplied lifetime total.
5. Five default mortality OR transforms did not consistently reproduce their
   cited beta/SE arithmetic. v1.51 explicitly replaces those rows at four decimals,
   retaining prior values in Git. Source betas/SEs are unchanged. The reference
   changes from 28.73 to 28.76 deaths; the persistence alternative stays 20.52.
6. Danish source notes conflated cumulative hazards with annual ORs and claimed
   published-version extraction. The pinned copy is the 2011 AKF working paper.
   Notes now preserve scale/window differences and pending version reconciliation.
   MI-or-stroke at 20 years is 1.09 [0.97, 1.23], not the all-circulatory result
   1.16 [1.07, 1.25]. The Canadian child anchor's country label is corrected.
7. Five default mortality and three Danish working-paper rows now use canonical
   publication tier under CITING section 1. Their actual table transcriptions
   remain explicit; publication-version equivalence is not assumed.
8. Age-stratum ranges are labeled Cartesian envelopes of marginal ranges;
   marginal 95% ranges do not establish simultaneous confidence coverage.

## Source audit scope

All 67 parameter rows underwent the mechanical citation/unit/DAG/distribution
checks and their regression fixtures. Fresh primary-table checks cover the
23-row source-contrast library and nine existing parameter links (five mortality
phases, the overall child contrast and three Danish cause-specific boundaries).
The remaining 58 parameter links were not freshly re-extracted from every primary
paper in this audit; no comprehensive fresh review of all cited literature is claimed.
The library's 23 contrasts are three study samples with overlapping subgroups/windows.
No compatible independent pool or new causal event-validation result is claimed.

Primary pages visually checked: NBER w13626 Tables 5/7 (PDF pages 54/56),
Oreopoulos JOLE Tables 2/8 (PDF pages 15/23), and Browning-Heinesen 2011 AKF
Tables 6.1/6.2 (PDF pages 23/25). All five raw acquisitions match their pinned hashes.
The new primary-table fixtures are in tests/test_audit04_sources.py.

SSA Supplement 2025 Table 4.B6 confirms the 2023 male age-band earnings shape.
Its 2,517,175-dollar synthetic career sum, converted with CPI-U 304.702 to
313.689, reproduces the pinned 2,591,418 USD-2024 total. This remains a synthetic
profile of worker medians, not the observed median of individual lifetime earnings.

- SSA: https://www.ssa.gov/policy/docs/statcomps/supplement/2025/4b.html
- CPI: https://www.bls.gov/regions/mid-atlantic/data/consumerpriceindexhistorical_us_table.htm
- BLS cohort table: https://www.bls.gov/news.release/archives/disp_08292024.htm

Both CPS tenure references reproduce exactly from their raw ZIP; all 20 CDC
age/sex baseline rows reproduce byte-for-byte from the pinned national XML.
The 2,578,000-worker BLS table total and inclusion definition were rechecked.
Sparse SIPP uncertainty, wider target admission and independent event validation
remain separate research tasks. This audit does not resolve transport error.

## Documentation review

Rechecked all seven original paper findings against the corrected engine.
The current generated mortality summary reports zero of three measured points
inside modeled bands; the pooled prediction is 18.78 [5.51, 42.87] against 4.27.
Paper, HTML, model card, sensitivity example and saved JSON use v1.51 and
retain the experimental scopes and known validation misses. Frozen historical
follow-through evaluations retain their original parameter stamp and are labeled archived.

The canonical paper rebuilt successfully. All 20 pages were rendered; the contact
sheet and changed methods/validation/inventory pages were visually inspected.
There are no compilation errors, undefined citations/references or overfull boxes.
The paper is an untagged PDF with the semantic HTML companion as its accessible path.

## Final verification receipts

- Full Coverage.py test run: 1,065 passed in 368.41 seconds.
- Coverage: statements 96.8%, branches 93.2%; unchanged gates 95% and 90% pass.
- Ruff, vulture and git diff --check pass; evidence audit: zero errors, zero warnings.
- Wheel built from sdist; isolated audit/export/family/validate/scenario,
  mortality-cohort/household/uncertainty/bundle commands all pass.
- Source digest: e8321a687ec44b93345c7e5502e6e96534d8c1752973eccf6ba9a685ffc424df.
- Canonical PDF SHA-256: 713edd6b6eccd99b116ba6f4c514ff9700a953feb807841f7cae86c8ec802281.
- Build/render receipts: build/release04-audit-20261014/ (regenerable, ignored output).
- Numerical fixes: f078daf, b006ea6, 150f9e0, b14f299, e454eaf.
- Source data/provenance replacement: 55381ec (parameters v1.51; engine 0.4.0).

Verification commands:

```sh
.venv/bin/python -m coverage run -m pytest -q
.venv/bin/python -m coverage json -o coverage.json
.venv/bin/python scripts/quality_gate.py coverage.json
.venv/bin/python -m ruff check src scripts
.venv/bin/python -m vulture
make -C paper
.venv/bin/python -m build --outdir build/release04-audit-20261014/dist
.venv/bin/python scripts/check_distribution.py build/release04-audit-20261014/dist/downstream-0.4.0-py3-none-any.whl
```
