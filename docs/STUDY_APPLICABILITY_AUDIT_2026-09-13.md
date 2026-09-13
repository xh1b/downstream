# Study applicability audit — 2026-09-13

## Decision

The model contains 45 parameter rows. They do not all support a worker-
displacement claim. This audit separates four uses that the public site and
engine must never blur:

| Status | Meaning | Public treatment |
| --- | --- | --- |
| Admitted | The study estimates this link for the named input and outcome. | Show only with its population and input conditions. |
| Conditional | The study is relevant, but its population, event, time, or unit differs. | Keep behind model details. State the transport condition. |
| Structural | The value describes persistence or a conversion rule, not an intervention effect. | Label it an assumption. Do not call the output a direct causal estimate. |
| Boundary only | The study informs a separate input type or is associational. | Do not start it from generic worker displacement. |

This is a parameter-and-study applicability audit. It reads each admitted row,
its source record, the engine route, and the public route. It also rechecks the
high-impact source papers at their primary publisher, author, or working-paper
locations. It is not a new meta-analysis and does not turn a study population
into a universal estimate.

## What a worker-displacement scenario may currently show

Only two absolute-count results pass from the public worker input without an
extra, independently documented exposure:

1. Child adult-earnings loss. This uses Oreopoulos, Page, and Stevens' Canadian
   firm-closure father-son design. It is conditional on the result transporting
   to the stated worker population, family structure, country, and period.
2. Excess deaths. This uses Sullivan and von Wachter's high-seniority male
   Pennsylvania mass-layoff result. It is conditional on the demographic,
   labor-market, and mortality-baseline match.

Grandchild and great-grandchild earnings are not additional direct estimates.
They are structural persistence projections from the child gap. The interface
must say this at the result, not only in an expanded note.

Local service employment does **not** pass from a count of displaced workers.
Moretti estimates the effect of a net city-level change in tradable employment.
The engine now requires a documented net local tradable-job loss. It must also
name the job mix before applying a high-tech multiplier.

## Pathway review

