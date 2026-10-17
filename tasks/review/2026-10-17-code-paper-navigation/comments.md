# comments

## c-7edc3fe9cb89

- At: 2026-10-17 20:40 HKT
- By: codex-doc-cleanup

Created in inbox.

## c-679716352762

- At: 2026-10-17 20:40 HKT
- By: codex-doc-cleanup

triage: inbox -> ready.

User explicitly requested code-to-paper rationale links.

## c-b9bf0acae2e2

- At: 2026-10-17 20:40 HKT
- By: codex-doc-cleanup

claim: ready -> active.

## c-2695522f87e3

- At: 2026-10-17 20:55 HKT
- By: codex-doc-cleanup

Implementation now points to paper rationale and software contracts

Commit 612b658 updates all 54 engine module headers with specific paper rationale and software-contract refs. SPEC is explicitly secondary to code/data; it no longer claims to be the algorithm's ultimate authority. Tests and maintenance-script navigation lead to implemented methods instead of plans or historical reviews.

The paper now explains the existing receiving-share transforms and retransformation assumption, sharp additive-coefficient SE bounds with a Gram-vector proof, per-result removal experiments, and expectation-versus-quantile mixture rules. The semantic HTML companion includes those explanations. No numerical method or parameter changed: AST comparison of all 54 engine modules against 26c4bb2 differs only in migrated documentation path strings. Historical evaluation JSON and the SIPP source manifest are byte-identical.

make -C paper succeeds (21 pages); all pages were rendered and contact-sheet reviewed, with detailed inspection of added passages. No overfull boxes or undefined references/citations; one underfull line remains a typesetting diagnostic. Focused checks: 89 generator/consumer/paper/ref tests passed; 231 additional adapter/sensitivity/CLI/audit/evidence/paper/calculator/task tests passed. refcheck: 327 anchors, 1432 links, no failures. Scientific validation blockers remain unchanged.

## c-a7d3b3968391

- At: 2026-10-17 20:55 HKT
- By: codex-doc-cleanup

done: active -> review.

Code, paper and software navigation are implemented and verified.
