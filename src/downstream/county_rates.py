"""Count-likelihood county baseline uncertainty.

The production place table intentionally does not reinterpret a generic
``*_n`` precision field as a binomial denominator.  This module is the strict
path for future county mortality inputs: it requires event counts and
person-years on the exact national-baseline population/window before allowing
Bayesian shrinkage or predictive sampling.
"""

from __future__ import annotations

import csv
import math
import random
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CountyRateObservation:
    key: str
    outcome: str
    events: int
    person_years: float
    population_scope: str
    time_window: str
    citation: str


@dataclass(frozen=True)
class NationalRatePrior:
    """A national event/person-time rate with compatibility metadata."""
    outcome: str
    rate: float
    population_scope: str
    time_window: str
    citation: str


REQUIRED_COLUMNS = ("key", "outcome", "events", "person_years", "population_scope", "time_window", "citation")


def load_county_rates(path: str | Path) -> tuple[CountyRateObservation, ...]:
    """Load count-compatible county observations; rates alone are refused."""
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(line for line in handle if not line.lstrip().startswith("#"))
        if reader.fieldnames is None or any(c not in reader.fieldnames for c in REQUIRED_COLUMNS):
            raise ValueError(f"county-rate CSV requires columns {REQUIRED_COLUMNS}")
        out = []
        for raw in reader:
            try:
                events = int(raw["events"])
                years = float(raw["person_years"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"invalid county-rate row {raw!r}") from exc
            row = CountyRateObservation(raw["key"].strip(), raw["outcome"].strip(), events, years,
                                        raw["population_scope"].strip(), raw["time_window"].strip(), raw["citation"].strip())
            if not row.key or not row.outcome or not row.population_scope or not row.time_window or not row.citation:
                raise ValueError("county-rate metadata fields may not be empty")
            if row.events < 0 or not math.isfinite(row.person_years) or row.person_years <= 0:
                raise ValueError(f"county rate {row.key!r} needs nonnegative events and positive finite person-years")
            out.append(row)
    keys = [(r.key, r.outcome, r.time_window) for r in out]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate county/outcome/time-window observation")
    return tuple(out)


def poisson_gamma_posterior(observation: CountyRateObservation, prior: NationalRatePrior,
                            prior_person_years: float, draws: int = 10_000,
                            seed: int = 1901) -> dict:
    """Gamma--Poisson posterior for an event/person-time mortality rate.

    This accepts fractional person-time and event counts exceeding one per
    person-year. A constant-hazard annual risk is reported as ``1-exp(-rate)``
    but is not substituted into a fixed-window binomial likelihood.
    """
    if (observation.outcome != prior.outcome or observation.population_scope != prior.population_scope
            or observation.time_window != prior.time_window):
        raise ValueError("county observation and national prior must have identical outcome, population_scope, and time_window")
    if not prior.citation:
        raise ValueError("national prior needs a citation")
    if not prior.rate > 0 or not math.isfinite(prior.rate):
        raise ValueError("national rate must be finite and positive")
    if not math.isfinite(prior_person_years) or prior_person_years <= 0:
        raise ValueError("prior_person_years must be finite and positive")
    if isinstance(draws, bool) or not isinstance(draws, int) or draws < 2:
        raise ValueError("draws must be an integer of at least 2")
    alpha = prior.rate * prior_person_years + observation.events
    beta = prior_person_years + observation.person_years
    rng = random.Random(seed)
    values = sorted(rng.gammavariate(alpha, 1 / beta) for _ in range(draws))
    last = draws - 1
    return {
        "key": observation.key,
        "outcome": observation.outcome,
        "posterior": {
            "mean": alpha / beta,  # compatibility alias; this is a RATE, not a probability
            "mean_rate": alpha / beta,
            "mean_annual_risk_constant_hazard": 1 - math.exp(-alpha / beta),
            "p05": values[int(.05 * last)], "p50": values[int(.50 * last)], "p95": values[int(.95 * last)],
        },
        "prior": {"mean_rate": prior.rate, "equivalent_person_years": prior_person_years,
                  "outcome": prior.outcome, "population_scope": prior.population_scope,
                  "time_window": prior.time_window, "citation": prior.citation},
        "observation": {"events": observation.events, "person_years": observation.person_years,
                        "population_scope": observation.population_scope, "time_window": observation.time_window,
                        "citation": observation.citation},
        "method": "Gamma-Poisson event/person-time likelihood; no spatial dependence assumed",
        "integration_status": "not wired into places.csv until its county counts match the national baseline population and window",
    }


def empirical_bayes_prior_person_years(observations, prior_rate: float) -> dict:
    """Method-of-moments empirical-Bayes estimate of the Gamma prior strength.

    Models county true rates as lambda_i ~ Gamma(mean m, variance v) with
    events_i | lambda_i ~ Poisson(py_i * lambda_i). The spread of the
    OBSERVED rates mixes real between-county heterogeneity with Poisson
    noise; subtracting the noise term estimates v, and the Gamma prior with
    mean m and variance v has rate parameter k = m / v - the "prior
    person-years" the posterior pools with. Unweighted across counties
    (each county is one unit of heterogeneity); refusal when the data show
    no residual heterogeneity (v <= 0), which would mean full pooling.
    """
    obs = list(observations)
    if len(obs) < 30:
        raise ValueError(f"need >= 30 county observations, got {len(obs)}")
    if not prior_rate > 0:
        raise ValueError("prior_rate must be positive")
    total_events = sum(o.events for o in obs)
    total_py = sum(o.person_years for o in obs)
    if total_events <= 0 or total_py <= 0:
        raise ValueError("observations must carry positive events and person-years")
    m = total_events / total_py
    rates = [o.events / o.person_years for o in obs]
    n = len(rates)
    spread = sum((r - m) ** 2 for r in rates) / n
    noise = m * sum(1.0 / o.person_years for o in obs) / n
    residual = spread - noise
    result = {
        "counties": n,
        "pooled_rate_per_person_year": m,
        "mean_observed_rate": sum(rates) / n,
        "observed_rate_variance": spread,
        "poisson_noise_variance": noise,
        "noise_share_of_spread": noise / spread if spread > 0 else None,
        "residual_heterogeneity_variance": residual,
    }
    if residual <= 0:
        result["estimate"] = None
        result["reason"] = ("no residual between-county heterogeneity after noise "
                            "subtraction; EB would imply full pooling, no prior "
                            "strength to estimate")
        return result
    k = m / residual
    pys = sorted(o.person_years for o in obs)
    def _w(q):
        py = pys[int(q * (len(pys) - 1))]
        return {"person_years": py, "shrinkage_weight": py / (py + k)}
    result.update({
        "estimate_prior_person_years": k,
        "implied_gamma_shape": m * k,
        "shrinkage_weight_deciles": {f"p{int(q * 100)}": _w(q) for q in (0.1, 0.25, 0.5, 0.75, 0.9)},
    })
    return result


@dataclass(frozen=True)
class CountyMortalityPosterior:
    """One county's pooled mortality rate with its full provenance chain.

    ``prior_*`` fields are the national baseline identity the posterior
    was pooled toward; consumers must verify them against the live
    baseline table before applying anything.
    """
    key: str
    outcome: str
    population_scope: str
    time_window: str
    events: int
    person_years: float
    posterior_mean_rate: float
    prior_rate: float
    prior_unit: str
    prior_population: str
    prior_citation: str
    prior_person_years: float
    observation_citation: str


COUNTY_MORTALITY_COLUMNS = (
    "key", "outcome", "population_scope", "time_window",
    "events", "person_years", "posterior_mean_rate",
    "prior_rate", "prior_unit", "prior_population", "prior_citation",
    "prior_person_years", "observation_citation",
)


def load_county_mortality_posteriors(path: str | Path) -> dict[str, CountyMortalityPosterior]:
    """Load the county posterior table built by scripts/build_county_mortality.py.

    Rows are refused unless every provenance field is present and finite;
    duplicate county keys are refused. Applying a row is a separate,
    metadata-checked decision (see place.place_baselines) — loading alone
    changes nothing.
    """
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(line for line in handle if not line.lstrip().startswith("#"))
        if reader.fieldnames is None or any(c not in reader.fieldnames for c in COUNTY_MORTALITY_COLUMNS):
            raise ValueError(f"county mortality posterior CSV requires columns {COUNTY_MORTALITY_COLUMNS}")
        out: dict[str, CountyMortalityPosterior] = {}
        for raw in reader:
            key = raw["key"].strip()
            if not key:
                continue  # separator/notes rows
            if key in out:
                raise ValueError(f"duplicate county mortality posterior key {key!r}")
            try:
                row = CountyMortalityPosterior(
                    key=key,
                    outcome=raw["outcome"].strip(),
                    population_scope=raw["population_scope"].strip(),
                    time_window=raw["time_window"].strip(),
                    events=int(raw["events"]),
                    person_years=float(raw["person_years"]),
                    posterior_mean_rate=float(raw["posterior_mean_rate"]),
                    prior_rate=float(raw["prior_rate"]),
                    prior_unit=raw["prior_unit"].strip(),
                    prior_population=raw["prior_population"].strip(),
                    prior_citation=raw["prior_citation"].strip(),
                    prior_person_years=float(raw["prior_person_years"]),
                    observation_citation=raw["observation_citation"].strip(),
                )
            except (TypeError, ValueError) as exc:
                raise ValueError(f"invalid county mortality posterior row {key!r}: {exc}") from exc
            if not all((row.outcome, row.population_scope, row.time_window,
                        row.prior_unit, row.prior_population, row.prior_citation,
                        row.observation_citation)):
                raise ValueError(f"county mortality posterior {key!r} has blank provenance")
            if row.events < 0 or row.person_years <= 0 or row.prior_person_years <= 0:
                raise ValueError(f"county mortality posterior {key!r} has invalid counts")
            if not all(math.isfinite(v) and v > 0 for v in
                       (row.person_years, row.posterior_mean_rate, row.prior_rate,
                        row.prior_person_years)):
                raise ValueError(f"county mortality posterior {key!r} has non-finite or nonpositive rates")
            expected = (row.prior_rate * row.prior_person_years + row.events) / (row.prior_person_years + row.person_years)
            # The builder serializes rates to nine decimal places.
            if not math.isclose(row.posterior_mean_rate, expected, rel_tol=0, abs_tol=5.00001e-10):
                raise ValueError(f"county mortality posterior {key!r} disagrees with its counts and prior")
            out[key] = row
    if not out:
        raise ValueError(f"county mortality posterior table {path} has no rows")
    return out


def beta_binomial_posterior(observation: CountyRateObservation, national_rate: float,
                            prior_person_years: float, draws: int = 10_000,
                            seed: int = 1901) -> dict:
    """Deprecated compatibility wrapper; use :func:`poisson_gamma_posterior`.

    It cannot establish metadata compatibility because its legacy signature
    lacks national population/window fields, so it is explicitly unsuitable
    for production place integration.
    """
    prior = NationalRatePrior(observation.outcome, national_rate,
                              observation.population_scope, observation.time_window,
                              "legacy caller supplied no national-prior locator")
    out = poisson_gamma_posterior(observation, prior, prior_person_years, draws, seed)
    out["integration_status"] = "legacy wrapper: metadata compatibility is unverified; never wire this output into places.csv"
    out["deprecated_api"] = "beta_binomial_posterior is retained for callers; it now uses Gamma-Poisson rather than a binomial likelihood"
    return out
