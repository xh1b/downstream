# comments

## c-f15525ff81a2

- At: 2026-10-15 18:43 HKT
- By: codex-dependabot

Created in inbox.

## c-9003b905633a

- At: 2026-10-15 18:43 HKT
- By: codex-dependabot

triage: inbox -> ready.

## c-3a0d95a89fca

- At: 2026-10-15 18:43 HKT
- By: codex-dependabot

claim: ready -> active.

## c-760fd6b0d67f

- At: 2026-10-15 18:50 HKT
- By: codex-dependabot

Applied PRs 7–9 and repaired the shared CI failure

Fetched [PR #7](https://github.com/xh1b/downstream/pull/7) at 4ef6f346, [PR #8](https://github.com/xh1b/downstream/pull/8) at 076d8d2a, and [PR #9](https://github.com/xh1b/downstream/pull/9) at 39c0d3c3. Commit 1917007 applies upload-artifact v7, download-artifact v8, Hypothesis >=6.169.0 and Ruff >=0.17.0. All changes are local on master.

All three PRs failed test_semantic_methods_companion_is_current. [The failing job](https://github.com/xh1b/downstream/actions/runs/38721621928/job/116377307242) showed only the footer result hash differed. Downloaded model-after artifact 11967125425 from comparison run 38721745537 and compared its scenario-cohort output with the identical local CLI invocation. Exactly five sensitivity floats differed, at roughly 1e-14. Substituting those Linux values into the local reference calculation reproduced the CI raw SHA b2592cbd… exactly, versus local 85d50f3f…. Hash seeds 0–3 produced the same local SHA.

The repair normalizes only result-fingerprint floats to 12 significant digits and canonicalizes signed zero. The exact input hash, model arithmetic, exported JSON and rendered numerical content retain their precision. docs/PAPER.md documents the fingerprint scope; the new regression uses actual platform values and detects material result and input-provenance changes. Regenerated docs/methods.html differs only in its footer result-fingerprint label and digest. The reconstructed Linux reference and macOS reference now generate byte-identical full HTML.

Installed Hypothesis 6.169.4 and Ruff 0.17.0, matching the dependency versions resolved by CI. The CI fast suite plus all paper tests passes on Python 3.14.7 (154 passed in 32.86s) and Python 3.12.14 (154 passed in 35.23s). Ruff, Vulture, refcheck (314 anchors, 1335 links, zero failures), task validation and git diff --check pass. No remote writes or push were performed.
