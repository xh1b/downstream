"""Names vulture would otherwise flag, each with the reason it exists.

Whitelisting is a reviewed decision, not a suppress-all: every entry
carries its reason, and an entry should be deleted when its reason no
longer holds. The scan runs over src/ and scripts/ via the config in
pyproject.toml (`python -m vulture`); tests are excluded from the
dead-code gate because pytest and Hypothesis discover test names
reflectively, which a static scan cannot see.

This file is never executed — vulture only parses it.
"""

# stdlib callback: HTMLParser.feed invokes handle_data; there is no
# caller by name anywhere in the repo.
HTMLParser.handle_data

# Evidence-registry schema fields: load_corpus / load_findings admit the
# CSVs by reading these columns, and scripts/import_evidence_corpus.py
# writes them. They round-trip provenance for review, and removing them
# would weaken the admission contract (a missing column would pass
# silently). estimand is the declared estimand of a finding, consumed
# by reviewers during screening rather than by engine code.
EvidenceCorpus.import_status
EvidenceCorpus.local_filename
EvidenceCorpus.retrieval_status
EvidenceCorpus.screening_status
EvidenceFinding.estimand

# Documented public surface that is not reachable from the CLI:
# - verify_bundle: counterpart of export_bundle for RECEIVING a
#   published bundle; exercised by the bundle lifecycle state machine.
# - build_places: data-derivation pipeline run ad hoc
#   (docs/DATA_SOURCES.md, QUEUED_EXTRACTIONS #30).
# - beta_binomial_posterior: reviewed binomial-count posterior
#   (docs/REVIEW_2026-09-10.md), sibling of the wired
#   poisson_gamma_posterior.
# - load_corpus / load_findings: evidence registry admission loaders.
# - validate_rendered: rendered-output invariant checker (test oracle).
# - scoring functions: README documents CRPS/coverage scoring of
#   forecasts; validate.run uses the sample-level half of the module,
#   the point/table helpers are the reviewer-facing half.
verify_bundle
build_places
beta_binomial_posterior
load_corpus
load_findings
validate_rendered
coverage
calibration_table
crps_of_point

# SPEC'd outcome branches that are caller-invoked by design: each needs
# an explicit exposure input (a SchoolExposure, a wage move, a child
# count) rather than a DAG producer, and outputs report them side by
# side with the displacement path instead of composing it.
school_spending_child_earnings
youth_crime_delta
family_size_penalty

# Back-compat wrapper for the original v0 surface (commented as such in
# vignette.py).
standard_family_daughter

# The declared variant roster: surfaced through run_ensemble's output
# keys and pinned by tests, not read by name in engine code.
VARIANT_IDS

# Name of the second unrolled IGE row (grandchild->greatgrandchild):
# kept as a public alias for the unrolled copy of the ige_earnings
# relationship; consumed by the transmission tests that pin the
# row-level drift guard.
GREATGRANDCHILD

# Public single-parameter override for caller-specified experiments;
# sampling uses bulk materialization, while counterfactual and sabotage
# tests exercise this API to alter a point without changing its band.
ParameterSet.with_param
