"""Build params/places.csv from the Opportunity Atlas county outcomes
and the CDC WONDER county mortality export.

Derivation (declared):

- Source: Opportunity Insights `county_outcomes_simple.csv` (Chetty,
  Friedman, Hendren, Jones & Porter 2018, AER 108(2):241-250 companion
  data; published 2018-10), copied verbatim into
  `validation/opportunity_atlas_county_outcomes_simple.csv`.
- `mobility_percentile` = kfr_pooled_pooled_p25 x 100: the mean income
  rank percentile (age 24) of children of permanent residents whose
  parents sit near the 25th income percentile — the same
  permanent-resident outcome the Chetty & Hendren 2018 exposure
  effect is defined against (income rank at a given level of parental
  income, not an unconditioned rate).
- `mobility_n` = the file's `pooled_pooled_count` (children behind the
  county mean) — provenance only; shrinkage does not apply to
  percentiles.
- The `national` row's mobility_percentile = the count-weighted mean
  of kfr across ALL counties in the file (the exhaustive-county
  mean IS the national mean by construction of the Atlas data); the
  modifier pools toward this reference, never a hard-coded 50.
- County names from Opportunity Insights `GeoIDs - County.csv`
  (copied into validation/geoids_county.csv).
- Skipped: counties with missing kfr or a zero child count (no
  measured mobility), and US territories (state FIPS 60/66/69/72/78) —
  the model's scope is the 50 states + DC. Skips are counted and
  reported by the build.
- Counties with missing kfr are SKIPPED (no row): the place-resolved
  layer then falls back to national for them, honestly.

- Mortality source: CDC WONDER D76 county export
  `validation/cdc_wonder_county_male_45_54_2015_2019.csv` (+ the
  .metadata.json saved-query sidecar), male 45-54 years, pooled
  2015-2019 — the exact population and window of
  baselines.csv:all_cause_mortality_annual. Validated with
  county_mortality.parse_export + count_observations.
- `mortality_rate` = the Gamma-Poisson posterior mean per person-year:
  each county's deaths/person-years pooled toward the verified
  national baseline pin 0.004944 with 2000 prior person-years (the
  declared prior strength, place.py PRIOR_N) via
  county_rates.NationalRatePrior + poisson_gamma_posterior — closed
  form (prior_events + events)/(prior_person_years + person_years);
  draws (fixed seed) feed only the quantiles, which places.csv does
  not carry. Same unit and population as the national baseline: no
  conversion anywhere.
- `mortality_n` = the county person-years behind the export row: the
  precision label whose w = n/(n+k) with k = the 2000 prior
  person-years reproduces the posterior's pooling weight. It is NOT a
  binomial denominator (place.py's comment); events and person-years
  live in full in params/county_mortality.csv under the strict
  CountyRateObservation contract.
- Suppressed (<10 deaths) or absent counties keep EMPTY mortality
  columns: the place layer falls back to national for them. Never
  reconstructed from totals or neighbors.
- The `national` row carries the pin 0.004944 and the export Total
  row's person-years (the Total includes suppressed counties' deaths).
  The build refuses if Total deaths / Total person-years does not
  reproduce the pin at its 6-decimal precision — a wrong population or
  window must not ship silently.

Run: downstream build-places
"""

from __future__ import annotations

import csv
import io
import json
import math
from pathlib import Path

from .county_mortality import count_observations, parse_export
from .county_rates import NationalRatePrior, poisson_gamma_posterior
from .params import default_dir

ATLAS_FILE = "opportunity_atlas_county_outcomes_simple.csv"
GEOMAP_FILE = "geoids_county.csv"
WONDER_FILE = "cdc_wonder_county_male_45_54_2015_2019.csv"

KFR_COL = "kfr_pooled_pooled_p25"
KFR_SE_COL = "kfr_pooled_pooled_p25_se"
COUNT_COL = "pooled_pooled_count"

# The verified national baseline (baselines.csv:all_cause_mortality_annual):
# male 45-54, pooled 2015-2019, deaths per person-year.
NATIONAL_RATE_PIN = 0.004944
# Declared prior strength — place.py PRIOR_N["all_cause_mortality_annual"],
# the same 2000 equivalent person-years scripts/build_county_mortality.py
# pools with under the strict contract.
PRIOR_PERSON_YEARS = 2000.0
# Fixed seed for poisson_gamma_posterior's draws; the posterior MEAN is
# closed form (alpha/beta), so places.csv is deterministic regardless.
POSTERIOR_SEED = 1901

