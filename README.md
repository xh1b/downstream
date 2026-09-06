# downstream

A citation-calibrated dynamic microsimulation of the downstream
consequences of worker displacement. Fully open source.

Every modeled effect traces to a published study. Every parameter
carries its citation, its evidence precision tier, and its population
scope. The model publishes its own misses.

- `params/` — the parameter set (versioned; every row cited)
- `src/downstream/` — the DAG engine, deterministic ledger, and
  Monte Carlo propagation
- `paper/` — `make` builds `downstream.pdf` (methods paper)
- `tests/` — the compute checks

Companion project: xh1b.org (private repo), which applies the model
to employer, county, state, and family surfaces. This repo contains
only the model, the parameters, and the paper — no confidential
material.
