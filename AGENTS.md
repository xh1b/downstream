# Repo-wide instructions

This repository is worked on by multiple agents concurrently in one shared
checkout. The rules below are imported from `xh1b/AGENTS.md` ("Git commits
(MUST follow)" section) on 2026-09-13 so every worker here follows the same
isolation discipline. They are MUST-level rules, not style preferences.

## Git commits under concurrent agents (MUST follow)

**Always `git add` + `git commit` after completing a logical unit of work.**
Commits stay isolated and history is append-only. Only ever add new commits
on `master`.

- **Stage only the specific files you changed** — never `git add -A`/`.`/`*`.
  List each file explicitly.
- **NEVER run a bare/pathless `git commit`. Every commit MUST end with a
  `-- <paths>` pathspec naming exactly the files you authored:**
  `git add file1 file2 && git commit -m "..." -- file1 file2`.
  A pathless commit publishes the WHOLE shared index, including anything any
  concurrent agent left staged. With a trailing pathspec, git commits ONLY
  worktree state under those paths — nothing anyone else left staged or
  unstaged elsewhere can ride along. Notes: brand-new untracked files still
  need `git add` first (a pathspec alone never picks them up);
  renamed/deleted/modified tracked files under the named paths are captured
  as-is; and if one of your named files also carries someone else's in-flight
  hunks, that same-file collision is NOT solvable by scoping — surface it and
  use the same-file rule below.
- **Run `git add` and `git commit` in a single command (chained with `&&`).**
  The chain shrinks the race window in the shared index. Chaining alone does
  not isolate you: a neighbor's pathless commit can still sweep your
  just-staged items between your commands' steps.
- **Same-file collisions.** If you and another agent edited the SAME file, a
  `-- <paths>` commit would fold their hunks into yours. Publish only your
  lines: stage the file, then `git apply --cached -R` a patch of exactly the
  foreign hunks so the commit carries only your change, and leave their hunks
  in the worktree untouched. Never resolve a collision by picking "your"
  version and discarding theirs.
- **Directory moves are commit-first.** Run `git mv`, then IMMEDIATELY commit
  the move as its own unit with explicit old+new pathspecs (`git commit -m
  "move X" -- old-dir new-dir`) BEFORE starting reference sweeps or doc
  edits. Mass staged renames parked in the shared index are exactly what
  past commit-sweep incidents grabbed.
- **Check `git status` before staging** to see what you changed and avoid
  staging another agent's in-progress work.
- **Commit after each logical unit**, not at the end of a session.
- **Concise commit messages** matching repo style (`fix:`, `feat:`, `docs:`,
  `test:`, `chore:`; parameter-data landings use the `vX.Y:` convention).
- **Never commit secrets** (.env, API keys, credentials).
- **Never use `git stash` to debug or verify.** It can lose uncommitted work
  and collide with concurrent agents. To check whether a failure is
  pre-existing, inspect the code path, check `git log`/`git diff`, or run the
  test against a clean checkout in a separate directory.
- **NEVER discard, revert, or overwrite another agent's uncommitted work on a
  shared file.** If `git diff` / `git status` shows changes on a file you
  didn't touch (or changes beyond what you edited), that is almost certainly
  another agent's in-progress work — do NOT `git checkout HEAD -- <file>`,
  `git restore`, `git stash`, or any operation that discards working-tree
  changes you didn't make. If a file you edited also has someone else's
  changes (a concurrent edit collision), do NOT resolve it by picking "your"
  version and throwing away theirs. Instead: surface the collision to the
  user and ask how to proceed, or work around it by applying only your
  logical change as a targeted edit that preserves their work. The same rule
  applies to files that look "reformatted" or "noisy" — that reformatting may
  be another agent's intentional work. When in doubt, assume foreign changes
  are deliberate and leave them alone. Destroying a teammate's uncommitted
  work is one of the hardest mistakes to recover from in a multi-agent repo.
- **NEVER move, rename, or delete another agent's uncommitted files —
  including brand-new untracked files.** A script, parameter file, or doc
  another agent just created is their work in progress even though
  `git status` shows it only as `??`. You need the owner's express permission
  before you move, rename, delete, or rewrite it. Do not "replace" it with
  your own version either — even when it looks like a duplicate of yours. If
  a genuine collision blocks you, STOP and surface it to the owner instead of
  resolving it unilaterally. Defend your own work the same way: commit early
  in small units so nothing of yours sits long as invisible untracked output.
- **NEVER rewrite history — no `git commit --amend`, no `rebase`, no
  `git reset --hard` / `reset <commit>`, no reflog recovery.** In a
  multi-agent repo `HEAD` moves between your commit and your amend: another
  agent's commit can land in that window, and your amend then silently folds
  your changes into *their* commit (or theirs into yours), mislabeling both
  units and orphaning commits. Same class as the add/commit race above, but
  worse — it rewrites shared history. If a commit is wrong (bad message,
  missing file, stray line), make a **new** commit that corrects it
  (`git add <file> && commit -m "fix: ..."`), or leave it and tell the user.
  The only acceptable `reset` is `git reset HEAD <file>` to unstage; never
  reset commits. This rule has NO self-granted exception — not for your own
  minutes-old commits, not because they were never pushed, not because a
  `--keep` variant "loses nothing". If a landing went wrong, STOP and ask the
  owner; only they may direct a history move.
- **Commit directly to `master` — NEVER create feature branches.** No
  `fix/...`, `feat/...`, or any short-lived branch; no PRs; no
  `git checkout -b`. Parallel branches + PRs/merges cause divergent histories
  and merge collisions when agents commit concurrently. The ONLY exception is
  a long-lived, explicitly user-requested branch.
- **Before EVERY commit, verify `git branch --show-current` says `master`.**
  Another agent can switch the shared checkout to a stray branch between your
  edits and your commit — a commit made on a foreign branch lands on the
  wrong line of history and hides from every other agent. If the checkout is
  on a stray branch: do NOT commit there and do NOT delete the other agent's
  ref; commit your work after switching back to `master` (safe when the stray
  branch holds only commits — untracked and modified working-tree files
  travel with the checkout), and merge the stray branch's content back to
  `master` with `git merge --no-ff <branch>` so nothing is lost,
  appending-only.
- **NEVER create git worktrees or temp checkouts to land or rehearse work**
  (no `git worktree add`). Development is append-only on `master` in the main
  checkout; a side worktree's index is invisible to every other agent, so
  work built there hides the collisions the main checkout must face, and
  landing it back needs a second reconciliation. If another agent's
  staged/uncommitted work blocks a merge, wait with bounded retries for their
  commit to land (their cadence is minutes), then merge directly on `master`.
- **NEVER push or do any remote operation unless the user explicitly asks.**
  No `git push`/`fetch`/`pull`, no `gh pr create`/`repo`/`issue` mutations,
  no force-push, no `git push --tags` — nothing touching the remote. Local
  `git commit` is fine and expected; sharing with the remote is a separate,
  explicit decision each time. If unsure whether something counts as remote,
  treat it as remote and ask first.
