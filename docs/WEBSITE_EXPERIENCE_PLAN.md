# Website experience plan: explore possible futures

Status: product and design proposal, September 10, 2026. This plan concerns
usefulness, comprehension, trust, and visual quality. It does not prescribe
frameworks, components, databases, deployment, or other implementation choices.
The research dependencies are in [LIFE_COURSE_RESEARCH_PLAN.md](LIFE_COURSE_RESEARCH_PLAN.md).

## 1. The product promise

Help someone understand how a specified event could change outcomes for
people in a situation like theirs, what might alter those consequences,
and how much the available evidence can support.

A proposed opening:

> Explore how a life event could change the years ahead.
> Compare possible outcomes for a person and their household, using research
> and clearly stated assumptions.

Primary action: **Explore an example**. Secondary action: **Describe a situation**.
Examples make the experience useful before someone shares personal details.

The first useful moment is understanding a comparison, not completing a long
form or seeing a dramatic number. “All downstream effects” belongs in the
long-term vision, not the launch promise. The product must remain useful when
it can show only a small number of supported consequences.

## 2. Who the first experience serves

**Primary visitor:** a curious person or household exploring the implications
of an event. They may be worried, unfamiliar with statistics, or uncertain
about their inputs. They need context and control over how much detail to see.

**Secondary visitor:** a researcher, journalist, or adviser checking a scenario
and the evidence behind it. They need inspectable assumptions and reproducible
comparisons. Evidence detail should be available from the same result rather
than requiring a separate product.

Community or employer analysis is a later, distinct entry point with its own
exposure scale. A person should not unexpectedly receive a headline about
thousands of community deaths or a regional multiplier applied to their life.

## 3. A bounded first release

The intended first calculator compares a five-year household displacement
scenario with a reference scenario, once research milestones R0-R5 support it.
Show a small set of defensible employment, earnings, and household-resource
outcomes. Additional domains can appear in a compact coverage panel.

Before those capabilities exist, a design prototype can use unmistakably
fictional examples or current engine results with their actual limited scope.
The present engine's long-run earnings coefficient is not an annual trajectory.
Do not animate invented annual values between known endpoints. Do not publish
currently unresolved mortality or place calculations as reliable personal
headlines merely because the interface can render them.

A public release does not require a complete graph, arbitrary event sequences,
all counties, or every personal characteristic. It requires a complete and
understandable contract for the scenarios it does support.

## 4. The visitor journey

| Stage | Visitor's question | Experience | Completion signal |
|---|---|---|---|
| Discover | What can this help me understand? | One concrete example, scope, and two clear entry actions | Can describe the tool's purpose |
| Describe | Which details matter? | Short progressive profile, useful defaults visibly marked, optional detail | Understands which inputs are used |
| Specify | What exactly is changing? | Defined event, start, duration, comparison, and horizon | Can restate both scenarios |
| Review | Is this the situation I meant? | Editable plain-language scenario sentence and applicability check | No hidden assumptions about essential inputs |
| Understand | What changes, and by how much? | Compact comparison, trajectories where supported, uncertainty | Can identify direction, scale, and time |
| Explore | What would change this answer? | Duplicate comparison, edit one supported factor, inspect drivers | Knows what changed between runs |
| Inspect or save | Why should I take this seriously? | Evidence receipts, limitations, version, export/share preview | Can recover the basis of the result |

Progress should be recoverable: editing a household detail should not require
starting again. Use a short path by default and offer detail when it changes
the calculation or evidence applicability.

### Describe the situation

Start with the chosen event, then ask only for relevant profile information.
Candidate inputs are age range, location at a supported resolution, household
members, children's ages, employment context, and an income range. A name,
exact address, or precise date of birth is unnecessary for the proposed model.

For each input, explain its use: “Age affects the baseline estimate” or
“Child age determines the period of exposure.” If the engine does not use a
field, omit it or explicitly explain that it is context only. Never create
the impression of precision through an elaborate unused questionnaire.

Allow “I don't know” where it has a valid modeling interpretation. Show the
resulting assumed range or broader reference population. If an input is
essential and cannot be integrated over, explain what is needed and why.
Offer an example instead of silently supplying an exact value.

