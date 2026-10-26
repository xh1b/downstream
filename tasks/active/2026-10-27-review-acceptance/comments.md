# comments

## c-4be5e3bae4a6

- At: 2026-10-27 06:36 HKT
- By: codex-review

Created in inbox.

## c-ffa3ae1668eb

- At: 2026-10-27 06:36 HKT
- By: codex-review

triage: inbox -> ready.

## c-c626dcf31b88

- At: 2026-10-27 06:36 HKT
- By: codex-review

claim: ready -> active.

## c-845b5298b984

- At: 2026-10-27 06:42 HKT
- By: codex-review

Verified 31 review cards against their acceptance criteria

Reviewed all 30 cards present at the start, plus the completed task-board cleanup that entered review during this pass. Read each card/thread and checked the linked implementation, tests, reports and retained qualification evidence. The owner explicitly requested acceptance after verification.

Current verification receipts:

- Python 3.12 full coverage run: **1,475 passed, 9 subtests passed**, 281.73 seconds. Measured statement/branch coverage **97.1% / 93.1%** passes the unchanged 95%/90% gates. Command: `.venv/bin/python -m coverage run --data-file=build/review-acceptance.coverage -m pytest -q`; JSON/gate output: `build/review-acceptance/coverage.json`.
- Final task regressions after the concurrent cleanup landed: **38 passed, 9 subtests passed**. `make check-docs`: refs pass (346 anchors/1480 links), board has zero errors/warnings, 49 documents/587 local links/36 executable examples pass, and **19 doccheck tests pass**.
- Ruff, Vulture, `uv lock --check`, `pip check`, evidence audit (zero errors/warnings) and `git diff --check` pass.
- Fresh offline isolated sdist-to-wheel build passes; all **11 installed-wheel command checks** pass. Build/install logs and distributions: `build/review-acceptance-build.log`, `build/review-acceptance-distribution.log`, `build/review-acceptance/dist/`. The offline isolated backend avoids changing the shared environment, which lacks setuptools.
- Reproduced the mortality analysis into `build/review-acceptance/mortality-persistence.json`: every numerical value equals the saved reference; only version/input-hash metadata differ. Counts are 28.75872890253379 and 20.52335161286078, paired difference 8.23537728967301.
- Independently verified the corrected October 17 qualification archive SHA `e82f05458cf49122b8de7fe894c691d9c464084dc5f443c25f7ef7f6f43d0a10` and all **146 archived evidence hashes**. Runtime/parameter bytes matched that archive before separate concurrent child-support work began. This acceptance uses the corrected candidate, not its superseded predecessor.
- Fresh companion checks: **12 database-free Python integration tests** pass using the companion scraper environment and its check wrapper; **17 TypeScript consumer/display tests** pass. Verified the bundle SHA remains `99173fbf23e75037da3fb9b4a9017a1e56909260ccb112f9902bc5ac86242153`.
- Historical release-review table has 35 unique task IDs and exactly matches the prior Git-tree inventory. Inspected calculator 640px focus/reflow and 390px mobile captures. All docs Markdown filenames are lowercase; the top level contains five guides and their index.

The first docs attempt overlapped the cleanup's deletion/link update; it passed after that unit committed. The full run collected before the separate @task:2026-10-14-child-heterogeneity source changes. Its uncommitted code/docs/tests/fixtures are preserved and excluded from these acceptance commits; this is not a new frozen-candidate release qualification. Companion live caches/deployment, owner release/publication, native zoom/screen-reader/device/participant work and empirical research gates remain on their existing cards. Historical task features intentionally superseded by the owner-requested cleanup are reviewed as delivered history, not requirements to restore obsolete exemption files.

Task-specific findings:

