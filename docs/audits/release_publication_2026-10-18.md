# 0.4 publication preparation — 2026-10-18

<!-- @ref:release-publication-2026-10-18; @tag:release -->
<!-- @link:doc-open-source-release; @link:script-artifact-checks; @link:test-artifact-checks. -->

## Scope and identity

The owner authorized publication preparation and use in the companion's next
build. The final source is `d7691dac652a81bddb16c9f91a9cf8ecd88b70db`, now
available on the repository's remote master branch. The GitHub 0.4.0 release
remains a **draft**. Source-support review and final publication acceptance
remain open; software checks do not certify every retained historical input
as an admitted public estimate.

Engine 0.4.0 / parameters v1.52 retain bundle SHA-256
`99173fbf23e75037da3fb9b4a9017a1e56909260ccb112f9902bc5ac86242153`.
Every runtime source and parameter byte is unchanged from the
[October 17 qualified model](release_qualification_2026-10-17_interval_fix.md).
That qualification and its sealed archive remain intact.

The fixture SHA-256 is now
`1c806cc6707e9c30d995fc420e145f5eb52c866cde82d0758ef4c5c5f030c055`.
Only generator/helper provenance changes in the saved fixtures; calculated
values remain unchanged. The paper source digest is
`f9583e8f9f80fb1d6f8c6cf24dfb4500b4cbe42d27ce8aed9b3e470c98f2b9c3`.
The rebuilt [PDF](../../paper/downstream.pdf) changes only the page-15 source
fingerprint in extracted text. That page was rendered and visually checked.
The readable methods HTML remains byte-identical.

## Cross-platform repair

Fresh Linux CI exposed byte-equality checks that passed on macOS. Reproduction
using the same read-only checkout in official Python 3.12 on Linux found 57
computed sensitivity fields differing by at most 16 floating-point steps (ULP).
Source identities and authored inputs matched. Subtraction amplified small
math-library differences; this was not a change in the coefficient or model.

The [freshness helper](../../scripts/artifact_checks.py) allows at most 32 ULP
for finite computed JSON floats, preserving stored full precision. It keeps
zero, types, structure, strings and source hashes exact. The calculator checks
authored HTML outside its embedded result JSON byte-for-byte. Regressions reject
larger numeric changes, changed metadata, malformed data and altered markup.
See the [development contract](../development.md#documentation-and-reference-checks).
The calculator's older direct test assertion now uses that same contract.

## Verification

- Linux fixture and calculator freshness checks pass against the macOS-generated artifacts.
- Focused artifact/consumer/calculator checks pass: 34 tests; final calculator/helper selection: 17 tests.
- `make check-docs` passes, including 19 checker regressions; Ruff and Vulture pass.
- The final local wheel, built from its source distribution, passes all eleven isolated command checks.
- [Final CI](https://github.com/xh1b/downstream/actions/runs/39102846907) passes on the exact final source: **1,474 tests**, 97.2% statement / 94.1% branch coverage, lint, Python 3.12/3.14 fast checks and all four Windows/Linux distribution jobs. The scheduled-only mutation job is intentionally skipped on pushes.

The draft contains the final wheel, source distribution, PDF, readable methods,
consumer fixtures and a manifest of their SHA-256 digests. It does not publish
a Python registry package or deploy the companion. Companion preparation and
live acceptance remain separate from this repository's software receipts.

The [machine receipt](release_publication_2026-10-18.json) records final identities,
asset hashes and the sealed local evidence archive. Its 15 evidence files verify;
archive SHA-256: `7ed6015b70fb1cee65f13ba3ee97ede0aa2f59e8f636353abb53b603673f6c0e`.
