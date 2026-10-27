---
title: Bound CI distribution retention and remove approved redundant artifacts
area: ci
priority: P2
assignee: github-security-20261026
blocked-by: []
---

Owner-approved GitHub storage cleanup and prevention

The owner approved the frozen 139-artifact proposal from /tmp/xh1b-github-security-20261027/downstream-storage-cleanup-proposal.json (SHA-256 dbf9e79b98931c89b15ef52f7165bfee2b74c496aaaf723f12800705189c6e1e), plus distribution retention from 14 days to 1 day. Preserve the newest distribution per platform/Python, all coverage/model-comparison evidence and every unselected artifact. Verify completed runs and exact metadata before deletion. No model, source-data or release-asset changes are authorized. The companion heavy-CI/publication hold remains separate.

- [x] Delete only the approved artifacts and verify retained artifacts. [cleanup receipt](@task:2026-10-27-ci-artifact-storage#c-d2a407f07399)
- [x] Commit and publish the single retention change after validation. [publication receipt](@task:2026-10-27-ci-artifact-storage#c-c8a95f1b2ed7)
- [x] Record actual remaining storage and hosted-verification limits. [verification receipt](@task:2026-10-27-ci-artifact-storage#c-d2a407f07399)
