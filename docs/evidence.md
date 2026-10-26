# Evidence and data operations

<!-- @ref:doc-evidence; @tag:evidence -->
<!-- @link:docs-index; @link:code-params; @link:code-evidence; @link:paper-parameters. -->

This guide covers source custody, data admission and reproducible maintenance.
The [parameter loaders](../src/downstream/params.py),
[source library](../src/downstream/study_library.py) and named adapters enforce
the executable contracts. The paper explains scientific interpretation and
synthesis (@link:paper-parameters, @link:paper-synthesis). Passing a loader or
audit is a software check; it does not establish causal identification.

## Know which record you are editing

| Record | Purpose | Authoritative files / consumer |
| --- | --- | --- |
| Shipped parameters | Versioned points, bands, units, scope and citations | [parameters.csv](../params/parameters.csv), [params.py](../src/downstream/params.py) |
| Bibliography and extractions | Source identity and how a number was obtained | [references.bib](../params/references.bib), [dated extraction/correction notes](../params/CHANGELOG.md) |
| Screened evidence | Corpus membership, findings and exclusions | [evidence.py](../src/downstream/evidence.py), `params/evidence_*.csv` |
| Study contrasts | Version-pinned estimates with scale, SE and sample overlap | [study_estimates.csv](../params/study_estimates.csv), [study_library.py](../src/downstream/study_library.py) |
| Baselines and profiles | Reference levels, populations and windows | [baselines.csv](../params/baselines.csv), [mortality_profiles.csv](../params/mortality_profiles.csv) |
| Household transitions | Observed conditional employment shares | [baseline_employment_transitions.csv](../params/baseline_employment_transitions.csv), [household.py](../src/downstream/household.py) |
| Review outputs | Classification, compatibility and source checks | [Audit collection](audits/readme.md) |
| Pending extraction status | Source-row queue, coordinated through tasks | [Extraction register](research/queued_extractions.md) |

Extraction precision (`tier`), source applicability (`evidence_role`) and the
ledger's runtime `causal_role` are separate. A precisely extracted association
does not become a displacement effect. A direct source estimate can still
require conditional target transport. A loaded finding/contrast does not
become an admitted parameter automatically. See the generated
[classification review](audits/evidence_classification_0_4.md).

## Citation and extraction rules

<!-- @ref:doc-citing; @tag:evidence -->
<!-- @link:code-params; @link:code-citations; @link:code-audit; @link:test-source-reextraction; @link:paper-parameters. -->

Use peer-reviewed quasi-experimental studies or suitable meta-analyses for
causal parameter points, government statistics for baselines, and explicit
structural assumptions where no causal estimate is being claimed. Working
papers are allowed at `canonical` maximum pending published reconciliation.
Advocacy/think-tank material supplies context, not parameter points.
Observational baseline transitions retain their descriptive role.

| Precision tier | Required provenance |
| --- | --- |
| `EXACT` | Number read and pinned from the study's own full text/table/figure. |
| `EXACT-abstract` | Published abstract/summary or confirmed synthesis full text. |
| `EXACT-results` | Results section transcribed in the extraction log. |
| `canonical` | Literature value awaiting the queued full-text/version check. |

Do not promote an extraction tier from memory. Parameter citations are
semicolon-separated bib keys, never free text. Keys must resolve in
`params/references.bib`; retain its `xh1b-evidence` field and source locator.
The audit checks mechanical consistency. Corrections need dated row notes,
parameter version/changelog updates and a new commit.

Name each band's basis in the row notes: reported CI/SE interval, cited
cross-study spread, or a declared rounding band. A rounding band of point
±25% is allowed only for a canonical row with an extraction-queue entry.
Adding evidence does not silently shrink an existing band; replacement must
preserve the old row in Git history. A support band does not become a
confidence interval by being sampled.

Preserve null, protective, harmful and conflicting evidence. Do not set a
nonsignificant point to zero or average contested positions into a consensus
coefficient. Record refuting literature and refusals. Collapse duplicate
findings without manufacturing independent study counts. The
[source-reextraction tests](../tests/test_source_reextraction.py) pin important
source arithmetic; [audit tests](../tests/test_audit.py) check the mechanical gate.

## Add or revise evidence

