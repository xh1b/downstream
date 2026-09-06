# RENDERING — how to show the model's work to people who are not mathematicians

The problem this solves: the model makes claims like "a town hit by
X displacement is likely to see infant mortality about 3% higher over
20 years" — where the number flows through SEVERAL influences, from
DIFFERENT dimensions, several steps away from the source. Showing the
regression table is not an answer. Hiding the math is worse. The
design below makes the derivation itself the product.

Binding rule for every surface (CLI, web, paper, chat): rendering
starts from the **explanation object** (`explanation.Explanation.as_dict()`).
A renderer never re-derives the math, and never shows a number the
model did not compute. The reference renderer is `render.py`; its
hard rules are tested.

## 1. The five layers (progressive disclosure)

Each layer stands alone. A reader stops anywhere and is correctly
informed, just less precisely.

**Layer 1 — the claim.** One sentence, plain words:

> For a town of about 20,000 where 300 residents lose tradable jobs,
> the model estimates roughly 2 to 3 more deaths than usual over the
> next 20 years — most likely 2 [modeled range].

The formula: **[modeled range] + [outcome in plain words] + [who/where]
+ [timeframe] + [compared to what]**. Rules:

- Always "the model estimates / the model traces" — never "will".
- Bands ride along with every number. No naked point estimates,
  anywhere, ever (tested in `render.py`).
- Use **natural frequencies** (gigerenzer2002): "about 1 in 300
  residents", not "a 0.3 percentage-point increase". Both shown when
  space allows; the natural frequency goes first.
- Absolute counts before percentages; percentages only with their
  denominator.

**Layer 2 — why: the chain as a story.** The derivation rendered as
at most 7 numbered steps. One step, one sentence, one citation:

> 1. Workers who lose long-held jobs earn about 20% less over the
>    following decades [Sullivan & von Wachter 2009].
> 2. That income shock raises their death rate by about 17% in
>    sustained terms, for up to 20 years [same study].
> 3. Against a baseline death rate of about 0.4% per year at these
>    ages [CDC WONDER], 300 workers for 20 years comes to 2-3 extra
>    deaths.

Each step shows: the size it applied, the running result, and the
citation. Contribution shares tell the reader **which step does the
most work** ("step 1 accounts for about 60% of the movement").

**Layer 3 — where the remaining range lives.** Sobol drivers in
plain words:

> The range is mostly driven by how deep the earnings losses are. If
> we knew that better, the band would tighten — the death-rate link
> is already tightly estimated.

This is the honest answer to "why is the range so wide" and it
doubles as our research roadmap (it points at the next extraction).

**Layer 4 — what would prove this wrong.** The falsification rows
from the explanation object. A claim that cannot say how it would
die does not render.

**Layer 5 — the receipts.** Every parameter: value, band, tier,
population, study, design, and the caveat text. Rendered as a table.
This layer is the bridge to the paper and the repo.

## 2. The chain diagram (multiple influences, multiple steps)

For claims with branching causes (the infant-mortality case: income
loss, family stress, health-system response — arriving via different
paths and steps), render the DAG as a left-to-right flow:

```
 job loss ──(earnings -20%)──> income shock ──(+17% deaths/20y)──> deaths
     │                              │
     └──(divorce +11%)──> family break ──(queued)──> infant health
```

Rules: arrows carry the size in plain language; queued links render
as dashed with "not yet estimated — we refuse to guess"; every path
from source to outcome is drawn, including the ones that CANCEL
(the model's honest non-finding "the pooled evidence does not
support X" gets a crossed arrow, not silence).

## 3. The visual vocabulary (web surfaces)

| Chart | Used for | Rule |
|:---|:---|:---|
| Waterfall | chain contributions (layer 2) | one bar per step, share of total movement labeled |
| Tornado | uncertainty drivers (layer 3) | Sobol S_total, top 3 only |
| Fan chart | anything with a time profile (mortality window) | p05-p95 ribbon, median line |
| Chain diagram | multi-path claims (§2) | max 7 nodes visible; expand on click |

Design constants: bands are drawn wider than the point marker, never
as whiskers; "modeled" appears in the chart title; no red/green
coding (moral loading) — one hue, saturation carries magnitude.

## 4. Worked template — the infant-mortality claim

The user-facing sentence the system is being built to earn:

> For towns like this one, the model traces a 2-3% rise in infant
> mortality over 20 years [modeled; range driven by A and B].

Derivation layers when Lindo 2011 (queue #13) and the infant-health
baselines land:

```
step 1: displacement -> household income loss      [JLS band]
step 2: income loss   -> infant health             [Lindo 2011, TO EXTRACT]
step 3: infant health -> infant mortality rate     [baseline: CDC linked files]
counts: N births x baseline rate x rate-ratio x window
```

Every step above must be tiered, cited, and Sobol-attributed before
that sentence may render on any surface. Until then the claim is
BLOCKED and renders (if at all) with its missing pieces named. The
explanation object carries `blocked` for exactly this case — the
template is complete in `docs/QUEUED_EXTRACTIONS.md`.

## 5. Language rules (the whole system, one list)

1. "The model estimates/traces" — never "X will happen".
2. "Modeled" label on every number, every chart, every export.
3. Natural frequencies first ("1 in 300"), technical second ("0.3%/yr").
4. Ranges ride with points; points never travel alone.
5. Measured vs modeled vs contested are three different labels; a
   contested number renders both positions or does not render.
6. A refused computation is stated with its missing input, in the
   same voice as a result — refusals are results.
7. No causal verb outruns its design: quasi-experimental evidence
   "supports a link"; it does not "prove" one.
8. Honesty about weakness renders at the same size as honesty about
   strength (the great-grandchild caveat renders on the vignette,
   not in a footnote).