Location can affect baseline conditions without modifying the event effect.
State the actual geography used, including national fallback. Offer precise
geography only when it adds supported information.

### Specify the event

Use structured, plain-language choices. For displacement, distinguish
involuntary job loss from choosing to leave work, and distinguish job loss
from an income reduction with continued employment. Show onset and duration
where the evidence supports them.

The reference scenario should read **Without the specified job loss**, not
“Nothing happens.” Explain that ordinary life changes still occur. An
intervention such as temporary income support needs an explicit amount,
duration, eligibility, and comparison condition before it becomes selectable.

Future multi-event sequences need timing and ordering. Unsupported combinations
should explain the missing interaction evidence and offer separate comparisons;
they must not produce a precise combined headline.

### Review before calculating

Use a sentence with editable phrases:

> Compare the next five years for a [synthetic household] in [supported area],
> with [specified involuntary job loss] versus [reference conditions].

Under it, list the two or three assumptions that matter most. Show known
applicability limitations before the user invests in interpreting the result.
This is a review of the scenario, not a legal consent wall.

## 5. Results as a clear reading sequence

Use an editorial page rather than a wall of equally prominent metric cards.
The layout should answer one question at a time.

1. **Situation and comparison.** A compact, editable summary that remains easy
   to find while exploring. Include horizon and evidence applicability.
2. **What changes.** At most three outcome summaries, each with an absolute
   reference value, event value, difference, unit, and window where identified.
3. **How it changes over time.** One principal chart for the selected outcome.
4. **Who is affected.** Person and household views; community only when a
   compatible model exists. Identify whether totals include other members.
5. **What changes the answer.** A short list of influential supported inputs
   and uncertain assumptions, with a way to compare alternatives.
6. **What is known and missing.** A compact coverage statement and expandable
   evidence receipts. Meaningful limitations stay near the affected headline.

Desktop may use a quiet side panel for scenario controls and a wider reading
column for the results. Mobile should preserve the same reading order with
an accessible edit action; essential meaning must not depend on hover or a
wide table.

## 6. A visual language for comparisons

**Direction:** calm, warm, precise, and human. Use the restraint of a well-edited
research publication with the ease of a good consumer calculator. Avoid
presenting the interface as an oracle or a diagnosis.

- Warm near-white background, dark ink text, generous whitespace, and a
  limited accent palette. A restrained serif for editorial headings and a
  highly legible sans serif for controls/data are candidate directions to test.
- One consistent pair of scenario colors, such as slate and teal, supported
  by direct labels and different line styles. Keep their meaning stable when
  the user swaps views. Scenario colors identify scenarios, not moral value.
- Clear hierarchy: page purpose, selected outcome, interpretation, detail.
  Numbers should be readable without becoming theatrical. Use consistent
  decimal precision, currency year, and units.
- Repeated alignment, a small spacing scale, and shared chart geometry create
  visual coherence. Borders and shadows should help grouping rather than
  decorate every element. Keep prose line lengths comfortable.
- Use motion to explain a changed scenario or chart focus, with a reduced-
  motion alternative. Do not animate escalating losses, dying avatars, or
  a suspenseful “calculating your future” sequence.
- A map is appropriate for a genuine geographic question, not as evidence
  that every local effect is estimated. A relationship graph is an optional
  explanatory view after the visitor understands the result.

Accessibility target: WCAG 2.2 AA, with keyboard operation, visible focus,
legible contrast, non-color distinctions, and text/table equivalents for
charts. Design chart annotations for zoom and small screens. Reduced motion
is an additional product requirement; do not imply every motion preference
is an AA criterion. [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/).

**Design review question:** if decoration and animation disappear, is the
comparison still obvious, understandable, and pleasant to read?

## 7. Charts that answer actual questions

