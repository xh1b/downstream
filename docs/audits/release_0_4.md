# Downstream 0.4.0 — pending update and review follow-through

<!-- @ref:doc-release-0-4; @tag:release -->
<!--
Connections: @link:code-scenario; @link:code-audit; @link:code-consumer; @link:doc-consumer-fixtures-0-4; @link:doc-model-card; @link:doc-open-source-release; @link:docs-index; @link:test-release-repairs; @link:test-consumer-fixtures; @link:test-exposure-semantics.
-->

Related: [Documentation map](../readme.md) · [consumer fixtures 0 4](../integration.md#scaling-mixtures-and-acceptance-fixtures) · [model card](../model_card.md).
Implementation: [scenario](../../src/downstream/scenario.py), [audit](../../src/downstream/audit.py), [consumer](../../src/downstream/consumer.py). Checks: [release_repairs](../../tests/test_release_repairs.py), [consumer_fixtures](../../tests/test_consumer_fixtures.py), [exposure_semantics](../../tests/test_exposure_semantics.py).

Engine 0.4.0 / parameters v1.52, 2026-10-15. This pending update implements the
review's scenario improvements and records unresolved empirical requirements
in the `tasks/` board. Software correctness and source reproduction do not establish
that the effects transport to a particular policy or population.

This work remains in the 0.4 development cycle and has not been applied to
XH1B. The initial 0.5 label was premature and has been corrected; implementation
and numerical results are retained. Future release numbering follows the
owner's release decision, rather than each batch of model changes.

## Candidate scope and remaining acceptance

The 0.4 candidate is a conditional scenario tool with explicit source, exposure,
population and uncertainty limits. Release acceptance covers the supported
paths already implemented; new empirical claims require their own admission.
The complete task-by-task review is recorded in
[the October 17 scope review](@task:2026-10-17-release-task-review), and the
[release qualification card](@task:2026-10-14-release-04-readiness) tracks completion.

| Work | Required scope |
|:---|:---|
| Fixed-candidate qualification | Freeze the source revision, engine/parameter versions and input identity; regenerate bundle and consumer fixtures together; run full tests, coverage, audit, lint, sdist/wheel installation and a previous-reviewed-version comparison. Archive the actual outputs and review receipts. |
| Companion handoff | Verify nested alternatives, signed sensitivity, applicability, normalization and mixtures through the companion adapter, caches and rendered formats using the [consumer contract](../integration.md#scaling-mixtures-and-acceptance-fixtures). Fresh companion evidence is required before claiming a repin or deployment. |
| Artifact consistency | Generated evidence/pool guides must retain navigation and current input hashes. Consumer fixture source identities and the [saved household comparison](../integration.md#annual-household-comparisons) must match current code. Their regressions and generator checks are part of qualification. |
| Calculator public readiness | Keep the existing chosen surface and viewport checks. Before claiming an evaluated public experience, complete keyboard-only, 200% zoom, screen-reader, physical-device and human comprehension checks under the [calculator protocol](../calculator.md). |

If household modeling is expanded in this cycle, the first substantive data
priority is pooled SIPP trajectories and replicate-weight uncertainty. The
current annual prototype can retain its explicitly limited gross-earnings
and marginal state-time scope while those estimates remain unavailable.
Taxes/transfers, monthly and joint outcomes are additional work, not implied
by the existing five-year comparison.

Wider child/mortality admission, compatible independent coefficient pools,
published-profile source/covariance reconciliation, matched external event
validation, transport/dependence models, protective combinations and new
headline streams remain evidence or owner-decision tasks. Preserve their
limitations in the conditional release. They cannot be closed by relabeling
generic CPS composition, SIPP baseline calibration or successful software tests
as causal validation. A future evaluated public experience retains its
scientific and human-testing gates.

## Source correction

Re-extraction of Sullivan–von Wachter's Table 5 found that the offset 4–5
standard error had been copied from a different column/phase: .077 becomes
the source column's .138. The coefficient point remains .240. The corrected
odds-ratio band is [0.9700, 1.6661], including the null. Source population
labels now distinguish the study cohort from the 45–54 reference baseline.
The mortality persistence alternative remains separately reported.

The release audit additionally re-executes all five Table 5 transformations
at four decimals (v1.51). The 1,000-worker, 20-year point changes from 28.73
to 28.76 expected deaths; the null-persistence alternative remains 20.52.
Working-paper rows now use canonical publication tier. Danish cumulative
hazard ratios retain their different scale/window and 2011 source version;
the MI-or-stroke 20-year cross-check is corrected to 1.09 [0.97, 1.23].
Source coefficients and baseline values are unchanged; the derived OR values
and some support endpoints are corrected, with prior values retained in Git.

The code audit fixes custom subgroup-source handling across all scenario
adapters, verifies consumed source scales/windows, preserves signed near-null
mortality calculations, and refuses incompatible child-dollar baseline units.
Marginal source ranges are not described as simultaneous confidence bands.

## Completed scenario capabilities

- Reproduce January-2024 CPS displaced-worker composition under explicit
  known-year and tenure restrictions. The >=3-year weighted total is
  2,578,128, matching the BLS rounded 2,578,000 publication. A separate
  >=6-year reference is available. Neither identifies an H-1B cohort.
- Compare exact age-stratum mortality with aging versus fixed age-band
  baselines, using sourced male age-at-event contrasts and an explicit
  constant-source-window-response projection. Unsupported strata stay
  unknown and prevent a whole-cohort mortality total.
- Apply sourced child age/sex eligibility and income-quartile contrasts.
  Preserve null-compatible estimates and the positive third-quartile earnings
  coefficient. Unknown child profiles cannot qualify for reviewed headlines.
- Add explicit real discount rates, event/valuation years and annual earnings
  schedules. Keep undiscounted totals, observed-adult-age-window projections
  and constant-career-gap extrapolations separately labeled.
- Compare annual household employment probabilities and gross earnings
  under a supplied unemployment duration and observed SIPP transitions.
  Sparse cells require explicit acceptance. Partner marginal earnings and
  children's ages are tracked; causal recovery and partner responses are
  not identified by these observational transitions.
- Propagate documented mortality-baseline counts, a declared integer exposure
  distribution, coefficients and independent-cohort binomial process variation.
  Keep fixed-input parameter intervals separate; transport error, structural
  model probabilities and unknown dependence remain outside this budget.

Reproducible inputs and results are committed in `validation/`. The new
`mortality-cohort`, `household` and `uncertainty` CLI commands accept those
inputs directly; `scenario` accepts the child eligibility and valuation flags.

## Evidence and evaluation

The source library retains 23 contrasts from three study samples. Repeated
horizons and subgroups are overlapping observations, not independent studies.
Danish cumulative hazard ratios cannot be pooled with annual odds ratios.
Their SEs are explicitly approximate, reconstructed from rounded 95% limits.
No compatible independent pool is claimed. A rate-limited Swedish full-text
request and the incomplete Finnish re-extraction remain in the screening log.
The previously recorded Swedish long-run null-compatible finding remains
visible; missing uncertainty is not invented.

`scenario_evidence_protocol.md` freezes inclusion and scoring rules and records
the subsequent acquisition amendment. These are locally reproducible records,
not an independently timestamped prospective forecast. The original evaluation
is retained; `validation/followthrough_evaluation_expanded_20261014.json` executes the
expanded-library checks. Held-out SIPP transition discrepancies and existing
China-shock diagnostic misses remain visible.

Independent causal evaluation of the new paths still requires a matched
external displacement bridge and independently measured outcomes. Wider
age/sex admission, target-specific exposure/composition, monthly and joint
household dynamics, and a defensible transport-error model remain research
dependencies. The software refuses unsupported totals rather than filling
these gaps with zero or presenting conditional intervals as full certainty.

## Verification

The October 14 receipt measured 96.8% statements and 93.2% branches, above
the unchanged 95%/90% gates. Focused checks cover source arithmetic, signed subgroup effects,
eligibility, unsupported strata, zero-rate valuation equivalence, zero-duration
household equivalence, uncertainty input compatibility and CLI routing.
The October 14 full-suite receipt passed **1,065 tests** after the saved examples
and methods refresh. The later complete receipt passed **1,152 tests** before
the v1.52 receiving-unit changes; the current candidate is checked separately. Ruff and vulture pass; the evidence audit reports zero errors
and zero warnings. The built wheel passes an isolated-install check for all
three new commands plus audit, export, family, validate, scenario and bundle.

The final release audit rechecked 23 source-library contrasts and nine existing
parameter links against primary tables, alongside the 67-row mechanical audit
and existing extraction regressions. It does not claim a fresh primary-paper
re-extraction of the other 58 links. The current audit receipts are in
`tasks/review/2026-10-14-audit-04-release/card.md`.

## Per-result sensitivity - 2026-10-15

Scenario counts and child valuation projections now carry per-coefficient
removal experiments and supported-endpoint refits, with sources, units and
signed changes from the unrounded reference. Entity and policy-arm scenario
records inherit them. Reports retain fixed inputs and unavailable ranges;
they do not invent baseline, exposure or transport uncertainty. Optional
`scenario --sensitivity-base N` adds correlation-aware block variance
attribution separately from deterministic sensitivity and parameter intervals.
See `RESULT_SENSITIVITY.md` and the saved 2026-10-15 reference. Main estimates
and parameter versions are unchanged. Consumer rendering remains pending.


## Receiving units and local tools — 2026-10-15

Parameters v1.52 retire the generic immigrant-stock crime links. Source review
found that Light–Miller regresses log crime rates on an unlogged undocumented
population share in percentage points. Bianchi uses a log immigrant population
share, whose denominator can change. The new typed links preserve the stored
coefficient points/support but correct these exposure units. Bianchi's available
working-paper version remains distinct from the published article. The default
mortality and child-dollar reference values do not change.

`receiving-community --input` accepts explicit source-specific shares or resident
counts with both total-population denominators. It returns signed rate contrasts
and optional same-population annual endpoint incident differences. It does not
infer arrivals from displaced workers, annualize the ten-year source response,
sum violent and total crime, or establish reviewed target transport.
See [source and adapter checks](../integration.md#receiving-community-adapter).

The local calculator now uses numeric controls, equations and compact tables.
Its mobile rules align wrapped labels, provide a wide rate/earnings field and
confine risk-table scrolling. Browser file-preview access is blocked by the tool's
URL policy; rendered mobile and participant checks remain unverified.
Household results reconcile cumulative earnings and E/U/N person-years by member
and household. `downstream.consumer` exposes checked scaling and mixture helpers.
Remarriage screening refuses an unsupported coefficient without treating it as zero.
These are local changes; the XH1B pin and deployment remain pending.


## Final local qualification — 2026-10-15

The integrated run reported 1,389 passing tests and one task-board failure
while that tooling and its test were being changed concurrently. After the
other task's changes landed, the full board/workflow suite passed all 29 tests.
All model/source/calculation regressions passed. Model coverage is 97.2%
statements and 94.1% branches, above the 95%/90% gates. The final focused
calculation/source/artifact suite passed 137 tests.

Ruff, Vulture and the evidence audit pass; the audit reports zero errors and
zero warnings. The final wheel passed all eleven isolated CLI checks, including
receiving-community. It contains the new consumer/receiving APIs and parameter
set v1.52; the source archive includes all calculator assets. Generator checks
for calculator, evidence classification, pool readiness and consumer fixtures
pass. The paper has no LaTeX Warning entries or overfull boxes. One underfull
hbox diagnostic has no visible layout defect. Its current source digest was
recomputed from the final manifest and matches. Changed pages and the full
page overview were inspected for layout defects.

Independent reviews accepted the mobile implementation, receiving adapter,
household summaries, consumer transforms and source-limited remarriage screen.
The browser URL policy explicitly denies the local file preview and alternate
routes; rendered mobile, zoom, assistive technology and participant checks are
still unverified. No companion repin, deployment or independent causal
validation is claimed.

## Calculator app and local server — 2026-10-15 follow-up

The calculator now lives in `calculator/`. `make serve` builds current source
data and serves the app at `http://127.0.0.1:8000/`. The server serves only the
calculator; it does not expose repository files. `make calculator` builds the
self-contained page. Setup, method and review receipts are in [calculator.md](../calculator.md).

The HTTP app was reviewed in the in-app browser at 320, 390, 600 and 1440 px.
No page-wide overflow was found; wrapped labels retained aligned numeric inputs.
Fractional exposure, tail-null and reset controls worked. This completes the
responsive browser-viewport check that was blocked by the earlier file preview.
Physical devices, zoom, assistive technology and human participants remain untested.

## October 17 local qualification

The [fixed-candidate receipt](release_qualification_2026-10-17.md) records
1,458 passing tests plus 7 subtests, a final 19-test documentation rerun,
97.2% statement / 94.1% branch coverage, eleven isolated wheel checks and
eight standalone-bundle inventories. The prior local 0.3/v1.49 pin comparison
retains all field differences and the unavailable baseline-validation status.
The [calculator review](calculator_accessibility_2026-10-17.md) adds keyboard,
accessible-name and zoom-equivalent reflow checks; actual native zoom,
assistive technology, physical devices and participants remain unverified.
The [fresh companion handoff](xh1b_handoff_2026-10-17.md) reproduces the nested
mixture limitation and names its existing integration tasks. Owner release
acceptance and companion repin/cache/render/deployment receipts remain pending.


## Corrected consumer intervals — October 17 follow-up

The [latest qualification](release_qualification_2026-10-17_interval_fix.md)
supersedes the earlier candidate after a shared-object scaling bug was found
by cross-language fixture checks. Source-profile nested intervals now scale
once. Default model calculations are unchanged. The corrected candidate passes
1,463 tests plus 7 subtests and the full local distribution/coverage gates.
Use its recorded bundle and fixture identities for the pending handoff.

The [local handoff follow-up](xh1b_handoff_2026-10-17.md#local-integration-follow-up--2026-10-17)
records the prepared companion pin, checked mixtures, preserved nested metadata
and readable methods artifact. Earlier pending-local-pin statements above are
historical. Live cache, served browser and deployment acceptance remain open.
