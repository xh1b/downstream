# Downstream project review for public website use

## Repair report — October 7, 2026

The 13 repository findings below have been addressed in engine **0.3.0**, parameters **v1.49**. The original review is preserved after this update as a historical record; its examples and findings describe engine 0.2.0 before these repairs. No new causal coefficients or independent validation data were invented.

| Finding | Repair and resulting behavior |
| --- | --- |
| 1. Population applicability | Scenario and entity inputs accept structured target demographics and reviewed per-outcome transport decisions. Default mortality and child-dollar results are explicitly illustrative and ineligible for public headlines. Incompatible target populations block the relevant outcome. Baseline derivation, source-population and horizon qualifications survive in output. |
| 2. County mortality | National baselines carry sex, age, cause and period metadata. The builder refuses incompatible exports; the loader verifies Gamma–Poisson posterior arithmetic at serialization tolerance; consumption verifies the observation/prior chain. Audit covers county and mortality-profile registries. |
| 3. Validation timing | V1 and scoreable V2 mortality use the production five-phase profile and rate-to-risk conversion. Outputs name the method. Tables and plots are regenerated; published misses remain visible. The V2 method revision is recorded before event data are available. |
| 4. Snapshot contract | Snapshot, bundle and scenario use the shared mortality description and machine-readable phase boundaries, including +6 beginning in follow-up year 7. |
| 5. Explanation | The child-to-grandchild explanation ends at its named outcome, describes the narrowing gap against a stable reference, uses percentage points correctly, and carries evidence roles and structural-projection eligibility. Sampling labels come from the resolved sampler. |
| 6. Repeated uncertainty | Repeated aliases of one transmission relationship share one exact draw. Sensitivity and replicate summaries retain alias groups, closure truth vectors reuse the shared-variable sampler, declared external correlations resolve onto that shared identity, conflicting declarations fail, and independent-step analytic inference rejects repeated shared variables. |
| 7. Geography across routes | Policy comparisons, exposure endpoints and knob experiments receive county and profile context. Explicit demographic-profile precedence over county mortality is disclosed. Matched-input county results agree across routes. Mortality experiments resolve county data once per request and sample unrounded values. |
| 8. Empty mixtures | Explicitly empty mortality mixtures and empty resolved applicability lists fail instead of producing an estimated zero. |
| 9. Credits | Full author identities and reviewed aliases replace surname-only grouping. Corporate names and accents are retained. README/CREDITS regenerate with modest bibliography and author-record claims; CI checks freshness. |
| 10. Custom data context | Link simulation and explanations use the selected nodes/correlations context. Custom empty correlation registries produce uncorrelated sampling rather than silently loading defaults. |
| 11. Public inputs | Counts and sample sizes reject invalid types, ranges and nonfinite values. Family descriptions reflect the supplied child count. Derived nonfinite outcomes fail. CLI errors return readable messages without tracebacks, zero-variance sensitivity designs fail explicitly, and JSON serialization refuses NaN/Infinity. |
| 12. Methods equations | The paper uses separately documented net tradable-job loss, J = T × the declared class multiplier, and explicitly treats tradable share as metadata. Mortality equations match the implemented rate conversion and survival calculation. |
| 13. Readability and freshness | The regenerated 17-page paper uses readable relationship labels and data-derived chart axes that include every displayed band. A self-contained semantic HTML methods companion includes scoped tables, keyboard navigation and a complete CSV download. Engine/data versions were advanced, scenario inputs are content hashed, and the paper publishes its complete input manifest including JSON/XML provenance. Fresh distributions are built from corrected source; source archives include the lockfile and HTML companion. |

### Repair verification

