# Methods paper and generated companions

<!-- @ref:doc-paper; @tag:methods -->
<!--
Connections: @link:code-scenario; @link:code-ledger; @link:code-mortality; @link:code-validate;
@link:doc-model-card; @link:doc-citing; @link:doc-testing-quality; @link:docs-index; @link:paper-methods; @link:paper-build-tables; @link:script-build-methods-html; @link:test-paper-tables.
-->

Related: [Documentation map](README.md) · [model card](MODEL_CARD.md) · [citing](CITING.md).
Implementation: [scenario](../src/downstream/scenario.py), [ledger](../src/downstream/ledger.py), [mortality](../src/downstream/mortality.py), [validate](../src/downstream/validate.py). Checks: [paper_tables](../tests/test_paper_tables.py).

The authored manuscript is [paper/downstream.tex](../paper/downstream.tex).
Supporting methods and implementation contracts live in this documentation
collection; the manuscript retains its scientific citations and reader-facing
cross-references. Source navigation uses LaTeX `%` comments, so refs, links and
tags do not appear in the PDF. Figures use the same convention.

## Build and verification

From the repository root, run:

```sh
make -C paper
.venv/bin/python -m pytest -q tests/test_paper_tables.py
python3 scripts/refcheck.py check
```

[The paper build](../paper/Makefile) runs [the table generator](../paper/build_tables.py)
and [the HTML companion generator](../scripts/build_methods_html.py), then invokes
`latexmk`. Python uses the repository virtual environment when present. LaTeX
must be installed locally. The outputs are [the PDF](../paper/downstream.pdf) and
[the HTML methods companion](methods.html). The generated tables and scorecards
consume live engine results; their source digest records the authored inputs.
Source comment changes can update that digest without changing model arithmetic.

## Method connections

| Paper passage | Method or contract | Implementation | Verification |
|:---|:---|:---|:---|
| Model and typed composition | [Algorithm](../SPEC.md), [causal graph](CAUSAL_GRAPH_PLAN.md) | [Ledger](../src/downstream/ledger.py), [units](../src/downstream/units.py) | [Composition tests](../tests/test_ledger.py) |
| Exposure and count conversion | [Exposure semantics](EXPOSURE_SEMANTICS_0_4.md) | [Scenarios](../src/downstream/scenario.py), [mortality](../src/downstream/mortality.py) | [Exposure checks](../tests/test_exposure_semantics.py), [mathematical checks](../tests/test_mathematics_v02.py) |
| Children and place | [Child gaps](CHILD_GAP_VIEW.md), [same-place counterfactual](PLACE_COUNTERFACTUAL.md) | [Children](../src/downstream/children.py), [place](../src/downstream/place.py) | [Child eligibility](../tests/test_child_applicability.py), [place checks](../tests/test_place.py) |
| Mortality support and persistence | [Applicability](MORTALITY_APPLICABILITY_0_4.md), [persistence](MORTALITY_PERSISTENCE_SENSITIVITY.md) | [Strata](../src/downstream/mortality_strata.py), [persistence variants](../src/downstream/mortality_robustness.py) | [Admission checks](../tests/test_mortality_admission_0_4.py), [persistence checks](../tests/test_mortality_robustness.py) |
| Household comparison | [Annual summary](HOUSEHOLD_COMPARISON_0_4.md), [SIPP transitions](BASELINE_TRANSITION_R2_2026-09-14.md) | [Households](../src/downstream/household.py) | [Summary checks](../tests/test_household_summary.py) |
| Uncertainty and sensitivity | [Uncertainty roadmap](PROBABILISTIC_ROADMAP.md), [result sensitivity](RESULT_SENSITIVITY.md) | [Sampling](../src/downstream/mc.py), [inference](../src/downstream/inference.py), [sensitivity](../src/downstream/result_sensitivity.py) | [Distribution checks](../tests/test_distributions.py), [sensitivity checks](../tests/test_result_sensitivity.py) |
| Evidence synthesis and validation | [Pool readiness](POOL_READINESS_0_4.md), [evaluation protocol](SCENARIO_EVIDENCE_PROTOCOL.md) | [Synthesis](../src/downstream/synthesis.py), [validation](../src/downstream/validate.py) | [Pool checks](../tests/test_pool_readiness.py), [validation checks](../tests/test_validate.py) |
| Research program and calculator | [Life-course plan](LIFE_COURSE_RESEARCH_PLAN.md), [calculator](CALCULATOR.md) | [Calculator sources](../calculator/template.html) | [Browser/native parity](../tests/test_calculator.py) |

Generated outputs link back to their generators and authored contracts. Edit
those sources and rebuild; do not hand-edit generated numerical tables or HTML.
Original dataset extracts, bibliography records and archived evidence remain
unchanged by navigation work. Follow their provenance and source-review rules.
