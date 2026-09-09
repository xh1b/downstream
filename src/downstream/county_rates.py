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
            if row.events < 0 or not math.isfinite(row.person_years) or row.person_years <= 0 or row.events > row.person_years:
                raise ValueError(f"county rate {row.key!r} needs 0 <= events <= person_years")
            out.append(row)
    keys = [(r.key, r.outcome, r.time_window) for r in out]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate county/outcome/time-window observation")
    return tuple(out)


def beta_binomial_posterior(observation: CountyRateObservation, national_rate: float,
                            prior_person_years: float, draws: int = 10_000,
                            seed: int = 1901) -> dict:
    """Posterior for a crude annual event probability with a national prior.

    The prior is Beta(national_rate * strength, (1-rate) * strength), where
    ``strength`` is declared in compatible person-years.  This is intentionally
    inapplicable to age-standardized rates or mismatched windows.
    """
    if not 0 < national_rate < 1 or not math.isfinite(national_rate):
        raise ValueError("national_rate must be a finite probability strictly between 0 and 1")
    if not math.isfinite(prior_person_years) or prior_person_years <= 0:
        raise ValueError("prior_person_years must be finite and positive")
    if isinstance(draws, bool) or not isinstance(draws, int) or draws < 2:
        raise ValueError("draws must be an integer of at least 2")
    alpha = national_rate * prior_person_years + observation.events
    beta = (1 - national_rate) * prior_person_years + observation.person_years - observation.events
    rng = random.Random(seed)
    values = sorted(rng.betavariate(alpha, beta) for _ in range(draws))
    last = draws - 1
    return {
        "key": observation.key,
        "outcome": observation.outcome,
        "posterior": {
            "mean": alpha / (alpha + beta),
            "p05": values[int(.05 * last)], "p50": values[int(.50 * last)], "p95": values[int(.95 * last)],
        },
        "prior": {"mean": national_rate, "equivalent_person_years": prior_person_years},
        "observation": {"events": observation.events, "person_years": observation.person_years,
                        "population_scope": observation.population_scope, "time_window": observation.time_window,
                        "citation": observation.citation},
        "method": "Beta-binomial count likelihood; no spatial dependence assumed",
        "integration_status": "not wired into places.csv until its county counts match the national baseline population and window",
    }
