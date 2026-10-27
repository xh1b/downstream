# Downstream 0.4.1 candidate qualification

<!-- @tag:release -->

Qualified on October 27, 2026 HKT. Engine **0.4.1**, parameters **v1.54**,
source commit `1691850d70a27be5cfadf775c7a3edc9ce17b465`. This record captures the
candidate prepared for explicit publication confirmation under the
[publication rule](../../AGENTS.md#publication-requires-explicit-confirmation).
At qualification, the source had been pushed for CI and no release, tag or
release asset had been created or changed. Subsequent approved publication is
recorded below.

The [machine receipt](release_0_4_1.json) pins source/data trees, the bundle,
qualification logs, artifact hashes and the existing 0.4.0 release assets.
The prepared publication consists of eleven files: wheel, sdist, paper PDF,
methods HTML, source policy, consumer fixtures, uncertainty input/result,
source-contrast input/result and the release manifest.
Local staging is `build/release041-20261027/assets/`; proposed release notes are
`build/release041-20261027/release-notes.md`.

## Changes and qualification

The [individual source repair review](source_repairs_2026-10-27.md) documents all
sixteen decisions: six original estimates restored, seven typed corrections and
three unsupported original earnings relationships. There are 64 available rows;
ten legacy identifiers remain retired (seven superseded and three unsupported).
Corrected source contrasts preserve units, outcomes, currencies and follow-up
windows. The current README's stale blanket-withdrawal statement is corrected.
Version labels, calculator, consumer fixtures, saved uncertainty results and
methods artifacts are synchronized.

- Full local suite: **1,552 tests**, 725.50 seconds.
- Coverage: **96.7% lines / 93.8% branches**, above 95% / 90% gates.
- Twelve isolated-wheel CLI checks pass, including uncertainty and source contrasts.
- All eight required checks in the exact-source [CI quality run](https://github.com/xh1b/downstream/actions/runs/40478624183)
  pass: lint, Python 3.12/3.14 fast tests, coverage and all four Linux/Windows
  distribution combinations. A scheduled run at the same commit superseded
  the initial push run. Its mutation/benchmark job is outside these eight
  release checks; its actual status is preserved in the machine receipt.
- Audit: zero errors/warnings. Ruff, vulture, documentation checks and diff checks pass.
- All 48 point/range endpoints in the published 0.4.0 consumer fixtures are unchanged.
- Paper: 21 pages; full overview, custody discussion and corrected parameter table
  visually reviewed. No overfull boxes; one underfull line warning has no visible overflow.

## Remaining work and publication scope

Reviewed all inbox/ready/review cards and the active handoff. Remaining work
requires independent source estimates, expanded eligibility, matched event data,
target-cohort evidence, mortality covariance, SIPP pooling/design uncertainty,
monthly/resource models, human comprehension/accessibility checks or owner
decisions on headline streams. None is an additional small implementation fix
required for this patch. Completed subsets do not close the broader research.
Task review: @task:2026-10-27-prepare-041#c-3b28d9259e3c.

Parental divorce to child earnings, family size to child earnings and
fourth-generation earnings-gap propagation remain unsupported. Their original
records are retained; unrelated estimates and zeros are not substitutes.
Corrected contrasts remain ineligible for public headlines or arbitrary causal
aggregation. Transport/dependence cases are declared sensitivity assumptions,
not empirically calibrated probabilities or independent causal validation.

The proposed action is a new stable GitHub **v0.4.1** release at the exact source
above, marked latest, with the eleven qualified assets. Existing **v0.4.0**
tags/assets are preserved. PyPI uploads, companion repinning, production caches
and website deployment are outside this publication. The companion source holds
and independent-validation/public-experience requirements remain separate.

Preparation task: @task:2026-10-27-prepare-041. Historical publication:
[0.4.0 receipt](release_0_4.md).

## Approved publication

After reviewing this candidate, the owner explicitly confirmed publication.
[Downstream 0.4.1](https://github.com/xh1b/downstream/releases/tag/v0.4.1)
was published on October 27, 2026 HKT as the latest stable release, at the exact
qualified source above. The [publication receipt](release_publication_0_4_1_2026-10-27.json)
records the release ID, tag commit and all eleven uploaded asset identities,
sizes and SHA-256 digests. Each matches the sealed local candidate.
The 0.4.0 release body, metadata and nine asset identities/digests are unchanged.
Companion repinning, production cache updates and deployment were not performed.

Publication task: @task:2026-10-27-publish-041.
