# Repo-wide instructions

This repository is worked on by multiple agents concurrently in one shared
checkout. The rules below are imported from `xh1b/AGENTS.md` ("Git commits
(MUST follow)" section) on 2026-09-13 so every worker here follows the same
isolation discipline. They are MUST-level rules, not style preferences.

## Git commits under concurrent agents (MUST follow)

Use a one-line summary, then a blank line and optional Markdown details.
Task-board commits follow @link:task-command-reference.
`--only` keeps unrelated staged paths outside the commit and leaves them staged.
Path selection does not separate two agents' edits within the same file.
Inspect and coordinate shared-file edits before committing that path.

**Always `git add` + `git commit` after completing a logical unit of work.**
Commits stay isolated and history is append-only. Only ever add new commits
on `master`.

- **Stage only the specific files you changed** — never `git add -A`/`.`/`*`.
  List each file explicitly.
- **NEVER run a bare/pathless `git commit`. Every commit MUST end with a
  `-- <paths>` pathspec naming exactly the files you authored:**
  `git add -- <explicit paths> && git commit --only -m "<summary>" -- <same explicit paths>`.
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
- **Same-file collisions.** A path-scoped commit includes the worktree content
  of each selected file. Partial staging does not separate edits with `--only`.
  Coordinate with the other author before committing that path. Never discard
  their work to make a commit smaller.
- **Directory moves are commit-first.** Run `git mv`, then IMMEDIATELY commit
  the move as its own unit with explicit old+new pathspecs (`git add -- new-dir && git commit --only -m "move X" -- old-dir new-dir`) BEFORE starting reference sweeps or doc
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
- **Generated paper PDFs are rebuildable output.** Routine regeneration of
  `paper/downstream.pdf` from the current manuscript and build inputs is
  allowed even when that PDF already has uncommitted changes. Rebuilding it
  repeatedly during editing does not require confirmation or a backup.
  This exception applies to generated PDF output, not to manuscript sources
  or other authored inputs; preserve concurrent source edits as above.
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
  (`git add -- <file> && git commit --only -m "fix: ..." -- <file>`), or leave it and tell the user.
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

## Publication requires explicit confirmation

@ref:publication-approval

**Always ask the user for permission before publishing.** Preparing a release,
fixing release blockers, or discussing a version number does not authorize
publication. Complete local preparation and validation first, then present the
exact version, source commit, artifacts, checks and remaining limitations for
review and ask for explicit confirmation. Wait for the user's answer before
performing the approved publication action. A changed candidate or publication
scope requires renewed confirmation.

This applies to creating, publishing, replacing, editing or deleting remote
releases or release assets; pushing release tags; uploading packages to a
registry; deploying public sites or services; and triggering workflows or pushes
that publish automatically. Unpublishing an existing release also requires
confirmation. Approval for one publication does not authorize another. Local
builds, tests and commits may proceed under the repository rules above.

Release preparation and handoff: @link:doc-open-source-release.

## Task tracking

Use `tasks/` for all work tracking, following `tasks/AGENTS.md`.
Read the board with `python3 scripts/tasks.py list` or `next`; claim ready
work before starting it and record findings/receipts in the card thread.

## Documentation and connections

@ref:documentation-workflow

Start with [the documentation map](docs/readme.md) (@link:docs-index).
Make related documentation, implementation, tests, tasks and paper sources easy
to find from one another. Improve these connections as part of the work you touch.
Follow @link:reference-token-contract for token syntax and @link:task-workflow
for task ownership and receipts.

### Markdown documentation

- Code and admitted data define behavior. The paper explains the implementation,
  mathematics and scientific rationale; code should reference its relevant passages.
  The five maintained guides in `docs/` explain software use, integration and
  development. Use lowercase Markdown filenames throughout `docs/`, including
  indexes and supporting records. Extend the five guides before adding a top-level
  guide. Put dated reviews
  and diagnostics in `docs/audits/`, and supporting research/design plans in
  `docs/research/`. Reviews need clear scope and evidence, not the guides’
  editorial standard. Keep work status and follow-up in tasks.
- Keep root README and subsystem READMEs as concise entry points. Link new
  documents from the relevant README or existing guide so readers can discover
  them. Use descriptive relative Markdown links for files and normal links for
  external sources, datasets, citations and artifacts.
- Keep one authoritative explanation of each contract or decision. Link to it
  from related docs and code, and update it when behavior or assumptions change.
  Include purpose, scope, relevant limitations and reproducible evidence when
  they help the reader. Keep work status and discussion in task cards.
- Keep authored paper sources in `paper/` and generated artifacts with their
  established build workflow. Supporting methods and development notes belong
  in `docs/`; connect them to the paper and implementation.

### Stable refs, links and tags

- Define `@ref:<id>` once beside the section, module, API, algorithm, test or
  paper passage it identifies. Give it a meaningful, stable name. Cite it with
  `@link:<id>` from related locations; preserve IDs when moving their content.
- Link in both useful directions: a contract explains its implementation and
  verification; code and tests point back to the rationale, method or invariant.
  Give the document and implementation distinct anchor IDs. Add links at
  meaningful boundaries rather than repeating them on every function or line.
- Reuse `@tag:<name>` across task metadata, docs and source comments for shared
  topics and task types. Check `python3 scripts/tasks.py tags` and search the
  repository before adding a name. Tags group related material; refs identify
  a specific location. Use `@task:<id>` or a permanent comment reference for
  task decisions, provenance and receipts when that history is relevant.
- Keep explanations readable alongside the tokens. Use ordinary Markdown links
  for browsable files, sources and generated outputs as well as stable tokens
  for repository navigation. Avoid orphan documents, duplicate explanations,
  dangling links and parallel hand-maintained backlink lists.

For example, a Markdown method and its implementation can point to each other:

```markdown
## Example method

@ref:example-method

Implementation: @link:example-implementation. @tag:methods
```

```python
# @ref:example-implementation
# Method and assumptions: @link:example-method. @tag:methods
```

### Paper and rendered artifacts

Put navigation tokens in source comments when they should stay out of rendered
output. Use `%` comments in LaTeX, `<!-- ... -->` comments in Markdown or HTML,
and the language's comment syntax in code and other authored sources. Place the
comment beside the relevant passage so it moves with that passage. For example:

```tex
% @ref:example-paper-method
% Method: @link:example-method; implementation: @link:example-implementation.
% @tag:methods
```

```markdown
<!-- @ref:example-supporting-note -->
<!-- Related paper passage: @link:example-paper-method. @tag:methods -->
```

Commented tokens are still checked and searchable. Keep scientific citations,
reader-facing cross-references and attribution in the rendered paper; hidden
navigation metadata supplements those references. Generated files inherit their
links from authored sources and templates; make changes at the source.

### Checks when changing linked material

Update relevant documentation and connections with each logical code or method
change. Preserve existing task history. When retiring an anchor, update or
remove all its links in the same commit. Verify relative file links and examples,
then run these checks before review:

```sh
make check-docs
```

Run the relevant tests or artifact build when behavior or rendered content
changes. `refcheck` checks tracked text, including source comments, for anchor
uniqueness, missing link targets and token shape. Task validation resolves task
and comment references. Review still checks whether the explanation and evidence
match the implementation. Fenced examples above are placeholders, not live anchors.