| Check | Final result |
| --- | --- |
| Full current suite | **904 passed in 121.32 seconds**, Python 3.12.14 on macOS, four pytest workers. Includes 18 new review regressions and updated assertions for corrected contracts. Earlier interrupted runs and obsolete assertions are superseded by this complete run. |
| Coverage gate | **97.0% lines, 93.8% branches**. Required floors remain 95% and 90%; both pass. Coverage was collected across all four workers. |
| Lint and dead code | Ruff and Vulture pass. |
| Model audit | **0 errors, 0 warnings, 57 informational entries**, including checks of county and profile registries. |
| County rebuild | The supported male export rebuilds byte-for-byte unchanged. Female export rejection, corrupted posterior rejection, and shared geography context are covered by regressions. |
| Installed distribution | Fresh 0.3.0 wheel: audit, export, family, validation, scenario and bundle pass outside the checkout. Engine and parameter bytes are checked against source. The source archive includes the current lockfile and HTML companion; the lock validates offline. |
| Methods paper | 17 pages regenerated, all rendered and visually inspected. No LaTeX overfull/underfull or unresolved-reference warnings. Automated checks preserve chart precision and require axes to contain every displayed band/point. Extracted PDF values and its digest match generated results. |
| HTML companion | Checked at 1280px desktop and 375px mobile widths without document overflow. Keyboard skip link focuses the main content. Landmarks, scoped headers/captions, focusable table regions and complete identifier/CSV access are present. Freshness is checked by CI. |

The paper declares a 103-file input manifest with SHA-256 `fe4d5ffce0828fbf3227568bad568080534494a8507f3ab41e568c1f7b86404b`. These checks establish implementation consistency and release integrity; they do not establish predictive or causal validity. The corrected all-adult V1 diagnostic is **18.77 [6.12, 41.11]** excess deaths per 100,000 adults per unit shock, versus measured **4.27** (95% CI −2.67 to 11.21), and misses both comparisons. The revision is a documented mortality-method correction, not a coefficient adjustment to improve fit.

Reproduce the final checks with:

```sh
.venv/bin/python -m pytest -n 4 --cov=downstream --cov-branch --cov-report=json:coverage.json -q
.venv/bin/python scripts/quality_gate.py coverage.json
.venv/bin/python -m ruff check src scripts
.venv/bin/python -m vulture
.venv/bin/downstream audit
uv lock --check --offline
make -C paper all
.venv/bin/python scripts/check_distribution.py dist/downstream-0.3.0-py3-none-any.whl
```

The parallel runner and pytest coverage plugin were already installed locally. CI retains its normal coverage command; no thresholds were weakened. Historical 0.2.0 archives in the local `dist/` directory are not the corrected release.

### Release interpretation

The backend defects identified here are repaired. A public **illustrative reference-cohort calculator** can use the repaired contracts provided it preserves applicability, blocked states, provenance, horizons and uncertainty labels. Named employer or policy headlines require compatible target inputs, a documented upstream exposure and a reviewed transport decision. A reviewer declaration is a traceable decision, not independent empirical validation.

Actual xh1b.org frontend rendering, production caches, warehouse exposure conversion and deployment are outside this repository and have not been certified. Independent-event V2 and prospective V3 validation remain unestablished. The PDF remains untagged; the HTML companion supplies a semantic reading path, but a full assistive-technology audit of the deployed website remains separate. These scientific and integration limits cannot be removed by backend code changes.

## Original review — before repairs

Review date: October 7, 2026, Hong Kong time. Reviewed commit: `5ea7540e1a8666eff31e3590d855ee93e6cacbeb`, engine 0.2.0, parameters v1.48.

**Original recommendation (before repairs): hold general publication of employer, county, or personal impact headlines until the six P1 findings below are resolved.** The project has a substantial numerical testing and provenance foundation, but its calculation, validation, explanation, and export routes do not yet agree. A carefully labeled research demonstration is more defensible than a general calculator that appears to estimate the consequences attributable to a named employer or immigration policy.

The most consequential risks are scientific applicability and inconsistent public contracts. Passing tests does not establish that a displacement coefficient applies to an employer's actual workforce, or that an upstream worker-equivalent exposure is an identified displacement event. The engine already documents many of these limits; the public routes need to enforce and preserve them.

## Scope and verification

The review covers the Python model, parameter and baseline loaders, mortality calculations, generational transmission, sampling and sensitivity, entity and policy adapters, explanation and rendering, county data preparation, exports and packaging, validation, tests, CI configuration, credits, and the methods paper. The companion website frontend, warehouse runner, cached production outputs, authentication, mobile layouts, keyboard navigation, and deployment were outside this checkout and are not certified by this review.

