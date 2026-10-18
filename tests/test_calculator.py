# @ref:test-calculator
# Method: @link:doc-calculator.
# Implementation: @link:code-mortality; @link:code-scenario; @link:calculator-math;
# @link:calculator-app; @link:script-build-calculator; @link:script-serve-calculator.
# @tag:calculator @tag:testing
"""Browser equations must match native engine refits, including custom inputs."""
from dataclasses import replace
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess

import pytest

from scripts.build_calculator import same_html

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "calculator"


def generated():
    spec = importlib.util.spec_from_file_location("calculator_builder", ROOT / "scripts/build_calculator.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build()


def payload(html):
    return json.loads(re.search(r'<script id="engine-data" type="application/json">(.*?)</script>', html, re.S)[1])


def node(code, *args):
    result = subprocess.run(["node", "-e", code, *map(str, args)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout


def test_generated_data_freshness_source_identity_and_small_surface():
    html = generated()
    assert same_html((DIRECTORY / "index.html").read_text(), html)
    # Embedded copies reference the unique anchors in their authored sources.
    assert "@ref:" not in html
    for anchor in ("calculator-template", "calculator-math", "calculator-app", "calculator-style"):
        assert f"@link:{anchor}" in html
    data = payload(html)
    assert data["result"]["engine_version"] == "0.4.0"
    assert data["result"]["input_content_sha256"]
    assert len(data["phases"]) == 5
    assert data["child_presets"]["q3"]["point"] > 1
    assert data["browser_math_sha256"]
    assert all(not row["applicability"]["eligible_for_public_headline"] for row in data["result"]["modeled"].values())
    assert "not a confidence interval" in html
    assert "Visual and participant tests remain open" in html
    assert "Choose a visual direction" not in html
    assert "Understand the estimate" not in html
    assert not re.search(r'<(?:script|link)[^>]+(?:src|href)="https?://', html)
    template = (DIRECTORY / "template.html").read_text()
    # Short main surface; method and raw source receipt remain available on demand.
    main = template.split('<details>')[0]
    assert len(re.findall(r"[A-Za-z]+", re.sub(r"<[^>]*>", " ", main))) < 160


def test_numeric_controls_labels_keyboard_and_mobile_provisions():
    html = generated()
    for control in ("workers", "years", "rate", "children", "gap", "earnings"):
        assert f'for="{control}"' in html
        assert f'id="{control}"' in html
    for text in ('role="alert"', 'aria-live="polite"', 'prefers-reduced-motion', 'max-width:760px', 'aria-label="Father income group"'):
        assert text in html


def test_symbol_controls_and_tables_have_readable_accessible_names():
    from html.parser import HTMLParser

    class Elements(HTMLParser):
        def __init__(self):
            super().__init__()
            self.elements = []

        def handle_starttag(self, tag, attrs):
            self.elements.append((tag, dict(attrs)))

    parser = Elements()
    parser.feed(generated())
    ids = {attrs['id']: (tag, attrs) for tag, attrs in parser.elements if 'id' in attrs}
    assert ids['neutral'][1]['aria-label'] == 'Set all mortality odds ratios to one'
    assert 'source offset six' in ids['tail-null'][1]['aria-label']
    assert ids['child-loss'][1]['aria-live'] == 'polite'
    labels = [attrs.get('aria-label') for tag, attrs in parser.elements if tag == 'table']
    assert 'Expected deaths under current assumptions' in labels
    assert 'Child earnings under current assumptions' in labels


@pytest.mark.skipif(shutil.which("node") is None, reason="Node not installed")
def test_browser_math_matches_independent_native_refits():
    from downstream.params import load_all
    from downstream.scenario import ScenarioInput, compute_counts
    from downstream.worker import mortality_profile
    data = payload(generated())
    defaults = {**data["defaults"], "odds": [p["point"] for p in data["phases"]]}
    cases = [{**defaults, **change} for change in (
        {}, {"workers": 0}, {"workers": .125}, {"workers": 1e-8}, {"years": 0},
        {"years": .125}, {"years": 1}, {"years": 2}, {"years": 4}, {"years": 6}, {"years": 7},
        {"workers": 1e6, "years": 100, "rate": 1}, {"rate": 0}, {"rate": 1e-15},
        {"odds": [1]*5}, {"workers": 1e6, "years": 100, "rate": .003, "odds": [1e-20]*5}, {"odds": [.2, .5, .9, .8, .7]}, {"odds": [.5, 2, .7, 4, .9]},
        {"gap": 1.2, "earnings": 1e6, "children": 3}, {"children": 0}, {"earnings": 0},
        {"gap": data["child_presets"]["q3"]["point"]},
    )]
    out = json.loads(node('const m=require(process.argv[1]); console.log(JSON.stringify(JSON.parse(process.argv[2]).map(x=>m.calculate(x))));', DIRECTORY / 'math.js', json.dumps(cases)))
    parts = load_all()
    links = [p.link for p in mortality_profile(parts["params"]).values()]
    for x, actual in zip(cases, out):
        params = parts["params"]
        for link, odds in zip(links, x["odds"]):
            params = params.with_param(link, odds)
        params = replace(params, parameters=tuple(
            replace(p, point=x["gap"], low=x["gap"], high=x["gap"])
            if p.link == "displacement->child_earnings" else p for p in params.parameters))
        baselines = dict(parts["baselines"])
        baselines["all_cause_mortality_annual"] = replace(baselines["all_cause_mortality_annual"], value=x["rate"])
        baselines["median_male_lifetime_earnings"] = replace(baselines["median_male_lifetime_earnings"], value=x["earnings"])
        scenario = ScenarioInput(x["workers"], n_children=x["children"], exposure_years=x["years"])
        expected = compute_counts(params, baselines, scenario, _raw=True)
        assert actual["difference"] == pytest.approx(expected["modeled"]["excess_deaths"]["point"], rel=2e-10, abs=1e-18)
        assert actual["childLoss"] == pytest.approx(expected["modeled"]["child_lifetime_earnings_lost_usd"]["point"])
        from downstream.mortality import rate_to_risk
        import math
        assert actual["exposed"] >= 0
        assert actual["baseline"] == pytest.approx(x["workers"] * -math.expm1(-x["rate"] * x["years"]))
        assert actual["annualRisk"] == pytest.approx(rate_to_risk(x["rate"]))
        for i, driver in enumerate(actual["drivers"]):
            variant = compute_counts(params.with_param(links[i], 1), baselines, scenario, _raw=True)["modeled"]["excess_deaths"]["point"]
            assert driver["variant"] == pytest.approx(variant, rel=2e-10, abs=1e-18)
            assert driver["impact"] == pytest.approx(actual["difference"] - variant, rel=1e-8, abs=1e-12)


@pytest.mark.skipif(shutil.which("node") is None, reason="Node not installed")
def test_interactions_recalculate_and_refuse_invalid_inputs():
    harness = r'''
const fs=require("fs"),vm=require("vm"),assert=require("assert"),ids={};
class Element {
 constructor(){this.children=[];this.events={};this.attributes={};this.value="";this.textContent="";}
 set id(v){this._id=v;ids[v]=this;} get id(){return this._id;}
 append(...xs){this.children.push(...xs);} setAttribute(k,v){this.attributes[k]=v;}
 addEventListener(k,v){this.events[k]=v;}
}
const html=fs.readFileSync(process.argv[1],"utf8");
for(const m of html.matchAll(/id="([^"]+)"/g)){const e=new Element();e.id=m[1];}
ids["engine-data"].textContent=html.match(/<script id="engine-data" type="application\/json">([\s\S]*?)<\/script>/)[1];
const data=JSON.parse(ids["engine-data"].textContent);
const document={getElementById:id=>ids[id],createElement:()=>new Element()};
const context=vm.createContext({document,console});
vm.runInContext(fs.readFileSync(process.argv[2],"utf8"),context);
vm.runInContext(fs.readFileSync(process.argv[3],"utf8"),context);
const run=()=>JSON.parse(ids.receipt.textContent).current_calculation;
assert.ok(run().results.baseline>0);assert.ok(run().results.exposed>run().results.baseline);
assert.ok(Math.abs(run().results.difference-data.result.modeled.excess_deaths.sensitivity.reference_point)<1e-9);
assert.equal(ids["risk-rows"].children.length,5);assert.equal(ids.basis.textContent,"Reference assumptions");
ids.workers.value="0.125";ids.workers.events.input();
assert.ok(Number(ids["excess-deaths"].textContent)>0);assert.ok(ids.horizon.textContent.startsWith("0.125 ×"));
assert.ok(run().results.drivers.every(d=>d.impact>0));
ids.years.value="1";ids.years.events.input();assert.equal(run().results.phaseYears[4],0);
assert.equal(ids["impact-4"].textContent,"0.00");
ids.reset.events.click();const original=run().results.difference;
ids.rate.value="10";ids.rate.events.input();assert.notEqual(run().results.difference,original);
assert.ok(ids["baseline-basis"].textContent.startsWith("Custom λ"));
assert.equal(ids.basis.textContent,"Custom assumptions");
ids["tail-null"].events.click();assert.equal(run().inputs.odds[4],1);
ids.neutral.events.click();assert.equal(run().results.difference,0);assert.equal(run().results.baseline,run().results.exposed);
ids.reset.events.click();ids.quartile.value="q3";ids.quartile.events.change();assert.ok(run().results.childLoss<0);
assert.equal(run().selected_child_source.source.study_id,"oreopoulos2008_q3");
ids.children.value="0";ids.children.events.input();assert.equal(run().results.childLoss,0);
ids.reset.events.click();
for(const [field,bad] of [["workers",""],["workers","-1"],["years","101"],["rate","Infinity"],["gap","0"],["children",".5"],["odds-0","0"]]) {
 const old=ids.receipt.textContent;ids[field].value=bad;ids[field].events.input();
 assert.equal(ids.receipt.textContent,old);assert.equal(ids[field].attributes["aria-invalid"],"true");assert.equal(ids["input-error"].hidden,false);
 ids.reset.events.click();
}
ids.workers.value="1e-8";ids.workers.events.input();assert.ok(ids["excess-deaths"].textContent.includes("e-"));
assert.equal(run().inputs.workers,1e-8);assert.ok(ids["death-curve"].attributes.points.length>100);
assert.equal(JSON.parse(ids.receipt.textContent).source_receipt.input_content_sha256,data.result.input_content_sha256);
ids.workers.value="1000000";ids.workers.events.input();
assert.ok(ids["child-loss"].textContent.includes("e+"));
assert.equal(run().inputs.workers,1000000);
assert.ok(ids.blocked.children.length>0);
console.log("interaction checks pass");
'''
    node(harness, DIRECTORY / "index.html", DIRECTORY / "math.js", DIRECTORY / "app.js")


@pytest.mark.skipif(shutil.which("node") is None, reason="Node not installed")
def test_pure_analysis_preserves_inputs_and_mathematical_invariants():
    harness = r'''
const assert = require("node:assert/strict");
const math = require(process.argv[1]);
const data = JSON.parse(process.argv[2]);
const inputs = Object.freeze({...data.defaults,
  odds: Object.freeze(data.phases.map(phase => phase.point))});
const sources = Object.freeze(data.phases.map(phase => Object.freeze(phase)));
const before = JSON.stringify({inputs, sources});
const analysis = math.analyze(inputs, sources);
assert.deepEqual(math.analyze(inputs, sources), analysis);
assert.equal(JSON.stringify({inputs, sources}), before);
assert.equal(analysis.curve[0].difference, 0);
assert.equal(analysis.curve.at(-1).difference, analysis.results.difference);
assert.equal(analysis.curve.at(-1).years, inputs.years);
assert.ok(analysis.curve.every(point => Number.isFinite(point.difference)));
assert.ok(analysis.ranges.every(([low, high]) => low <= high));

// Source offsets are intersections of the horizon with five time intervals.
for (const years of [0, .125, 1, 2, 4, 6, 7, 20, 100]) {
  const durations = math.durations(years);
  assert.equal(durations.reduce((a, b) => a + b, 0), years);
  assert.ok(durations.every(duration => duration >= 0));
  for (let i = 0; i < durations.length; i++) {
    if (durations[i] === 0) {
      const result = math.calculate({...inputs, years});
      assert.equal(result.drivers[i].impact, 0);
    }
  }
}
assert.deepEqual(math.durations(6.5), [1, 1, 2, 2, .5]);

const close = (actual, expected) => assert.ok(
  Math.abs(actual - expected) <= 1e-9 + 1e-10 * Math.abs(expected),
  `${actual} != ${expected}`);
// With one constant odds ratio, the phase product reduces to a single power.
for (const workers of [.125, 1000, 1e6]) {
  for (const rate of [0, .003, .1]) {
    for (const years of [.125, 6.5, 20]) {
      for (const theta of [.2, 1, 3]) {
        const odds = Array(5).fill(theta);
        const actual = math.mortality(workers, rate, odds, years);
        const p = 1 - Math.exp(-rate);
        const q = theta * p / (1 - p + theta * p);
        close(actual.difference, workers * ((1 - p) ** years - (1 - q) ** years));
        close(actual.exposed - actual.baseline, actual.difference);
        close(math.mortality(workers / 4, rate, odds, years).difference, actual.difference / 4);
        assert.ok(Math.abs(actual.difference) <= workers);
        if (theta === 1) assert.equal(actual.difference, 0);
        if (theta < 1) assert.ok(actual.difference <= 0);
        if (theta > 1) assert.ok(actual.difference >= 0);
      }
    }
  }
}
// Increasing any active phase's odds cannot reduce expected excess deaths.
for (let i = 0; i < 5; i++) {
  const odds = inputs.odds.map((value, j) => j === i ? value * 2 : value);
  assert.ok(math.calculate({...inputs, odds}).difference >= analysis.results.difference);
}
assert.deepEqual(math.invalidFields({...inputs, workers: NaN, children: .5,
  odds: [1, 0, 1, Infinity, 1]}), ["workers", "children", "odds-1", "odds-3"]);
assert.deepEqual(math.invalidFields({...inputs, odds: Array(5)}),
  ["odds-0", "odds-1", "odds-2", "odds-3", "odds-4"]);
'''
    node(harness, DIRECTORY / "math.js", json.dumps(payload(generated())))
