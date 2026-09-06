# Parameter set changelog

Semantics: a new parameter-set version is REQUIRED whenever a value,
band, tier, or sampling methodology changes. Old versions stay
queryable in git; published outputs stamp the version they used.

## v1.7 — all five baselines verified (2026-09-06)

- `youth_crime_participation` flipped pending -> **verified**:
  0.055948 arrests per person-year, US men 18-24, 2023 (OJJDP SBB
  arrest counts joined with Census population denominators, both via
  new keyless verbs `ojjdp-arrests-download` + `census-popest-download`;
  warehouse `ojjdp_arrests` 4,185 rows + `census_popest_agesex` 1,818
  rows). BRACKET CORRECTION documented: published brackets give 18-24,
  not the placeholder 16-24.
- **baselines.csv is now fully verified** — every count conversion the
  engine grows will land on cited absolute numbers.

## v1.6 — fourth baseline pinned (2026-09-06)

- `ipv_annual_incidence` flipped pending -> **verified**: 0.0027
  victimizations per person-year (BJS Criminal Victimization 2024
  bulletin, NCVS intimate-partner-violence rate 2.7 per 1,000 persons
  age 12+, 2024; warehouse `bjs_ncvs_victimization`, 10 rows via the
  new `bjs-ipv-download` verb). UNIT CORRECTION: the placeholder row
  declared a per-household rate; the pinned semantics follow the
  published per-person measure (documented in the row). No count
  conversion consumes it yet.
- One baseline remains pending: youth_crime_participation.

## v1.5 — third baseline pinned (2026-09-06)

- `divorce_5y_cumulative` flipped pending -> **verified**: 0.1045
  probability a first marriage ends within 5 years (Census P70-125
  Table 4, SIPP 2008 panel, 1995-1999 marriage cohort: 89.6/89.5
  percent of men's/women's first marriages reached the 5th anniversary;
  warehouse `census_marriage_survival`, 128 rows via the new
  `census-marriage-download` verb). No count conversion consumes it
  yet — the family-stream module stays a relative rate ratio until its
  absolute-count conversion is built.

## v1.4 — second baseline pinned (2026-09-06)

- `median_male_lifetime_earnings` flipped pending -> **verified**:
  2,591,418 usd_2024, US male median lifetime earnings (SSA Annual
  Statistical Supplement 2025 Table 4.B6, male 2023 medians by age,
  synthetic career ages 20-64 = 2,517,175 usd_2023, CPI-U-deflated to
  2024 dollars; warehouse `ssa_median_earnings`, 1,845 rows via the new
  `ssa-earnings-download` verb). Unlocks the child-earnings dollar
  conversion in `scenario.py`.
- Remaining pending baselines: divorce_5y_cumulative,
  ipv_annual_incidence, youth_crime_participation.
- No parameter bands or link values changed.

## v1.3 — first baseline pinned (2026-09-06)

- `all_cause_mortality_annual` flipped pending -> **verified**:
  0.004944 deaths per person-year, US prime-age men 45-54
  (CDC WONDER D76, Male 45-54 years, pooled 2015-2019 =
  514,314 / 104,024,440 = 494.4 per 100k; pulled via the new
  `wonder-mortality` warehouse verb, 528 rows 1999-2020).
  Unlocks the excess-deaths count conversion in `scenario.py`.
  The other four baselines stay pending (fail-loud gates hold).
- No parameter bands or link values changed.

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
