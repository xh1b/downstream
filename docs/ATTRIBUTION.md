# ATTRIBUTION — how this model credits research

The model's authority is borrowed and the loans are itemized. These
rules keep the credit exact.

## 1. The computed claim

Public surfaces state the collective ONLY through the generated
sentences (`downstream credits`):

> This model incorporates the findings of 81 peer-reviewed studies by
> 166 researchers, 1979-2023. Its parameters rest directly on 19
> studies by 43 research teams. Every modeled number carries its
> sources with it; nothing here is a model-originated estimate of a
> scientific fact.

These numbers are computed from `params/references.bib` by
`downstream/credits.py` and regenerate `CREDITS.md`. Never round them
up, never paraphrase ("over 100 researchers" is forbidden when the
exact count is 166 — exact is more credible anyway).

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

When the paper exists: cite the paper. Until then, cite the repo with
the parameter-set version: "downstream model, parameter set v1.2,
xh1b/downstream (local)". Every exported number already stamps its
own version, seed, and sources — that stamp is the citation.
