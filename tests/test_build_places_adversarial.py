"""Small hostile fixtures for Opportunity Atlas place-file ingestion."""
from __future__ import annotations

import csv
import io

import pytest

from downstream.build_places import build_places

WONDER_CSV = "cdc_wonder_county_male_45_54_2015_2019.csv"
WONDER_METADATA = "cdc_wonder_county_male_45_54_2015_2019.metadata.json"
WONDER_HEADER = '"Notes","County","County Code",Deaths,Population,Crude Rate\n'
# Two measured counties and one suppressed one; the Total (618/125000 =
# 0.004944 exactly) intentionally exceeds the visible sum because the
# suppressed deaths exist only in it — the real export behaves the same.
WONDER_ROWS = (
    ',"Alpha County, AA","01001",115,19096,602.2\n'
    ',"Beta County, AA","01003",370,68663,538.9\n'
    ',"Hidden County, AA","01009",Suppressed,500,\n'
)
WONDER_TOTAL = (618, 125000)
WONDER_METADATA_JSON = (
    '{"years":[2015,2016,2017,2018,2019],"sex":"Male","age":"45-54 years",'
    '"cause":"All causes","group_by":["County"],"population_unit":"person-years",'
    '"source_url":"fixture","retrieved_at":"fixture"}'
)


def _write_wonder(validation, rows=WONDER_ROWS, total=WONDER_TOTAL):
    (validation / WONDER_CSV).write_text(
        WONDER_HEADER + rows + f'"Total",,,{total[0]},{total[1]},494.4\n',
        encoding="utf-8",
    )
    (validation / WONDER_METADATA).write_text(WONDER_METADATA_JSON, encoding="utf-8")


def _fixture_root(tmp_path, atlas_rows, geoid_rows="1001,Alpha,AA\n", **wonder_kwargs):
    params = tmp_path / "params"
    validation = tmp_path / "validation"
    params.mkdir(parents=True)
    validation.mkdir()
    (validation / "geoids_county.csv").write_text(
        "countyfips,countyname,stateabbrev\n" + geoid_rows,
        encoding="utf-8",
    )
    (validation / "opportunity_atlas_county_outcomes_simple.csv").write_text(
        "state,county,kfr_pooled_pooled_p25,kfr_pooled_pooled_p25_se,pooled_pooled_count\n"
        + atlas_rows,
        encoding="utf-8",
    )
    _write_wonder(validation, **wonder_kwargs)
    return params


def _read_places(params):
    lines = [
        ln
        for ln in (params / "places.csv").read_text(encoding="utf-8").splitlines()
        if ln and not ln.startswith("#")
    ]
    return {r["key"]: r for r in csv.DictReader(io.StringIO("\n".join(lines)))}


def test_build_places_filters_territory_and_weights_only_valid_counties(tmp_path):
    params = _fixture_root(
        tmp_path,
        "1,1,0.4,,10\n1,3,0.7,,30\n72,1,0.9,,100\n1,5,,,9\n1,7,0.2,,0\n",
        "1001,Alpha,AA\n1003,Beta,AA\n",
    )
    report = build_places(params)
    assert report["counties"] == 2
    assert report["skipped_missing_kfr"] == 3
    assert report["national_percentile"] == pytest.approx(62.5)
    output = (params / "places.csv").read_text(encoding="utf-8")
    assert "01001" in output and "01003" in output
    assert "72001" not in output


@pytest.mark.parametrize(
    "row, message",
    [
        ("1,1,not-a-number,,10\n", "malformed Atlas numeric"),
        ("1,1,nan,,10\n", "non-finite Atlas numeric"),
        ("1,1,1.1,,10\n", r"income rank must be in \[0, 1\]"),
        ("1,1,0.4,,-1\n", "negative Atlas child count"),
        ("x,1,0.4,,10\n", "malformed Atlas FIPS"),
    ],
)
def test_build_places_refuses_malformed_atlas_rows(tmp_path, row, message):
    params = _fixture_root(tmp_path, row)
    with pytest.raises(ValueError, match=message):
        build_places(params)
    assert not (params / "places.csv").exists()


def test_build_places_refuses_duplicate_atlas_or_geoid_fips(tmp_path):
    params = _fixture_root(tmp_path / "atlas", "1,1,0.4,,10\n1,1,0.5,,20\n")
    with pytest.raises(ValueError, match="duplicate Atlas county FIPS 01001"):
        build_places(params)

    params = _fixture_root(tmp_path / "geoid", "1,1,0.4,,10\n", "1001,Alpha,AA\n01001,Again,AA\n")
    with pytest.raises(ValueError, match="duplicate countyfips 01001"):
        build_places(params)


def test_build_places_output_is_byte_stable_and_sorted(tmp_path):
    params = _fixture_root(tmp_path, "1,3,0.7,,30\n1,1,0.4,,10\n", "1001,Alpha,AA\n1003,Beta,AA\n")
    build_places(params)
    first = (params / "places.csv").read_bytes()
    build_places(params)
    assert (params / "places.csv").read_bytes() == first
    assert first.index(b"01001") < first.index(b"01003")


# --- the WONDER mortality columns -------------------------------------

def test_build_places_fills_hand_checked_shrunk_mortality(tmp_path):
    params = _fixture_root(
        tmp_path,
        "1,1,0.4,,10\n1,3,0.7,,30\n1,5,0.6,,15\n1,9,0.5,,20\n",
        "1001,Alpha,AA\n1003,Beta,AA\n1005,Delta,AA\n1009,Hidden,AA\n",
    )
    report = build_places(params)
    assert report["mortality_counties"] == 2
    assert report["mortality_suppressed_or_unavailable"] == 1
    # 01005 is absent from the export entirely, 01009 is suppressed:
    # both keep empty mortality columns (national fallback, honestly).
    assert report["counties_without_export_row"] == 2
    places = _read_places(params)
    # Hand check (Gamma-Poisson closed form, prior 0.004944 x 2000 py):
    # (0.004944*2000 + 115) / (2000 + 19096) = 124.888 / 21096.
    assert places["01001"]["mortality_rate"] == "0.005919985"
    assert places["01001"]["mortality_n"] == "19096"
    # (0.004944*2000 + 370) / (2000 + 68663) = 379.888 / 70663.
    assert places["01003"]["mortality_rate"] == "0.005376053"
    assert places["01003"]["mortality_n"] == "68663"
    for key in ("01005", "01009"):
        assert places[key]["mortality_rate"] == ""
        assert places[key]["mortality_n"] == ""
    # the citation names the WONDER export alongside the Atlas
    assert "cdc_wonder_county_male_45_54_2015_2019.csv" in places["01001"]["citation"]


def test_build_places_national_row_pins_the_baseline(tmp_path):
    params = _fixture_root(tmp_path, "1,1,0.4,,10\n")
    report = build_places(params)
    nat = _read_places(params)["national"]
    assert nat["mortality_rate"] == "0.004944"
    # the export Total row's person-years (suppressed deaths included)
    assert nat["mortality_n"] == "125000"
    assert report["national_total_person_years"] == 125000


def test_build_places_refuses_export_total_that_misses_the_pin(tmp_path):
    params = _fixture_root(tmp_path, "1,1,0.4,,10\n", total=(100, 125000))
    with pytest.raises(ValueError, match="does not reproduce"):
        build_places(params)


def test_build_places_requires_the_wonder_inputs(tmp_path):
    params = _fixture_root(tmp_path, "1,1,0.4,,10\n")
    (tmp_path / "validation" / WONDER_CSV).unlink()
    with pytest.raises(FileNotFoundError, match="WONDER"):
        build_places(params)