| Parameter row(s) | Study and estimand | Status | Required condition or action |
| --- | --- | --- | --- |
| `displacement→worker_earnings` | Jacobson, LaLonde, and Sullivan estimate long-run earnings losses for high-tenure Pennsylvania workers leaving distressed firms. Davis and von Wachter summarize recession displacement losses. Oreopoulos et al. study Canadian firm closures. | Conditional | Do not present `0.80` as a universal loss from a replacement. Require an involuntary separation/displacement definition, and name tenure, place, period, and horizon. Keep the cross-study band as a transport range, not a confidence interval. |
| `earnings_shock→mortality_*` | Sullivan and von Wachter estimate mortality after displacement for high-seniority male Pennsylvanian workers. | Conditional | Keep the five source-offset phases. Refuse profiles outside the male 45–54 response scope unless an explicit transport assumption is selected. Do not describe the result as a general effect of an earnings ratio; the study identifies displacement and reports earnings as a possible channel. |
| `displacement→divorce_hazard` | Rege, Telle, and Votruba study Norwegian plant closures and married couples. Charles and Stephens study US displacement, disability, and divorce. | Conditional | A displacement result may expose a separate divorce pathway, but it cannot be added to child earnings without an incidence model and a no-overlap rule. Keep it parallel. |
| `displacement→child_earnings` | Oreopoulos, Page, and Stevens use more than 39,000 Canadian father-son pairs and firm closures. | Conditional | This is the current direct child result. Name it as a father–son, Canadian, firm-closure estimate. It cannot identify outcomes for daughters or any named family. |
| `divorce→child_earnings` | Gruber identifies effects of unilateral-divorce-law changes. | Boundary only | A law-reform estimand is not the effect of a particular parent's divorce. Do not route displacement into this row without a separate, defensible bridge. |
| `family_size→child_earnings` | Black, Devereux, and Salvanes use Norwegian administrative data and sibling instruments. | Boundary only | An extra-child estimand is not a displacement consequence. Keep it outside the default displacement graph. |
| `child→grandchild earnings` | Solon, Corak, and Chetty estimate intergenerational income persistence or mobility. | Structural | The row transmits a pre-existing child earnings *gap*. It does not identify the causal effect of a grandparent's displacement. Label it “structural persistence assumption” everywhere. |
| `grandchild→great-grandchild earnings` | Lindahl et al. and Adermon et al. use Swedish multigeneration data. | Structural | Same rule, with a stronger geography and outcome mismatch. The result must carry the weakest-link warning and no-new-harms statement. |
| `ipv_exposure→daughter_violence_odds` | Widom and Ehrensaft are prospective violence-exposure studies. | Boundary only | There is no admitted displacement-to-IPV incidence edge. This outcome must remain blocked from worker displacement. |
| `displacement→local_service_jobs` | Moretti estimates changes in city tradable employment and local nontradable employment. | Conditional | Require net metro tradable-job change and a documented industry/skill mix. The generic manufacturing result is 1.6 local jobs per added tradable manufacturing job; skilled-job and high-tech figures are different estimands. Never apply the high-tech value to every displaced worker. |
| `school_spending→child_earnings` | Jackson, Johnson, and Persico estimate school-finance-reform exposure. | Boundary only | A change in public school spending is a different treatment. Do not infer it from job loss. |
| `youth_wages→youth_crime` | Gould et al. and Grogger estimate local wage/labor-market effects on youth crime. | Boundary only | Requires a measured youth-wage change and matching crime outcome. It is not a continuation of adult worker displacement. |
| `wage_ratio→household_ipv` | Aizer estimates county female-to-male wage changes and female assault hospitalizations. | Boundary only | The unit is a county wage ratio and hospitalizations, not an individual earnings loss or household IPV incidence. Do not compose it from the worker result. |
| `displacement→infant_birth_weight` | Lindo uses PSID sibling comparisons around husbands' job displacement. | Conditional | This is a child-born-after-displacement estimate. It needs a pregnancy/birth timing input and must not be applied to existing children. |
| `import_shock→non_displaced_wage_spillover` | Autor, Dorn, and Hanson estimate commuting-zone import-exposure effects for noncollege workers outside manufacturing. | Boundary only | Input is dollars of import exposure per worker over a decade. It is not a displaced-worker count. Keep it in the China-shock validation route only. |
| `family_income_shock→child_achievement_sd` | Dahl and Lochner use EITC-induced income variation for US children. | Conditional | This is a short-run test-score effect of policy-induced income change. It needs a measured income-dose and child age, and does not prove an adult-earnings effect. |
| `family_income_shock→life_expectancy_years` | Chetty et al. report an income–longevity association at age 40. | Boundary only | The paper is explicitly associational. Keep it as a descriptive conversion check only; never use it to generate causal deaths or life-years from income loss. |
| `displacement→college_enrollment` and `→parental_income_shortrun` | Hilger uses the timing of roughly seven million US fathers' layoffs. | Conditional | Stronger US coverage than the child-earnings row, but the result is for fathers and child ages 12–29. Show it only with those conditions and do not substitute it for the Canadian adult-earnings estimate. |
| `unemployment_rate→property_crime` | Raphael and Winter-Ebmer estimate state unemployment effects using aggregate instruments. | Boundary only | Input is a state unemployment-rate change. Do not convert individual displacement into percentage points without a documented aggregate bridge. |
| `eitc_exposure→adult_earnings_early` | Bastian and Michelmore estimate childhood EITC exposure. | Boundary only | Policy income exposure at ages 13–18 is not an adult job-loss treatment. |
| `male_earnings→marital_fertility` | Kearney and Wilson use US fracking-driven male earnings changes. | Boundary only | Requires a local male-earnings shock and the study's fertility outcome. It cannot be inferred from an individual worker's earnings loss. |
| `import_shock→gop_win_probability` | Autor, Dorn, Hanson, and Majlesi estimate trade-exposure electoral effects. | Boundary only | Input and outcome are geographic political aggregates. Keep separate from person/family results. |
| `male_job_loss_rate→child_maltreatment` | Lindo, Schaller, and Hansen estimate California county labor-market conditions, including male mass layoffs, and maltreatment reports. | Boundary only | Requires the male county mass-layoff rate. The opposite-signed female result prevents a generic all-worker multiplier. The source key is `lindo2018maltreatment`; the older nearby bibliography key is not this study. |
| `displacement→grade_retention_hazard` | Stevens and Schaller use US SIPP child panels and specified involuntary head-of-household job losses. | Conditional | Use only for a child of the stated household and outcome window. Do not compose it into adult earnings without an admitted education-to-earnings bridge. |
| `eviction_order→emergency_shelter_use` and `→eviction_earnings_response` | Collinson et al. use judge-leniency IV among eviction-court cases in Cook County and New York City. | Boundary only | An eviction order is a distinct legal exposure. It must not appear downstream of displacement unless a separately identified displacement-to-eviction link lands. |
| `foreclosure_order→house_price_gap` | Campbell, Giglio, and Pathak estimate forced-sale price effects in Massachusetts transactions. | Boundary only | This is a property-sale and spatial-distance estimand, not a household consequence of job loss. |
| `household_ipv→child_internalizing_sd` and `→child_externalizing_sd` | Evans, Davies, and DiLillo meta-analyze child exposure to interparental physical violence. | Boundary only | The row is a parallel exposure contrast. It cannot enter the displacement chain without a supported IPV-incidence edge. |
| `local_unemp_shock`, `household_hardship`, and `couple_unemployment→household_ipv` | Schneider, Harknett, and McLanahan study Fragile Families mothers in 20 US cities. | Boundary only | Inputs and samples differ: area unemployment, hardship, and couple unemployment. The design does not license a generic worker-displacement-to-IPV result. |
| `unemployment_status→mental_health_sd` | Paul and Moser meta-analyze unemployed versus employed adults across 26 countries. | Boundary only | This is mainly a heterogeneous status contrast, not a single causal displacement effect. It must remain separate until a compatible causal design is selected. |
| `import_shock→radical_right_vote_share` | Colantone and Stanig estimate European regional import-competition effects. | Boundary only | Input is regional trade exposure and outcome is vote share. Do not convert it from US worker counts. |
| `neighborhood_exposure→child_outcomes_modifier` | Chetty and Hendren estimate childhood exposure effects from family moves across US counties. | Structural | The engine may use it only as an explicitly exploratory same-place modifier. It does not identify that a place changes the causal effect of displacement. |
| `unconditional_income→child_education_years`, `→youth_any_crime`, and `→youth_minor_crime_ever` | Akee et al. study casino transfers to previously poor Eastern Band of Cherokee households. | Boundary only | A recurring unconditional transfer is not a one-time loss of a job. Keep it as a separate intervention branch. |
| `youth_crime_conviction_share` and `youth_violent_crime_conviction_share→youth_crime_convicted` | Damm and Dustmann study quasi-random municipality assignment of male refugee children in Denmark. | Boundary only | The input is neighborhood conviction exposure for a specific assigned-child population. It is not a worker-displacement continuation. |

