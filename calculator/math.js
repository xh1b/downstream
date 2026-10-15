// @ref:calculator-math
// Context: @link:doc-calculator; @link:code-mortality; @link:code-result-sensitivity; @link:test-calculator. @tag:calculator
"use strict";
// Pure equations; source offsets and survival match downstream.mortality.
const DownstreamMath = (() => {
  const phases = [
    {start: 0, span: 1},
    {start: 1, span: 1},
    {start: 2, span: 2},
    {start: 4, span: 2},
    {start: 6, span: Infinity},
  ];
  const limits = {
    workers: [0, 1e6], years: [0, 100], rate: [0, 1],
    children: [0, 100], earnings: [0, 1e9], gap: [1e-6, 10],
  };
  const inRange = (value, low, high) => typeof value === "number"
    && Number.isFinite(value) && value >= low && value <= high;
  const validOdds = value => inRange(value, 0, 1e6) && value > 0;
  const dot = (xs, ys) => xs.reduce((sum, x, i) => x ? sum + x * ys[i] : sum, 0);
  const replaceAt = (xs, index, value) => xs.map((x, i) => i === index ? value : x);
  const withOdds = (inputs, index, value) => ({
    ...inputs, odds: replaceAt(inputs.odds, index, value),
  });
  const durations = years => phases.map(({start, span}) =>
    Math.min(Math.max(years - start, 0), span));

  function invalidFields(inputs) {
    const fields = Object.entries(limits)
      .filter(([key, [low, high]]) => !inRange(inputs[key], low, high)
        || (key === "children" && !Number.isInteger(inputs[key])))
      .map(([key]) => key);
    const odds = Array.isArray(inputs.odds) && inputs.odds.length === phases.length
      ? Array.from(inputs.odds).flatMap((value, i) => validOdds(value) ? [] : [`odds-${i}`])
      : ["odds"];
    return [...fields, ...odds];
  }

  function validate(inputs) {
    const [field] = invalidFields(inputs);
    if (field) throw Error(field.startsWith("odds") ? "odds" : field);
  }

  // S₀ − S₁, factored by the larger survival. expm1 retains tiny effects;
  // choosing the factor by sign avoids overflow for protective odds.
  function survivalDifference(logReference, logExposed, logRatio) {
    const difference = logRatio <= 0
      ? -Math.exp(logReference) * Math.expm1(logRatio)
      : Math.exp(logExposed) * Math.expm1(-logRatio);
    return Math.min(1, Math.max(-1, difference));
  }

  function mortality(workers, rate, odds, years) {
    const annualRisk = -Math.expm1(-rate);
    const phaseYears = durations(years);
    const risks = odds.map(theta => theta * annualRisk / (1 - annualRisk + theta * annualRisk));
    const logReference = -rate * years;
    // log(S₁/S₀) directly, rather than subtracting nearly equal log-survivals.
    const logRatio = -dot(phaseYears, odds.map(theta => Math.log1p((theta - 1) * annualRisk)));
    // Sum exposed survival directly to retain nonnegative deaths even for
    // tiny protective odds, where logReference + logRatio can cancel.
    const logExposed = dot(phaseYears, risks.map(risk => Math.log1p(-risk)));
    return {
      baseline: workers * -Math.expm1(logReference),
      exposed: Math.max(0, workers * -Math.expm1(logExposed)),
      difference: workers * survivalDifference(logReference, logExposed, logRatio),
      annualRisk, phaseYears,
    };
  }

  const mortalityFor = inputs => mortality(inputs.workers, inputs.rate, inputs.odds, inputs.years);

  function calculate(inputs) {
    validate(inputs);
    const result = mortalityFor(inputs);
    const drivers = inputs.odds.map((_, i) => {
      const variant = mortalityFor(withOdds(inputs, i, 1)).difference;
      return {variant, impact: result.difference - variant};
    });
    return {
      ...result, drivers,
      childLoss: inputs.workers * inputs.children * (1 - inputs.gap) * inputs.earnings,
      childGap: 100 * (1 - inputs.gap),
    };
  }

  // One source endpoint changes at a time; these are not joint intervals.
  const sourceRanges = (inputs, sources) => sources.map((source, i) =>
    [source.low, source.high].map(value => mortalityFor(withOdds(inputs, i, value)).difference));

  const mortalityCurve = inputs => Array.from({length: 101}, (_, i) => {
    const years = inputs.years * i / 100;
    return {years, difference: mortalityFor({...inputs, years}).difference};
  });

  const analyze = (inputs, sources) => ({
    results: calculate(inputs),
    ranges: sourceRanges(inputs, sources),
    curve: mortalityCurve(inputs),
  });

  return {calculate, analyze, mortality, durations, validate, invalidFields};
})();
if (typeof module !== "undefined") module.exports = DownstreamMath;
