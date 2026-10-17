# Local 0.4 candidate qualification — 2026-10-17

<!-- @ref:release-qualification-2026-10-17; @tag:release -->
<!-- @link:doc-open-source-release; @link:script-quality-gate; @link:script-check-distribution; @link:code-bundle; @link:code-compare. -->

**Superseded for release use:** the [interval-alias follow-up](release_qualification_2026-10-17_interval_fix.md)
qualifies a corrected bundle. The receipt and archive below identify the earlier candidate.

Engine **0.4.0 / parameters v1.52**, committed candidate
`429af5397752a8fd4c1062b54b0835d82d2b13e4`. This receipt qualifies the existing
conditional scenario tool locally. [Release scope and scientific limits](release_0_4.md),
[calculator accessibility](calculator_accessibility_2026-10-17.md), and
[companion handoff](xh1b_handoff_2026-10-17.md) remain separate evidence.
Work history: @task:2026-10-17-candidate-qualification.

The retained inputs, before/after outputs, comparisons, coverage, build/install
logs, bundle, distributions and environment are in
`build/release04-qualification-20261017/`. The [machine-readable receipt](release_qualification_2026-10-17.json) records
checks and artifact identities. The compressed archive is `build/release04-qualification-20261017/qualification-artifacts.tar.gz`;
all 144 archived file hashes verify. Its SHA-256 is
`76889f9ed7c3e6949e8d439c8ee7b38ef3eb4e58c12ca12aa33c40c445e0da65`.
Later receipt/task commits do not change the qualified engine or parameter bytes.

## Verification

| Check | Result |
| --- | --- |
| Complete Python 3.12.14 suite under coverage | 1,458 tests and 7 subtests passed in 318.86 seconds. |
| Final committed documentation tests | 19 passed under appended coverage. |
| Statement / branch coverage | 97.2% / 94.1%; required floors remain 95% / 90%. |
| Python 3.14.7 fast numerical/lifecycle selection | 151 passed. |
| Ruff, Vulture and evidence audit | Pass; audit has zero errors and warnings. |
| Documentation examples, paths/headings and six generated-artifact checks | Pass; 36 executable example statements. |
| Repository refs and task validation | Pass, with historical accepted evidence gaps reported separately. |
| Distribution build and isolated wheel install | Wheel built from sdist; all 11 command checks pass. |
| Standalone bundle | 74 files verify; eight CLI inventories pass outside the checkout. |
| Companion probes | Seven old-pin tests pass; eight candidate cases run. Nested-mixture limitation is explicitly retained. |

The coverage run began while the documentation unit was being finalized.
Content manifests prove that engine, parameters, fixtures and all implementation
scripts stayed byte-identical. Only `tests/test_doccheck.py` changed after
collection began; its final committed version was rerun under appended coverage.
The final committed content manifest and initial manifest are both retained.
This avoids attributing coverage to changing source lines or silently ignoring
a concurrent test change.

The paper was rebuilt after the source freeze. Its input manifest recomputes to
`689ff559d3af01da8f14c4b5e467bf6cde6924fc618bcd8618c1ea58e15130a4`.
Text comparison finds only the source fingerprint changed, on page 15. That
page was rendered and inspected. No LaTeX warnings or overfull boxes occurred;
the existing underfull-box diagnostic has no visible layout defect. Generated
paper output is separate from the engine bundle identity.

## Previous reviewed pin comparison

The baseline is the existing verified local XH1B **0.3.0 / v1.49** bundle,
SHA-256 `bb2b77ddfb379bb71d40b91abb25658940160a679c3a22be1ac7f116f8a1a606`.
This identifies a locally reviewed pin; no deployed state was inspected.
Each side executes its own engine/data with identical arguments, including
200 draws and seed 1901 for zero, one-person and 1,000-worker scenarios.
Eight inventories cover audit, parameter export, family, those three scenarios,
transmissions and grandchild inference. Every field is retained in JSON, CSV
and Markdown comparison reports, with **no numeric tolerance or filtering**:
33,654 unchanged, 199 changed, 881 added and 30 removed fields.

