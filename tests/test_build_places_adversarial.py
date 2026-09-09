"""Small hostile fixtures for Opportunity Atlas place-file ingestion."""
from __future__ import annotations

import pytest

from downstream.build_places import build_places


def _fixture_root(tmp_path, atlas_rows, geoid_rows="1001,Alpha,AA\n"):
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
    return params


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