1. Claim a task and check the [extraction register](research/queued_extractions.md).
   Preserve the source/version, raw artifact hash, locator and access date.
2. Record treatment/comparator, population/subgroup, outcome definition, scale,
   follow-up, design, uncertainty and overlap before assessing usability.
   Preserve exclusions and unread candidates; do not select by sign or fit.
3. Load the source contrast through the declared custom `params_dir`. Verify
   the adapter consumes compatible fields; a fallback to bundled sources can
   hide a missing extraction.
4. Inspect compatibility before synthesis. Common overlap groups need an
   explicit dependence model. Different labels alone do not prove independence;
   shared controls, registry reuse and duplicate versions still need review.
5. Review the scientific change explicitly. A synthesis comparison is a manual
   admission report, not an automatic parameter rewrite. Update versions,
   notes, tests and downstream artifacts only for the reviewed landing.

```sh
downstream audit
python3 scripts/build_evidence_classification.py --check
python3 scripts/build_pool_readiness.py --check
```

Remove `--check` to regenerate those audit reports after a source/code change.
Their builders are [classification](../scripts/build_evidence_classification.py)
and [pool readiness](../scripts/build_pool_readiness.py); their output belongs
in `docs/audits/`. The [readiness report](audits/pool_readiness_0_4.md) preserves
scale/window/subgroup mismatches. Annual odds ratios, cumulative hazard ratios,
hazard ratios, risk differences and log earnings coefficients are not freely
interchangeable. Subgroups and phases are not independent replications.

## Mortality baseline import

<!-- @ref:doc-cdc-wonder-profile-import; @tag:mortality -->
<!-- @link:code-county-mortality; @link:code-mortality-profiles; @link:script-fetch-wonder; @link:script-build-county-mortality; @link:paper-place; @link:paper-synthesis. -->

Use a separate CDC WONDER export per demographic profile. The importer needs
**County only** as the group-by dimension; sex, age, cause and years are
filters. Preserve raw counts and population totals over the selected years as
person-years. A crude-rate column or generic precision weight is not a trial
count or denominator.

[scripts/fetch_wonder.py](../scripts/fetch_wonder.py) supplies `national`
(machine XML API) and `county` (scripted web session) pulls and provenance
sidecars. The county pull also writes importer metadata. A compatible import
requires:

- `years`: contiguous source window;
- `sex`, `age`, `cause` and `group_by: ["County"]`;
- `population_unit: "person-years"`;
- `source_url` and `retrieved_at`.

Missing metadata is refused. Add a profile row only after verifying its matching
national annual rate and citation; `context_only` cannot produce counts.
`county-wonder-posterior` requires a national prior with the same outcome,
population and window. Cause-specific counts cannot be pooled against an
all-cause prior. Suppressed/absent compatible county rows use the named
national fallback; preserve that provenance in the result.

