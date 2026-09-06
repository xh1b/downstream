# downstream

A citation-calibrated microsimulation of the downstream consequences
of worker displacement. Fully open source.

Every modeled effect traces to a published study. Every parameter
carries its citation, its evidence precision tier, and its population
scope. Missing inputs fail loudly. The model publishes its own misses.

- `SPEC.md` — the algorithm: what is computed, from what, with which citations
- `params/` — the parameter set (versioned), node units, baselines, references.bib
- `src/downstream/` — the DAG engine, typed ledger (level / gap / direct /
  rate / elasticity composition), modules, scenario aggregation, Monte
  Carlo, audit, validation
- `docs/CITING.md` — the binding citation and evidence-tier rules
- `docs/QUEUED_EXTRACTIONS.md` — modeled links awaiting their number, with
  the exact extraction target named
- `docs/PRIOR_ATTEMPTS.md` — the four prior modeling traditions and what
  this model takes and refuses from each
- `paper/` — `make` builds `downstream.pdf` (methods paper)
- `tests/` — the compute checks (51; `pytest tests/`)

CLI:

```
downstream family        # the standard-family vignette, fully cited
downstream scenario --workers 1000
downstream explain --text   # a claim walked from headline to citations
downstream sensitivity      # Sobol: what drives the remaining range
downstream audit         # parameter/citation/DAG/unit checks
downstream validate      # V0 internal consistency + V1 retrodiction target
downstream citations     # coverage report
downstream simulate --links a,b --kinds direct,gap
```

Uncertainty methodology: Latin Hypercube Sampling, log-space sampling
for ratio parameters, optional declared rank correlation (empty until
citable), Sobol sensitivity, CRPS/coverage scoring for the validation
program. See `SPEC.md` §7-10 and `docs/MODEL_CARD.md`.

Companion project: xh1b.org, which applies the model to employer,
county, state, and family surfaces. This repo contains only the model,
the parameters, and the paper — no confidential material.
