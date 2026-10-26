# comments

## c-e68a4f22a7c3

- At: 2026-10-17 20:23 HKT
- By: codex-release-review

Created in inbox.

## c-f50e50b89de2

- At: 2026-10-17 20:23 HKT
- By: codex-release-review

triage: inbox -> ready.

Owner requested a complete remaining-task and navigation review for the next 0.4 release.

## c-d04250289f91

- At: 2026-10-17 20:23 HKT
- By: codex-release-review

claim: ready -> active.

## c-58acce20734e

- At: 2026-10-17 20:35 HKT
- By: codex-release-review

All 35 remaining tasks reviewed; bounded 0.4 fixes verified

The card contains an explicit, evidence-linked disposition for every one of the 35 pre-existing inbox/ready/review cards; a set-equality check against the live card inventory verified no omissions. No review card was self-accepted or canceled. Seven stale cards were reconciled in 7953802, preserving comments, historical migration context and the frozen legacy evidence ledger. Final candidate qualification is now ready. docs/RELEASE_0_4.md defines the bounded acceptance scope in b7915fd; research or public-experience requirements remain on their original cards.

Navigation is verified at maintained-file scope: 54 engine modules, 25 Python scripts, 42 Markdown guides, seven authored LaTeX files and four authored calculator files. The intentional test_refcheck.py fixture exemption and generated calculator anchor links are documented. Final checks: 314 anchors, 1357 links, zero failures; 904 maintained Markdown file targets, zero missing. Historical task comments and the 45 frozen evidence gaps across 30 legacy cards were preserved, not filled with invented receipts.

Confirmed fixes in b4a9480: both generated evidence/pool guide headers now come from their source generators, with current source hashes and freshness/navigation regressions; 56 stale consumer fixture file hashes and the collection identity refreshed with a committed-identity regression; five-year household result refreshed with summary/window fields and current paired precision/limitations, with a saved-example regression. Consumer fixture numerical results did not change. All four generator --check commands pass.

Verification: 393 targeted task/reference/calculator/server/household/consumer/source/admission/paper/sensitivity/mortality tests passed in 56.96 seconds. Ruff, Vulture, git diff --check and task validation pass. Evidence audit: zero errors and zero warnings. This is a focused review receipt, not a new full-suite, coverage or distribution qualification of a frozen release candidate.

make -C paper rebuilt the 20-page PDF successfully. Its manifest digest recomputes to d0020e87d8a8befb90e76ad52a79554120e606461fd594e42ec727a66bfcd2cd. Extracted text differs only in the source-digest prefix on page 14; that page was rendered and visually inspected. No LaTeX warnings, undefined references or overfull boxes; one existing underfull-box diagnostic remains. Rebuild/render receipts are in build/release-task-review-20261017/. No remote operation, publication, companion change or source-data acquisition occurred.

## c-618a361e2d90

- At: 2026-10-17 20:36 HKT
- By: codex-release-review

done: active -> review.

## c-3441c46df523

- At: 2026-10-17 22:03 HKT
- By: codex-release-finish

The selected simpler 0.4 follow-through is complete

@task:2026-10-17-calculator-accessibility, @task:2026-10-17-candidate-qualification and @task:2026-10-14-xh1b-handoff are now in review with implementation and verification receipts. The concurrent documentation-reliability unit is also committed and in review; its final test file was rechecked under the full candidate's coverage. Final source/data/test/build and artifact hashes still match the qualification receipt after the documentation/task commits.

The release parent has only owner release/publication acceptance left unchecked. Companion adapter/cache/render/deployment acceptance, actual assistive-technology/native-zoom/physical-device/participant testing and empirical research requirements retain their existing cards. No feature expansion or research claim was fabricated to close them.
