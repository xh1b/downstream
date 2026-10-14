"""The local UI must preserve engine data and edit only its linear exposure scale."""
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "examples" / "calculator"


def generated():
    spec = importlib.util.spec_from_file_location(
        "calculator_builder", ROOT / "scripts" / "build_calculator_prototype.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build()


def payload(html):
    return json.loads(re.search(
        r'<script id="engine-data" type="application/json">(.*?)</script>', html, re.S)[1])


def test_generated_html_matches_current_engine_and_preserves_full_receipt():
    html = generated()
    assert (DIRECTORY / "index.html").read_text() == html
    data = payload(html)
    result = data["result"]
    assert data["reference_exposure"] == result["exposure"]["displaced_workers"] == 1000
    assert result["engine_version"] == "0.4.0"
    assert len(result["modeled"]["excess_deaths"]["sensitivity"]["effect_drivers"]) == 5
    assert result["blocked"]
    assert all(not row["applicability"]["eligible_for_public_headline"]
               for row in result["modeled"].values())
    assert result["input_content_sha256"]
    assert "not a confidence interval" in html
    assert "Human comprehension testing is pending" in html
    assert not re.search(r'<(?:script|link)[^>]+(?:src|href)="https?://', html)


def test_controls_have_labels_and_sources_are_embedded():
    html = generated()
    for control in ("exposure", "outcome"):
        assert f'for="{control}"' in html
        assert f'id="{control}"' in html
    assert 'role="alert"' in html
    assert 'aria-live="polite"' in html
    assert 'prefers-reduced-motion' in html
    assert 'max-width:760px' in html


@pytest.mark.parametrize("exposure", [0, .125, 500, 1000000])
def test_exposure_scaling_matches_independent_engine_refits(exposure):
    from downstream.params import load_all
    from downstream.scenario import ScenarioInput, compute_counts

    seed = payload(generated())["result"]
    parts = load_all()
    refit = compute_counts(parts["params"], parts["baselines"], ScenarioInput(exposure))
    scale = exposure / 1000
    for outcome, source in seed["modeled"].items():
        actual = refit["modeled"][outcome]["sensitivity"]
        expected = source["sensitivity"]
        assert actual["reference_point"] == pytest.approx(expected["reference_point"] * scale)
        actual_drivers = {driver["input_id"]: driver for driver in actual["effect_drivers"]}
        for source_driver in expected["effect_drivers"]:
            actual_driver = actual_drivers[source_driver["input_id"]]
            assert actual_driver["input_value"] == source_driver["input_value"]
            for key in ("point", "reference_minus_variant"):
                assert actual_driver["effect_removed"][key] == pytest.approx(
                    source_driver["effect_removed"][key] * scale)
            for key in ("outcome_low", "outcome_high"):
                assert actual_driver["supported_range"][key] == pytest.approx(
                    source_driver["supported_range"][key] * scale)


@pytest.mark.skipif(shutil.which("node") is None, reason="Node not installed")
def test_js_controls_scaling_invalid_input_direction_and_coverage():
    # Unit-level DOM double: verifies event behavior, not visual/browser accessibility.
    harness = r'''
const fs = require("fs"), vm = require("vm"), assert = require("assert");
class Element {
  constructor() {this.children=[];this.events={};this.style={};this.dataset={};this.attributes={};this.value="";this.textContent="";}
  append(...items) {this.children.push(...items);}
  replaceChildren(...items) {this.children=items;}
  setAttribute(k,v) {this.attributes[k]=v;}
  addEventListener(k,fn) {this.events[k]=fn;}
  insertBefore(item,before) {this.children=this.children.filter(x=>x!==item);this.children.splice(this.children.indexOf(before),0,item);}
}
const html=fs.readFileSync(process.argv[1],"utf8"), app=fs.readFileSync(process.argv[2],"utf8");
const ids={};for(const m of html.matchAll(/id="([^"]+)"/g)) ids[m[1]]=new Element();
ids["engine-data"].textContent=html.match(/<script id="engine-data" type="application\/json">([\s\S]*?)<\/script>/)[1];
ids.exposure.value="1000";ids.outcome.value="excess_deaths";
const radios=[new Element(),new Element()];radios[0].value="comparison";radios[1].value="sensitivity";
ids.results.children=[new Element(),ids.comparison,ids.sensitivity,new Element()];
const document={getElementById:id=>ids[id],createElement:()=>new Element(),querySelectorAll:()=>radios,body:new Element()};
vm.runInNewContext(app,{document,console});
const reference=JSON.parse(ids["engine-data"].textContent).result;
const format=x=>x.toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2});
assert.equal(ids["event-value"].textContent,format(reference.modeled.excess_deaths.sensitivity.reference_point));
assert.equal(ids["driver-list"].children.length,5);
ids.exposure.value="0";ids.exposure.events.input();assert.equal(ids["event-value"].textContent,"0.00");
ids.exposure.value="0.125";ids.exposure.events.input();
assert.equal(ids["event-value"].textContent,format(reference.modeled.excess_deaths.sensitivity.reference_point*.125/1000));
for(const invalid of ["", "-1", "Infinity", "1000001"]) {
 const old=ids["event-value"].textContent;ids.exposure.value=invalid;ids.exposure.events.input();
 assert.equal(ids["event-value"].textContent,old);assert.equal(ids.exposure.attributes["aria-invalid"],"true");assert.equal(ids["input-error"].hidden,false);
}
ids.reset.events.click();assert.equal(ids.exposure.value,"1000");assert.equal(ids["input-error"].hidden,true);
radios[1].events.change();assert.equal(document.body.dataset.direction,"sensitivity");assert.equal(ids.results.children[1],ids.sensitivity);
radios[0].events.change();assert.equal(ids.results.children[1],ids.comparison);
ids.outcome.value="child_lifetime_earnings_lost_usd";ids.outcome.events.change();
assert.ok(ids["event-value"].textContent.startsWith("$"));assert.equal(ids["driver-list"].children.length,1);
assert.ok(ids["fixed-description"].textContent.includes("unknown"));
assert.ok(ids.blocked.children.length>1);assert.equal(JSON.parse(ids.receipt.textContent).engine_version,"0.4.0");
console.log("DOM control checks pass");
'''
    result = subprocess.run(["node", "-e", harness, str(DIRECTORY / "index.html"),
                             str(DIRECTORY / "app.js")], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