| Question | Preferred visual | Interpretation requirement |
|---|---|---|
| How do the next years differ? | Directly labeled paired trajectories with an optional difference view | Shared time/unit axes; draw time paths only when the model identifies them |
| How large is the expected change? | Interval dot plot or a compact comparison table | Zero reference for differences; explain what the interval includes |
| How varied are possible outcomes? | Two distributions with plain-language annotations | Distinguish variation among lives from uncertainty about the model |
| How many people might experience an outcome? | Natural frequencies or a simple rate display | Same population denominator and period in both arms |
| Which assumptions matter? | Ranked sensitivity view with alternative scenarios | A sensitive parameter is not necessarily an available real-world intervention |
| How does an effect reach a household member? | Small, selected pathway diagram | Distinguish estimated causal links from assumed links; do not imply path contributions add |

The main chart should favor the most useful supported outcome, selected from
user research, rather than whichever estimate looks most dramatic. Give the
reader a plain-language finding before requiring chart interpretation.

Charts should retain axes and scales during comparisons. A missing year or
unknown pathway should look missing, not like a flat zero line. Do not attach
a smooth uncertainty fan to a few unsupported endpoint coefficients.

## 8. Explain magnitude, uncertainty, and applicability separately

Use absolute comparisons first. For example, this **fictional communication
fixture, not an engine prediction**, illustrates percentage points:

> Reference: 12 in 100. Event scenario: 15 in 100, over the same five years.
> Difference: 3 more in 100, or 3 percentage points.

Do not substitute “25% higher” for that absolute context. Currency displays
need their price year and whether amounts are annual, cumulative, discounted,
or lifetime. Cohort counts must not become “your probability” without an
appropriate probability model.

Every visible interval needs a short explanation such as “This range reflects
uncertainty in the estimated event effect; baseline conditions are fixed.”
Expand to technical detail on request. Parameter-only ranges must not be
labeled as ranges of individual futures. Show structural alternatives as
alternatives unless justified probabilities over them exist.

Use separate, descriptive applicability statements:

- Evidence includes a similar population and event.
- Uses a broader population estimate; subgroup response is uncertain.
- Applies evidence outside its studied setting.
- Cannot estimate this outcome for the supplied scenario.

Do not compress extraction precision, causal identification, population fit,
and validation into one unexplained “confidence: 87%” badge.

For rare or emotionally charged outcomes, keep frequency, population, period,
and uncertainty together. Do not describe expected fractional deaths in a
one-person cohort as a personal prognosis. Default outcome prominence should
follow usefulness and evidence, not fear or virality.

## 9. Evidence that is available without overwhelming the page

Each outcome should offer **Why this estimate?** Open a short explanation:

- What was measured and which comparison the source supports.
- Which population and follow-up window were studied.
- Which parts are estimated, pooled, transported, or assumed.
- How that evidence enters this particular result.
- The most material limitation and current validation status.
- A full citation, source locator, and model/evidence version.

Keep the first explanation readable without statistical training. Offer the
formula, parameter receipt, and study details one level deeper. The graph is
an audit tool, not the mandatory homepage. An explanation generator must not
invent a causal mechanism to make a pathway sound complete.

If pathways overlap or interact, say so. Do not promise an additive “share of
your outcome” for every edge without a justified attribution method.

## 10. States that deserve intentional design

| Situation | What the visitor should see |
|---|---|
| Missing optional detail | The assumption or integrated range being used, with an edit action |
| Essential missing input | One focused explanation and a path to supply it or explore an example |
| Unsupported population or location | Actual reference population/geography and the limits of extrapolation; refusal where required |
| Known null or small effect | Estimate and uncertainty, with a distinction between evidence of little effect and imprecision |
| Missing scientific bridge | “We cannot estimate this pathway with the current evidence,” with the missing bridge named |
| Conflicting evidence | Named alternatives and what differs; no invented consensus |
| Some outcomes blocked | Available results plus a visible coverage gap, never zeros for the blocked ones |
| Invalid event combination | Which interaction is unknown and which separate comparisons are possible |
| Calculation failure | A distinct operational failure message; do not frame it as missing scientific evidence |
| Changed assumptions | A readable comparison of what changed before interpreting new results |
| Older saved result | Its original version and scope; recomputation is explicit rather than silently replacing it |