Primary-source spot checks included the Canadian father–son earnings study and the Sullivan–von Wachter mortality research. This is not a fresh extraction of every coefficient in all 110 bibliography entries. Existing extraction records, roles, and applicability audits remain necessary evidence.

| Check | Result |
| --- | --- |
| Focused regression suite | **142 passed in 66.01 seconds**: mortality mathematics, mortality profiles, transmissions, parameters, audit, policy, county rates, and comparisons. |
| Full suite with coverage | **84 passed before interruption at 959.19 seconds**; 886 tests were collected. The run had reached about 8% and was deliberately bounded. Fresh full-suite success and coverage thresholds are **unverified**. |
| Ruff and Vulture | Both completed successfully with exit code 0. |
| Model audit | 0 errors, 0 warnings, 57 informational entries. This audit does not cover all cross-route and scientific issues below. |
| Validation command | Completed; V1 retains misses and real V2 event evaluations remain blocked on missing data. Completion is not a scientific pass verdict. |
| Fresh source distribution and wheel | Built successfully using the locally cached setuptools backend, without dependency downloads. Wheel engine and parameter bytes match the reviewed checkout. |
| Installed wheel outside checkout | Audit, export, family, validate, scenario, and bundle all passed through `scripts/check_distribution.py`. |
| Existing methods PDF | Text extracted from all 17 pages; pages 1 and 14 rendered and visually inspected. A complete visual/accessibility review remains outstanding. |

The tested wheel has SHA-256 `d639392c6411b3eb16c9939fa21a51ddf2c3b33e6b8b4c40c4e7d47ab7c3bcc0`. The checkout's normal development environment lacked setuptools for a nonisolated build; using the existing cached backend resolved that environment limitation. It is not reported as a package defect. Historical coverage percentages in README were not treated as measurements from this review.

The diagnostic examples below use the reviewed source and shipped data. Numerical comparisons are computed examples, not observed population effects. No model or parameter changes were made for this review.

## What is strong

- The model distinguishes composition in levels, earnings gaps, odds, rates, and conditional mixtures. The mortality kernel converts odds to annual risks and accounts for survival rather than adding rates indiscriminately.
- Parameter rows retain citations, extraction precision, population scope, and applicability roles. Loaders reject many malformed, duplicate, nonfinite, and unsupported records. Arbitrary chains require declared composition.
- Local service-job counts require a separate net job-loss exposure and a job class. Worker replacement alone is correctly refused.
- Scenario results distinguish parameter support envelopes, central parameter intervals, and simulated reference-cohort mortality variation. Excluded uncertainty is named. Fractional exposures cannot masquerade as integer predictive cohorts.
- Forecast registrations are immutable local records, and bundle exports have transactional creation and checksum verification. Tests include adversarial properties and lifecycle state machines.
- Validation publishes misses and blocks missing independent event data. The paper candidly describes the narrower present implementation and avoids claiming that numerical consistency proves causal validity.

These are valuable foundations. They make the remaining problems identifiable and repairable; they do not remove the need for the release gates below.

## Findings requiring resolution before general publication

P1 means a finding can materially change a displayed result, its scientific interpretation, or a consumer's understanding of the implemented model. P2 means an important contract, input, or credibility issue. P3 means presentation or maintenance polish. These priorities concern website release readiness, not security exploit severity.

### P1 1 Generic exposure routes do not establish population applicability

**Evidence:** `src/downstream/employer.py:10,81`; `src/downstream/scenario.py:208,243,303`; `src/downstream/mortality_profiles.py:108`; `docs/MODEL_CARD.md`, caveats.

`DocumentedExposure` records an identity, worker count, source, and method. It has no worker age/sex/tenure composition, child population, or reviewed applicability decision. Omitting a mortality profile takes the ordinary baseline branch and bypasses the profile compatibility check. The engine then applies a high-seniority male mortality response and a male age 45–54 baseline to the entire supplied exposure. Child-dollar totals multiply the Canadian father–son result by the supplied number of children and a US male synthetic career baseline.

