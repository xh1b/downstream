# Literature Acquisition Plan

## Purpose

Build a broad, reproducible corpus of causal studies for the `downstream`
consequence graph. The aim is not a hand-picked collection of stories about
job loss. It is a continually expanding set of study-backed bridges between
life events, intermediate states, and later outcomes.

This plan acquires papers and their machine-readable receipts. It does not
automatically turn a paper into a parameter: extraction and the rules in
`docs/CITING.md` remain the gate for every numerical edge.

Acquisition priorities now follow
[LIFE_COURSE_RESEARCH_PLAN.md](LIFE_COURSE_RESEARCH_PLAN.md): source corrections,
baseline household dynamics, a five-year displacement contrast, and independent
evaluation precede long multigenerational chains. Track dataset documentation
and baseline-transition estimates separately from causal intervention studies.
The former cannot silently become causal edges.

## Acquisition rules

1. Prefer the version of record, its DOI, and a legal open-access copy.
2. Prefer peer-reviewed quasi-experimental studies, randomized experiments,
   administrative-data event studies, and rigorous meta-analyses.
3. Store a candidate even when it is null or contradicts a current edge.
4. Capture study population, treatment, comparison, outcome, time horizon,
   causal design, DOI, and open-access URL before full-text extraction.
5. Never use an abstract-only number as an `EXACT` parameter.
6. Prioritize evidence needed for the current scenario and its evaluation.
   Among otherwise comparable candidates, a compatible bridge can be more
   useful than an isolated endpoint; graph connectivity alone is not priority.

## Sources and retrieval order

1. Existing bibliography and its backward/forward citation graph.
2. NBER working-paper pages and PDFs for economics papers; these give stable
   DOIs and often legal full text.
3. PubMed / PubMed Central for health, developmental, and public-health work.
4. Crossref for DOI resolution; use the existing `scripts/fetch_dois.py` only
   to propose matches, never to silently accept ambiguous ones.
5. Author manuscripts, university repositories, RePEc, and journal open-access
   copies when the version of record is paywalled.
6. Systematic reviews only as discovery indexes; the graph edge must still be
   sourced to a qualifying study or a suitable meta-analysis.

## Corpus map

The corpus is organized by bridge demand rather than by advocacy topic.

| Region | High-value bridges |
|---|---|
| Economic security | work, earnings, unemployment, debt, credit, bankruptcy, benefits |
| Health | illness, disability, mental health, medical debt, work, mortality |
| Housing and place | eviction, foreclosure, moves, neighborhood exposure, school disruption |
| Family | partnership, divorce, bereavement, parenting, fertility, child resources |
| Childhood and education | prenatal conditions, birth outcomes, school experience, skills, adult outcomes |
| Crime and justice | victimization, offending, incarceration, employment, family spillovers |
| Environment and disasters | pollution, heat, disasters, displacement, migration, health, earnings |
| Protective interventions | income supports, health care, school finance, housing mobility, treatment |

## First corpus milestone: 100 qualifying papers

The initial batch below is a bootstrap, not a sufficient literature base. The
first corpus milestone is **100 qualifying papers**, each with a DOI or stable
retrieval URL, a legal full-text route where available, and enough
methodological information to be screened as a potential graph edge.

The target is deliberately balanced so the graph does not become a dense
job-loss narrative with sparse bridges elsewhere:

| Region | Initial target |
|---|---:|
| Economic security, work, debt, and benefits | 18 |
| Physical health, disability, and mortality | 15 |
| Housing, mobility, neighborhood, and place | 15 |
| Family, fertility, bereavement, and parenting | 15 |
| Childhood development, education, and adult outcomes | 15 |
| Crime, victimization, and incarceration | 12 |
| Mental health, substance use, environment, and disasters | 10 |
| **Total** | **100** |

This is a corpus-acquisition target, not a promise that all 100 become active
parameters. Some will be null findings, structural counterweights, context-only
evidence, or unsuitable for composition. Retaining those outcomes is part of
the model's scientific discipline.

## Acquisition status — 2026-09-09

The first acquisition milestone is complete: **100 distinct PDFs** are stored
outside the repository at
`/Users/jt/Downloads/downstream-literature-2026-09-09`. Every file passed PDF
metadata inspection. Ninety-six have an extractable first-page text layer;
four older working papers require OCR or manual transcription before numerical
extraction. A small number of older PDFs also emit recoverable cross-reference
warnings.

The same papers are imported into `params/evidence_corpus.csv`: one
hash-pinned, source-addressable record per PDF. The registry is deliberately
separate from `parameters.csv`; its `unreviewed` status is a scientific safety
gate, not a missing-file marker.

`params/evidence_findings.csv` is the next layer: a finding is recorded after
reading, even when it is directional-only, a non-composable index, a null, or
already represented by an existing parameter. That keeps the graph from
silently losing a result merely because it cannot yet be multiplied through a
path.

This count is a retrieval and file-integrity milestone only. It is explicitly
*not* a claim that 100 papers have been approved as causal parameters. Each
paper still needs the screening and extraction workflow above: identify its
estimand, exposure and outcome definitions, comparison, time horizon, effect
scale, uncertainty, population/scope, and whether its estimate overlaps a
total or mediated edge already in the graph.

## Initial acquisition batch

These are known candidate bridges with a DOI or an open, stable full-text
source. `status` means acquisition priority, not that a numerical edge has
been accepted.

