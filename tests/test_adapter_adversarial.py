"""Hostile I/O fixtures for source adapters; no network calls are made."""
from __future__ import annotations

import pytest

import downstream.brac as brac
from downstream.county_mortality import parse_export


METADATA = {
    "years": [2015, 2016, 2017, 2018, 2019],
    "sex": "Male",
    "age": "45-54 years",
    "cause": "All causes",
    "group_by": ["County"],
    "population_unit": "person-years",
    "source_url": "fixture",
    "retrieved_at": "fixture",
}


@pytest.mark.parametrize(
    "body, message",
    [
        ('"County Code"\t"Deaths"\t"Population"\n"0100"\t"20"\t"100"\n', "invalid county FIPS"),
        ('"County Code"\t"Deaths"\t"Population"\n"01001"\t"101"\t"100"\n', "deaths exceed"),
        ('"County Code"\t"Deaths"\t"Population"\n""\t""\t""\n', "no county rows"),
    ],
)
def test_county_adapter_refuses_hostile_rows(tmp_path, body, message):
    path = tmp_path / "county.tsv"
    path.write_text(body, encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        parse_export(path, metadata=METADATA)


def test_county_adapter_requires_complete_query_provenance(tmp_path):
    path = tmp_path / "county.tsv"
    path.write_text('"County Code"\t"Deaths"\t"Population"\n"01001"\t"20"\t"100"\n')
    with pytest.raises(ValueError, match="source_url"):
        parse_export(path, metadata={k: v for k, v in METADATA.items() if k != "source_url"})


def test_brac_network_failure_never_creates_an_output_directory(tmp_path, monkeypatch):
    def offline(*args, **kwargs):
        raise OSError("network unavailable")

    monkeypatch.setattr(brac, "urlopen", offline)
    destination = tmp_path / "brac-output"
    with pytest.raises(OSError, match="network unavailable"):
        brac.build(destination)
    assert not destination.exists()


def test_brac_parser_refuses_incomplete_or_non_utf8_source():
    with pytest.raises(ValueError, match="reconcile"):
        brac.parse(b"Major base: x; BRAC round: 1991;")
    with pytest.raises(UnicodeDecodeError):
        brac.parse(b"\xff\xfe")
