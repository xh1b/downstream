# comments

## c-3f73965337e8

- At: 2026-10-15 17:33 HKT
- By: codex-repo-links

Created in inbox.

## c-c0fe89c8bcdd

- At: 2026-10-15 17:33 HKT
- By: codex-repo-links

triage: inbox -> ready.

Owner explicitly requested the existing-repository rollout. Checked the board: earlier tooling and instructions changes are in review; no active task covers applying them across existing sources.

## c-8b1c5082d095

- At: 2026-10-15 17:33 HKT
- By: codex-repo-links

claim: ready -> active.

## c-28310db0d70b

- At: 2026-10-15 17:56 HKT
- By: codex-repo-links

Repository-wide rollout is committed and verified

Main implementation: c2edfae (266 files). The final rebuilt PDF is committed separately. Navigation now covers all 54 engine Python modules, all 25 scripts, all 110 test files, all 40 pre-existing guides plus the new documentation map and paper guide, the manuscript and all six authored figure/style sources, calculator sources, build/configuration entry points and supporting root/provenance documents.

[Documentation map](../../../docs/README.md) groups the maintained guides, code, scripts and verification. [Paper guide](../../../docs/PAPER.md) connects methods and passages to their implementations and checks. Source comments carry subject tags and stable anchors. Meaningful reciprocal links join methods, implementation and representative verification; test comments identify their actual imported or focused contracts. Root README, contributor instructions and agent instructions lead to the new map.

Generated HTML/credits inherit navigation comments from their source generators. Inline calculator copies convert definitions to links so canonical anchors remain unique. The intentional reference-test fixtures remain exempt from scanning; their verification anchor and direct file link are documented in the testing guide. Original numerical inputs, bibliography records, imported Census code, archived results and retained task-card bodies/comments were preserved.

Verification:

- Affected task/reference, attribution, calculator/server and paper tests: 78 passed in 56.07 seconds. After final comment formatting/regeneration, the two generator freshness/navigation checks passed again.
- `python3 scripts/refcheck.py check`: 313 anchors, 1,331 links, 0 failures after the implementation commit.
- All newly introduced relative Markdown file links resolve (789 checked before the final focused-check substitutions; substituted test targets also exist).
- `python3 scripts/tasks.py validate`: 0 errors, 0 warnings; historical evidence exemptions unchanged.
- `.venv/bin/python -m ruff check src scripts paper/build_tables.py`, `.venv/bin/python -m vulture`, and `git diff --check`: passed.
- Executable AST comparison: 185 Python files are identical to their pre-rollout ASTs. Only three source generators and their two navigation checks change intentionally. All manuscript and figure edits are LaTeX comments; calculator JavaScript equations, rendering logic and CSS are unchanged.
- `make -C paper`: successful 20-page PDF. Extracted PDF text is identical to the prior paper except its rebuilt source-content digest. No reference/link/tag tokens appear in the PDF. The methods companion and calculator keep identical visible text; navigation metadata stays hidden. Calculator freshness check passes.

Work landed in scoped local commits on master. Unrelated concurrent work was left intact. This is navigation and documentation work, not new numerical or scientific validation.

## c-2fdc1a73226c

- At: 2026-10-15 17:57 HKT
- By: codex-repo-links

done: active -> review.

## c-ea7c306eb55b

- At: 2026-10-17 20:33 HKT
- By: codex-release-review

Follow-up coverage review and generated-navigation repair

The owner requested a review of all remaining tasks and whether navigation is complete. @task:2026-10-17-release-task-review records the full disposition. Confirmed file-level coverage: all 54 engine modules, 25 Python scripts, 42 Markdown guides, seven authored LaTeX sources and four authored calculator assets. Of 110 test files, test_refcheck.py is the documented deliberate-fixture exception; generated calculator/index.html links to unique authored anchors. Initial 898 and final 904 maintained Markdown file targets resolve.

Two reproducibility gaps remained: evidence-classification and pool-readiness guides contained manually added navigation that their source generators did not retain, and their source hashes were stale. b4a9480 moves those headers into generator output, refreshes the reports and adds committed-report freshness/navigation regressions. Consumer fixture source identities and the saved five-year household report were also refreshed with regressions. Current refcheck: 314 anchors, 1357 links, zero failures. Historical receipts/comments and the frozen legacy evidence ledger are preserved; this follow-up does not claim every raw data/archive file needs navigation metadata or confer scientific validation.

## c-6f84a5eb646c

- At: 2026-10-27 06:42 HKT
- By: codex-review

accept: review -> done.

Verified maintained-source navigation, documented fixture/generated-copy exceptions, generator-owned headers and later repair receipts. Current refs, file links and generated freshness checks pass.

Verification receipt: @task:2026-10-27-review-acceptance#c-845b5298b984. Accepted under the owner's request to verify and complete review tasks.
