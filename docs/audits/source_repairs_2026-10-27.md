# Individual source-input repair — October 27, 2026

<!-- @ref:doc-source-input-repair; @tag:evidence -->

This corrects the blanket withdrawal in parameters v1.53. Parameters **v1.54**
restore six original estimates and add seven corrected typed replacements. Three
original relationships remain unsupported by their cited studies. All sixteen
have individual dispositions in the [authoritative source policy](../../params/source_support.json).
The [machine receipt](source_repairs_2026-10-27.json) records source artifacts,
table locators, numerical extraction, identities and qualification.

Contracts: [source custody](../evidence.md#source-withdrawals-and-retained-records) and
[corrected source contrasts](../integration.md#corrected-source-contrasts).
Implementation: [adapter](../../src/downstream/source_contrasts.py),
[regression checks](../../tests/test_source_repairs.py).

## All sixteen dispositions

| Original input | Decision | Evidence / correction |
| --- | --- | --- |
| `displacement->college_enrollment` | Restored original | Table 3 confirms −0.432pp (SE .094) and 40.66% pre-event mean. [Primary source](https://doi.org/10.1257/app.20150295) |
| `displacement->parental_income_shortrun` | Restored original | Table 3 confirms −$8,138.09 (SE 219.53) and $59,832 pre-event mean. [Primary source](https://doi.org/10.1257/app.20150295) |
| `eitc_exposure->adult_earnings_early` | Restored original | Table 2 col.6 confirms $564 (SE 244.9), maximum potential EITC eligibility in 2013 dollars. [Primary source](https://doi.org/10.1086/697477) |
| `household_ipv->child_internalizing_sd` | Restored original | Reported d=.48, CI .39–.57; exposure association, not intervention effect. [Primary source](https://doi.org/10.1016/j.avb.2008.02.005) |
| `household_ipv->child_externalizing_sd` | Restored original | Reported d=.47, CI .38–.56; heterogeneous exposure association. [Primary source](https://doi.org/10.1016/j.avb.2008.02.005) |
| `unemployment_status->mental_health_sd` | Restored original | Table 1 outlier-excluded d=.51, CI .47–.54; cross-sectional association. [Primary source](https://doi.org/10.1016/j.jvb.2009.01.001) |
| `unemployment_rate->property_crime` | Corrected replacement | Semi-log b=5.018 per unemployment fraction: .05018 log points per unemployment percentage point; exact percent conversion uses expm1. [Primary source](https://doi.org/10.1086/320275) |
| `wage_ratio->household_ipv` | Corrected replacement | −.813 (SE .317) per absolute female/male wage-ratio change, output log female assault hospitalizations. [Primary source](https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/PMC4123456/unicode) |
| `import_shock->gop_win_probability` | Corrected replacement | 24.08pp (SE 12.07) per import-penetration percentage point, not USD1000/worker. [Primary source](https://economics.mit.edu/sites/default/files/publications/Autor%20et%20al.%20-%202020%20-%20Importing%20Political%20Polariza.pdf) |
| `import_shock->radical_right_vote_share` | Corrected replacement | 13.2pp (SE 5.1) per real-2006-EUR1000/worker two-year import shock; no dollar or persistence substitution. [Primary source](https://doi.org/10.1111/ajps.12358) |
| `eviction_order->eviction_earnings_response` | Corrected replacement | −613 (SE 248) scaled by matching quarters-5–8 non-evicted mean 4254, not year-1 mean 4300. [Primary source](https://economics.yale.edu/sites/default/files/2023-09/qjad042.pdf) |
| `displacement_event->exam_noncompletion_hazard` | Corrected replacement | .54pp (SE .27pp) probability difference; regression constant .0785 is not a control mean or hazard denominator. [Primary source](https://docs.iza.org/dp16367.pdf) |
| `ipv_exposure->daughter_violence_odds` | Corrected replacement | Table 3 adjusted OR 2.68 [1.49,4.82] for pooled adult victimization; not a daughters-only effect. [Primary source](https://www.apa.org/pubs/journals/releases/ccp-714741.pdf) |
| `divorce->child_earnings` | Remains unsupported | Gruber estimates unilateral-divorce-law exposure, not the earnings effect of an individual parental divorce. [Primary source](https://www.nber.org/papers/w7968) |
| `family_size->child_earnings` | Remains unsupported | Black studies schooling and birth order; the paper does not identify a .98 earnings multiplier. [Primary source](https://www.nber.org/system/files/working_papers/w10720/w10720.pdf) |
| `grandchild_earnings->greatgrandchild_earnings` | Remains unsupported | Lindahl observes earnings for three generations, education for four; no identified .55 fourth-generation earnings-gap rule. [Primary source](https://docs.iza.org/dp6463.pdf) |

The seven corrected identifiers are separate from their retired aliases.
Use the machine policy for exact identifiers, nodes, units, coefficients and
bands. The adapter refuses unit substitutions, changed reviewed coefficients,
nonfinite doses, impossible percentage-point changes and population-count
scaling of fixed study contrasts. The pooled adult violence result does not
fill the daughters-only branch; no new aggregate or intergenerational claim
is admitted.

## Custody and verification

All 67 original CSV records remain byte-for-byte in the first 82,447 bytes
(SHA-256 `f6ce70a100042189691eb10291c9ead48655cbf37dc49d49c4ac2ce4a3a468d6`).
Seven corrected rows are appended. Exports contain 64 available parameters and
ten retired aliases: seven superseded and three unsupported. All sixteen old
withdrawals remain in historical policy metadata; source repair provenance is
included in schema-3 exports.

The full suite passes **1,552 tests plus 9 subtests**. Coverage is **96.7% lines /
93.8% branches**, above unchanged 95%/90% gates. The source-built wheel passes
**twelve isolated CLI checks**, including the new adapter. Audit errors/warnings
are zero; Ruff, Vulture, documentation links/examples and generator freshness
checks pass. The 21-page methods paper was rebuilt and visually inspected, with
no LaTeX warnings or overfull boxes. Commands and machine artifact/log identities
are recorded in the receipt. The initial code/data unit is `6d8d92f`; `d9bbb05` adds reviewed active notes,
keeps original notes explicit and handles oversized JSON integer doses. The
final full-suite and distribution qualification uses that corrected source/data
tree. The installed-wheel check was extended separately in `99bd37e`.

Reproduce:

```sh
python -m pytest -q
python scripts/check_distribution.py path/to/downstream-0.4.0-py3-none-any.whl
make check-docs
downstream source-contrast --input validation/source_contrast_input.json
```

## Release and scientific limits

The correction is committed locally on `master`. The already-published v0.4.0
tag and assets remain unchanged; this work has not published a patch release or
repinned/deployed the companion. The source policy identifies working-paper and
accepted-manuscript versions explicitly. For Ehrensaft, the source PDF was read
through browsing, but local download returned HTML: the stored hash covers the
numeric table extraction, not original PDF bytes. Verification does not supply
target transport, new population admission, independent causal validation or
an empirically calibrated transport/dependence distribution.

The three unsupported earnings relationships require new evidence or an
explicitly separate, uncalibrated structural assumption. They cannot be restored
as source-identified coefficients or silently replaced by zero. Work receipts:
@task:2026-10-27-repair-withdrawn-inputs.

The six restored rows expose the reviewed interpretation through `by_link` and
active snapshot exports; `retained_by_link` preserves the original notes. For
example, EITC eligibility is not automatically an ordinary income change. New
evidence for the three unsupported relationships is tracked in
@task:2026-10-27-unsupported-earnings-bridges.
