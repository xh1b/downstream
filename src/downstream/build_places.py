"""Build params/places.csv from the Opportunity Atlas county outcomes.

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

Run: downstream build-places
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

from .params import default_dir

ATLAS_FILE = "opportunity_atlas_county_outcomes_simple.csv"
GEOMAP_FILE = "geoids_county.csv"

KFR_COL = "kfr_pooled_pooled_p25"
KFR_SE_COL = "kfr_pooled_pooled_p25_se"
COUNT_COL = "pooled_pooled_count"

CITATION = (
    "opportunity_atlas county_outcomes_simple (Chetty, Friedman, Hendren, "
    "Jones & Porter 2018, AER 108(2):241-250 companion data, 2018-10 "
    "release); mobility_percentile = kfr_pooled_pooled_p25 x 100; national "
    "= count-weighted mean of all counties in the file; names from "
    "Opportunity Insights GeoIDs - County.csv"
)

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
)


def _read_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# The Atlas also ships Puerto Rico (state FIPS 72); the model is US
# 50-states + DC, so state FIPS >= 60 (territories) are skipped too.
NONSTATE_FIPS = {"60", "66", "69", "72", "78"}


def build_places(params_dir: str | Path | None = None) -> dict:
    """Derive places.csv. Returns {"counties", "national_percentile", "out_path"}."""
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

    rows: list[str] = []
    total_n = 0.0
    weighted_sum = 0.0
    skipped = 0
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
        rows.append(
            ",".join(
                [
                    fips,
                    f'"{name}"',
                    "county",
                    f"{pct:.4f}",
                    f"{count:.1f}",
                    "", "", "", "",
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
            "", "", "", "",
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
        "out_path": str(out_path),
    }
