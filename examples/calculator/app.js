"use strict";
const payload = JSON.parse(document.getElementById("engine-data").textContent);
const receipt = payload.result;
const byId = id => document.getElementById(id);
const number = x => {
  // A fractional expected count is still nonzero; never round it away.
  if (x !== 0 && Math.abs(x) < 0.01) {
    return Math.abs(x) < 0.000001 ? x.toExponential(2)
      : x.toLocaleString("en-US", {minimumSignificantDigits: 3, maximumSignificantDigits: 3});
  }
  return x.toLocaleString("en-US", {minimumFractionDigits: 2, maximumFractionDigits: 2});
};
const names = {
  "earnings_shock->mortality_peak": "Displacement year",
  "earnings_shock->mortality_offset_1": "Follow-up year 2",
  "earnings_shock->mortality_offsets_2_3": "Follow-up years 3–4",
  "earnings_shock->mortality_offsets_4_5": "Follow-up years 5–6",
  "earnings_shock->mortality_sustained": "Follow-up years 7–20",
  "displacement->child_earnings": "Father-to-son adult earnings response"
};
const citations = {
  sullivan2009: {name:"Sullivan & von Wachter · Job Displacement and Mortality", url:"https://doi.org/10.1162/qjec.2009.124.3.1265"},
  oreopoulos2008: {name:"Oreopoulos, Page & Stevens · The Intergenerational Effects of Worker Displacement",url:"https://poverty.ucdavis.edu/sites/main/files/file-attachments/stevens_2008jole.pdf"}
};
function text(tag, value, className) {
  const element = document.createElement(tag);
  element.textContent = value;
  if (className) element.className = className;
  return element;
}
function render() {
  const input = byId("exposure");
  const exposure = input.value.trim() === "" ? NaN : Number(input.value);
  const valid = Number.isFinite(exposure) && exposure >= 0 && exposure <= 1000000;
  byId("input-error").hidden = valid;
  byId("input-error").textContent = valid ? "" : "Enter a finite exposure from 0 to 1,000,000. Results below retain the last valid input.";
  input.setAttribute("aria-invalid", String(!valid));
  if (!valid) return;
  const key = byId("outcome").value;
  const row = receipt.modeled[key];
  const mortality = key === "excess_deaths";
  const scale = exposure / payload.reference_exposure;
  const value = x => mortality ? number(x * scale) : "$" + number(x * scale);
  const unit = mortality ? "additional expected deaths over 20 years" : "lifetime earnings loss, USD 2024, undiscounted";
  byId("comparison-heading").textContent = mortality ? "Mortality difference over 20 years" : "Children’s lifetime earnings difference";
  byId("scenario-line").textContent = `${input.value.trim()} worker equivalents · ${mortality ? "20-year follow-up" : "2 children per worker equivalent; lifetime outcome"} · fixed national reference`;
  byId("fixed-description").textContent = mortality ? "US male mortality baseline, ages 45–54, pooled 2015–2019; fixed for 20 years without cohort aging. Pennsylvania high-tenure male displacement response." : "Two children per worker equivalent. Canadian father-to-son response converted using US synthetic male lifetime earnings. Child ages and sex are unknown; eligibility for a target household is not established.";
  byId("applicability").textContent = row.applicability.reason;
  byId("reference-value").textContent = value(0);
  byId("event-value").textContent = value(row.sensitivity.reference_point);
  byId("difference").textContent = `${value(row.sensitivity.reference_point)} ${unit}`;
  byId("comparison-note").textContent = mortality ? "These values count only the additional deaths attributed to the displacement response. Ordinary baseline deaths are excluded from both displayed values; zero is not zero total deaths." : "Zero means no earnings loss attributed to this specified displacement effect. The display is a difference in lifetime totals, not annual income, household resources or discounted present value.";
  byId("support").textContent = `${value(row.low)} to ${value(row.high)} ${unit}`;
  const drivers = row.sensitivity.effect_drivers;
  const max = Math.max(...drivers.map(d => Math.abs(d.effect_removed.reference_minus_variant)), 1e-12);
  byId("driver-list").replaceChildren();
  for (const driver of drivers) {
    const item = text("article", "", "driver");
    const head = text("div", "", "driver-head");
    head.append(text("h3", names[driver.input_id] || driver.input_id), text("strong", `${value(driver.effect_removed.reference_minus_variant)} removal impact`));
    const meter = text("div", "", "driver-meter");
    meter.setAttribute("aria-hidden", "true");
    const fill = text("span", "");
    fill.style.width = `${100 * Math.abs(driver.effect_removed.reference_minus_variant) / max}%`;
    meter.append(fill);
    item.append(head, meter, text("p", `Effect removed: ${value(driver.effect_removed.point)} ${unit}. Removal impact = reference minus this variant; a positive value means removal lowers the estimate.`));
    const details = text("details", "");
    const range = driver.supported_range;
    details.append(text("summary", "Source input and supported-range experiment"), text("p", `Current ${driver.input_unit}: ${driver.input_value}. Source endpoints: ${range.input_low}–${range.input_high}. Removal sets it to ${driver.effect_removed.input_value}.`), text("p", `Changing this input alone across its source range gives ${value(range.outcome_low)}–${value(range.outcome_high)} ${unit}.`), text("p", `Source: ${driver.citation}; ${driver.population_scope}. Evidence role: ${driver.evidence_role}; extraction tier: ${driver.tier}.`));
    item.append(details);
    byId("driver-list").append(item);
  }
  byId("sources").replaceChildren();
  const ids = [...new Set(drivers.map(d => d.citation))];
  for (const id of ids) {
    const citation = citations[id];
    const paragraph = text("p", "");
    if (citation) {const link = text("a", citation.name); link.href = citation.url; paragraph.append(link);} else paragraph.textContent = id;
    byId("sources").append(paragraph);
  }
  byId("sources").append(text("p", `Baseline: ${row.baseline.citation}`), text("p", row.applicability.transport_assumptions.join(". ") + "."));
}
byId("version").textContent = `Engine ${receipt.engine_version} · parameters ${receipt.parameter_set_version}`;
byId("receipt").textContent = JSON.stringify(receipt, null, 2);
for (const row of receipt.blocked) byId("blocked").append(text("li", `${row.outcome.replaceAll("_", " ")}: ${row.reason}.`));
byId("blocked").append(text("li", "Target-population transport: no reviewed target-cohort decision supplied; both displayed outcomes remain illustrative."));
byId("exposure").addEventListener("input", render);
byId("outcome").addEventListener("change", render);
document.querySelectorAll("input[name=direction]").forEach(input => input.addEventListener("change", () => {
  document.body.dataset.direction = input.value;
  // Move the actual DOM so keyboard and screen-reader order matches visual order.
  const first = byId(input.value === "sensitivity" ? "sensitivity" : "comparison");
  byId("results").insertBefore(first, byId("results").children[1]);
}));
byId("reset").addEventListener("click", () => {byId("exposure").value = String(payload.reference_exposure); render();});
render();