For an employer exposure of 1,000 with default inputs, the engine returns **28.73 modeled excess deaths over 20 years** and **$478,894,046.40 in modeled child lifetime earnings losses**, despite receiving no target-population declaration. Both numbers are conditional reference calculations. The inputs do not establish that these are expected effects for that employer's workforce or families.

The child baseline is also a sum of cross-sectional age-band median earnings. Its own notes correctly say this approximates rather than equals the median of individual lifetime earnings and excludes nonworking-year semantics. Those qualifications do not survive in the output's baseline object, which retains only value, citation, and population. Applying an adult annual-earnings effect throughout a synthetic career adds a separate horizon assumption.

**Required change:** introduce an applicability decision at the scenario/entity boundary. General inputs should produce blocked or explicitly illustrative results unless a compatible target population and a reviewed transport rule are supplied. Preserve baseline derivation, synthetic-cohort qualification, fixed-age mortality assumption, source country/sex, and horizon assumptions beside the result. A profile selector alone does not solve child or tenure applicability.

**Acceptance:** unknown or mixed populations cannot obtain an unlabeled employer-specific mortality or child-dollar headline; unsupported populations are refused or presented as named reference scenarios. Tests cover both omitted and explicitly incompatible demographics. The same restrictions apply to direct API calls and website adapters.

### P1 2 County preparation and consumption can accept the wrong population

**Evidence:** `scripts/build_county_mortality.py:102`; `src/downstream/county_rates.py:204`; `src/downstream/place.py:195`.

The county builder takes the national male baseline's numeric rate, but constructs the prior's population and time window from the supplied export metadata. Thus the observation and prior appear to match even when the national rate belongs to a different population. The exported posterior then carries the male baseline's identity in `prior_population` and `prior_citation`. The place adapter verifies that copied identity without checking the observation population and time window against the actual national source.

**Confirmed reproduction:** building from the committed **female ages 45–54, 2015–2019** export succeeds and writes 2,567 posteriors. Feeding that table into Los Angeles County `06037` gives `applied: true`, with an observation population of female county residents, a male national prior of 0.004944, and an applied posterior rate of **0.002154145**. This is a real data-preparation route, not a hypothetical hand-edited file.

In addition, the posterior loader trusts `posterior_mean_rate` without recomputing it from events, person-years, and prior strength. A positive but inconsistent posterior, including a diagnostic value of 0.5, is accepted by the place route. The shipped male table itself reconciles to the posterior formula to within **5.0 × 10⁻¹⁰**, consistent with nine-decimal serialization; the finding concerns protection against future incompatible or corrupted rebuilds.

**Required change:** give the national baseline structured sex, age, cause, and window metadata. Match the export against that identity before fitting. Validate the observation metadata again at consumption, and recompute or verify the posterior mean at serialization tolerance. Extend the audit to the county posterior and profile registries.

**Acceptance:** the female export is refused for the shipped male scenario; age/cause/window mismatches and altered posterior values fail; the current male export remains byte-reproducible and numerically unchanged.

### P1 3 Mortality validation still scores the historical timing

**Evidence:** `src/downstream/validate.py:424,863`; `src/downstream/mortality.py:60,99`; `src/downstream/scenario.py:249`; `paper/downstream.tex:238`.

V1 and the scoreable V2 code call `excess_deaths()` with two coefficients and its default `source_aligned` timing. Production scenarios instead call `excess_deaths_profile()` with all five phases. Sharing the survival kernel family does not make the timing specifications equivalent. The paper explicitly says validation uses the production source-offset profile by default, which is false for these routes.

With 1,000 workers, the shipped annual baseline converted to risk, and point coefficients:

| Follow-up | Historical validation timing | Production five-phase timing |
| --- | ---: | ---: |
| 5 years | 7.9675 excess deaths | 20.8279 excess deaths |
| 10 years | 10.9092 excess deaths | 24.0367 excess deaths |
| 20 years | 16.3231 excess deaths | 28.7345 excess deaths |

These examples isolate the timing discrepancy. They are not revised V1 scorecards, whose exposure and comparison assumptions also require attention. V2 remains blocked on real event data, but its future scoring route has the same discrepancy.

