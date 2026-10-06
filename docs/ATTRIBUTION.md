# ATTRIBUTION — how this model credits research

The model's authority is borrowed and the loans are itemized. These
rules keep the credit exact.

## 1. The computed claim

Public surfaces state the collective ONLY through the generated
sentences (`downstream credits`):

See the generated attribution in [CREDITS.md](../CREDITS.md) and the README. `downstream credits --write` regenerates both from `params/references.bib`.

Counts describe bibliography sources and named author records, including organizations. Full names distinguish unrelated people sharing a surname; a small reviewed alias map reconciles abbreviated names. These are not independently verified researcher or research-team counts, and the bibliography includes working papers, books, government sources and methods material as well as journal articles. Never label all entries as peer-reviewed studies.

## 2. Citation etiquette

- Every modeled number travels with its citations — in the same
  sentence, at the same size (RENDERING.md layer 2).
- Findings are attributed to their authors, never absorbed: "Jacobson,
  LaLonde & Sullivan's finding that displaced workers lose ~20% of
  long-run earnings", never "our finding".
- Methodology choices cite their inventors too (LHS: McKay, Beckman &
  Conover 1979; Sobol: Saltelli 2002; CRPS: Gneiting & Raftery 2007,
  Hersbach 2000). We did not invent the craft and do not imply it.
- The refusal rows cite the refuting literature (Ousey & Kubrin 2018).

## 3. DOI policy

- `scripts/fetch_dois.py` queries Crossref (polite pool). Auto-apply
  only at certain title match (>=0.92); a relaxed pass applies at
  >=0.85 with year + container agreement; everything else lands in
  `params/doi_review.json` for eyes, never in the bib.
- Working papers and books without DOIs stay without; absence is
  honest.

## 4. Known review items (as of 2026-09-06)

- 25 entries without DOIs sit in `params/doi_review.json` (books,
  working papers, government series, title ambiguities).
- RESOLVED 2026-09-07 (v1.14): the pair was NOT two copies of one
  paper. `kearney2020` is the real Pill study (REStat 102(2):341-355,
  kept). `kearney2020fracking` was a broken stub conflating the
  fracking title with a Pill subtitle - deleted, and replaced by the
  full record `kearney2018fracking` (REStat 100(4):678-690, DOI
  10.1162/rest_a_00739), which queue #7 landed from (NBER w23408).

## 5. Citing this model

Cite the methods paper, or cite the repository with the engine version, content hash and parameter-set version: "downstream model, parameter set v1.2,
xh1b/downstream (local)". Every exported number already stamps its
own version, seed, and sources — that stamp is the citation.
