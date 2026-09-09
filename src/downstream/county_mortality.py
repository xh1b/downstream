"""Validate county aggregates exported by the public CDC WONDER form.

The national WONDER API does not support county queries. Keep suppressed
cells missing. Never reconstruct them from totals or adjacent counties.
"""
from __future__ import annotations

import csv
import hashlib
import io
from pathlib import Path


def parse_export(path, *, metadata):
    """Return place inputs, plus source and suppression counts.

    Metadata must come from the saved query settings. The expected table
    groups by county only and pools 2015–2019 men aged 45–54. Population
    is the sum of annual population counts (person-years).
    """
    expected = {"years": [2015, 2016, 2017, 2018, 2019], "sex": "Male",
                "age": "45-54 years", "group_by": ["County"],
                "population_unit": "person-years"}
    for key, value in expected.items():
        if metadata.get(key) != value:
            raise ValueError(f"incompatible WONDER query setting: {key}")
    if not metadata.get("source_url") or not metadata.get("retrieved_at"):
        raise ValueError("source_url and retrieved_at are required")
    raw = Path(path).read_bytes()
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")), delimiter="\t")
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
            "unavailable_count": unavailable, "query": metadata,
            "source_sha256": hashlib.sha256(raw).hexdigest()}


def count_observations(parsed: dict):
    """Adapt a validated WONDER export into strict count-likelihood rows.

    This is the only supported bridge from a county WONDER export to the
    Bayesian county-rate layer. Suppressed cells never enter the result.
    """
    from .county_rates import CountyRateObservation

    query = parsed["query"]
    years = query["years"]
    window = f"{min(years)}-{max(years)}"
    citation = query.get("citation") or query["source_url"]
    scope = f"county residents, {query['sex'].lower()}, ages {query['age']}"
    return tuple(
        CountyRateObservation(
            key=key, outcome="all_cause_mortality_annual", events=row["events"],
            person_years=row["person_years"], population_scope=scope,
            time_window=window, citation=citation,
        )
        for key, row in sorted(parsed["count_rows"].items())
    )
