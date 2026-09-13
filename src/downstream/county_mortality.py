"""Validate profile-declared county aggregates exported by CDC WONDER.

The importer intentionally validates a supplied demographic/time profile,
rather than hard-coding a prime-age-male slice. Keep suppressed cells missing;
never reconstruct them from totals or adjacent counties.
"""
from __future__ import annotations

import csv
import hashlib
import io
from pathlib import Path
from dataclasses import dataclass


@dataclass(frozen=True)
class MortalityQueryProfile:
    """The exact population/time definition behind one county export."""

    years: tuple[int, ...]
    sex: str
    age: str
    cause: str = "All causes"
    geography: str = "County"
    population_unit: str = "person-years"

    @classmethod
    def from_metadata(cls, metadata: dict) -> "MortalityQueryProfile":
        try:
            years = tuple(sorted(int(value) for value in metadata["years"]))
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("metadata.years must be a nonempty list of integer years") from exc
        if not years or len(set(years)) != len(years):
            raise ValueError("metadata.years must be nonempty and unique")
        if any(later - earlier != 1 for earlier, later in zip(years, years[1:])):
            raise ValueError(
                "metadata.years must be a contiguous window; the reported "
                "min-max time window would misrepresent a disjoint selection"
            )
        fields = {name: str(metadata.get(name, "")).strip()
                  for name in ("sex", "age", "cause", "population_unit")}
        if not fields["sex"] or not fields["age"]:
            raise ValueError("metadata.sex and metadata.age are required")
        undeclared = [name for name in ("cause", "population_unit") if not fields[name]]
        if undeclared:
            raise ValueError(
                f"metadata must declare {', '.join(undeclared)} explicitly; "
                "silent defaults would repeat the unreproducible-filter problem "
                "that keeps raw WONDER exports context-only"
            )
        return cls(years, fields["sex"], fields["age"], fields["cause"],
                   "County", fields["population_unit"])

    def as_dict(self) -> dict:
        return {"years": list(self.years), "sex": self.sex, "age": self.age,
                "cause": self.cause, "geography": self.geography,
                "population_unit": self.population_unit}


def parse_export(path, *, metadata):
    """Return place inputs, plus source and suppression counts.

    Metadata must come from saved query settings. The table must group only
    by county; any sex, age band, years, and cause are accepted when declared
    in that metadata. Population is summed person-time for the chosen window.
    """
    profile = MortalityQueryProfile.from_metadata(metadata)
    if metadata.get("group_by") != ["County"]:
        raise ValueError("incompatible WONDER query setting: group_by must be ['County']")
    if profile.population_unit != "person-years":
        raise ValueError("incompatible WONDER query setting: population_unit must be 'person-years'")
    if not metadata.get("source_url") or not metadata.get("retrieved_at"):
        raise ValueError("source_url and retrieved_at are required")
    raw = Path(path).read_bytes()
    decoded = raw.decode("utf-8-sig")
    # WONDER's browser export is CSV; some saved exports are TSV. Sniffing
    # mis-handles quoted commas ("Autauga County, AL") and shifts footnote
    # cells into data columns, so detect the delimiter directly: a genuine
    # export is tab-delimited iff it contains tabs.
    dialect = csv.excel_tab if "\t" in decoded[:8192] else csv.excel
    reader = csv.DictReader(io.StringIO(decoded), dialect=dialect)
    if not {"County Code", "Deaths", "Population"} <= set(reader.fieldnames or []):
        raise ValueError("expected a county WONDER tab-delimited export")
    rows, count_rows, suppressed, unavailable = {}, {}, 0, 0
    seen = set()
    for row in reader:
        code = (row.get("County Code") or "").strip()
        if not code:
            continue  # export notes and totals have no county key
        if len(code) != 5 or not code.isdigit():
            raise ValueError(f"invalid county FIPS: {code!r}")
        if code in seen:
            raise ValueError(f"duplicate county: {code}; group by county only")
        seen.add(code)
        deaths = (row.get("Deaths") or "").strip()
        pop = (row.get("Population") or "").strip()
        if deaths.lower() == "suppressed":
            suppressed += 1
            continue
        if not deaths.isdigit() or not pop.isdigit() or int(pop) <= 0:
            unavailable += 1
            continue
        deaths, pop = int(deaths), int(pop)
        if deaths <= 9:
            suppressed += 1
            continue
        if deaths > pop:
            raise ValueError(f"deaths exceed person-years for {code}")
        rows[code] = {"mortality_rate": deaths / pop, "mortality_n": deaths}
        count_rows[code] = {"events": deaths, "person_years": pop}
    if not seen:
        raise ValueError("export contains no county rows")
    return {"rows": rows, "count_rows": count_rows, "suppressed_count": suppressed,
            "unavailable_count": unavailable, "query": {**metadata, "profile": profile.as_dict()},
            "source_sha256": hashlib.sha256(raw).hexdigest()}


def _outcome_id(cause: str) -> str:
    """Map the declared cause of death to a count-layer outcome id.

    ``All causes`` keeps the historical ``all_cause_mortality_annual`` id. Any
    other declared cause becomes its own outcome so the Bayesian prior can
    only match a national rate for the *same* cause — never an all-cause
    prior silently fit to cause-specific events.
    """
    normalized = " ".join(cause.split()).lower()
    if normalized == "all causes":
        return "all_cause_mortality_annual"
    slug = "_".join(part for part in
                    "".join(ch if ch.isalnum() else "_" for ch in normalized).split("_")
                    if part)
    if not slug:
        raise ValueError(f"declared cause {cause!r} cannot be mapped to an outcome id")
    return f"{slug}_mortality_annual"


def count_observations(parsed: dict):
    """Adapt a validated WONDER export into strict count-likelihood rows.

    This is the only supported bridge from a county WONDER export to the
    Bayesian county-rate layer. Suppressed cells never enter the result.
    """
    from .county_rates import CountyRateObservation

    query = parsed["query"]
    profile = query.get("profile", query)
    years = profile["years"]
    window = f"{min(years)}-{max(years)}"
    citation = query.get("citation") or query["source_url"]
    outcome = _outcome_id(profile["cause"])
    scope = f"county residents, {profile['sex'].lower()}, ages {profile['age']}; cause: {profile['cause']}"
    return tuple(
        CountyRateObservation(
            key=key, outcome=outcome, events=row["events"],
            person_years=row["person_years"], population_scope=scope,
            time_window=window, citation=citation,
        )
        for key, row in sorted(parsed["count_rows"].items())
    )
