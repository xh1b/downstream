# downstream

A citation-calibrated microsimulation of the downstream consequences
of worker displacement. Fully open source.

Incorporates the findings of 81 peer-reviewed studies by 166
researchers (1979-2023); its parameters rest directly on 19 studies
by 43 research teams. The claim is computed from the bibliography —
see CREDITS.md and `downstream credits` — never asserted.

Every modeled effect traces to a published study. Every parameter
carries its citation, its evidence precision tier, and its population
scope. Missing inputs fail loudly. The model publishes its own misses.

- `SPEC.md` — the algorithm: what is computed, from what, with which citations
- `params/` — the parameter set (versioned), node units, baselines, references.bib
- `src/downstream/` — the DAG engine, typed ledger (level / gap / direct /
  rate / elasticity composition), modules, scenario aggregation, Monte
  Carlo, audit, validation
- `CREDITS.md` — the computed collective: every researcher, every study, every DOI
- `docs/CITING.md` — the binding citation and evidence-tier rules
- `docs/ATTRIBUTION.md` — how credit is given and kept exact
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
downstream sensitivity --ci 5   # ...with seed-replicate design noise
downstream knobs --action sweep --link 'earnings_shock->mortality_sustained' --values 1.15,1.17,1.20
downstream knobs --action voi --outcome grandchild   # which knob is worth pinning next
downstream infer --outcome grandchild    # exact moments + normal band (no seed)
downstream ensemble     # structural-variant spread (composition assumptions priced)
downstream infer --outcome grandchild --action closure   # do the 90% bands cover 90%?
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
