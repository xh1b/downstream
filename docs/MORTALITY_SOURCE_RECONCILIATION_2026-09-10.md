# Mortality source reconciliation — 2026-09-10

## Decision

The production `source_profile` continues to use the directly reported,
mutually exclusive phase coefficients from Sullivan and von Wachter's NBER
Working Paper 13626 (2007), Table 5 column 3. The published QJE article is
the bibliographic version of record, but its Table 4 does **not** reproduce
that parameterization. It therefore cannot replace the current profile's
intervals without inventing covariance that neither table reports.

This is a source-reconciliation result, not evidence that the working-paper
specification is preferable or more transportable.

## What was checked

| Source | Table / specification | Dynamic mortality representation |
| --- | --- | --- |
| NBER WP 13626 (2007) | Table 5, column 3; born 1930–59, stable 1974–79 jobs, tenure at least six years, no work restriction | Direct coefficients for displacement, +1, +2–3, +4–5, and pooled +6+; each has its own SE. |
| QJE 124(3):1265–1306 (2009) | Table 4, column 1; same birth-cohort/tenure column family | A 16+ main effect plus additions for 1, 2–3, 4–5, 6–10, and 11–15 years. The phase total is a sum of coefficients. |

For example, the published column-1 point effects are 0.847 for year 1
(`0.131 + 0.716`), 0.690 for years 2–3 (`0.131 + 0.559`), 0.329 for years
4–5 (`0.131 + 0.198`), 0.188 for years 6–10 (`0.131 + 0.057`), 0.065 for
years 11–15 (`0.131 - 0.066`), and 0.131 for 16+. Its printed marginal SEs
are not enough to calculate SEs for those sums: their covariances are absent.

The working-paper profile instead reports 0.982, 0.685, 0.549, 0.240, and
0.127 directly for its five intervals. The former implementation mixed two
working-paper columns and shifted the final interval by a year. The current
profile no longer does either.

## Consequences for the model

- The default time mapping is explicit: displacement is follow-up year 1,
  so source offset +6 starts in follow-up year 7.
- Published Table 4 is retained as a source-consistency check, not a
  replacement uncertainty source. A future published-profile variant needs
  either the coefficient covariance matrix, author-provided joint draws, or
  a separately declared conservative interval method.
- Neither profile solves external validity: both describe high-tenure men in
  Pennsylvania mass layoffs in the early-1980s recession.

## Source locators

- Sullivan and von Wachter, *Mortality, Mass-Layoffs, and Career Outcomes*,
  NBER Working Paper 13626 (2007), Table 5:
  <https://www.nber.org/papers/w13626>
- Sullivan and von Wachter, *Job Displacement and Mortality: An Analysis
  Using Administrative Data*, *Quarterly Journal of Economics* 124(3),
  1265–1306 (2009), DOI 10.1162/qjec.2009.124.3.1265, Table 4.
