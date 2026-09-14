# Receiving-community channel: evidence scan and search protocol (2026-09-14)

Status: **first-pass scan, anchors verified by search 2026-09-14; nothing
admitted yet.** Motivation: running the 1,000-worker displacement scenario
with replacement inflows (`docs/BASELINE_TRANSITION_R2_2026-09-14.md` is
the displacement side) showed the engine is **silent** on the
receiving community: there is no parameter connecting a local
immigration inflow to any outcome. Silence is not an estimated zero —
it is an unmodeled channel, and the engine reports it as such. This
document maps the literature that could fill the gap, states which
links would connect to nodes the model already carries, and fixes the
search protocol for completing the sweep.

Admission rule restated up front, because this literature tests it:
**direction-agnostic.** A well-identified null (e.g., immigration-crime)
is admitted exactly like a well-identified harm. The defense against
publication bias — which exists in both directions in this field — is
the design-tier contract (quasi-experimental identification, population
scope, EXACT/conditional/exploratory roles), not the direction of the
result.

## The channel map: what a replacement scenario needs

The exposure node would be a *local immigrant inflow / immigrant-share
change* (persons or percentage points, the scale each source paper
uses). The model already carries the outcome side of most candidate
links, so most of these are one-row extractions, not new subsystems:

| channel | candidate link | outcome side already in model? |
|---|---|---|
| housing | immigrant inflow → local rents/house prices | partially: rent-burden/arrears → eviction (`collinson2024`) conversion is queued; a rents node would feed it |
| labor, same-skill | inflow → natives' wage by skill group | partially: `local_wage_response` exists but its only producer is the China import shock (`adh2013`); an immigration producer would be a parallel boundary row |
| mental health | inflow → host residents' depression/anxiety | yes: `unemployment_status->mental_health_sd` (`paul2009`) exists; a new boundary row would join it |
| social trust / cohesion | local diversity → natives' trust/participation | no node yet; exploratory tier only (see below) |
| crime | inflow → local crime | yes: `youth_crime_rate`, `property_crime_response` exist |
| political | inflow → anti-immigration party vote share | yes: `import_shock->radical_right_vote_share` (`colantone2018`) and `import_shock->gop_win_probability` (`autor2020polarization`) are the templates |
| school peers | inflow → native children's school outcomes | yes: `child_achievement_sd`, `exam_noncompletion_hazard`, enrollment nodes exist |
| native mobility | inflow → native outflows | no node; would modulate every local density effect above |

The model already admits one composition-effect row — `damm2014` (area
youth conviction share → child conviction probability) — so
composition links are admissible in principle when identified.

## Verified anchors (found 2026-09-14; screening pending)

Each anchor below was located and verified by search this session.
Design tier is a first visual assessment only; full screening happens
under the admission contract before anything becomes a row.

- **Labor market, natives' wages/employment**
  - Longhi, Nijkamp & Poot (2005, Tinbergen 04134): meta-analysis, 348
    estimates — negative but small wage effects, concentrated on
    same-skill natives. <https://papers.tinbergen.nl/04134.pdf>
  - Longhi, Nijkamp & Poot (2008): meta-analysis, 1,572 effect sizes,
    wages + employment + participation.
    <https://ideas.repec.org/p/wai/pscdps/dp-67.html>
  - Nedoncelle et al. (2025, CEPII 2025-07): updated meta-analysis of
    native-wage effects. <https://www.cepii.fr/PDF_PUB/wp/2025/wp2025-07.pdf>
- **Housing**
  - Saiz (2007, JUE 61(2):345–371): +1% rents/values per 1%-of-population
    inflow, US cities, IV.
    <https://www.sciencedirect.com/science/article/pii/S009411900600074X>
  - Sá (2015, Economic Journal 125(587):1393–1424): −1.7% house prices
    per 1pp immigrant share, UK — negative via affluent native
    outflows. <https://onlinelibrary.wiley.com/doi/abs/10.1111/ecoj.12158>
  - Sanchis-Guarner et al. (JUE, decomposing demand vs native
    adjustment). <https://www.sciencedirect.com/science/article/pii/S0166046223000285>
- **Host mental health**
  - Shin (2026, IZA DP 18586): sudden Yemeni asylum-seeker influx on
    Jeju Island, difference-in-differences — worsened host residents'
    depression and anxiety, reduced life satisfaction; mechanisms:
    safety worries and trust in government. Working-paper tier until
    journal-published; the single most on-point quasi-experiment found.
    <https://docs.iza.org/dp18586.pdf>,
    <https://www.iza.org/publications/dp/18586>
