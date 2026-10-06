# Open source release checklist

Repository files prepare the project for contribution and review. The owner
must separately configure hosting settings and publish the reviewed release.

## Before making the repository public

- Review tracked files and history for credentials, private records, restricted
  source material, and redistribution rights. MIT covers project code; imported
  studies and datasets retain their own terms. Review `docs/DATA_SOURCES.md`.
- Confirm the maintainer's contact route for conduct/security reports and enable
  GitHub private vulnerability reporting.
- Run the full checks in `CONTRIBUTING.md`, inspect the built distributions, and
  review the model card, citations, credits, and limitations.
- Confirm package/repository names and metadata before publishing to a registry.

## GitHub settings after publication

- Enable Actions with read-only default workflow permissions. Keep approval for
  first-time fork contributors; PR checks do not require secrets or write tokens.
- Add a ruleset for `master`: require a pull request and review, resolution of
  review conversations, and the lint, fast (3.12/3.14), coverage, distribution
  (all OS/Python matrix combinations), and model comparison `compare` checks.
  Select actual check names from a successful run. Require branches to be
  up to date and block force pushes and deletion. Configure owner bypass
  deliberately to accommodate the maintainer's shared-checkout commit workflow.
- Enable issues and Dependabot. Consider Discussions for research proposals
  that are not yet actionable changes.
- Test one fork PR, including the full comparison artifact and an installed
  package check. Hosted runner checks remain unverified until this first run.

GitHub documents [fork workflow permissions](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)
and [workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax).

## Each release

Update the engine version in both `pyproject.toml` and
`src/downstream/__init__.py` when engine behavior changes. Parameter versions
are separate: update `params/VERSION` and `params/CHANGELOG.md` for data changes.
Describe both versions in the release notes and include a comparison against
the previous reviewed release using identical calculation inputs.

Run `python -m build`; it creates an sdist and builds the wheel from that sdist.
Run `scripts/check_distribution.py` on the resulting wheel outside the checkout
through its isolated environment. Archive the tested files, parameter export,
raw calculation outputs, comparison report, and review notes. Publish only after
review. This repository does not automatically publish Python packages.

The existing `paper-v*` workflow publishes methods-paper releases independently.
It does not replace review of the engine, parameter set, or third-party data.
