"use strict";
// Equations mirror downstream.mortality.excess_deaths_profile.
const DownstreamMath = (() => {
  const durations = years => {
    let remaining = years;
    return [1, 1, 2, 2, Infinity].map(span => {
      const take = Math.min(remaining, span);
      remaining -= take;
      return take;
    });
  };
  function validate(x) {
    const limits = {workers:[0,1e6], years:[0,100], rate:[0,1], children:[0,100], earnings:[0,1e9], gap:[1e-6,10]};
    for (const [key, [low, high]] of Object.entries(limits)) {
      if (typeof x[key] !== "number" || !Number.isFinite(x[key]) || x[key] < low || x[key] > high) throw Error(key);
    }
    if (!Number.isInteger(x.children)) throw Error("children");
    if (!Array.isArray(x.odds) || x.odds.length !== 5 || x.odds.some(v => typeof v !== "number" || !Number.isFinite(v) || v <= 0 || v > 1e6)) throw Error("odds");
  }
  function mortality(workers, rate, odds, years) {
    const p = -Math.expm1(-rate), phaseYears = durations(years);
    const logReference = -rate * years;
    const logRatio = -phaseYears.reduce((sum, t, i) => sum + t * Math.log1p((odds[i] - 1) * p), 0);
    // Sum exposed log-survival directly; subtracting two near-opposites can
    // otherwise produce negative death counts at tiny protective odds.
    const risks = odds.map(theta => theta * p / (1 - p + theta * p));
    const logExposed = phaseYears.reduce((sum, t, i) => t ? sum + t * Math.log1p(-risks[i]) : sum, 0);
    let difference = logRatio <= 0
      ? -Math.exp(logReference) * Math.expm1(logRatio)
      : Math.exp(logExposed) * Math.expm1(-logRatio);
    difference = Math.min(1, Math.max(-1, difference));
    return {baseline:workers * -Math.expm1(logReference),
      exposed:Math.max(0, workers * -Math.expm1(logExposed)), difference:workers * difference,
      annualRisk:p, phaseYears};
  }
  function calculate(x) {
    validate(x);
    const m = mortality(x.workers, x.rate, x.odds, x.years);
    const drivers = x.odds.map((_, i) => {
      const odds = [...x.odds]; odds[i] = 1;
      const variant = mortality(x.workers, x.rate, odds, x.years).difference;
      return {variant, impact:m.difference - variant};
    });
    return {...m, drivers, childLoss:x.workers * x.children * (1 - x.gap) * x.earnings,
      childGap:100 * (1 - x.gap)};
  }
  return {calculate, mortality, durations, validate};
})();
if (typeof module !== "undefined") module.exports = DownstreamMath;
