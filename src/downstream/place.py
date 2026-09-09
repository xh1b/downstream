"""Place-resolved layer: partial pooling of county baselines + the
Chetty-Hendren mobility modifier.

The shipped model assumes the median county everywhere (vignette,
scenarios, baselines). This layer lets a place (state, county) swap in
its own measured baselines SHRUNK toward the national mean — so a
sparse county does not inherit a noisy local estimate — and applies a
mobility modifier to child-outcome parameters.

Design rules:

- **No silent conversions.** A county value replaces the national
  baseline in the SAME unit and population as
  `baselines.csv:<outcome>`; the loader carries no unit arithmetic.
  The county source must derive the value in that unit (note it in
  the row's citation).
- **Partial pooling** is the empirical-Bayes shrinkage weight
  w = n/(n+k): the county estimate is weighted by its own precision n
  against a declared prior sample size k. k is a modeling choice,
  declared here and test-pinned; when county panels land, an
  empirical-Bayes estimator (between-county dispersion over within-
  county sampling variance) may replace k — the formula stays.
- **The mobility modifier is a parameter, not a hard-coded number.**
  The Chetty-Hendren exposure-effect estimate lands as the parameter
  row `neighborhood_exposure->child_outcomes_modifier` (extraction
  queued). Until it exists the modifier reports `blocked` naming the
  link — never an invented number.
- **National fallback.** No file, no row, or missing columns fall
  back to the shipped national baselines unchanged; the provenance
  dict says exactly what was applied and what was not.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .params import Baseline, ParameterSet, default_dir

PLACES_PATH = Path(default_dir()) / "places.csv"

# Column map (places.csv): key,name,level,mobility_percentile,
# mobility_n,mortality_rate,mortality_n,divorce_rate,divorce_n,citation
# mortality_rate / divorce_rate MUST be in the same unit and population
# as baselines.csv:all_cause_mortality_annual / divorce_5y_cumulative.
# *_n columns are the precision counts behind those county values.
PLACE_COLUMNS = (
    "key", "name", "level", "mobility_percentile", "mobility_n",
    "mortality_rate", "mortality_n", "divorce_rate", "divorce_n", "citation",
)
PLACE_LEVELS = ("national", "state", "county")

# The Chetty-Hendren modifier parameter lands as this link. The row's
# declared unit: EXACT annual exposure effect gamma (Appendix Table V
# col 1, county level, Table II col 1 CZ baseline): the increase in a
# child's adult income rank per additional year of childhood spent in
# a county where children of permanent residents rank 1 percentile
# higher, at a given level of parental income. The engine applies the
# dose: DOSE_YEARS years of exposure to the county.
MOBILITY_MODIFIER_LINK = "neighborhood_exposure->child_outcomes_modifier"

# Declared exposure dose: a complete childhood in the county (0-18),
# matching the model's child window. The paper's exposure effect is
# linear in exposure years to age 23 and flat after (Figure IV a);
# the model's dose uses ITS OWN child window, and the difference is
# declared here, not hidden.
DOSE_YEARS = 18.0

# Declared prior sample sizes k for the shrinkage weight w = n/(n+k).
# Mortality: county deaths are Poisson; k = 2,000 deaths is roughly the
# national prime-age rate accumulated over 1M person-years — counties
# below that precision move materially toward the national mean.
# Divorce: county-level 5y-cumulative divorce rates are not published
# at all (the plug stays empty and the national value is used); k is
# declared for when a survey-backed county plug lands, set at the
# P70-125 cohort subsample order of magnitude.
PRIOR_N: dict[str, float] = {
    "all_cause_mortality_annual": 2000.0,
    "divorce_5y_cumulative": 200.0,
}

# Which place column maps to which baseline outcome.
_RATE_COLUMNS = {
    "mortality_rate": "all_cause_mortality_annual",
    "divorce_rate": "divorce_5y_cumulative",
}
_N_COLUMNS = {
    "mortality_rate": "mortality_n",
    "divorce_rate": "divorce_n",
}


@dataclass(frozen=True)
class Place:
    key: str
    name: str
    level: str
    mobility_percentile: float | None
    mobility_n: float | None
    mortality_rate: float | None
    mortality_n: float | None
    divorce_rate: float | None
    divorce_n: float | None
    citation: str


def _maybe_float(s: str) -> float | None:
    s = s.strip()
    return float(s) if s else None


def load_places(path: str | Path = PLACES_PATH) -> dict[str, Place]:
    """Read params/places.csv. Comment lines start with #.

    An absent file yields {} — every consumer then falls back to the
    national baselines and reports why (no fabrication).
    """
    path = Path(path)
    if not path.exists():
        return {}
    places: dict[str, Place] = {}
    with open(path, newline="", encoding="utf-8") as f:
        lines = [ln for ln in f if not ln.lstrip().startswith("#")]
    reader = csv.DictReader(lines)
    for row in reader:
        key = row["key"].strip()
        if not key:
            continue
        places[key] = Place(
            key=key,
            name=row["name"].strip(),
            level=row["level"].strip(),
            mobility_percentile=_maybe_float(row["mobility_percentile"]),
            mobility_n=_maybe_float(row["mobility_n"]),
            mortality_rate=_maybe_float(row["mortality_rate"]),
            mortality_n=_maybe_float(row["mortality_n"]),
            divorce_rate=_maybe_float(row["divorce_rate"]),
            divorce_n=_maybe_float(row["divorce_n"]),
            citation=row["citation"].strip(),
        )
    return places


def national(places: dict[str, Place]) -> Place:
    """The required national fallback row."""
    p = places.get("national")
    if p is None:
        raise KeyError(
            "places.csv has no 'national' row; every county shrinkage "
            "pools toward it — add the national row with its citation"
        )
    return p


def shrink(
    county_value: float | None,
    n: float | None,
    national_value: float,
    k: float,
) -> tuple[float, float]:
    """Partial pooling: (shrunk value, weight). w = n/(n+k).

    n <= 0 or a missing county value returns the national value with
    weight 0 — an unmeasured county IS the national mean, honestly.
    """
    if county_value is None or n is None or n <= 0:
        return national_value, 0.0
    w = n / (n + k)
    return (1.0 - w) * national_value + w * county_value, w


def place_baselines(
    places: dict[str, Place],
    baselines: dict[str, Baseline],
    key: str,
) -> dict:
    """Shrunk county baselines for one place.

    Returns {"baselines": <dict>, "provenance": <dict>}. The returned
    dict is a COPY: the national baseline rows stay untouched, county
    overrides swap the value in the same unit and record the pooling
    arithmetic in the row's notes. Outcomes without a county value,
    without a precision n, or without a declared k fall back to the
    national value with the reason stated.
    """
    if not places:
        # No places.csv at all: the honest fallback is the shipped
        # national baselines, unchanged, with the reason stated.
        return {
            "baselines": dict(baselines),
            "provenance": {
                "key": key,
                "applied": False,
                "reason": (
                    "params/places.csv absent — no place-resolved overrides; "
                    "national baselines passed through unchanged"
                ),
                "overrides": {},
            },
        }
    place = places.get(key)
    if place is None:
        raise KeyError(
            f"unknown place {key!r}; load_places() has: "
            f"{sorted(places) if places else 'nothing (places.csv absent)'}"
        )
    nat = national(places)

    out: dict[str, Baseline] = dict(baselines)
    overrides: dict = {}
    for col, outcome in _RATE_COLUMNS.items():
        county_value = getattr(place, col)
        county_n = getattr(place, _N_COLUMNS[col])
        base = baselines.get(outcome)
        if base is None or base.status != "verified" or base.value is None:
            overrides[outcome] = {
                "applied": False,
                "reason": f"no verified national baseline {outcome!r} to pool toward",
            }
            continue
        if county_value is None:
            overrides[outcome] = {
                "applied": False,
                "reason": "no county value in places.csv — national value used",
            }
            continue
        if county_n is None:
            overrides[outcome] = {
                "applied": False,
                "reason": "county value present but precision n missing — "
                "pooling would be a guess; add the n column",
            }
            continue
        k = PRIOR_N.get(outcome)
        if k is None:
            overrides[outcome] = {
                "applied": False,
                "reason": f"no declared prior n for {outcome!r}",
            }
            continue
        shrunk, w = shrink(county_value, county_n, base.value, k)
        out[outcome] = Baseline(
            outcome=outcome,
            unit=base.unit,
            population=base.population,
            value=shrunk,
            citation=base.citation,
            source=base.source,
            status="verified",
            notes=(
                f"place-resolved: county {place.key} value {county_value} "
                f"(n={county_n}, citation: {place.citation}) shrunk toward the "
                f"national {base.value} with k={k}, w={round(w, 6)}; "
                "same unit and population as the national baseline — no "
                "conversion applied"
            ),
        )
        overrides[outcome] = {
            "applied": True,
            "county_value": county_value,
            "county_n": county_n,
            "county_citation": place.citation,
            "national_value": base.value,
            "k": k,
            "weight": round(w, 6),
            "shrunk_value": shrunk,
        }
    return {
        "baselines": out,
        "provenance": {
            "key": place.key,
            "name": place.name,
            "level": place.level,
            "overrides": overrides,
        },
    }


def place_json(
    places: dict[str, Place],
    baselines: dict[str, Baseline],
    key: str,
    params: ParameterSet,
) -> dict:
    """CLI-ready form of place_baselines + mobility_modifier.

    Baselines become plain dicts (JSON-safe); the compute path keeps
    the Baseline objects.
    """
    import dataclasses

    out = place_baselines(places, baselines, key)
    out["baselines"] = {
        k: dataclasses.asdict(v) for k, v in out["baselines"].items()
    }
    out["mobility_modifier"] = mobility_modifier(params, places, key)
    return out


def mobility_modifier(
    params: ParameterSet,
    places: dict[str, Place],
    key: str,
) -> dict:
    """The Chetty-Hendren mobility multiplier for one place.

    multiplier = 1 + DOSE_YEARS * gamma * (place_pct - national_pct)/100:
    the county's permanent-resident income-rank percentile gap vs the
    national row (NOT a hard-coded 50), scaled by the annual exposure
    effect gamma over a declared 18-year childhood. Band direction
    follows the gap sign. Missing percentile, missing national
    reference, missing parameter, or an unextracted link reports
    `blocked` with the exact missing input — never a number without a
    citation.
    """
    if not places:
        return {
            "place": key,
            "applied": False,
            "blocked": True,
            "reason": (
                "params/places.csv absent — no place-resolved overrides; "
                "the national mobility baseline is the median county by "
                "definition, multiplier 1.0"
            ),
        }
    place = places.get(key)
    if place is None:
        raise KeyError(f"unknown place {key!r}")
    try:
        p = params.by_link(MOBILITY_MODIFIER_LINK)
    except KeyError:
        return {
            "place": key,
            "applied": False,
            "blocked": True,
            "reason": (
                f"parameter {MOBILITY_MODIFIER_LINK!r} not extracted yet — "
                "queued: Chetty & Hendren 2018 (QJE 133(3):1163) exposure-"
                "effect estimate; the formula is frozen, the number is not"
            ),
        }
    nat = national(places)
    if nat.mobility_percentile is None:
        return {
            "place": key,
            "applied": False,
            "blocked": True,
            "reason": (
                "the national row has no mobility_percentile — the "
                "modifier's reference gap has no basis; rebuild places.csv"
            ),
        }
    if place.mobility_percentile is None:
        return {
            "place": key,
            "applied": False,
            "blocked": True,
            "reason": (
                f"no mobility_percentile for {place.key!r} in places.csv — "
                "the Opportunity Atlas county plug is the source"
            ),
        }
    gap = place.mobility_percentile - nat.mobility_percentile
    scale = DOSE_YEARS / 100.0
    lo_part, hi_part = (p.low, p.high) if gap >= 0 else (p.high, p.low)
    return {
        "place": place.key,
        "applied": True,
        "blocked": False,
        "parameter": MOBILITY_MODIFIER_LINK,
        "mobility_percentile": place.mobility_percentile,
        "national_percentile": nat.mobility_percentile,
        "gap_vs_national": gap,
        "dose_years": DOSE_YEARS,
        "multiplier": {
            "point": 1.0 + scale * p.point * gap,
            "low": 1.0 + scale * lo_part * gap,
            "high": 1.0 + scale * hi_part * gap,
        },
        "declared_unit": (
            "annual exposure effect gamma (increase in adult income rank "
            "per year of childhood per 1 percentile of county permanent-"
            "resident income rank); dose = 18y complete childhood in the "
            "county, declared"
        ),
        "citation": p.citation,
    }