- **Social trust / cohesion**
  - Putnam (2007, Scand. Pol. Studies): diversity → lower trust
    ("hunkering down"), 8,300+ citations — correlational; exploratory
    tier at best.
  - Dinesen & Sønderskov (2020, Annual Review of Sociology): narrative +
    meta-analytic review; negative diversity–trust association,
    strongest at the most local scale.
    <https://pure.au.dk/ws/files/230771020/Ethnic_Diversity_and_Social_Trust_Final_version_2020.pdf>
- **Crime**
  - Ousey & Kubrin (2018, Annual Review of Criminology): meta-analysis
    of 51 studies — immigration–crime association ~zero to slightly
    negative. Would enter as a near-null link if admitted.
    <https://www.annualreviews.org/content/journals/10.1146/annurev-criminol-032317-092026>
- **Political behavior**
  - Halla, Wagner & Zweimüller (2017, European Economic Review
    15(6):1341–1385): local immigrant share → FPÖ vote share, IV
    design, Austria. <https://ideas.repec.org/a/oup/jeurec/v15y2017i6p1341-1385..html>
- **School peers**
  - Gould, Lavy & Paserman (2009, Economic Journal 119:1243–1269):
    Soviet-collapse influx to Israel — ~no effect on natives'
    schooling. <https://ideas.repec.org/a/wly/econjl/v119y2009i540p1243-1269.html>
  - Hassan et al. (2023, European Sociological Review): Danish refugee
    peer effects on native children.
    <https://academic.oup.com/esr/article/39/3/352/6843667>

Honest summary of what the verified anchors say: the effects that are
well identified are **large for housing and political behavior,
moderate and skill-concentrated for labor markets, present for host
mental health (one working-paper quasi-experiment), local-scale for
trust, and near-null for crime**. A replacement scenario built from
these would show the receiving community's harms concentrated in rents,
political polarization, and possibly mental health — not in crime or
average wages. That mixture is what the real data currently look like,
and the model should carry it with declared roles rather than either
silence or a uniform sign.

## Search protocol for completing the sweep

1. **Meta-analyses and reviews first** (they bound the field and cite
   everything): Annual Reviews, Campbell Collaboration, Handbook of the
   Economics of International Migration (Chiswick & Miller, eds.),
   recent meta-analyses on each channel. The six channels above each
   get one review pass before any single-paper extraction.
2. **Snowball from each verified anchor**: backward (what it cites) and
   forward (Google Scholar "cited by") with the design filter on:
   keep only quasi-experimental or longitudinal-administrative designs
   for causal roles.
3. **Working-paper series sweeps**: NBER, IZA, CEPR (DPs), CEPII,
   Norface — this field lands in journals 2–4 years after the working
   paper; the working-paper versions carry the identification.
4. **Registry checks for publication-bias defense**: screend registered
   reports/AEA RCT Registry entries where they exist; when a channel
   rests on observational designs only (trust), the row stays
   exploratory regardless of sign.
5. **Query strings that worked** (recorded for the next agent):
   - `immigration natives labor market meta-analysis Longhi`
   - `immigration housing rents quasi-experimental Saiz Sá`
   - `refugee allocation Denmark Germany natives mental health quasi-experiment`
   - `ethnic diversity social trust natives quasi-experimental meta`
   - `immigration crime meta-analysis Ousey Kubrin`
   - `immigration voting radical right quasi-experimental`
6. **Screening**: every candidate goes through the admission contract
   (design tier, population scope, unit match to a model node or a
   declared boundary coefficient) and lands in the queue as an
   extraction row — same workflow as every other parameter. US-external
   populations (Austria, Denmark, Israel, Korea, UK) are admissible
   with population_scope declared, as the existing non-US rows
   (browningheinesen2012, marcus2013, bingley2026) already are.

## Explicitly out of scope for this scan

- Aggregate/macro effects of immigration (growth, fiscal balances at
  the national level): different exposure scale than the town-level
  scenario the engine runs.
- Effects *on the immigrants themselves*: separable literature,
  separate scan if wanted.
- Any claim about effects no identified study supports. If a channel
  (e.g., "replacement → native displacement from housing") stays
  without admissible evidence, the engine keeps reporting it as
  unmodeled rather than filling the gap with an assumption.
