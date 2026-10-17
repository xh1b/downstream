# @ref:script-build-methods-html
# Method: @link:doc-paper.
# Implementation: @link:code-credits; @link:code-mortality; @link:code-params.
# Verification: @link:test-paper-tables.
# Related: @link:paper-methods; @link:paper-build-tables.
# @tag:methods
"""Build a self-contained, semantic HTML companion to the methods paper."""
from __future__ import annotations

import argparse
import hashlib
from html import escape
import json
from pathlib import Path
import sys
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from downstream.credits import parse_authors, _clean_latex  # noqa: E402
from downstream import __version__  # noqa: E402
from downstream.mortality import source_profile_contract  # noqa: E402
from downstream.params import load_all  # noqa: E402
from downstream.scenario import ScenarioInput, compute_counts  # noqa: E402
from downstream.validate import run  # noqa: E402


# @ref:methods-result-digest
# Portable display fingerprint contract: @link:doc-paper. @tag:methods
def reference_result_digest(result):
    """Fingerprint results at 12 significant digits, tolerating libm roundoff."""
    def normalize(value):
        if isinstance(value, float):
            return 0.0 if value == 0 else float(format(value, '.12g'))
        if isinstance(value, dict):
            return {key: normalize(child) for key, child in value.items()}
        if isinstance(value, (list, tuple)):
            return [normalize(child) for child in value]
        return value

    content = json.dumps(normalize(result), sort_keys=True, allow_nan=False)
    return hashlib.sha256(content.encode()).hexdigest()


