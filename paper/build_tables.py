"""Generate paper data from the current engine; never hand-copy score values."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
# Standalone paper builds resolve the local source tree before these imports.
from downstream.params import load_all, load_correlations  # noqa: E402
from downstream.validate import run  # noqa: E402
from downstream.children import child_line  # noqa: E402

OUT = Path(__file__).resolve().parent / 'generated'


def tex(value):
    replacements = {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$',
                    '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}',
                    '~': r'\textasciitilde{}', '^': r'\textasciicircum{}',
                    '—': '---', '–': '--', '−': '-', '→': r'$\to$'}
    return ''.join(replacements.get(c, c) for c in str(value))


def n(value):
    return f'{value:,.4f}'.rstrip('0').rstrip('.')


def band(row):
    return f"{n(row['point'])} [{n(row['low'])}, {n(row['high'])}]"


def write(name, text):
    path = OUT / name
    # Avoid changing mtimes when content is identical.
    if not path.exists() or path.read_text() != text:
        path.write_text(text, encoding='utf-8')


def plot_data(name, rows):
    """Keep plot coordinates unrounded and in the same units as the scorecard."""
    lines = ['row point low high measured']
    for index, (modeled, measured) in enumerate(rows):
        lines.append(' '.join(str(v) for v in
                              (index, modeled['point'], modeled['low'],
                               modeled['high'], measured)))
    write(name, '\n'.join(lines) + '\n')
    values = [value for modeled, measured in rows for value in (modeled['point'], modeled['low'], modeled['high'], measured)]
    lo, hi = min(0, min(values)), max(0, max(values))
    span = max(hi - lo, 1e-9)
    scale = 10 ** math.floor(math.log10(span / 5))
    step = next(multiplier * scale for multiplier in (1, 2, 5, 10) if multiplier * scale >= span / 5)
    lower = 0 if lo == 0 else math.floor((lo - .03 * span) / step) * step
    upper = 0 if hi == 0 else math.ceil((hi + .03 * span) / step) * step
    write(name.replace('.dat', '_limits.tex'),
          f"\\def\\PlotMin{{{lower:g}}}\n\\def\\PlotMax{{{upper:g}}}\n\\def\\PlotStep{{{step:g}}}\n")


def main():
    OUT.mkdir(exist_ok=True)
    parts = load_all(ROOT / 'params')
    ps = parts['params']
    validation = run(ps)
    correlations = load_correlations(ROOT / 'params/correlations.csv')
    source_files = sorted(p for directory in ('src/downstream', 'params', 'validation')
                          for p in (ROOT / directory).rglob('*')
                          if p.is_file() and (p.suffix in {'.py', '.csv', '.bib', '.json', '.xml', '.txt', '.md'}
                                             or p.name == 'VERSION'))
    # Include the manuscript, generator, and build configuration; generated
    # output is excluded to avoid a self-referential content hash.
    source_files = sorted(set(source_files) | set((ROOT / 'paper/figures').glob('*.tex')) | {
        ROOT / 'paper/downstream.tex', ROOT / 'paper/build_tables.py',
        ROOT / 'paper/review_references.bib', ROOT / 'paper/Makefile',
        ROOT / 'pyproject.toml', ROOT / 'uv.lock', ROOT / 'scripts/build_methods_html.py',
    })
    digest = hashlib.sha256()
    for path in source_files:
        digest.update(str(path.relative_to(ROOT)).encode() + b'\0' + path.read_bytes())
    write('results.json', json.dumps({'parameter_set_version': ps.version,
          'source_sha256': digest.hexdigest(), 'source_manifest': [str(p.relative_to(ROOT)) for p in source_files], 'declared_correlation_pairs': len(correlations), 'validation': validation}, indent=2) + '\n')
    macros = [r'\newcommand{\CorrelationCount}{' + str(len(correlations)) + '}',
              r'\newcommand{\ParameterVersion}{' + tex(ps.version) + '}',
              r'\newcommand{\ParameterCount}{' + str(len(ps.parameters)) + '}',
              r'\newcommand{\SourceDigest}{' + digest.hexdigest()[:16] + '}',
              r'\newcommand{\PanelCount}{' + str(validation['v1_panel']['panel']['cz_periods']) + '}']
    for name, ledger in child_line(ps).items():
        if name in {'child', 'grandchild', 'greatgrandchild'}:
            macros.append('\\newcommand{\\' + name.title() + 'Point}{' + n(ledger.point) + '}')
    v0 = validation['v0_internal_consistency']
    macros += [r'\newcommand{\VzeroDirect}{' + band(v0['direct']) + '}',
               r'\newcommand{\VzeroComposed}{' + band(v0['ige_composed']) + '}']
    write('macros.tex', '\n'.join(macros) + '\n')

    rows = []
    for p in ps.parameters:
        refs = ','.join(k.strip() for k in p.citation.split(';'))
        rows.append(tex(p.link.replace('_', ' ').replace('->', ' → ')) + ' & ' + band(vars(p)) + ' & ' +
                    tex(p.tier).replace('-', r'-\allowbreak ') + r' & \cite{' + refs + r'} \\')
    write('parameters.tex', '\n'.join(rows) + '\n')
    rows = []
    for b in parts['baselines'].values():
        rows.append(tex(b.outcome.replace('_', ' ')) + ' & ' +
                    (f'{b.value:,.6f}'.rstrip('0').rstrip('.') if b.value is not None else 'pending') + ' & ' +
                    tex(b.population) + r' \\')
    write('baselines.tex', '\n'.join(rows) + '\n')
    rows = []
    for r in validation['v1_retrodict']['scored']:
        rows.append(tex(r['variant'].replace('_', ' ')) + ' & ' + band(r['modeled_excess_deaths_per100k']) +
                    ' & ' + n(r['measured_differential_per100k']['point']) + ' & ' +
                    ('yes' if r['measured_inside_modeled_band'] else 'no') + r' \\')
    write('mortality.tex', '\n'.join(rows) + '\n')
    rows = []
    labels = ['Divorce, pooled (pp)', 'Divorce, male shock (pp)', 'Earnings, direct (USD)',
              'Earnings, with spillover (USD)']
    for label, r in zip(labels, validation['v1_panel']['tercile_tests'], strict=True):
        unit = 'usd' if 'modeled_gap_usd' in r else 'pp'
        rows.append(label + ' & ' + band(r[f'modeled_gap_{unit}']) + ' & ' +
                    n(r[f'measured_gap_{unit}']) + ' & ' +
                    ('yes' if r['measured_inside_modeled_band'] else 'no') + r' \\')
    write('panel.tex', '\n'.join(rows) + '\n')
    plot_data('mortality_plot.dat', [
        (r['modeled_excess_deaths_per100k'], r['measured_differential_per100k']['point'])
        for r in validation['v1_retrodict']['scored']])
    plot_data('divorce_plot.dat', [
        (r['modeled_pp_women'], r['measured_pp_women']['point'])
        for r in validation['v1_retrodict']['scored_divorce']['windows']])
    panel = validation['v1_panel']['tercile_tests']
    plot_data('panel_divorce_plot.dat', [
        (r['modeled_gap_pp'], r['measured_gap_pp']) for r in panel[:2]])
    plot_data('panel_earnings_plot.dat', [
        (r['modeled_gap_usd'], r['measured_gap_usd']) for r in panel[2:]])
    rows = []
    for r in validation['v1_retrodict']['scored_divorce']['windows']:
        rows.append(n(r['window_years']) + ' & ' + band(r['modeled_pp_women']) + ' & ' +
                    n(r['measured_pp_women']['point']) + r' \\')
    write('divorce.tex', '\n'.join(rows) + '\n')
    slope = validation['v1_panel']['slope_scoring']
    write('slope.tex', f"The model median slope is {n(slope['model_slope_pp_per_pp']['p50'])} "
          f"against an observed slope of {n(slope['observed_slope'])}. "
          f"CRPS is {n(slope['crps'])} in percentage-point units; PIT is {n(slope['pit'])}.\n")
    # Serialize parsed bibliography fields; exclude extraction notes from printed references.
    bib = []
    for key, entry in parts['bib'].items():
        fields = {k: v for k, v in entry.fields.items()
                  if k in {'author', 'title', 'journal', 'year', 'volume', 'number', 'pages',
                           'publisher', 'booktitle', 'institution'}}
        bib.append('@' + entry.kind + '{' + key + ',\n' +
                   '\n'.join('  ' + k + ' = {' + v + '},' for k, v in fields.items()) + '\n}\n')
    write('references.bib', '\n'.join(bib))


if __name__ == '__main__':
    main()
