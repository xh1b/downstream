# Remarriage-margin screen

<!-- @ref:doc-remarriage-margin-screen-0-4; @tag:family -->
<!--
Connections: @link:code-family; @link:code-admission; @link:doc-queued-extractions; @link:doc-citing; @link:docs-index; @link:test-remarriage-screen.
-->

Related: [Documentation map](../readme.md) · [queued extractions](../research/queued_extractions.md) · [citing](../evidence.md#citation-and-extraction-rules).
Implementation: [family](../../src/downstream/family.py), [admission](../../src/downstream/admission.py). Checks: [remarriage_screen](../../tests/test_remarriage_screen.py).

**Disposition: screen complete; no coefficient admitted.** The original task
names a candidate from the V1 divorce row but no specific table. We checked both
cited anchors, `rege2007` and `charles2004`. Neither identifies a displacement
effect on entry into a subsequent union. This is missing evidence for that link,
not evidence of a zero effect or a systematic literature review.

## What the sources measure

[Rege, Telle and Votruba, DP 514](https://www.ssb.no/a/publikasjoner/pdf/DP/dp514.pdf)
measures divorce by 2003 after plant closure exposure during 1995-2000.
Its preferred Table 2 Model 3 reports a signed probability difference **+0.00783**,
SE **0.00210**, with plant-clustered errors. That outcome is dissolution, not
remarriage. The text's remarriage mention is a book citation, not an estimated
transition. The checked source is the 2007 working paper, not a new published
extraction. Its sample and calendar restrictions are recorded in the receipt.

[Charles and Stephens, April 2002 author draft](https://sites.lsa.umich.edu/mstep/wp-content/uploads/sites/930/2021/06/divorce_final.pdf)
uses PSID marital histories and a pooled probit dissolution model. Appendix
Table 1's first specification includes these marital-history controls:

| Control | Signed probit coefficient | Reported robust SE |
| --- | ---: | ---: |
| Husband already in second marriage | +0.220 | 0.083 |
| Wife already in second marriage | +0.252 | 0.083 |

These predict next-year dissolution conditional on controls. They are neither
probability changes nor causal effects of displacement on remarriage. Footnote 9
distinguishes excluded same-pair reunions from different unique spouse pairs,
which the sample can include. It does not identify a union-formation hazard.
Data cover 1968-1993; dissolution follow-up begins in 1985. This is an author
draft, not fresh verification of the 2004 version of record.

## Admission decision

Under [CITING](../evidence.md#citation-and-extraction-rules), a new parameter needs an eligible design, the intended
estimand, compatible population/window and supported uncertainty. The available
numbers fail the remarriage estimand match. The marital-history coefficients also
fail causal identification for that target. A known signed coefficient and SE do
not resolve either failure.

Do not convert the probit coefficients with `exp`, call them odds ratios or use
them as percentage-point effects. Do not reverse the divorce coefficient, assume
all extra divorces create later marriages, or encode the unknown effect as zero.
No `params/`, source metadata tiers, default outputs or extraction tables changed.

To reopen, obtain a primary estimate for first subsequent union after dissolution.
It must define the eligible origin population, timing, marriage versus cohabitation,
same-pair reunion versus new partner, competing death/censoring, treatment contrast,
effect scale and uncertainty. Selection into divorce must be addressed before
interpreting a conditional post-divorce association as a displacement effect.

## Receipts and checks

[Structured screen](../../validation/remarriage_margin_screen_20261015.json) preserves
all signed adjacent estimates, their incompatible estimands, source versions,
population/windows, locators and immutable PDF hashes. The target estimate and its
uncertainty are `null`, separately from `effect_is_zero: false`.

No matching locally acquired source copy was located in the two repository roots;
primary SSB and author-hosted copies were acquired on 2026-10-15. PDF page 13 of
DP 514 and pages 13/42 of the author draft were rendered and visually inspected.
The source PDFs are not bundled by this change. Their hashes are:

- DP 514: `c429f80c3ea93cde98a6b6c161c1d928051e7cbf0b8ecaa58197631206fe3243`.
- Charles-Stephens draft: `b9c064029ab09939a1d036bea46ba697fbfdb8e6f7bc42165e113adfbb468632`.

```sh
.venv/bin/python -m pytest tests/test_remarriage_screen.py -q
.venv/bin/ruff check tests/test_remarriage_screen.py
```

The tests enforce the refusal boundary, distinct missing-versus-zero semantics,
signed transcription, effect-scale distinctions and source/version traceability.
They do not establish a new scientific effect or substitute for source review.