| Task | Verification and scope |
| --- | --- |
| @task:2026-10-14-audit-04-release | Inspected eight documented repairs, bounded primary-table scope, audit/source/precision regressions and retained build receipts. Current evidence audit has zero errors/warnings. Acceptance does not imply fresh re-extraction of all 67 parameter links. |
| @task:2026-10-14-child-present-values | Verified explicit age schedules, observed-age versus career projections, signed gains, fixed SSA shape, currency validation and zero-rate equivalence in valuation.py and its regression coverage. |
| @task:2026-10-14-kanban-markdown-port | Verified references, relationships, append-only comments, workflow transitions, dirty-card refusal, explicit-path commits and commit-first moves against current task tests and CLI. |
| @task:2026-10-14-mortality-persistence | Verified the shared-input source/null-persistence structures, separately labeled structural spread, shared-draw intervals and baseline/profile/custom-input regressions. Reproduced 28.7587289 versus 20.5233516 deaths. |
| @task:2026-10-14-mortality-persistence-analysis | Reran analyze_mortality_persistence.py to a separate output. Every numerical result equals the saved analysis; only parameter-version/input-hash metadata differ. Source/annual-OR versus Swedish HR distinctions and transport limits remain explicit. |
| @task:2026-10-14-result-sensitivity | Verified effect removals, endpoints, interactions, fixed/unavailable inputs, correlated variance attribution and scenario/entity/valuation/CLI delivery against implementation, saved reference and regression coverage. |
| @task:2026-10-14-sustained-mortality-alternative | Verified named no_sustained_excess alternative and unchanged source anchor. Implementation retains early phases and distinguishes source evidence, declared structure, null compatibility and incompatible estimands. |
| @task:2026-10-14-xh1b-handoff | Verified model-side handoff report, corrected bundle identity and links to the three companion operational tasks. Fresh local Python/TypeScript parity checks pass. Live cache, browser/deployment and owner publication acceptance remain separate. |
| @task:2026-10-14-xh1b-usage-plan | Reviewed dated inspection receipt and plan covering pin, exposure, worker, cache, presentation, missing metadata, priorities and minimum acceptance. This accepts the historical inspection/plan; it does not assert current deployed state. |
| @task:2026-10-15-calculator-app-server | Verified permanent calculator paths, narrow loopback HTTP server, GET/HEAD/path/CWD regressions, build/serve commands, retained browser receipt and mobile capture. |
| @task:2026-10-15-calculator-functional | Inspected pure math functions and focused DOM/render code, validation/receipt flow, native parity and immutability/invariant regressions. Retained browser checks and current generated calculator freshness agree. |
| @task:2026-10-15-dependabot-followup | Verified landed action/dependency updates and portable 12-significant-digit methods fingerprint regression. Current model arithmetic/export precision is preserved; documentation freshness and tool checks pass. |
| @task:2026-10-15-dependabot-updates | Verified original six-update landing and retained exact dependency/CI receipts in local history. Newer dependency versions intentionally supersede older floors; fresh package/tool/regression checks cover the current state. |
| @task:2026-10-15-linked-documentation-guidance | Verified root documentation policy, discoverable placement, reciprocal anchors/tags, hidden paper metadata examples and current navigation checks. |
| @task:2026-10-15-repository-reference-rollout | Verified maintained-source navigation, documented fixture/generated-copy exceptions, generator-owned headers and later repair receipts. Current refs, file links and generated freshness checks pass. |
| @task:2026-10-15-task-tags-refs-links | Verified canonical/legacy references, normalized tag operations, backlinks, uniqueness/resolution checks and isolated mutation regressions. Historical exemption machinery was intentionally superseded by the newly reviewed cleanup task. |
| @task:2026-10-15-task-tool-convenience | Verified stable-ID show, multiline messages, title-based commit messages, blocked reporting, dirty-card/staging isolation and commit-first moves. The delivered historical-exemption feature was intentionally superseded by the owner-requested cleanup. |
| @task:2026-10-17-calculator-accessibility | Reviewed retained keyboard/accessibility-tree evidence and 640/320px reflow results; visually inspected the 640px focus capture and mobile capture. Accessible-name/table/error regressions pass. Native zoom, screen-reader/device and participant testing remain on the parent. |
| @task:2026-10-17-candidate-qualification | Verified superseding corrected candidate b41ca50, sealed archive SHA and all 146 evidence-file hashes, source/build/test manifests, comparison scope and unavailable old validation disclosure. Fresh current tests/build checks supplement this dated fixed-candidate qualification; release/publication stays separate. |
| @task:2026-10-17-code-paper-navigation | Verified engine headers point to specific paper/software contracts and reviewed added methods explanations plus retained rendered-paper receipts. Current reference resolution and generated HTML checks pass. |
| @task:2026-10-17-consumer-interval-alias | Verified real shared-dictionary regression and detach-before-scaling implementation; sealed corrected qualification hashes verify. Fresh Python companion and TypeScript consumer/display tests pass with the corrected bundle identity. |
| @task:2026-10-17-doc-navigation-checks | Verified lowercase audit/research generator destinations, corrected live links and frozen historical provenance. Report/fixture/calculator/HTML freshness and maintained-file navigation checks pass. |
| @task:2026-10-17-doc-reliability | Verified concise README/SPEC, code-derived calling reference, executable successful/blocked/refused examples, errors/cache guidance and CI-wired docs gate. All 19 doccheck regressions and 36 examples pass. |
| @task:2026-10-17-documentation-consolidation | Verified five maintained guides plus index, separate audit/research collections, preserved contract anchors and completed child-task evidence. Current docs/reference/freshness checks pass. |
| @task:2026-10-17-lowercase-docs-tooling | Scanned all docs Markdown filenames: none have uppercase characters. Verified development tool/test/task/CI instructions and exact-case navigation/freshness checks. |
| @task:2026-10-17-release-task-review | Compared the 35 unique disposition-table task IDs with the pre-review Git-tree inventory: exact equality. Reviewed corrected artifact/navigation/task-scope receipts and verified current refs/freshness and sealed later qualification. |
| @task:2026-10-17-software-guides | Confirmed exactly five focused top-level software guides plus readme.md, authoritative transferred contract sections and separate discoverable audit/research indexes. Docs/reference checks pass. |
| @task:2026-10-18-fix-board-commit-format | Verified shared board formatter, tests and actual new board(action): title commits, with supplied Markdown bodies and no repeated action/task-ID paragraph. |
| @task:2026-10-18-merge-pr-10 | Verified PR head 955710f is an ancestor of local master through the retained merge. Current Hypothesis floor intentionally supersedes 6.169.3; fresh lock/environment/regression checks pass. |
| @task:2026-10-27-dependabot-updates | Inspected local application commits 38ac7b1/134e1e0, preserved Dependabot authorship/provenance, latex-action v4 and current dependency floors. uv lock --check, pip check, Ruff/Vulture and offline sdist/wheel installation checks pass. No workflow dispatch/remote integration is claimed. |
| @task:2026-10-27-task-board-cleanup | Reviewed removal of migration/exemption scaffolding, 45 added direct criterion links and preservation of prior card/comment history. Current uniform-evidence/dirty-card/workflow tests pass (38 plus 9 subtests); documentation gate passes. |