def build(params_dir=None):
    directory = Path(params_dir) if params_dir else ROOT / 'params'
    parts = load_all(directory)
    params = parts['params']
    result = compute_counts(params, parts['baselines'], ScenarioInput(1000))
    persistence = result['modeled']['excess_deaths']['persistence_sensitivity']
    validation = run(params)
    evaluation = json.loads((ROOT / 'validation/followthrough_evaluation_expanded_20261014.json').read_text())
    cohort_check = evaluation['cohort_reproduction']
    sipp_check = evaluation['sipp_heldout_baseline']['coverage']
    synthesis = evaluation['evidence_synthesis']
    h = escape
    mortality = validation['v1_retrodict']['scored']
    mortality_covered = sum(row['measured_inside_modeled_band'] for row in mortality)
    mortality_rows = ''.join(
        f'<tr><th scope="row">{h(row["variant"].replace("_", " "))}</th>'
        f'<td>{row["modeled_excess_deaths_per100k"]["point"]:g} '
        f'[{row["modeled_excess_deaths_per100k"]["low"]:g}, '
        f'{row["modeled_excess_deaths_per100k"]["high"]:g}]</td>'
        f'<td>{row["measured_differential_per100k"]["point"]:g}</td>'
        f'<td>{"yes" if row["measured_inside_modeled_band"] else "no"}</td></tr>'
        for row in mortality)
    rows = []
    for p in params.parameters:
        unit = parts['nodes'][p.to_node].unit
        rows.append(f'<tr><th scope="row">{h(p.link.replace("_", " ").replace("->", " → "))}<details><summary>Full identifier</summary><code>{h(p.link)}</code></details></th>'
                    f'<td>{p.point:g} [{p.low:g}, {p.high:g}]</td><td>{h(unit)}</td><td>{h(p.evidence_role)}</td>'
                    f'<td>{h(p.citation)}<br>{h(p.population_scope)}<br>{h(p.notes)}</td></tr>')
    baselines = ''.join(f'<tr><th scope="row">{h(b.outcome.replace("_", " "))}</th><td>{b.value}</td><td>{h(b.unit)}</td>'
                        f'<td>{h(b.population)}<br>{h(b.citation)}<br>{h(b.notes)}</td></tr>'
                        for b in parts['baselines'].values())
    references = ''.join(f'<li id="source-{h(key)}"><strong>{h(key)}</strong>: {h("; ".join(parse_authors(e.fields.get("author", ""))))}. '
                         f'{h(_clean_latex(e.title))} ({h(e.year)}). {h(_clean_latex(e.fields.get("journal", e.fields.get("publisher", ""))))}.</li>'
                         for key, e in sorted(parts['bib'].items()))
    csv_uri = 'data:text/csv;charset=utf-8,' + quote((directory / 'parameters.csv').read_text())
    digest = reference_result_digest(result)
    return f'''<!doctype html>
<!-- Generated companion: @link:script-build-methods-html; @link:paper-methods; @link:doc-paper. @tag:methods -->
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Downstream methods and evidence</title><style>
:root{{color-scheme:light dark}}body{{font:18px/1.65 system-ui,sans-serif;margin:0 auto;padding:2rem 1.2rem;max-width:1000px}}
a{{text-underline-offset:.2em}}h1,h2,h3{{line-height:1.25}}nav a{{display:inline-block;margin:0 .8rem .6rem 0}}
table{{border-collapse:collapse;width:100%;font-size:15px}}th,td{{border:1px solid #888;padding:.6rem;vertical-align:top;text-align:left}}
caption{{text-align:left;font-weight:600}}summary{{cursor:pointer;font-size:.9em;font-weight:400}}code{{font-size:.85em;overflow-wrap:anywhere}}.scroll{{overflow:auto}}.notice{{border-left:4px solid #777;padding:1rem;background:Canvas}}
:focus-visible{{outline:3px solid #777;outline-offset:3px}}@media print{{body{{font-size:11pt}}nav{{display:none}}table{{font-size:8pt}}}}
</style></head><body><a href="#main">Skip to methods</a><header><h1>Downstream methods and evidence</h1>
<p>Engine {h(__version__)} · parameter set {h(params.version)}. Reproducible reference calculations for displacement consequences.</p>
<nav aria-label="Methods sections"><a href="#scope">Scope</a><a href="#counts">Count calculations</a><a href="#uncertainty">Uncertainty</a>
<a href="#persistence">Mortality persistence</a><a href="#cohorts">Cohorts and households</a><a href="#validation">Validation</a><a href="#parameters">Parameters</a><a href="#baselines">Baselines</a><a href="#references">Sources</a></nav></header>
<main id="main" tabindex="-1"><section id="scope"><h2>Scope and interpretation</h2><p class="notice">Default results are illustrative reference calculations.
They are conditional modeled expected differences, not forecasts about identified people, observed attributable counts, or identified policy effects.
Target-cohort applicability requires structured demographics and a reviewed transport decision. Grandchild and later earnings outcomes are structural projections.</p>
<p>Worker displacement, net tradable-job loss, and changes in immigration exposure are distinct inputs. A displacement count does not establish either of the other exposures.
The mortality response comes from high-tenure male workers exposed to Pennsylvania mass layoffs in the early 1980s. The selected baseline is US men aged 45–54 in 2015–2019.
The child earnings estimate concerns Canadian father-son pairs after firm closure. Moving those estimates to another population, place or period requires an explicit transport rationale.</p>
<p>Each causal chain preserves citations, evidence roles and composition kinds. Relative earnings gaps transmit in gap space rather than by multiplying income levels.
The same intergenerational earnings relationship is reused at each generation; it has one shared uncertainty draw.
The implemented log_elasticity_transmission ensemble variant compares the finite-change v**t mapping with the default linear gap rule,
using the same coefficient. Both are structural transmission assumptions, not independently identified intervention responses.</p></section>
<section id="counts"><h2>Count calculations</h2><h3>Mortality</h3><p>{h(source_profile_contract()['description'])}</p>
<p>For annual event/person-year rate λ, annual risk m = 1 − exp(−λ). For odds ratio r, exposed annual risk q = r m / (1 − m + r m).
Expected excess deaths = N × (counterfactual survival − exposed survival). Counterfactual survival is (1 − m) raised to the follow-up years;
exposed survival is the product of (1 − q) raised to each phase duration. Deaths deplete the surviving cohort.
Fractional durations assume constant hazards within a phase. The five phases cover offsets 0, +1, +2–3, +4–5 and +6 onward.</p>
<p>Demographic profiles must match the admitted male 45–54 all-cause response. Other baseline rates do not establish effect transport.
An explicit profile takes precedence over county mortality. County rates require compatible sex, age, cause, calendar window and national prior,
and a Gamma–Poisson posterior verified against deaths and person-years. Suppressed counties remain absent; national fallback is disclosed.</p>
<h3>Unknown-covariance diagnostic</h3><p>The separate additive-coefficient diagnostic uses marginal standard errors without inventing covariance.
For one contrast T = sum(aᵢ βᵢ), let lᵢ = |aᵢ| SEᵢ. Its sharp standard-error bounds over compatible positive-semidefinite covariance matrices are
max(0, 2 max(lᵢ) − sum(lᵢ)) and sum(lᵢ). A Gram-vector representation proves attainability by alignment or polygon closure.
The point ± 1.96 times the upper bound is an outer normal-approximation envelope, not a source-reported interval or simultaneous band.
Separate phase extrema need not be jointly attainable. This diagnostic does not replace the production mortality profile or create joint survival draws.</p>
<h3>Child lifetime earnings</h3><p>Undiscounted lifetime loss = displaced workers × children per worker × relative adult earnings gap × the cited US male synthetic career earnings baseline.
This is a lifetime dollar amount in 2024 dollars, not an annual loss. The baseline sums cross-sectional age-band medians and approximates individual lifetime sums;
it excludes nonworking years. The Canadian father-son effect and US dollar conversion each require a transport decision.</p>
<p>The source child cohort is boys aged 10–14 at paternal displacement. Known age/sex mismatches block the child-dollar count;
unknown child profiles cannot qualify for reviewed headline use. Optional income-quartile contrasts retain every reported coefficient and its uncertainty,
including null and beneficial possibilities. Quartiles refer to father's average pre-displacement income in 1978–1979 and require an explicit target-rank definition.</p>
<p>Optional child valuation requires known child ages, a real discount rate and a valuation year equal to the event year.
Annual synthetic career earnings are discounted by (1+r) raised to years after that date, with dollars kept in 2024 purchasing power.
The observed adult-age window (25–33) is shown separately from the constant-gap career projection (20–64).
Neither recovers a source-identified annual earnings path; the career path extrapolates beyond observed ages. Zero-rate career valuation matches the undiscounted reference.</p>
<h3>Receiving-community comparisons</h3><p>The receiving-community command uses separate source-specific shares.
Light–Miller applies a percentage-point change in undocumented population share to log violent-crime rates.
Bianchi applies a log regular-resident share ratio to log total-crime rates. Both population denominators must be retained.
Source windows and conditional fixed-effects versus IV roles remain distinct. Optional count differences use the same post population
in both annual endpoint rate scenarios. No displaced-worker-to-arrival bridge, cumulative-crime extrapolation or additive crime total is supplied.</p>
<p>With reference/post shares s₀ and s₁, Light–Miller uses exp(100 β (s₁ − s₀)); Bianchi uses exp(β log(s₁/s₀)) and requires positive shares.
For baseline b incidents per 100,000 and post population P₁, the endpoint difference is (b P₁ / 100000) × (rate ratio − 1).
The arithmetic rate interpretation assumes an unchanged residual retransformation factor. Correct source units do not establish target transport.</p>
<h3>Local service jobs</h3><p>Local service jobs lost = T × ℓ, where T is independently documented net local loss of tradable jobs and ℓ is the multiplier for a declared job class.
Manufacturing and high-tech multipliers represent different classes, not endpoints of one uncertainty interval. The tradable-share field is metadata and does not infer T from displaced workers.</p>
<h3>Reference example</h3><p>For 1,000 displaced workers, two children per worker and 20 years of mortality follow-up,
the shipped national reference produces {result['modeled']['excess_deaths']['point']:,.2f} expected excess deaths and
${result['modeled']['child_lifetime_earnings_lost_usd']['point']:,.2f} undiscounted child lifetime earnings loss.
Both are illustrative and ineligible for public headline treatment until applicability is reviewed. Service-job losses remain blocked without a separate net-job input and job class.</p></section>
<section id="uncertainty"><h2>Uncertainty and dependence</h2><p>Low/high values are parameter-support envelopes, not confidence intervals.
Monte Carlo p05–p95 is a central 90% interval for parameter uncertainty only. Exposure, baseline estimates, county measurements and pooling weights are held fixed;
unmodeled pathways and structural uncertainty are excluded. Latin hypercube sampling preserves marginal coverage; declared correlations use Iman–Conover rank induction.
Repeated relationship aliases share exactly one draw. Sobol attribution groups them, and dependent parameters are reported as joint blocks.
Independent-step analytic moments refuse repeated shared variables. Predictive mortality, where available, adds binomial cohort variation in separately simulated exposed and counterfactual cohorts;
their contrast is not an observable paired individual causal effect.</p>
<p>Per-result effect-removal and one-input source-endpoint experiments refit the same scenario while retaining all other inputs and admission gates.
A neutral ratio is one; additive/job and place-coefficient removal uses zero where the outcome defines it. Removal changes need not sum because propagation is nonlinear,
and removal can leave observed support. These are hypothetical comparisons, not causal shares. Endpoint spans are not variance indices, and fixed inputs acquire no inferred distribution.</p>
<p>A separate experimental uncertainty command samples a documented national event/person-time baseline using a Poisson likelihood and
declared Jeffreys rate prior: Gamma(events + 0.5, rate = person-years). Baseline counts must reproduce the verified rate and match its
sex, age, cause, calendar window and geography. Exposure is a caller-declared discrete uniform over integer bounds;
it is a sensitivity assumption, not an inferred confidence distribution. Baseline, exposure and study parameters are assumed independent.
Expected-effect intervals, independent-cohort process contrasts and the original fixed-input reference remain separate.
The budget requires national source-profile mortality, excludes demographic-profile overrides, and does not sample county posteriors,
transport error, age/time trends or probabilities over structural models.</p></section>
<section id="persistence"><h2>Mortality persistence sensitivity</h2>
<p>The default source-profile calculation also reports a declared alternative that retains the early odds ratios and sets source offset +6 onward to OR=1,
first changing follow-up year seven. Both structures use the same resolved baseline, exposure and horizon.
For the 1,000-worker, 20-year national reference, the source profile gives {persistence['variants']['source_profile']['point']:,.2f} expected excess deaths
and the no-sustained-excess alternative gives {persistence['variants']['no_sustained_excess']['point']:,.2f}.</p>
<p>The alternative is motivated by the long-run divergence recorded for <a href="#source-eliasonstorrie2009">Eliason–Storrie</a>.
It is a hybrid structural assumption, not a reproduction of the Swedish study or a substitution of its hazard ratios for
<a href="#source-sullivan2009">Sullivan–von Wachter</a> odds ratios. A nonsignificant estimate does not establish an exactly zero effect.
The cutoff follows the source profile, not the Swedish study's windows; persistence beyond its 12-year follow-up remains an assumption.</p>
<p>Scenario Monte Carlo reports separate parameter-only intervals within each structure and a difference calculated on shared parameter draws.
The range across their point estimates is not a confidence interval or a bound on the true effect; no probabilities or averaging weights are assigned to the structures.
The source estimate remains unchanged. Both structures retain fixed-baseline aging and population-transport limits, and the sensitivity report is ineligible for a validated public headline.</p></section>
<section id="cohorts"><h2>Cohorts, aging and household comparisons</h2>
<p>The pinned CPS January-2024 reference reproduces the published BLS known-year displacement total and includes separate three- and six-year-tenure cohorts.
Interview age and household composition are not historical event characteristics, and these reference cohorts do not identify H-1B displacement.</p>
<p>The mortality-cohort command aggregates sourced male age-group contrasts exactly and compares aging age-band baselines with fixed baselines.
Its response support is men aged 30–69 at mass layoff or firm closure with at least six years of tenure.
It requires a declared constant projection of Table 7 source-window annual-logit responses, distinct from the default Table 5 phase profile.
Event age selects the response, which stays fixed as survivors age through 2015–2019 period-rate bands.
Uncovered workers remain unknown; partial coverage never becomes a whole-cohort total. These are Cartesian envelopes of marginal coefficient ranges,
not simultaneous confidence bands. They exclude baseline
variance, exposure error, cross-coefficient covariance and transport error, and are ineligible for public headlines.</p>
<p>The household command compares annual employment-state probabilities and gross earnings under a supplied unemployment duration.
It calculates member marginal expectations exactly over one to five years, reusing observed SIPP 2021–2022 conditional transitions under
stationarity and Markov assumptions, not an identified displacement recovery curve. Adults stay within ages 25–54; children age without an inferred earnings effect.
Any reemployment earnings multipliers are declared assumptions. Sparse cells require explicit acceptance and no full household prediction interval is claimed;
partner responses, joint household outcomes, taxes/transfers, savings, marriage, fertility and protective interventions remain unmodeled.</p>
<p>The uncertainty command adds documented national baseline count uncertainty, a declared integer exposure distribution and binomial variation to parameter draws.
It states the Poisson/Gamma model and component-independence assumptions. Transport error and structural model probabilities remain excluded;
parameter-only results and independent-cohort process contrasts retain separate labels.</p></section>
<section id="validation"><h2>Validation status</h2><p>V0 checks internal consistency; it does not validate the model against an independent event.
V1 historical transport diagnostics use the same five-phase mortality calculation as production, but population differences and fit failures remain visible.
Independent-event V2 and prospective V3 validation have not been established. Code repairs and passing tests do not supply missing empirical validation.</p></section>
<section id="scorecard"><h2>Current mortality scorecard</h2>
<p>Measured points lie inside the modeled bands for {mortality_covered} of {len(mortality)} mortality variants.
These compare modeled mortality with a male–female differential; the population/outcome mismatch limits interpretation.
Point coverage is neither a test against the measured confidence interval nor evidence of causal validity.</p>
<div class="scroll" role="region" aria-label="Mortality validation scorecard" tabindex="0"><table>
<caption>Excess deaths per 100,000 adults per unit shock</caption><thead><tr><th scope="col">Variant</th>
<th scope="col">Model point [band]</th><th scope="col">Measured point</th><th scope="col">Covered?</th></tr></thead>
<tbody>{mortality_rows}</tbody></table></div>
<p>The archived October 14 expanded evaluation reports a cohort reproduction difference of {cohort_check['difference']:,.4f} workers
against the published {cohort_check['published_workers']:,}-worker benchmark, within its {cohort_check['tolerance']:,}-worker rounding tolerance.
The SIPP baseline check includes {sipp_check['heldout_calibration_cells']} held-out calibration cells;
the largest absolute transition-probability difference is {sipp_check['heldout_max_abs_diff']:.4f}.
There are {len(synthesis['reports'])} compatible pooled reports and {len(synthesis['blocked'])} explicit pooling refusals.
These are archived descriptive reproduction/baseline checks, not causal displacement validation or a new independent-event score.</p>
<p>The evidence selection protocol is locally frozen research work, not retrospective preregistration or an independently timestamped forecast.
The archived results are retained in validation/followthrough_evaluation_expanded_20261014.json.</p></section>
<section id="consumer"><h2>Consumer scaling and mixtures</h2><p>Declared display factor s multiplies expected outcomes and corresponding experiments; output variance scales by s².
Compatible mixtures use sum(wₖ E[Xₖ]) while retaining every baseline and applicability decision. Linearity of expectation does not require independence,
but does not identify a joint distribution. Quantiles and variance indices cannot generally be averaged. A positive-weight unavailable component withholds the total.
Joint mixture intervals remain unavailable until a joint draw/dependence calculation exists.</p>
<p>The code and admitted data define behavior. The paper explains the mathematics; <a href="readme.md">software guides</a> describe calling contracts and integration.</p></section>
<section id="parameters"><h2>Parameter inventory</h2><p><a download="downstream-parameters.csv" href="{csv_uri}">Download the complete parameter CSV with full identifiers, precision and notes</a>.</p>
<div class="scroll" role="region" aria-label="Parameter inventory" tabindex="0"><table><caption>Parameter support bands, destination units and evidence roles</caption>
<thead><tr><th scope="col">Relationship and identifier</th><th scope="col">Point [low, high]</th><th scope="col">Unit</th><th scope="col">Evidence role</th><th scope="col">Sources, population and qualifications</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></section>
<section id="baselines"><h2>Baseline inventory</h2><div class="scroll" role="region" aria-label="Baseline inventory" tabindex="0"><table><caption>Cited absolute-rate and dollar inputs</caption>
<thead><tr><th scope="col">Outcome</th><th scope="col">Value</th><th scope="col">Unit</th><th scope="col">Population, citation and derivation</th></tr></thead><tbody>{baselines}</tbody></table></div></section>
<section id="references"><h2>Source bibliography</h2><p>Inclusion in the bibliography does not establish peer review or independent validation.</p><ol>{references}</ol></section></main>
<footer><p>Generated by scripts/build_methods_html.py. Reference input content SHA-256: <code>{result['input_content_sha256']}</code>.
Reference result SHA-256 (12 significant digits): <code>{digest}</code>.</p></footer></body></html>'''


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    output = ROOT / 'docs/methods.html'
    document = build()
    current = output.read_text() if output.exists() else None
    if args.check and current != document:
        print(f"stale methods HTML: {output}", file=sys.stderr)
        return 1
    if not args.check and current != document:
        output.write_text(document, encoding='utf-8')
    print(output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
