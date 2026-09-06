# Parameter set changelog

Semantics: a new parameter-set version is REQUIRED whenever a value,
band, tier, or sampling methodology changes. Old versions stay
queryable in git; published outputs stamp the version they used.

## v1.2 — uncertainty methodology upgrade (2026-09-06)

- Monte Carlo switched from IID-uniform to **Latin Hypercube
  Sampling** (McKay, Beckman & Conover 1979).
- Positive ratio parameters (rate ratios, odds ratios, level ratios)
  now sample in **log space** by default — linear sampling of a ratio
  is biased toward the top of its band.
- **Rank-correlation induction** (Iman & Conover 1982) added; the
  declared correlation matrix ships EMPTY (params/correlations.csv).
  Correlations enter only with a citation.
- New layers: Sobol global sensitivity (`sensitivity.py`), proper
  scoring rules (`scoring.py`), the explanation/rendering contract
  (`explanation.py`, `render.py`).
- No parameter VALUES changed in this version; every output range
  shifts because the sampler changed.

## v1.1 — anchor read (2026-09-06)

- `displacement->worker_earnings` band widened to [0.75, 0.85] per
  the Davis & von Wachter 2011 full-text synthesis (15-20% below
  controls at 20 years; cross-study spread rule, CITING.md §3.2).
- Mortality rows carry full-text confirmation (near-term up to +100%,
  1-1.5 life-years) and the bad-case scope caveat.
- `davis2011` evidence class `results`.

## v1.0 — engine (2026-09-06)

- First full parameter set: 13 cited rows across worker / children /
  family / community streams.
- Gap-space composition for IGE links (fixes the v0 level-product
  bug), Moretti level-ratio corrected, divorce parameter corrected to
  Rege, Telle & Votruba 2007 DP514 (+11%).
