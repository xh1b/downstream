
## v1.19 — closure-selection ensemble variant (2026-09-08)

- No parameter VALUES changed. The V2 item queued at v1.13 landed:
  `closure_selection_contrast` joins the structural-variant ensemble
  (variants.py). It sets the direct child anchor (oreopoulos2008, a
  firm-closure design) aside and stands the children line on the JLS
  father-shock path composed through the SAME cited IGE band — the
  design contrast Hilger 2016 fn31 forces. Full fn31 text read from
  the published copy: Hilger's closure-DD is wrong-signed and not
  significant (his Table 4), which he reads as assortative matching of
  workers and firms on unobservables correlated with children's
  outcomes; fn31 names Oreopoulos, Page & Stevens (2005, 2008) as
  "the most directly related example" of closure designs yielding
  "surprisingly large estimates" against cross-sectional benchmarks.
- Variant state: child gap 0.89 [0.85, 0.94] vs baseline 0.9076
  [0.844, 0.976]; grandchild 0.9395 [0.91, 0.976]. The composed band
  sits INSIDE the direct band (reconciliation within the evidence).
  Direction pinned: dropping the closure anchor moves the modeled
  child loss UP — the critique does not imply smaller losses under
  current evidence. Ensemble spread: child [0.8376, 0.9076],
  grandchild [0.9107, 0.9623].

## v1.18 — Thornton 1980 cross-check notes (2026-09-08)

- No parameter VALUES changed; no new row. Thornton 1980 (Population
  and Environment 3(1):51-72, DOI 10.1007/bf01253070, Crossref-verified;
  full text read, page-1 title confirmed) landed as CROSS-CHECK NOTES
  on the male_earnings->marital_fertility row, per the Behrman &
  Taubman precedent: PSID two-generation OLS is observational, and
  CITING §1 allows only quasi-experimental designs to set points.
- Findings recorded on the row: ACTUAL parental family size transmits
  near-null (siblings-of-husband -> total expected fertility: zero-
  order .070, standardized .058 with education controls, ns; parity
  sign-inconsistent across 1972/1974); IDEAL family size (preferences)
  transmits strongly (.282* zero-order, .237* controlled; text
  unstandardized: +1 parental ideal child -> child ideal +0.15,
  expected +0.08); parental economic status correlates negatively
  with child parity, attenuated by education controls.
- This note is the recorded reason the model carries NO cross-
  generation fertility multiplier.

## v1.17 — spillover wired into V1 (2026-09-08)

- No parameter VALUES changed. The v1.12 spillover row
  (import_shock->non_displaced_wage_spillover, adh2013) is now COMPOSED
  into the V1 panel earnings row (validate.v1_panel), the open wiring
  left by v1.12. Four tercile rows now publish:
  - direct-only p25 row RETAINED unchanged (miss −$73.59 [−91.99, −55.19]
    vs measured −$352.73) — misses publish, not overwritten;
  - composed row (direct + spillover, applied to the non-displaced
    share, exact exp conversion): −$165.31 [−237.03, −93.24] — closes
    32.9% of the point-gap, measured still outside the band (residual
    undershoot published);
  - new aggregate cross-check: implied TOTAL male wage response
    −1.408 [−2.019, −0.794] log pts per $1k/worker vs ADH 2013 T6 col 2
    −0.892 (SE 0.294) — model point inside the measured CI AND measured
    inside the model band. The residual p25 undershoot is therefore
    distributional (bottom-quartile concentration), not aggregate.
- Spillover units need no pp conversion: the coefficient is per
  $1k/worker, the panel exposure's native unit.

## v1.10 (2026-09-07)
- NEW displacement->infant_birth_weight (EXACT, lindo2011): queue #13 landed.
  Level multiplier 0.954 [0.912, 0.998] from Table 2 col 3 (log birth weight
  -0.047, SE 0.023, mother fixed effects; read via IZA DP 5213). Bib entry
  CORRECTED: it previously cited Lindo's unemployment-insurance paper (JHE
  30:1120-1131) instead of Parental Job Loss and Infant Health (JHE 30:869-879).

## v1.9 (2026-09-07)
- Sullivan & von Wachter 2009 mortality rows pinned from the tables (queue #6 /
  plan #4 head): full text read from the NBER WP version (w13626; tables of the
  QJE article). Table 5 col 2 (born 1930-59 main sample): sustained (year 6+)
  log-odds 0.127 (SE 0.048) -> OR 1.135 [1.033, 1.247]; peak (displacement
  year) log-odds 0.983 (SE 0.119) -> OR 2.672 [2.116, 3.374]. Both rows now
  tier EXACT. The table-fitted bands are WIDER than the prior abstract-derived
  ones (honest widening per CITING 3); the peak point is materially higher
  (the immediate spike at low baseline hazard). OR~RR conversion declared.
  V1 effect: the mortality model band widens so the measured ADH differential
  now sits INSIDE the band (evidence-driven verdict flip, documented); the
  point still overshoots.

## v1.8 (2026-09-07)
- NEW wage_ratio->household_ipv (EXACT-results, aizer2010): elasticity of ln(IPV)
  w.r.t. female/male wage ratio, -0.813 [CI -1.45, -0.18], AER Table 2 col 3 read
  from full text. First producer for household_ipv (queue #3 landed). Node
  wage_ratio added. Sign recorded honestly: male displacement lowers IPV against
  women via the relative-wage channel; daughter-chain composition deliberately
  deferred (needs incidence weights).
- autor2019 bib corrected (was miscited as AEA P&P 109; actually AER: Insights
  1(2):161-178) and upgraded to fulltext; Tables 4-8 transcribed to
  validation/adh2019_measured_coefficients.csv (11 V1 targets).
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