**Required change:** use the same explicit mortality profile and baseline rate/risk convention across production and validation. Keep historical timing only as a named historical variant. Recompute validation outputs and regenerate paper tables and charts after the change; retain published misses.

**Acceptance:** a synthetic matched-input test produces the same mortality contrast through scenario, V1, and V2. Scorecards name the timing method, and the paper accurately describes it.

### P1 4 The production snapshot exports obsolete mortality assumptions

**Evidence:** `src/downstream/snapshot.py:61`; `src/downstream/scenario.py:163`; `src/downstream/bundle.py:26`.

`build()` exports “initial peak year; years 2–5 unidentified and held at baseline; year-6+ coefficient thereafter.” That is the historical incomplete profile. The current default uses displacement, +1, +2–3, +4–5, and +6+, with +6 beginning in follow-up year 7. The bundle embeds this same snapshot, so checksum correctness does not protect the consumer from incorrect model metadata.

**Required change:** derive exported assumptions from the production method definition rather than maintaining a separate prose constant. Export a machine-readable method identifier and phase boundaries as well as prose.

**Acceptance:** snapshot, bundle, scenario, and public explanation agree on all phases and the +6 boundary; an integration test compares these contracts.

### P1 5 The explanation tells the wrong generational story

**Evidence:** `src/downstream/explanation.py:73,101,131,167`; `src/downstream/children.py:54`; `src/downstream/render.py:39`.

The computed earnings multipliers are **0.9076 → 0.94918 → 0.972049**. Relative to the no-displacement reference, the model's gaps therefore shrink from **9.24% → 5.082% → 2.7951%**. The explanation instead describes the second and third transitions as “a further 4.2% down” and “a further 2.3% down.” Those transitions actually move toward the reference. The quoted numbers are absolute changes in the multiplier multiplied by 100, so percentage-point language is required if the transitions themselves are described.

The explanation's outcome and Monte Carlo distribution are for the **grandchild**, but its derivation includes a **great-grandchild** step. Contribution shares consequently include a step outside the stated claim. Its schema also drops the evidence and causal roles retained in the ordinary ledger. It describes the population as US-style children while the direct estimate comes from Canadian father–son closures and later generations are structural assumptions.

**Required change:** describe the remaining gap relative to a stable counterfactual; end the derivation at its claimed outcome; preserve `evidence_role`, `causal_role`, eligibility, source population, and transport conditions. Structural generations need a visible assumption label, not just citations or a weakness sentence.

**Acceptance:** semantic tests check direction against numeric transitions, percentages against their denominator, final step against the named outcome, and eligibility labels in both JSON and rendered text. Existing tests that merely require citations and the word “modeled” are insufficient.

### P1 6 Sampling splits one transmission relationship into independent parameters

**Evidence:** `src/downstream/distributions.py:89`; `src/downstream/transmissions.py:111,240,330`; `src/downstream/mc.py:76`.

The registry explicitly declares the grandchild and great-grandchild IGE rows to be **one relationship unrolled across generations**. The deterministic audit requires their points and bands to agree. Sampling nevertheless assigns each CSV row its own draw, and the walker reads the two separately.

At seed 1901, a four-draw plan's first materialized set gives the two IGE points **0.5714727278** and **0.4327486108**. `drift_relationships()` then reports `ige_earnings`. The sampled result no longer represents repetition of the same uncertain relationship. Great-grandchild uncertainty and attribution therefore describe a different model from the declared recursive one.

**Required change:** sample each relationship once and reuse that value in its unrolled rows. Alternatively, explicitly declare generation-specific relationships and their dependence as a scientific model change. Update analytic inference and sensitivity so repeated random variables are not treated as independent merely because they have different link names.

**Acceptance:** every sampled set preserves equality for a shared relationship; repeated transmission agrees with the shared-variable formula; sensitivity and inference state the dependence they use. Do not attempt to approximate exact equality with a near-perfect copula correlation.

## Other actionable findings

### P2 7 County policy and experiment routes fall back to national mortality

**Evidence:** `src/downstream/policy.py:49`; `src/downstream/knobs.py:97`; `src/downstream/cli.py:588`; `src/downstream/place.py:208`.

