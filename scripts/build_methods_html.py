"""Build a self-contained, semantic HTML companion to the methods paper."""
from __future__ import annotations

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


def build(params_dir=None):
    directory = Path(params_dir) if params_dir else ROOT / 'params'
    parts = load_all(directory)
    params = parts['params']
    result = compute_counts(params, parts['baselines'], ScenarioInput(1000))
    h = escape
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
    digest = hashlib.sha256(json.dumps(result, sort_keys=True, allow_nan=False).encode()).hexdigest()
    return f'''<!doctype html>
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
<a href="#validation">Validation</a><a href="#parameters">Parameters</a><a href="#baselines">Baselines</a><a href="#references">Sources</a></nav></header>
<main id="main" tabindex="-1"><section id="scope"><h2>Scope and interpretation</h2><p class="notice">Default results are illustrative reference calculations.
They are conditional modeled expected differences, not forecasts about identified people, observed attributable counts, or identified policy effects.
Target-cohort applicability requires structured demographics and a reviewed transport decision. Grandchild and later earnings outcomes are structural projections.</p>
<p>Worker displacement, net tradable-job loss, and changes in immigration exposure are distinct inputs. A displacement count does not establish either of the other exposures.
The mortality response comes from high-tenure male workers exposed to Pennsylvania mass layoffs in the early 1980s. The selected baseline is US men aged 45–54 in 2015–2019.
The child earnings estimate concerns Canadian father-son pairs after firm closure. Moving those estimates to another population, place or period requires an explicit transport rationale.</p>
<p>Each causal chain preserves citations, evidence roles and composition kinds. Relative earnings gaps transmit in gap space rather than by multiplying income levels.
The same intergenerational earnings relationship is reused at each generation; it has one shared uncertainty draw.</p></section>
<section id="counts"><h2>Count calculations</h2><h3>Mortality</h3><p>{h(source_profile_contract()['description'])}</p>
<p>For annual event/person-year rate λ, annual risk m = 1 − exp(−λ). For odds ratio r, exposed annual risk q = r m / (1 − m + r m).
Expected excess deaths = N × (counterfactual survival − exposed survival). Counterfactual survival is (1 − m) raised to the follow-up years;
exposed survival is the product of (1 − q) raised to each phase duration. Deaths deplete the surviving cohort.
Fractional durations assume constant hazards within a phase. The five phases cover offsets 0, +1, +2–3, +4–5 and +6 onward.</p>
<p>Demographic profiles must match the admitted male 45–54 all-cause response. Other baseline rates do not establish effect transport.
An explicit profile takes precedence over county mortality. County rates require compatible sex, age, cause, calendar window and national prior,
and a Gamma–Poisson posterior verified against deaths and person-years. Suppressed counties remain absent; national fallback is disclosed.</p>
<h3>Child lifetime earnings</h3><p>Undiscounted lifetime loss = displaced workers × children per worker × relative adult earnings gap × the cited US male synthetic career earnings baseline.
This is a lifetime dollar amount in 2024 dollars, not an annual loss. The baseline sums cross-sectional age-band medians and approximates individual lifetime sums;
it excludes nonworking years. The Canadian father-son effect and US dollar conversion each require a transport decision.</p>
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
their contrast is not an observable paired individual causal effect.</p></section>
<section id="validation"><h2>Validation status</h2><p>V0 checks internal consistency; it does not validate the model against an independent event.
V1 historical transport diagnostics use the same five-phase mortality calculation as production, but population differences and fit failures remain visible.
Independent-event V2 and prospective V3 validation have not been established. Code repairs and passing tests do not supply missing empirical validation.</p></section>
<section id="parameters"><h2>Parameter inventory</h2><p><a download="downstream-parameters.csv" href="{csv_uri}">Download the complete parameter CSV with full identifiers, precision and notes</a>.</p>
<div class="scroll" role="region" aria-label="Parameter inventory" tabindex="0"><table><caption>Parameter support bands, destination units and evidence roles</caption>
<thead><tr><th scope="col">Relationship and identifier</th><th scope="col">Point [low, high]</th><th scope="col">Unit</th><th scope="col">Evidence role</th><th scope="col">Sources, population and qualifications</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></section>
<section id="baselines"><h2>Baseline inventory</h2><div class="scroll" role="region" aria-label="Baseline inventory" tabindex="0"><table><caption>Cited absolute-rate and dollar inputs</caption>
<thead><tr><th scope="col">Outcome</th><th scope="col">Value</th><th scope="col">Unit</th><th scope="col">Population, citation and derivation</th></tr></thead><tbody>{baselines}</tbody></table></div></section>
<section id="references"><h2>Source bibliography</h2><p>Inclusion in the bibliography does not establish peer review or independent validation.</p><ol>{references}</ol></section></main>
<footer><p>Generated by scripts/build_methods_html.py. Reference input content SHA-256: <code>{result['input_content_sha256']}</code>.
Reference result SHA-256: <code>{digest}</code>.</p></footer></body></html>'''


if __name__ == '__main__':
    output = ROOT / 'docs/methods.html'
    document = build()
    if not output.exists() or output.read_text() != document:
        output.write_text(document, encoding='utf-8')
    print(output)