CITATION_MOBILITY = (
    "opportunity_atlas county_outcomes_simple (Chetty, Friedman, Hendren, "
    "Jones & Porter 2018, AER 108(2):241-250 companion data, 2018-10 "
    "release); mobility_percentile = kfr_pooled_pooled_p25 x 100; national "
    "= count-weighted mean of all counties in the file; names from "
    "Opportunity Insights GeoIDs - County.csv"
)
CITATION_MORTALITY = (
    "mortality_rate: CDC WONDER D76 county export "
    f"{WONDER_FILE} (male 45-54 years, pooled 2015-2019), Gamma-Poisson "
    "posterior mean per person-year shrunk toward the national baseline "
    "pin 0.004944 with 2000 prior person-years; mortality_n = county "
    "person-years (precision label, NOT a binomial denominator); "
    "suppressed/absent counties left empty — national fallback"
)
CITATION = CITATION_MOBILITY + "; " + CITATION_MORTALITY

HEADER = (
    "# places.csv — the place-resolved layer's data plug (built by "
    "downstream build-places; DO NOT hand-edit).\n"
    "# mobility_percentile: mean income-rank percentile (0-100) of "
    "children of permanent residents at pooled parental income p25\n"
    "#   (kfr_pooled_pooled_p25 x 100 from the Opportunity Atlas county "
    "file) — the Chetty-Hendren exposure effect's own treatment scale.\n"
    "# mortality_rate / divorce_rate: MUST be in the same unit and "
    "population as baselines.csv:all_cause_mortality_annual /\n"
    "#   divorce_5y_cumulative (no conversion in the loader); *_n are "
    "the precision counts behind those county values.\n"
    "# mortality_rate derivation: CDC WONDER D76 county export (male "
    "45-54 years, pooled 2015-2019;\n"
    f"#   validation/{WONDER_FILE}), Gamma-Poisson posterior mean per "
    "person-year, shrunk toward the national\n"
    "#   baseline pin 0.004944 with 2000 prior person-years — the exact "
    "unit and population of\n"
    "#   baselines.csv:all_cause_mortality_annual; no conversion anywhere.\n"
    "# mortality_n: the county person-years — a precision label for the "
    "pooling weight w = n/(n+k)\n"
    "#   (k = 2000 prior person-years), NOT a binomial denominator. "
    "Counties suppressed (<10 deaths)\n"
    "#   or absent from the export keep empty mortality columns and fall "
    "back to national; never\n"
    "#   reconstructed from totals or neighbors.\n"
)


def _read_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _export_dialect(decoded: str):
    # Same detection rule as county_mortality.parse_export: a genuine
    # export is tab-delimited iff it contains tabs (sniffing mis-handles
    # quoted commas like "Autauga County, AL").
    return csv.excel_tab if "\t" in decoded[:8192] else csv.excel


def _read_export_total(path: Path) -> tuple[int, int]:
    """The export's Total row as (deaths, person-years).

    The Total includes the suppressed counties' deaths, so it is the
    quantity that reproduces the national pin — the per-county visible
    rows never sum to it.
    """
    decoded = path.read_bytes().decode("utf-8-sig")
    for row in csv.DictReader(io.StringIO(decoded), dialect=_export_dialect(decoded)):
        first = next(iter(row.values())) or ""
        if first.strip() != "Total":
            continue
        deaths = (row.get("Deaths") or "").strip()
        person_years = (row.get("Population") or "").strip()
        if not deaths.isdigit() or not person_years.isdigit():
            raise ValueError("WONDER export Total row is not integral")
        return int(deaths), int(person_years)
    raise ValueError(
        "WONDER export has no Total row; the build verifies the national "
        "baseline pin against it before shipping"
    )


# The Atlas also ships Puerto Rico (state FIPS 72); the model is US
# 50-states + DC, so state FIPS >= 60 (territories) are skipped too.
NONSTATE_FIPS = {"60", "66", "69", "72", "78"}