Scenario and entity CLI routes load and pass county posteriors. Policy comparisons and mortality knob experiments do not provide this argument, and those function signatures do not support it. A county place key therefore modifies the child pathway while mortality stays national with a fallback reason.

For 1,000 workers in Los Angeles County, the production scenario gives **22.82** excess deaths. The same county and worker count in the policy comparison baseline gives **28.73**, because it uses the national mortality rate. The fallback is disclosed in nested provenance, but the routes still represent different geography for what a visitor will regard as the same scenario.

**Required change:** pass the same resolved data context through all routes, including every exposure-envelope endpoint. Explicit profile selection also needs an intentional county/profile precedence rule. Pin matched-input parity tests.

### P2 8 An empty mortality mixture becomes a zero estimate

**Evidence:** `src/downstream/scenario.py:216`; `src/downstream/mortality_profiles.py:83,121`.

`ScenarioInput(1000, mortality_mix={})` is accepted by the direct API. `resolve_mix()` returns an empty list, applicability validates it vacuously, and the selected-profile branch sums no components. With an empty supplied registry, the result is **0 deaths**, an empty profile list, and no blocked mortality outcome. The ordinary default for the same exposure is 28.73 deaths. The CLI parser does not normally construct this empty mixture, but JSON-to-API integration can.

**Required change and acceptance:** distinguish an omitted mixture from an explicitly empty declaration. Reject the empty declaration before calculation, including an empty mix after zero-weight filtering. Never represent missing demographic information as an estimated zero.

### P2 9 Public credits are stale and the counting method misidentifies people

**Evidence:** `README.md:18`; `CREDITS.md:8`; `src/downstream/credits.py:89,135`.

README and CREDITS claim 81 studies, 166 researchers, 19 parameter studies, and 43 research teams, ending in 2023. The current collector emits 110 entries, 213 researcher records, 53 parameter-source entries, and a purported 120 teams, ending in 2026. Neither output should be used as a verified replacement headline yet:

- Researchers are keyed only by surname. **Sandra E. Black and Dan A. Black**, **Rucker C. Johnson and Jeffrey G. Johnson**, and **Nicholas Turner and Rebecca Turner** are merged. Sullivan also merges Teresa A. with Daniel/Daniel G. Normalizing variants of one author requires a different operation from merging distinct people.
- The number described as “research teams” is the count of researcher names associated with parameter entries.
- Every bibliography entry is described as a peer-reviewed study without a publication-class filter. The bibliography includes books and context/methodology sources; membership in it does not establish a peer-reviewed causal result.

**Required change:** use explicit author identities or reviewed aliases, separate people from teams, classify source types, and regenerate documentation. Prefer modest claims such as “a bibliography of X sources, with Y sources cited by the parameters” until classification is verified. Add a CI freshness check for generated credits and README figures.

### P2 10 Custom parameter directories leak default sampling context

**Evidence:** `src/downstream/mc.py:167,193`; `src/downstream/explanation.py:126,164,205`; `src/downstream/cli.py:621`.

`simulate --outcome` passes the selected parameter directory to the sampler. `simulate --links` does not: `simulate_chain()` has no `params_dir` argument, so it loads the checkout's default correlations. The explanation similarly loads default nodes and correlation context.

**Confirmed reproduction:** in a temporary data-only directory containing the shipped files but an empty `correlations.csv`, outcome simulation reports `lhs`, zero correlations. Link simulation using that same directory reports `lhs+iman-conover`, two correlations. Parameter version and visible coefficients alone do not identify the assumptions used.

**Required change:** carry one explicit nodes/correlations/data-directory context throughout every route. Tests must exercise distinct custom registries, not only copies of default data.

### P2 11 Input validation differs between public routes

**Evidence:** `src/downstream/vignette.py:30,74`; `src/downstream/distributions.py:200`; `src/downstream/cli.py:35,343,610`; `src/downstream/scenario.py:303`.

