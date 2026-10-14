"use strict";
(() => {
  const payload = JSON.parse(document.getElementById("engine-data").textContent);
  const source = payload.result;
  const fields = ["workers", "years", "rate", "children", "gap", "earnings"];
  const oddsIds = payload.phases.map((_, i) => `odds-${i}`);
  const inputIds = [...fields, ...oddsIds];
  const byId = id => document.getElementById(id);
  const setText = (id, value) => { byId(id).textContent = value; };
  const inputScale = id => id === "rate" ? 1000 : 1;
  const numericValue = value => value.trim() === "" ? NaN : Number(value);

  function number(value) {
    const magnitude = Math.abs(value);
    if (magnitude >= 1e9) return value.toExponential(3);
    if (value !== 0 && magnitude < .01) {
      return magnitude < 1e-6 ? value.toExponential(2)
        : value.toLocaleString("en-US", {maximumSignificantDigits: 3});
    }
    return value.toLocaleString("en-US", {minimumFractionDigits: 2, maximumFractionDigits: 2});
  }

  const isReference = inputs => fields.every(key => inputs[key] === payload.defaults[key])
    && inputs.odds.every((value, i) => value === payload.phases[i].point);

  function curveGeometry(curve) {
    const values = curve.map(point => point.difference);
    const low = Math.min(0, ...values), high = Math.max(0, ...values);
    const span = high - low || 1;
    const y = value => 118 - 106 * (value - low) / span;
    return {
      low, high, zero: y(0),
      points: values.map((value, i) => `${8 + 884 * i / (values.length - 1)},${y(value)}`).join(" "),
    };
  }

  function calculationReceipt(inputs, analysis, preset) {
    return {
      schema: "downstream-browser-calculation/1", inputs, results: analysis.results,
      preset, selected_child_source: payload.child_presets[preset],
      source_reference: isReference(inputs), eligibility: "illustrative; target transport not reviewed",
      fixed_baseline: true,
      child_valuation: "undiscounted constant lifetime gap; child demographics unknown",
      curve: analysis.curve, implementation_sha256: payload.browser_math_sha256,
    };
  }

  // DOM reads and writes stay here; all outcome calculations are in math.js.
  function readInputs() {
    return {
      ...Object.fromEntries(fields.map(id => [id, numericValue(byId(id).value) / inputScale(id)])),
      odds: oddsIds.map(id => numericValue(byId(id).value)),
    };
  }

  function renderValidation(invalid) {
    inputIds.forEach(id => byId(id).setAttribute("aria-invalid", String(invalid.includes(id))));
    setText("input-error", "Check the marked input. Results use the last valid inputs.");
    byId("input-error").hidden = invalid.length === 0;
  }

  function renderTotals(inputs, result, preset) {
    const child = payload.child_presets[preset];
    setText("basis", isReference(inputs) ? "Reference assumptions" : "Custom assumptions");
    setText("baseline-basis", inputs.rate === payload.defaults.rate
      ? "Reference λ · US · Male · 45–54 · 2015–19" : "Custom λ · fixed over T");
    setText("horizon", `${byId("workers").value.trim()} × ${byId("years").value.trim()} y`);
    for (const [id, value] of Object.entries({
      "baseline-deaths": result.baseline, "exposed-deaths": result.exposed,
      "excess-deaths": result.difference, "child-gap": result.childGap, "child-loss": result.childLoss,
    })) setText(id, number(value));
    setText("child-support", `Source g: ${number(child.low)}–${number(child.high)}.`);
  }

  function renderPhases({results, ranges}) {
    payload.phases.forEach((_, i) => {
      setText(`duration-${i}`, number(results.phaseYears[i]));
      setText(`impact-${i}`, number(results.drivers[i].impact));
      setText(`range-${i}`, ranges[i].map(number).join("…"));
    });
  }

  function renderCurve(curve) {
    const plot = curveGeometry(curve);
    byId("death-curve").setAttribute("points", plot.points);
    for (const key of ["y1", "y2"]) byId("zero-line").setAttribute(key, String(plot.zero));
    setText("curve-scale", `ΔD [${number(plot.low)}, ${number(plot.high)}]`);
    setText("curve-end", `${byId("years").value.trim()} y`);
  }

  function render() {
    const inputs = readInputs();
    const invalid = DownstreamMath.invalidFields(inputs);
    renderValidation(invalid);
    if (invalid.length) return;
    const preset = byId("quartile").value;
    const analysis = DownstreamMath.analyze(inputs, payload.phases);
    renderTotals(inputs, analysis.results, preset);
    renderPhases(analysis);
    renderCurve(analysis.curve);
    setText("receipt", JSON.stringify({
      current_calculation: calculationReceipt(inputs, analysis, preset), source_receipt: source,
    }, null, 2));
  }

  function reset() {
    fields.forEach(id => { byId(id).value = String(payload.defaults[id] * inputScale(id)); });
    oddsIds.forEach((id, i) => { byId(id).value = String(payload.phases[i].point); });
    byId("quartile").value = "overall";
    render();
  }

  function text(tag, value) {
    const element = document.createElement(tag);
    element.textContent = value;
    return element;
  }

  function phaseRow(phase, i) {
    const row = document.createElement("tr");
    const duration = text("td", ""), range = text("td", ""), impact = text("td", "");
    duration.id = `duration-${i}`;
    range.id = `range-${i}`;
    impact.id = `impact-${i}`;
    const cell = document.createElement("td"), input = document.createElement("input");
    input.id = oddsIds[i];
    Object.assign(input, {type: "number", min: "0", max: "1000000", step: "any"});
    input.setAttribute("aria-label", `Odds ratio, source offset ${phase.label}`);
    cell.append(input);
    row.append(text("td", phase.label), duration, cell,
      text("td", `${number(phase.low)}–${number(phase.high)}`), range, impact);
    return row;
  }

  function initialize() {
    payload.phases.forEach((phase, i) => byId("risk-rows").append(phaseRow(phase, i)));
    inputIds.forEach(id => {
      byId(id).setAttribute("aria-describedby", "input-error");
      byId(id).addEventListener("input", render);
    });
    byId("calculator").addEventListener("submit", event => event.preventDefault());
    byId("reset").addEventListener("click", reset);
    byId("neutral").addEventListener("click", () => {
      oddsIds.forEach(id => { byId(id).value = "1"; });
      render();
    });
    byId("tail-null").addEventListener("click", () => { byId("odds-4").value = "1"; render(); });
    byId("quartile").addEventListener("change", () => {
      byId("gap").value = String(payload.child_presets[byId("quartile").value].point);
      render();
    });
    setText("version", `${source.engine_version} / ${source.parameter_set_version}`);
    for (const [label, baseline] of [
      ["Mortality baseline", source.modeled.excess_deaths.baseline],
      ["Earnings baseline", source.modeled.child_lifetime_earnings_lost_usd.baseline],
    ]) byId("sources").append(text("p", `${label}: ${baseline.citation}; ${baseline.population}.`));
    source.blocked.forEach(row => byId("blocked").append(text("li", `${row.outcome}: ${row.reason}`)));
    reset();
  }

  initialize();
})();
