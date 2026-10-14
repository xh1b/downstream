"use strict";
const payload = JSON.parse(document.getElementById("engine-data").textContent);
const source = payload.result;
const byId = id => document.getElementById(id);
const number = x => x !== 0 && Math.abs(x) < .01
  ? (Math.abs(x) < 1e-6 ? x.toExponential(2) : x.toLocaleString("en-US", {maximumSignificantDigits:3}))
  : x.toLocaleString("en-US", {minimumFractionDigits:2, maximumFractionDigits:2});
const text = (tag, value) => {const el = document.createElement(tag); el.textContent = value; return el;};
const fields = ["workers", "years", "rate", "children", "gap", "earnings"];
let preset = "overall";
let lastRun;
function readInputs() {
  const values = Object.fromEntries(fields.map(key => [key, byId(key).value.trim() === "" ? NaN : Number(byId(key).value)]));
  values.rate /= 1000;
  values.odds = payload.phases.map((_, i) => byId(`odds-${i}`).value.trim() === "" ? NaN : Number(byId(`odds-${i}`).value));
  return values;
}
function reset() {
  for (const key of fields) byId(key).value = String(payload.defaults[key] * (key === "rate" ? 1000 : 1));
  payload.phases.forEach((phase, i) => {byId(`odds-${i}`).value = String(phase.point);});
  preset = "overall"; byId("quartile").value = preset;
  render();
}
function render() {
  const x = readInputs();
  for (const id of [...fields, ...payload.phases.map((_, i) => `odds-${i}`)]) byId(id).setAttribute("aria-invalid", "false");
  let result;
  try {result = DownstreamMath.calculate(x);}
  catch (error) {
    const id = error.message === "odds" ? payload.phases.map((_, i) => `odds-${i}`).find(id => {
      const value = byId(id).value.trim() === "" ? NaN : Number(byId(id).value);
      return !Number.isFinite(value) || value <= 0 || value > 1e6;
    }) : error.message;
    if (id) byId(id).setAttribute("aria-invalid", "true");
    byId("input-error").textContent = "Check the marked input. Results use the last valid inputs.";
    byId("input-error").hidden = false; return;
  }
  byId("input-error").hidden = true;
  const reference = fields.every(key => x[key] === payload.defaults[key]) && x.odds.every((v, i) => v === payload.phases[i].point);
  byId("basis").textContent = reference ? "Reference assumptions" : "Custom assumptions";
  byId("baseline-basis").textContent = x.rate === payload.defaults.rate
    ? "Reference λ · US · Male · 45–54 · 2015–19"
    : "Custom λ · fixed over T";
  byId("horizon").textContent = `${byId("workers").value.trim()} × ${byId("years").value.trim()} y`;
  byId("baseline-deaths").textContent = number(result.baseline);
  byId("exposed-deaths").textContent = number(result.exposed);
  byId("excess-deaths").textContent = number(result.difference);
  byId("child-gap").textContent = number(result.childGap);
  byId("child-loss").textContent = number(result.childLoss);
  const child = payload.child_presets[preset];
  byId("child-support").textContent = `Source g: ${number(child.low)}–${number(child.high)}.`;
  payload.phases.forEach((phase, i) => {
    byId(`duration-${i}`).textContent = number(result.phaseYears[i]);
    byId(`impact-${i}`).textContent = number(result.drivers[i].impact);
    const endpoint = bound => {
      const odds = [...x.odds]; odds[i] = phase[bound];
      return DownstreamMath.mortality(x.workers, x.rate, odds, x.years).difference;
    };
    byId(`range-${i}`).textContent = `${number(endpoint("low"))}…${number(endpoint("high"))}`;
  });
  const curve = Array.from({length:101}, (_, i) => DownstreamMath.mortality(x.workers, x.rate, x.odds, x.years * i / 100).difference);
  const low = Math.min(0, ...curve), high = Math.max(0, ...curve);
  const span = high - low || 1;
  const y = value => 118 - 106 * (value - low) / span;
  byId("death-curve").setAttribute("points", curve.map((v, i) => `${8 + 884 * i / 100},${y(v)}`).join(" "));
  for (const key of ["y1", "y2"]) byId("zero-line").setAttribute(key, String(y(0)));
  byId("curve-scale").textContent = `ΔD [${number(low)}, ${number(high)}]`;
  byId("curve-end").textContent = `${byId("years").value.trim()} y`;
  lastRun = {schema:"downstream-browser-calculation/1", inputs:x, results:result,
    preset, selected_child_source:payload.child_presets[preset], source_reference:reference, eligibility:"illustrative; target transport not reviewed",
    fixed_baseline:true, child_valuation:"undiscounted constant lifetime gap; child demographics unknown",
    curve:Array.from(curve, (difference, i) => ({years:x.years * i / 100, difference})),
    implementation_sha256:payload.browser_math_sha256};
  byId("receipt").textContent = JSON.stringify({current_calculation:lastRun, source_receipt:source}, null, 2);
}
for (const [i, phase] of payload.phases.entries()) {
  const row = document.createElement("tr");
  row.append(text("td", phase.label), text("td", "")); row.children[1].id = `duration-${i}`;
  const cell = document.createElement("td"), input = document.createElement("input");
  input.id = `odds-${i}`; input.type = "number"; input.min = "0"; input.max = "1000000"; input.step = "any";
  input.setAttribute("aria-label", `Odds ratio, source offset ${phase.label}`);
  input.setAttribute("aria-describedby", "input-error");
  cell.append(input); row.append(cell, text("td", `${number(phase.low)}–${number(phase.high)}`), text("td", ""));
  row.append(text("td", ""));
  row.children[4].id = `range-${i}`;
  row.children[5].id = `impact-${i}`;
  byId("risk-rows").append(row);
  input.addEventListener("input", render);
}
for (const field of fields) {
  byId(field).setAttribute("aria-describedby", "input-error");
  byId(field).addEventListener("input", render);
}
byId("calculator").addEventListener("submit", event => event.preventDefault());
byId("reset").addEventListener("click", reset);
byId("neutral").addEventListener("click", () => {payload.phases.forEach((_, i) => {byId(`odds-${i}`).value = "1";}); render();});
byId("tail-null").addEventListener("click", () => {byId("odds-4").value = "1"; render();});
byId("quartile").addEventListener("change", () => {preset = byId("quartile").value; byId("gap").value = String(payload.child_presets[preset].point); render();});
byId("version").textContent = `${source.engine_version} / ${source.parameter_set_version}`;
for (const [label, row] of [["Mortality baseline", source.modeled.excess_deaths.baseline], ["Earnings baseline", source.modeled.child_lifetime_earnings_lost_usd.baseline]]) {
  byId("sources").append(text("p", `${label}: ${row.citation}; ${row.population}.`));
}
for (const row of source.blocked) byId("blocked").append(text("li", `${row.outcome}: ${row.reason}`));
reset();