`family --children -1` succeeds. `family --children 0` still defines the family as three children aged 3, 7, and 12. `simulate --outcome child --draws 0` raises an uncaught `ValueError` from correlation matrix construction rather than a useful parser error. A finite worker input of `1e308` passes scenario validation but produces an infinite child-dollar total; `_dump()` permits nonstandard `Infinity` JSON.

**Required change:** centralize finite/type/range validation, enforce useful operational limits for website inputs, build vignette descriptions from inputs, validate draw/base counts before allocating, check derived values for finiteness, and serialize with `allow_nan=False`. These probes identify concrete classes; they are not a claim that every invalid-input path was exhaustively tested.

**Acceptance:** malformed inputs receive consistent, readable errors; every successful response is standards-compliant JSON with finite modeled values. Zero children and nondefault family sizes have truthful descriptions.

### P2 12 The methods paper still states an obsolete local jobs formula

**Evidence:** `paper/downstream.tex:219`; `src/downstream/scenario.py:195`; `src/downstream/community.py:28`.

The paper presents `J = N s ℓ` as a current scenario equation, where N is displaced workers and s is their tradable share. The current engine deliberately requires separately documented `net_tradable_jobs_lost` and a job class; it does not calculate local service losses from worker displacement times tradable share. Copying the equation into website logic would reintroduce a bug that the engine has already fixed.

**Required change:** use the separate net-job exposure in the paper's notation, definition, diagram, and worked example. Explain that `tradable_share` is currently not the service-job input. Regenerate and review the checked-in PDF together with the validation corrections in P1 3.

### P3 13 Public artifacts need final readability and freshness checks

The existing PDF is typeset clearly on the opening page and exposes limitations prominently. Its parameter inventory, however, breaks long raw link identifiers onto fragments as small as a lone `d` or `te` on the next line, visible on page 14. Prefer readable outcome labels with full identifiers in an appendix or downloadable data table. `pdfinfo` reports that the PDF is untagged; a readable HTML methods page would improve access, and the public download needs a screen-reader review.

The existing local `dist/` wheel differed from the reviewed source in `cli.py` and `compare.py`; do not distribute it merely because its filename says 0.2.0. The freshly built review wheel is a separate artifact. Many engine behavior changes share the same engine version, so release and cache identities should include content hashes rather than just engine 0.2.0 and parameter v1.48.

The current paper's source digest includes a selected set of extensions and does not include every JSON/XML provenance input. A general reproducibility digest should declare and hash its full input boundary. This is a reproducibility improvement, not evidence that the current shipped tables are wrong.

## Scientific and website release decisions

The current model is a conditional propagation model, not yet an evaluated annual household life-course simulator. V0 checks internal consistency. V1 has useful comparisons but substantive population/comparison limitations and published misses, in addition to the timing discrepancy above. Real V2 evaluations remain blocked, and there is no real independently timestamped prospective forecast. These are scientific limits, not failed unit tests.

The annual male mortality rate remains constant across a 20-year follow-up, so it is not an age-progressing life table. County mobility is an exploratory interaction assumption; geographic resolution should not be presented as evidence of more accurate causal transport. Later-generation earnings are structural projections. The central 90% scenario band excludes exposure estimation, baseline estimation, structural uncertainty, and unmodeled pathways. It must not be described as covering 90% of actual future outcomes.

For xh1b.org, the exposure boundary is especially consequential. This engine does not identify how many Americans were displaced by an LCA, a wage offer, a WARN notice, an employer, or an immigration policy. A cited downstream coefficient does not validate the upstream exposure conversion. The provenance of that conversion and its own uncertainty must be visible before multiplying it into downstream harms. The current entity route also returns support envelopes rather than the central parameter intervals provided by the scenario route; the website must not relabel those fields.

An appropriate first public surface would let a visitor explore a **fictional, explicitly specified reference cohort**, with the comparison, population, period, evidence roles, and excluded uncertainty visible. Avoid default personal predictions, causal employer rankings, accumulated totals across incompatible populations, or a single headline that sums different outcomes.

Each result card should show:

1. The initiating exposure and who supplied or estimated it.
2. The treated and reference populations, place, timeframe, and unit.
3. Whether the result is a transported estimate, a structural projection, or an illustrative assumption.
4. A clearly named uncertainty object, with important excluded uncertainty nearby.
5. Source receipts and the applicability decision, including contradictory or null evidence where relevant.
6. A stable engine/data content identity and seed/draw count for sampled outputs.

