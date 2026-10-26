---
title: Review paper against current code
area: docs
priority: P2
assignee: paper-review
blocked-by: []
expected-paths: []
---

# Review paper against current code

User-requested audit of paper/downstream.tex and the distributed PDF against current implementation and parameter data.
Review only; record concrete drift and distinguish missing coverage from incorrect claims.

## Acceptance

- [x] Compare model, uncertainty, validation and reproducibility claims with current code. [dated review receipts](#verification-receipts)
- [x] Check generated tables and PDF freshness without changing the paper. [dated review receipts](#verification-receipts)
- [x] Record prioritized findings with source references and verification receipts. [dated review receipts](#verification-receipts)

## Review verdict

The paper is partially out of date. Generated numerical artifacts match the current engine, but one V1 result
interpretation is incorrect and several implemented experimental capabilities are still described as future work.
The default propagation formulas remain consistent. Updating the narrative is necessary before publication.

Reviewed on 2026-10-14 against master e6ca7de (engine 0.4.0, parameters v1.50), including the working-tree PDF.
The PDF was already modified by another worker; this review did not edit it or the manuscript.
This is a paper-to-implementation review, not an independent assessment of the underlying empirical studies.

## Findings

### F1 - P1: pooled-adult mortality coverage is incorrectly claimed

Paper: paper/downstream.tex:438-439; PDF page 7, section 5.2.
Code: src/downstream/validate.py:448; generated evidence: paper/generated/mortality.tex:1-3.

The prose says the pooled-adult row covers the observed point. The live result is 18.77 [5.51, 42.87]
against 4.27 deaths per 100,000 adults per unit shock, so the measured point is outside the modeled band.
All three mortality rows report measured_inside_modeled_band=false. The other two bands are
27.16 [7.98, 61.94] and 25.88 [7.60, 59.02], also above the measured point.
The generated appendix is correct; rebuilding alone cannot repair this manually written claim.

Required change: state that all three mortality variants overpredict and exclude the observed point.
Preserve the population/outcome-transfer cautions and distinguish point coverage from measured-interval coverage.

### F2 - P2: an implemented transmission alternative is called future work

Paper: paper/downstream.tex:183-185 and 388-391; PDF page 3, section 3.2.
Code: src/downstream/variants.py:46-52, 127-130 and 171-176.

The paper proposes a future comparison of the linear gap mapping with the finite-change v**t mapping.
The log_elasticity_transmission variant already runs in the public ensemble with the same cited coefficient
and structural-transmission label. This is a definite implementation-status mismatch.

Required change: describe the existing named alternative and include it in the structural-ensemble inventory.
Neither mapping should be presented as an independently identified intervention response.

### F3 - P2: the five-year household demonstration is already implemented

Paper: paper/downstream.tex:589-597 and paper/figures/future.tex:5; PDF page 10, section 7.1.
Code: src/downstream/household.py:18-116; src/downstream/cli.py:84-86.

The text says a five-year household employment/earnings comparison is the next demonstration and explicitly
states these capabilities are not currently claimed. The figure labels all of them not implemented.
The household command already compares E/U/N state probabilities and gross earnings, ages members and children,
and reuses observed SIPP 2021-2022 transitions under explicit stationarity/Markov assumptions.
The saved five-year fixture reproduces a cumulative displacement-minus-reference earnings difference of
-105587.1582773834 USD in 2024 purchasing power.

Required change: describe this limited experimental prototype, then distinguish the remaining research work.
It has supplied unemployment duration/scars, sparse-cell opt-in, no full prediction intervals, and no causal
recovery estimate, joint household dependence, taxes/transfers, marriage, or protective-intervention model.
It remains ineligible for a public headline. This does not establish a representative life-course simulator.

### F4 - P2: blanket statements that mortality cannot age are now too broad

Paper: paper/downstream.tex:261-263, 511-513 and 551-552; PDF pages 4 and 9.
Code: src/downstream/mortality_strata.py:57-100; src/downstream/cli.py:81-83.

The ordinary scenario still uses a fixed reference baseline, so its formula and limitation remain accurate.
However, the separate mortality-cohort command now aggregates supported male age strata and compares aging
age-band baselines with fixed baselines. It uses Table 7 source-window responses held constant by a declared
projection assumption, rather than recovering age-specific Table 5 phase profiles.
The saved hypothetical 1000-worker example covers 524.5038 workers and leaves 475.4962 unmodeled;
its covered expected totals are 18.3625 deaths with aging and 9.9594 with fixed baselines.
A whole-cohort estimate remains unavailable because some strata are unsupported.

Required change: scope the fixed-age limitation to the default scenario, document the separate experimental
projection, and retain transport, period-rate, covariance, and incomplete-coverage qualifications.

### F5 - P2: baseline/exposure uncertainty is still presented entirely as future work

Paper: paper/downstream.tex:523-527, 540-549; PDF pages 9-10.
Code: src/downstream/uncertainty_budget.py:19-25, 56-92; src/downstream/cli.py:87-89.

Default scenario sampling remains parameter-only. The separate uncertainty command now propagates a documented
national event/person-time baseline through a Gamma likelihood calculation, a declared integer-uniform exposure,
parameter draws, and separate binomial process contrasts. It retains a fixed-input reference report.
This implemented method is absent from the paper while baseline uncertainty remains a next-release priority.

Required change: document both interfaces and their distinct scope. The new budget requires the national
source-profile scenario and assumes independence among baseline, exposure, and study parameters. It excludes
transport error and structural probabilities. County posterior uncertainty is still not sampled in the default
scenario; the paper's specific statement at lines 415-416 remains accurate and should not be removed wholesale.

### F6 - P2: child applicability, subgroup contrasts, and present values are undocumented

Paper: paper/downstream.tex:118-130, 212-219 and 268-270.
Code: src/downstream/child_applicability.py:31-69; src/downstream/scenario.py:385-417;
code: src/downstream/valuation.py:14-55; src/downstream/scenario.py:501-510.

The paper describes generic child counts and one lifetime dollar conversion. The interface now accepts
child age/sex profiles, rejects known incompatibility with the male age-10-14 source cohort, and requires
reviewed applicability before headline eligibility. Unknown profiles remain illustrative.
Optional father-income-quartile contrasts preserve signed/null/beneficial effects and source uncertainty.
Optional age-timed real present values distinguish the observed adult-age window 25-33 from the assumed
constant-gap career projection 20-64, and include separate parameter-only intervals when sampled.

Required change: state the eligibility rules and conditional inputs, and distinguish the original undiscounted
count from the optional discounted projection. Retain the Canadian-effect/US-dollar transport limitations
and the fact that a constant lifetime response is an extrapolation.

### F7 - P2: default mortality persistence robustness is missing

Paper: paper/downstream.tex:229-240, 388-391 and 511-516.
Code: src/downstream/scenario.py:417-430 and 497-519; src/downstream/mortality_robustness.py:32-75.

Default source-profile mortality now includes a no_sustained_excess alternative, setting source offset +6
onward to OR=1. It first changes follow-up year 7 and uses the same baseline, exposure, horizon and early odds.
For the 1000-worker, 20-year national reference, the source result is 28.73 expected deaths and the alternative
is 20.52, a difference of 8.21. Sampling calculates within-draw differences on shared parameter draws.
The paper documents other mortality timing alternatives but omits this scientifically material default output.

Required change: describe the persistence sensitivity and its paired parameter calculation. It is a hybrid
structural assumption motivated by source divergence, not a reproduction of the Swedish study, an HR-to-OR
substitution, evidence of exact zero long-run effect, or a probability-weighted model average.
The general policy comparator still uses support-envelope subtraction; its separate limitation remains accurate.

## Additional missing coverage

The paper does not summarize the new CPS displaced-worker reference cohorts or the SIPP baseline checks.
The expanded evaluation retains a passed reproduction of the published BLS total (difference 128.318 workers
within a 1000-worker rounding tolerance), 54 held-out SIPP calibration cells, and 23 explicit pooling refusals.
There are zero compatible pooled reports and no matched independent new-event score.
See scripts/evaluate_followthrough.py:26-38 and validation/followthrough_evaluation_expanded_20261014.json.
These should be reported as descriptive cohort reproduction/baseline calibration, not promoted to V2 validation.
The HTML companion already documents most new capabilities; its generator is ahead of the LaTeX narrative.

## Verification receipts

- Regenerated every paper data artifact into an isolated output directory, without modifying repository outputs.
- All generated files matched byte-for-byte; live validation exactly equaled paper/generated/results.json.
- Parameter set v1.50, 67 parameters, 2 declared correlation pairs, and 1444 panel rows agree with the paper macros.
- Full source digest: 0ec140f7bffbd0e59fbccead3f3d9ecac1368fded8e4f7fb8b4e6ab666f440f2.
- The 17-page PDF includes that digest prefix and v1.50; pages 7 and 10 were rendered and visually inspected.
- Reviewed PDF SHA-256: 3054f4f8b942baca58fa3871331740610190676b93a6ade3fcbaa2e2d7dfcee0.
- Fresh household, stratified-mortality, and uncertainty calculations exactly reproduced their saved JSON fixtures.
- docs/methods.html matched its current builder output.
- Relevant test run: 102 passed in 1.31s; no code or manuscript changes were made by this review.

Test command:

```sh
.venv/bin/python -m pytest -q tests/test_paper_tables.py tests/test_variants.py \
  tests/test_mortality_robustness.py tests/test_mortality_strata.py \
  tests/test_child_applicability.py tests/test_valuation.py tests/test_household.py \
  tests/test_uncertainty_budget.py tests/test_followthrough_cli.py
```

## Claims still consistent with the code

The five-phase odds-to-risk survival kernel, direct child effect and linear gap transmission, null-safe place
adjustment, independent-cohort predictive interpretation, and policy envelope subtraction match implementation.
V0 bands overlap; family-status panel contrasts are covered; both earnings panel variants still miss.
V2 event scoring remains blocked and no real prospective result is established by repository evidence.
The added experimental capabilities do not justify removing the paper's causal-validity or public-use cautions.

## Recommended update order

1. Correct the mortality coverage statement and add a check tying qualitative coverage prose to the scorecard.
2. Replace obsolete future-work language with scoped descriptions of implemented experimental methods.
3. Document child eligibility/subgroups/valuation and mortality persistence before broadening claims.
4. Add cohort/baseline evaluation receipts and retain independent-event, transport and public-use research gates.
5. Regenerate paper artifacts and check PDF/HTML narrative agreement after editing.