def build_places(params_dir: str | Path | None = None) -> dict:
    """Derive places.csv. Returns {"counties", "national_percentile", ...}."""
    d = Path(params_dir) if params_dir else default_dir()
    validation = d.parent / "validation"

    atlas = _read_csv(validation / ATLAS_FILE)
    names = {}
    for row_number, r in enumerate(_read_csv(validation / GEOMAP_FILE), start=2):
        raw_fips = (r.get("countyfips") or "").strip()
        if not raw_fips.isdigit():
            continue
        fips = f"{int(raw_fips):05d}"
        if fips in names:
            raise ValueError(f"duplicate countyfips {fips} in {GEOMAP_FILE} row {row_number}")
        names[fips] = (r.get("countyname", ""), r.get("stateabbrev", ""))

    wonder_path = validation / WONDER_FILE
    metadata_path = wonder_path.with_suffix(".metadata.json")
    for required in (wonder_path, metadata_path):
        if not required.exists():
            raise FileNotFoundError(
                f"missing {required.name} under {validation}/ — the mortality "
                "columns of places.csv are derived from the committed WONDER "
                "county export (scripts/fetch_wonder.py county)"
            )
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    parsed = parse_export(wonder_path, metadata=metadata)
    observations = count_observations(parsed)
    if not observations:
        raise ValueError("the WONDER export yielded no usable county observations")
    # One export = one declared profile, so every observation shares the
    # same outcome/scope/window; the prior is built from the first and
    # poisson_gamma_posterior re-verifies the identity on every call.
    head = observations[0]
    prior = NationalRatePrior(
        outcome=head.outcome,
        rate=NATIONAL_RATE_PIN,
        population_scope=head.population_scope,
        time_window=head.time_window,
        citation=parsed["query"].get("citation") or parsed["query"]["source_url"],
    )
    mortality: dict[str, tuple[str, str]] = {}
    for obs in observations:
        posterior = poisson_gamma_posterior(
            obs, prior, PRIOR_PERSON_YEARS, draws=2, seed=POSTERIOR_SEED
        )
        mortality[obs.key] = (
            f"{posterior['posterior']['mean_rate']:.9f}",
            f"{int(obs.person_years)}",
        )
    total_deaths, total_person_years = _read_export_total(wonder_path)
    if round(total_deaths / total_person_years, 6) != round(NATIONAL_RATE_PIN, 6):
        raise ValueError(
            f"WONDER export Total {total_deaths}/{total_person_years} does not "
            f"reproduce the national baseline pin {NATIONAL_RATE_PIN} — wrong "
            "population or window for this places build"
        )

    rows: list[str] = []
    total_n = 0.0
    weighted_sum = 0.0
    skipped = 0
    without_mortality = 0
    seen_fips = set()
    for row_number, r in enumerate(atlas, start=2):
        kfr = (r.get(KFR_COL) or "").strip()
        count_raw = (r.get(COUNT_COL) or "").strip()
        if not kfr or not count_raw:
            skipped += 1
            continue
        try:
            count = float(count_raw)
            percentile_fraction = float(kfr)
        except ValueError as exc:
            raise ValueError(f"malformed Atlas numeric value at row {row_number}") from exc
        if not math.isfinite(count) or not math.isfinite(percentile_fraction):
            raise ValueError(f"non-finite Atlas numeric value at row {row_number}")
        if count < 0:
            raise ValueError(f"negative Atlas child count at row {row_number}")
        if not 0 <= percentile_fraction <= 1:
            raise ValueError(f"Atlas income rank must be in [0, 1] at row {row_number}")
        if count == 0:
            skipped += 1
            continue
        try:
            state = int(r["state"])
            county = int(r["county"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"malformed Atlas FIPS at row {row_number}") from exc
        if not 1 <= state <= 78 or not 1 <= county <= 999:
            raise ValueError(f"out-of-range Atlas FIPS at row {row_number}")
        state_fips = f"{state:02d}"
        if state_fips in NONSTATE_FIPS:
            skipped += 1
            continue
        pct = percentile_fraction * 100.0
        fips = f"{state:02d}{county:03d}"
        if fips in seen_fips:
            raise ValueError(f"duplicate Atlas county FIPS {fips}")
        seen_fips.add(fips)
        cname, sabb = names.get(fips, ("", ""))
        name = f"{cname} County, {sabb}" if cname else f"county FIPS {fips}"
        mortality_cols = mortality.get(fips, ("", ""))
        if mortality_cols[0] == "":
            without_mortality += 1
        rows.append(
            ",".join(
                [
                    fips,
                    f'"{name}"',
                    "county",
                    f"{pct:.4f}",
                    f"{count:.1f}",
                    *mortality_cols,
                    "", "",
                    f'"{CITATION}"',
                ]
            )
        )
        weighted_sum += pct * count
        total_n += count

    national_pct = weighted_sum / total_n if total_n else None
    national_row = ",".join(
        [
            "national",
            '"United States"',
            "national",
            f"{national_pct:.4f}" if national_pct is not None else "",
            f"{total_n:.1f}",
            str(NATIONAL_RATE_PIN),
            str(total_person_years),
            "", "",
            f'"{CITATION}"',
        ]
    )

    out_path = d / "places.csv"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(HEADER)
        f.write(
            "key,name,level,mobility_percentile,mobility_n,mortality_rate,"
            "mortality_n,divorce_rate,divorce_n,citation\n"
        )
        f.write(national_row + "\n")
        for line in sorted(rows):
            f.write(line + "\n")

    return {
        "counties": len(rows),
        "skipped_missing_kfr": skipped,
        "national_percentile": round(national_pct, 4) if national_pct is not None else None,
        "mortality_counties": len(mortality),
        "mortality_suppressed_or_unavailable": (
            parsed["suppressed_count"] + parsed["unavailable_count"]
        ),
        "counties_without_export_row": without_mortality,
        "export_counties_outside_the_atlas": len(set(mortality) - seen_fips),
        "national_total_person_years": total_person_years,
        "out_path": str(out_path),
    }