| Reference result at 1,000 workers | Prior pin | Candidate |
| --- | ---: | ---: |
| Expected excess deaths | 28.73 | 28.76 |
| Mortality support low / high | 12.32 / 48.49 | 11.26 / 50.10 |
| Child lifetime earnings difference, USD | 478,894,046.40 | 478,894,046.40 |
| Service jobs for 1,000 separately supplied tradable jobs | 1,600 | 1,600 |

The mortality changes follow the existing source transcription/scale corrections,
including the null-compatible offset +4/+5 support. New fields expose structural
alternatives, signed sensitivity and child applicability. The generic immigrant
influx links are replaced by the already documented source-specific receiving
units. Provenance and version/hash changes are retained. The national
no-sustained-excess structural point is 20.52; it is an assumption comparison,
not a confidence interval, independent estimate or model probability.
Parameter draws and process intervals also change; this 200-draw inventory is
a reproducibility comparison, not a precision-qualified uncertainty analysis.
Last-bit annual-probability changes are recorded rather than suppressed.

The old consumer bundle omits `validation/`, so its `validate` command cannot
load `adh2019_measured_coefficients.csv`. The exact failure is retained in
`baseline-validation.stderr.txt` and its status in `baseline-identity.json`.
Validation is therefore **not** presented as a before/after result. Current
validation output is archived separately and exercised successfully from the
installed wheel with its packaged validation data. This qualification does not
supply new independent causal validation or erase known held-out misses.

## Artifact identity and reproduction

- Bundle content SHA-256:
  `6af38c54fa3131a0a5665ea034d664c64bf64152132fa7ae1f62f02fced611d2`.
- Consumer fixture file SHA-256:
  `d6b29db411020f35c6c989f88878330a3bd9be070d1c1c1dc4e44e6da586e866`.
- Wheel file SHA-256:
  `a580178e2b889f6b57f2939db5eea68b642fa2108ad54b4cf9afc1fa2ecfca73`.
- Source archive file SHA-256:
  `3a0919ea92774b257f21873e72b507979760dd7294989b9e9cd897c11e33fa21`.
- Committed qualification input manifest SHA-256:
  `256939a0977ef2330f193fd8148e2015b78314f758fed244692080ae5398badb`.

The bundle verifies all 74 listed files. Its eight supported CLI inventories
run with isolated imports and working directory `/tmp`; all eight companion
worker outputs match the source probes. The bundle deliberately exports code
and parameters, whereas the wheel includes validation datasets. For integration,
retain the bundle manifest, parameter export, consumer fixtures, raw-input/output
hashes and comparison reports together. Review the reproduced nested-mixture
limitation before accepting a companion update.

Use the development environment and [qualification commands](../development.md#release-and-companion-handoff).
The archive retains the exact driver, command arguments, runtime/tool versions,
source manifests and logs. Core commands are:

```sh
python -m coverage run --data-file=build/release04-qualification-20261017/.coverage -m pytest -q
python -m coverage json --data-file=build/release04-qualification-20261017/.coverage -o build/release04-qualification-20261017/coverage.json
python scripts/quality_gate.py build/release04-qualification-20261017/coverage.json
python -m ruff check src scripts
python -m vulture
python scripts/doccheck.py --examples --freshness
python scripts/refcheck.py check
python scripts/tasks.py validate
python -m downstream.cli audit
python -m build --no-isolation --outdir build/release04-qualification-20261017/dist
python scripts/check_distribution.py build/release04-qualification-20261017/dist/downstream-0.4.0-py3-none-any.whl
```

A fresh bundle destination must not already exist. For the comparison, run the
arguments in the archived `commands.json` against each isolated engine, then
use `downstream compare --before <directory> --after <directory> --format json`
(and `csv`/`markdown`). Preserve the unavailable-baseline validation status.

## Remaining acceptance

Owner release/publication acceptance, companion repin/cache/rendering/deployment,
real native zoom, screen-reader and physical-device checks, and participant
comprehension remain open on their existing cards. Broader target-cohort,
independent evidence, covariance, household survey-uncertainty and external-event
evaluation tasks retain their empirical dependencies. Local software checks do
not complete those research or human-review requirements.