## 11. Exploration, agency, and saving

Start with two scenarios. Let a visitor duplicate one and alter a single
supported factor; a later third scenario may compare a protective intervention.
Keep an edit history or readable change summary so the apparent cause of a
new result is clear.

Separate an **editable situation** from an **uncertain scientific assumption**.
A visitor can explore an assumption without being told it is something they
can change in real life. Do not turn correlation into a personal recommendation.
Show tradeoffs across outcomes without combining health, money, relationships,
and community effects into an unrequested “life score.”

Offer a concise saved report containing the profile summary, both scenarios,
horizon, outcomes, limitations, and version. Sharing is a separate deliberate
action with a preview of included details. Personal profiles should be private
by default; exact addresses and names are not needed for this product concept.
An anonymous/example entry path should remain usable without an account.
These are product requirements; later implementation must make them true.

## 12. Research and design milestones

| ID | Deliverable | Decision it should resolve |
|---|---|---|
| W0 | Interviews and representative questions | Which comparisons matter to the first audience and which outcomes they can use |
| W1 | Content-first storyboard with clearly fictional fixtures | Can visitors understand the scenario and result without polished styling? |
| W2 | Two visual directions applied to the same complete journey | Which hierarchy, chart treatment, and tone improve clarity and comfort? |
| W3 | Interactive prototype including blocked and uncertain states | Can people edit, compare, inspect assumptions, and recover from uncertainty? |
| W4 | Evaluated experience using eligible model outputs | Does the interface accurately communicate the model's actual scope? |
| W5 | Limited public calculator and feedback process | Are scientific and usability release criteria met for each exposed scenario? |

W0-W3 can proceed before the life-course model is ready, with fixtures clearly
marked. W4-W5 depend on research milestones R0-R5 for the claims they expose.
No launch date is implied by this sequence.

### Comprehension and usefulness study

Recruit people from the intended audience, including different levels of
numeracy, mobile users, and people with access needs. A first formative round
might use 6-8 participants per primary audience; that is a design discovery
sample, not a statistically representative validation study. Revise and run
another round before setting final evaluation targets.

Give participants these tasks without explaining the answer first:

1. Describe what differs between the reference and event scenario.
2. Identify an outcome's units, horizon, and absolute change.
3. Explain what a displayed range means and whether it predicts their life.
4. Find one unsupported outcome and distinguish it from a zero effect.
5. Change one input and explain which assumptions stayed fixed.
6. Find why the evidence may or may not apply to the supplied profile.
7. Save or share only the details they intend to include.

Record correct interpretations, assistance needed, task failures, and the
questions visitors still want answered. Ask what the comparison helped them
understand. Measure perceived trust alongside understanding so attractive
presentation does not mask overconfidence.

Proposed pilot goals, to refine after the first baseline study: at least 80%
of participants correctly explain comparison, horizon, and interval meaning
without assistance; no recurring confusion between a missing estimate and
zero; no unresolved critical keyboard or screen-reader barriers. These are
product targets, not a statistical claim about all future users. Persistent
misinterpretation of personal certainty is a reason to redesign and retest.

### Release checklist

- Every exposed scenario and profile has a scientific applicability decision.
- Reference and event calculations compare compatible outcomes and windows.
- Serious review findings affecting exposed headlines are resolved or those
  headlines are withheld; limitations are not hidden in a general footer.
- Actual model outputs, source receipts, and user-facing explanations agree.
- Partial results, missing evidence, and failures have distinct tested designs.
- Representative users demonstrate comprehension, not just satisfaction.
- Accessibility, responsive reading order, and sharing controls are reviewed.
- A feedback route supports reporting misleading explanations or evidence
  errors, with a visible model-update history.

## 13. What to defer

Defer arbitrary event combinations, immersive single-life storytelling,
large animated causal graphs, public profile sharing, automatic advice,
composite life scores, and broad geographic personalization until their
scientific and user value is demonstrated. A visually impressive feature
should earn its space by helping someone understand a supported comparison.

The quality standard is a visitor who can say: “I understand what was compared,
what might change, why the model says so, and what it cannot tell me.”
