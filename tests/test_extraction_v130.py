"""v1.30 pins: #23 Chetty-Hendren extraction + #30 Opportunity Atlas plug.

What this file hunts:
- the landed gamma row drifting: EXACT tier, the county-level estimate
  (NOT the CZ-level), the declared per-year unit, the dose semantics,
  and the dist shape (normal: reported CI = 1.96 SE)
- the CZ/county mixup: the paper's CZ estimate (0.040) must NOT be
  the landed point — county geography is the pin
- build_places regressions: deterministic output, count-weighted
  national mean, skip semantics (missing kfr, zero count, territories)
- the real places.csv: 3k+ county rows, the national row present,
  Philadelphia's value pinned, no US territories
- the real modifier: national = exactly 1.0, Philly below 1, bands
  bracket points, magnitudes match the declared 18-year dose
"""
import csv

import pytest

from downstream.build_places import build_places
from downstream.params import default_dir, load
from downstream.place import DOSE_YEARS, load_places, mobility_modifier

PARAMS_DIR = default_dir()
PARAMS = load(PARAMS_DIR / "parameters.csv")
LINK = "neighborhood_exposure->child_outcomes_modifier"


def test_version_is_v130():
    assert (PARAMS_DIR / "VERSION").read_text().strip() == "v1.36"


def _row():
    return PARAMS.by_link(LINK)


# --- the gamma row ---------------------------------------------------

def test_gamma_landed_exact_county_level():
    p = _row()
    assert p.tier == "EXACT"
    assert p.point == 0.037
    assert p.low == 0.031 and p.high == 0.043


def test_gamma_is_the_county_not_cz_estimate():
    # the CZ estimate is 0.040 — landing it for county places would be
    # a geography mismatch the paper itself flags (gamma smaller at
    # county level); the notes must record the CZ number beside
    assert "0.040" in _row().notes and "Appendix Table V" in _row().notes


def test_gamma_unit_is_per_year_and_cited():
    p = _row()
    assert "ADDITIONAL YEAR" in p.notes or "additional year" in p.notes
    assert p.citation == "chettyhendren2018"
    assert p.dist == "normal"


def test_dose_years_declared():
    assert DOSE_YEARS == 18.0


# --- build_places ----------------------------------------------------

def test_build_places_is_deterministic(tmp_path):
    r1 = build_places(PARAMS_DIR)
    out1 = (PARAMS_DIR / "places.csv").read_text()
    build_places(PARAMS_DIR)
    out2 = (PARAMS_DIR / "places.csv").read_text()
    assert out1 == out2
    assert r1["counties"] > 3000


def test_build_places_report_is_json_safe():
    import json

    json.dumps(build_places(PARAMS_DIR))


def test_build_places_skips_and_weighted_mean():
    atlas = list(
        csv.DictReader(
            open(
                PARAMS_DIR.parent / "validation"
                / "opportunity_atlas_county_outcomes_simple.csv",
                newline="",
            )
        )
    )
    rep = build_places(PARAMS_DIR)
    total_count = sum(
        float(r["pooled_pooled_count"])
        for r in atlas
        if r["kfr_pooled_pooled_p25"].strip()
        and r["pooled_pooled_count"].strip()
        and float(r["pooled_pooled_count"]) > 0
    )
    assert f"{rep['national_percentile']:.4f}" == "40.7679"
    assert rep["counties"] == 3134


# --- the real places.csv ---------------------------------------------

PLACES = load_places()


def test_places_national_row_present_with_percentile():
    nat = PLACES["national"]
    assert nat.level == "national"
    assert nat.mobility_percentile == pytest.approx(40.7679)


def test_places_county_rows_have_names_and_n():
    assert PLACES["42101"].name == "Philadelphia County, PA"
    assert PLACES["42101"].mobility_percentile == pytest.approx(36.6101)
    assert PLACES["17031"].name == "Cook County, IL"
    # every county row carries the file citation
    assert all(
        p.citation.startswith("opportunity_atlas")
        for k, p in PLACES.items()
        if k != "national"
    )


def test_places_no_territories():
    bad = [k for k, p in PLACES.items() if k[:2] in ("60", "66", "69", "72", "78")]
    assert bad == []


def test_places_percentiles_within_rank_scale():
    vals = [p.mobility_percentile for p in PLACES.values() if p.mobility_percentile is not None]
    assert min(vals) > 0 and max(vals) < 100


# --- the real modifier ------------------------------------------------

def test_real_modifier_national_is_exactly_one():
    m = mobility_modifier(PARAMS, PLACES, "national")
    assert m["applied"] is True
    assert m["multiplier"]["point"] == pytest.approx(1.0)
    assert m["dose_years"] == 18.0


def test_real_modifier_philadelphia_below_national():
    m = mobility_modifier(PARAMS, PLACES, "42101")
    assert m["gap_vs_national"] == pytest.approx(36.6101 - 40.7679, abs=1e-6)
    expected = 1 + (DOSE_YEARS / 100) * 0.037 * m["gap_vs_national"]
    assert m["multiplier"]["point"] == pytest.approx(expected)
    assert m["multiplier"]["low"] < m["multiplier"]["point"] < m["multiplier"]["high"]
    # Philadelphia (kfr 36.6 vs national 40.8) lands near -2.8%
    assert m["multiplier"]["point"] == pytest.approx(0.9723, abs=1e-3)


def test_real_modifier_high_mobility_county_above_one():
    m = mobility_modifier(PARAMS, PLACES, "49035")  # Salt Lake County UT
    assert m["multiplier"]["point"] > 1.0
    assert m["multiplier"]["low"] > 1.0  # positive gap: the band stays above 1


def test_real_modifier_band_brackets_point_across_counties():
    for key in ("42101", "08014", "25013", "36047"):
        m = mobility_modifier(PARAMS, PLACES, key)
        assert m["multiplier"]["low"] <= m["multiplier"]["point"] <= m["multiplier"]["high"], key