Select a profile with `--mortality-profile PROFILE_ID` on `scenario` or `entity`.
Explicit `--mortality-mix profile_a:0.4,profile_b:0.6` needs unique verified
profiles and weights summing to one. Every response must also be admitted:
baseline availability for women or other age groups does not qualify the
standard male 45–54 response. Predictive cohort uncertainty remains unavailable
without stratum-specific counts. See [integration limits](integration.md#mortality-outputs)
and [profile tests](../tests/test_mortality_profiles.py).

The old all-ages county export is context only because its parameter block
does not reproduce the filters. The [source inventory review](audits/data_sources.md)
retains historical acquisition details; current importer behavior lives in code.

## Household and other source data

Preserve raw input manifests and derivations separately from admitted tables.
The [SIPP manifest](../validation/sipp/MANIFEST.md) and
[transition review](audits/baseline_transition_r2_2026-09-14.md) explain the
existing ordinary December-to-December transition artifact. Its held-out
baseline check does not validate a causal displacement-recovery model.
Sparse cells require explicit acceptance in the household API; uncertainty
about survey design and complete trajectories remains unquantified.

Keep source restrictions and redistribution terms with imported material.
The historical [PSID](audits/psid_baseline_data_assessment_2026-09-13.md) and
[SIPP](audits/sipp_baseline_data_assessment_2026-09-13.md) assessments are review
records, not permission to reuse arbitrary data. Do not commit credentials,
restricted microdata or private records. Follow existing acquisition tooling
and retain its provenance rather than creating an unrecorded manual data path.

## Evaluation records

<!-- @ref:evidence-evaluation; @tag:validation -->
<!-- @link:code-validate; @link:code-scoring; @link:code-forecast-registry; @link:paper-validation; @link:paper-independent-validation. -->

`downstream validate` reports the software's V0/V1 diagnostics and gated V2
status. The [evaluation protocol](research/scenario_evidence_protocol.md)
records source-selection and frozen external-event requirements. It was written
after existing anchors were known, so it does not retrospectively preregister
them. Saved evaluations retain the protocol hash used at execution; do not
rewrite an old receipt to claim it ran against a later document revision.

Before scoring a genuinely external event, freeze the displacement bridge,
target composition, timing, geography, comparator, outcomes and scoring rules.
Preserve all endpoints, missingness, misses and amendments. CRPS/coverage require
a compatible predictive distribution, not a support envelope. A local registry
entry needs an independent timestamp to establish public prospective timing.
Use the [forecast registry](../src/downstream/forecast_registry.py) and its
[lifecycle tests](../tests/test_forecast_fsm.py) for executable registration rules.
New paths remain unvalidated until matched independent evidence exists;
synthetic scoreable fixtures only verify software behavior.

## Attribution and citing an output

<!-- @ref:doc-attribution; @tag:evidence -->
<!-- @link:code-credits; @link:code-citations; @link:test-credits; @link:paper-reproducibility. -->

Each displayed estimate travels with its source authors, units, window and
assumptions. Credit methods as well as substantive findings. Compute collective
source/author statements with `downstream credits`; do not hand-maintain counts
or label every bibliography entry a peer-reviewed study. Named author records
include organizations and reviewed aliases; they are not verified team counts.

```sh
downstream credits --write
```

This updates [CREDITS.md](../CREDITS.md) and the generated README attribution
from the bibliography. DOI acquisition uses [fetch_dois.py](../scripts/fetch_dois.py);
uncertain matches stay in [doi_review.json](../params/doi_review.json), and
working papers/books without DOIs remain without one.

Cite the paper or repository together with engine version, parameter version,
content identity, inputs and seed where sampled. A published number needs a
reproducible source revision and its scientific citations, not just “the model.”
For rebuilding and comparing the resulting artifacts, see
[development](development.md).


## Source withdrawals and retained records

<!-- @ref:source-withdrawal-contract; @tag:evidence -->
<!-- @link:code-source-support; @link:code-params; @link:code-ledger; @link:test-source-withdrawals. -->

Parameters v1.53 retain all 67 original CSV records while withdrawing 16 from
calculation: seven source/estimand/unit mismatches and nine unverified numerical
extractions. The authoritative [source-support policy](../params/source_support.json)
records every link, reason, finding class and public review provenance. These
are conservative withdrawals, not replacement estimates or a fresh review of all
remaining sources. Absence from the withdrawal list does not establish new source
verification or target transport.

`ParameterSet.by_link` and ledger composition refuse these inputs with
`SourceUnavailable`, including after overrides, sampling and variant construction.
`retained_by_link` explicitly inspects original records; inspection does not
admit them for calculation. Custom parameter directories cannot replace the
engine's reviewed withdrawal policy. Reinstatement requires supported source
corrections and a reviewed policy/version change.

Grouped reports retain supported branches and expose unavailable branches with
null numeric fields and the named source reason. A known zero, favorable effect,
transport decision or place modifier does not restore a withdrawn input. The
later earnings transmission and daughter partner-violence result are unavailable;
the additive divorce/family-size variant is excluded from ensemble spreads.
Direct child and supported mortality paths retain their numerical results.

Snapshot schema `downstream-parameter-set/3` separates 51 available `parameters`
from 16 original `withdrawn_parameters`. The latter carry their original values
and source-support disposition explicitly as an archive. `citations` covers
available inputs; `unidentified_reference_archive` retains the original
`adermon2018` and `lindo2018` records without citing them as identified sources.
The effective policy SHA-256 accompanies exports. Older consumers must handle
this schema and unavailable branches before repinning; deployment and cache
refresh retain the companion's separate acceptance requirements.