| Priority | Candidate bridge | Study / retrieval | Status |
|---|---|---|---|
| P0 | job displacement → criminal charges | Rege, Skardhamar, Telle & Votruba (2019), *Job displacement and crime: Evidence from Norwegian register data*, DOI [10.1016/j.labeco.2019.101761](https://doi.org/10.1016/j.labeco.2019.101761), [open PDF](https://ssb.brage.unit.no/ssb-xmlui/bitstream/handle/11250/2653196/10-1016j-labeco-2019-101761.pdf?isAllowed=y&sequence=3) | acquire + extract |
| P0 | parental divorce → child income, college, incarceration, mortality, teen birth | Johnston, Jones & Pope (2025), [NBER w33776](https://www.nber.org/papers/w33776), DOI [10.3386/w33776](https://doi.org/10.3386/w33776) | acquire + extract |
| P0 | hospitalization → work, earnings, debt, credit, bankruptcy | Dobkin, Finkelstein, Kluender & Notowidigdo (2018), DOI [10.1257/aer.20161038](https://doi.org/10.1257/aer.20161038), [open manuscript](https://pmc.ncbi.nlm.nih.gov/articles/PMC5809140/) | acquire + extract |
| P0 | birth weight → adult earnings and education | Black, Devereux & Salvanes (2007), [NBER w11796](https://www.nber.org/papers/w11796) | acquire + verify DOI + extract |
| P0 | childhood move → adult earnings, college, family formation | Chetty, Hendren & Katz (2016), [NBER w21156](https://www.nber.org/papers/w21156), DOI [10.3386/w21156](https://doi.org/10.3386/w21156) | acquire + extract |
| P0 | childhood years in place → adult outcomes | Chetty & Hendren (2018), [NBER w23001](https://www.nber.org/papers/w23001), DOI [10.3386/w23001](https://doi.org/10.3386/w23001) | acquire + extract |
| P1 | early pollution → adult labor-force participation and earnings | Isen, Rossin-Slater & Walker (2017), [NBER w19858](https://www.nber.org/papers/w19858), DOI [10.3386/w19858](https://doi.org/10.3386/w19858) | acquire + extract |
| P1 | disaster → migration, income, work, marriage, fertility | Deryugina, Kawano & Levitt (2018), [NBER w20713](https://www.nber.org/papers/w20713), DOI [10.1257/app.20160307](https://doi.org/10.1257/app.20160307) | acquire + extract |
| P1 | disaster relocation → mortality | Deryugina & Molitor (2020), [NBER w24822](https://www.nber.org/papers/w24822), DOI [10.3386/w24822](https://doi.org/10.3386/w24822) | acquire + extract |
| P1 | school shooting → attendance, progression, education, work, earnings | Cabral, Kim, Rossin-Slater, Schnell & Schwandt, [NBER w28311](https://www.nber.org/papers/w28311), DOI [10.3386/w28311](https://doi.org/10.3386/w28311) | acquire + extract |
| P1 | parental incarceration → child crime, pregnancy, employment | Dobbie et al., [NBER w24186](https://www.nber.org/papers/w24186), DOI [10.3386/w24186](https://doi.org/10.3386/w24186) | acquire + extract |
| P1 | incarceration → parent employment; null child outcomes | Bhuller, Dahl, Løken & Mogstad, [NBER w24227](https://www.nber.org/papers/w24227), DOI [10.3386/w24227](https://doi.org/10.3386/w24227) | acquire as structural counterweight |
| P1 | childhood disability → later education, retirement, work | Gensowski et al., [NBER w24753](https://www.nber.org/papers/w24753), DOI [10.3386/w24753](https://doi.org/10.3386/w24753) | acquire + extract |
| P2 | parental mental health → child mental health; intervention effect | Bütikofer et al., [NBER w31446](https://www.nber.org/papers/w31446), DOI [10.3386/w31446](https://doi.org/10.3386/w31446) | acquire; classify causal role carefully |

## Batch process

### 1. Acquire

For each candidate, record DOI, canonical publication, legal full-text URL,
download date, and checksum. Keep the paper itself outside the repository if
its license does not permit redistribution; keep the retrieval receipt in the
repository.

### 2. Screen

Reject or mark `context_only` when a study cannot answer a causal transition.
For surviving candidates, identify the exact treatment, comparison, outcome,
unit, population, and follow-up horizon before reading coefficients.

### 3. Extract

One study can yield multiple edges. Extract each estimate with its standard
error/CI, baseline where required, timing, heterogeneity, nulls, and the
authors' stated identification limits.

### 4. Place in the graph

Classify the estimate as total, direct, mediated, null, or context-only. Link
it to existing nodes. If it introduces a new node, add that node with explicit
unit and time semantics.

### 5. Test composition

Before shipping a new long path, test unit compatibility, time ordering,
double-counting rules, and uncertainty propagation. Preserve alternate
structures when credible studies disagree.

## Discovery cadence

For each graph region, run a reproducible search sweep:

1. Search the region's root events with `causal`, `quasi-experimental`,
   `natural experiment`, `randomized`, `administrative data`, and
   `long-term outcomes`.
2. Read systematic reviews and the reference lists of qualifying papers.
3. Follow forward citations to newer causal designs.
4. Deduplicate against `references.bib`.
5. Add candidates to the queue with a retrieval receipt, including null and
   contradictory findings.
6. Re-rank by graph bridges unlocked and value of information.

The first milestone is not “all papers.” It is saturation of the first long
chain: `job displacement → child adult conditions → pregnancy conditions →
grandchild birth weight`, plus a documented list of every missing bridge.