## Corrections and release gates

1. **Done:** worker replacement no longer produces local service-job loss. The
   scenario needs `net_tradable_jobs_lost`.
2. **Required before a local-jobs headline:** replace the generic point of 5.0
   with an industry/skill-specific input contract, or use the manufacturing
   estimate only where the input identifies manufacturing jobs. A band from
   1.6 to 5.0 does not solve this problem because its endpoints describe
   different job types, not uncertainty around one shared estimand.
3. **Required public labels:** identify the direct child result as Canadian
   father–son firm closures; identify mortality as high-seniority male
   Pennsylvania displacement; identify later generations as structural
   projections.
4. **Required graph behavior:** default worker-displacement views must hide or
   visibly block every “Boundary only” row. They may appear in the full graph
   as separate input families, with the input named.
5. **Required before scorecard claims:** the China-shock rows use geographic
   import exposure, not a worker count. The scorecard must define its unit,
   comparison, period, and held-out outcome before it reports a fit.

## Source register

- [Jacobson, LaLonde, and Sullivan (1993), Pennsylvania high-tenure earnings losses](https://research.upjohn.org/up_workingpapers/11/)
- [Davis and von Wachter (2011), recession job-loss costs](https://www.nber.org/papers/w17638)
- [Oreopoulos, Page, and Stevens (2008), Canadian father–son firm closures](https://www.journals.uchicago.edu/doi/10.1086/588493)
- [Sullivan and von Wachter (2009), displacement and mortality](https://www.nber.org/papers/w13626)
- [Moretti (2010), city tradable-employment multiplier](https://eml.berkeley.edu/~moretti/multipliers.pdf)
- [Rege, Telle, and Votruba (2007), Norwegian plant closure and dissolution](https://www.econstor.eu/bitstream/10419/192496/1/dp514.pdf)
- [Lindo (2011), parental job loss and infant health](https://www.iza.org/publications/dp/5213/parental-job-loss-and-infant-health)
- [Hilger (2016), US fathers' layoffs](https://www.aeaweb.org/articles?id=10.1257%2Fapp.20150295)
- [Autor, Dorn, and Hanson (2013), China-shock labor-market design](https://pubs.aeaweb.org/doi/10.1257/aer.103.6.2121)
- [Dahl and Lochner (2012), EITC and child achievement](https://pubs.aeaweb.org/doi/10.1257/aer.102.5.1927)
- [Chetty et al. (2016), income and longevity association](https://pmc.ncbi.nlm.nih.gov/articles/PMC4866586/)
- [Lindo, Schaller, and Hansen (2018), gender-specific labor conditions and maltreatment](https://www.nber.org/papers/w18994)
- [Collinson et al. (2024), eviction and poverty](https://doi.org/10.1093/qje/qjad042)
- [Chetty and Hendren, childhood exposure effects](https://opportunityinsights.org/paper/movers/)
- [Damm and Dustmann (2014), neighborhood exposure and youth crime](https://doi.org/10.1257/aer.104.6.1806)

The full bibliographic metadata, parameter points, extraction notes, and
evidence tiers remain in `params/references.bib` and `params/parameters.csv`.
