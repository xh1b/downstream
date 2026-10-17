# comments

## c-0668bf8f2e69

- At: 2026-10-17 20:40 HKT
- By: codex-doc-cleanup

Created in inbox.

## c-e867d41d87f2

- At: 2026-10-17 20:40 HKT
- By: codex-doc-cleanup

triage: inbox -> ready.

User authorized generator and navigation repairs as part of the refactor.

## c-831064a98d03

- At: 2026-10-17 20:40 HKT
- By: codex-doc-cleanup

claim: ready -> active.

## c-2f90e31ea7ac

- At: 2026-10-17 20:55 HKT
- By: codex-doc-cleanup

Moved-report builders and live navigation are verified

Commit 067c188 is not assumed; use the preceding implementation commit titled “docs: repair audit builders and migrated documentation paths” in Git history. Both report builders now default to docs/audits, emit correctly rebased links and pass their freshness tests. The evaluator and pool screen consume docs/research/SCENARIO_EVIDENCE_PROTOCOL.md. Consumer fixtures were regenerated for code/provenance identity. No old top-level report was recreated.

494 relative file/heading links pass across maintained/supporting docs and repository entry points. Stable refs pass (327 anchors, 1432 links); task validation has zero errors/warnings. Ruff, Vulture and evidence audit pass (0 audit errors/warnings). All four freshness checks pass: evidence classification, pool readiness, consumer fixtures and calculator. The 89-test report/consumer/paper/ref run and 231-test adapter/sensitivity/CLI/audit/evidence/paper/calculator/task run pass.

The evaluator executed into a new temporary output and retained its honest independent-event blockage (no matched external source). Saved historical evaluations and validation/sipp/MANIFEST.json were not rewritten. Protocol changes only repair navigation: original digest 6da5c238bb9466a9a591b0f9361fb815e22f92f430c0c117e64ab1c68878e94d at 26c4bb2:docs/SCENARIO_EVIDENCE_PROTOCOL.md; current digest 67767deb04df553d12aa9335175489d15e5a666fcf7c23b1688a25a52f289bd7 at docs/research/SCENARIO_EVIDENCE_PROTOCOL.md. Old receipts keep their original protocol hashes. Historical task comments and frozen evidence exemptions stay unchanged.