Explanations should lead with a comprehensible comparison rather than an alarming absolute number. “Not modeled” and “not applicable” must remain distinct from zero. Employer/entity, scenario, policy, and explanation views should share the same computation and eligibility objects so their totals and caveats cannot drift.

## Recommended order of work

**First, align the scientific computation and its consumers:** fix the county population gate, unify mortality production and validation timing, and generate export assumptions from that shared definition. Add a small set of cross-route numerical contract tests before rerunning the whole suite.

**Next, repair the public meaning:** enforce applicability at entity/scenario entry; correct the generational narrative and retain structural labels; share random draws for a repeated relationship; fix credits and paper equations. Review changes using the existing before/after comparison facility, preserving both numerical deltas and changes to metadata.

**Then, stabilize release behavior:** give every adapter the same county and custom-data context; reject empty mixtures and malformed inputs; make successful JSON strictly finite; produce a content-addressed release bundle and installed-package evidence. Review the paper and public copy against the resulting release.

**Finally, review the actual website:** inspect fictional and production-like examples on desktop and mobile; check accessibility, loading/failure/blocked states, caching/version freshness, rounding, provenance links, and language comprehension. Test whether a visitor can identify the reference population and explain what the interval does and does not cover. A passing backend suite cannot substitute for this review.

## Reproduction examples

Run from the repository with its Python environment:

```sh
.venv/bin/python -m pytest -q \
  tests/test_mathematics_v02.py tests/test_mortality_profiles.py \
  tests/test_transmissions.py tests/test_params.py tests/test_audit.py \
  tests/test_policy.py tests/test_county_rates.py tests/test_compare.py
.venv/bin/python -m downstream.cli audit
.venv/bin/python -m downstream.cli validate
.venv/bin/python -m downstream.cli export
.venv/bin/python -m downstream.cli explain --text
.venv/bin/python -m downstream.cli family --children -1
.venv/bin/python -m downstream.cli simulate --outcome child --draws 0
```

The last two commands deliberately probe rejected-input expectations. A successful result for the negative-child command and an unhandled error for the zero-draw command are the defects described above.

To reproduce the incompatible county rebuild without changing repository data, write to a newly created temporary directory:

```sh
.venv/bin/python scripts/build_county_mortality.py \
  --export validation/cdc_wonder_county_female_45_54_2015_2019.csv \
  --out /path/to/new-review-directory/female-county-posterior.csv
```

Load that output with `load_county_mortality_posteriors()` and pass it to `place_baselines()` with the shipped male baseline and place `06037`. The current result incorrectly applies it.

For the empty-mixture and shared-relationship probes:

```python
from downstream.params import load_all
from downstream.scenario import ScenarioInput, compute_counts
from downstream.distributions import plan, materialize_parameter_set
from downstream.transmissions import drift_relationships

p = load_all()
r = compute_counts(p['params'], p['baselines'],
                   ScenarioInput(1000, mortality_mix={}),
                   mortality_profiles={})
print(r['modeled']['excess_deaths']['point'])  # Incorrect zero

d = plan(p['params'], p['nodes'], 4, 1901)
sampled = materialize_parameter_set(p['params'], p['nodes'], d.u[0], d.dists)
print(drift_relationships(sampled))  # ['ige_earnings']
```

## Primary source checks

The [published Oreopoulos, Page, and Stevens abstract](https://www.journals.uchicago.edu/doi/full/10.1086/588493) identifies the Canadian administrative father–son design and the roughly 9% adult annual-earnings result, concentrated in families toward the bottom of the income distribution. This supports the need to retain source-population and outcome qualifications; it does not establish an identical lifetime-dollar effect for all US children.

The [Sullivan and von Wachter working paper](https://www.nber.org/papers/w13626) is the declared source of the implemented phase profile. The repository's mortality reconciliation distinguishes that profile from the published QJE parameterization. Keep the distinction in source receipts; an exact transcription tier is not a general applicability certification.
