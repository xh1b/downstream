"""Credits engine checks — the computed collective must stay exact."""

import pytest

from downstream.citations import parse_bib
from downstream.credits import attribution_sentences, collect, parse_authors, write_credits_md
from downstream.params import default_dir


@pytest.fixture
def data():
    d = default_dir()
    return collect(parse_bib(d / "references.bib"), d)


def test_attribution_numbers_match_the_bib(data):
    sents = attribution_sentences(data)
    assert str(data["bib_entries"]) in sents[0]
    assert str(len(data["researchers"])) in sents[0]
    assert sents[0].endswith(".")


def test_author_parsing_traps():
    # corporate authors stay whole
    assert parse_authors("{World Bank}") == ["World Bank"]
    # accented LaTeX cleans without loss
    assert parse_authors("Galofr{\\'e}-Vil{\\`a}, Gregori and Meissner, Chris")[0].endswith("Gregori")
    # 'and others' contributes no name
    assert parse_authors("Sullivan, Daniel and others") == ["Sullivan, Daniel"]
    # suffixes survive the surname split
    assert parse_authors("Charles, Kerwin Kofi and Stephens, Melvin, Jr.")[1] == "Stephens, Melvin, Jr."


def test_parameter_keys_are_a_subset_of_the_bib(data):
    bib_keys = {s["key"] for s in data["studies"]}
    assert set(data["parameter_keys"]) <= bib_keys


def test_roles_partition(data):
    roles = {s["role"] for s in data["studies"]}
    assert {"parameter", "methodology", "context"} <= roles
    every = {s["key"] for s in data["studies"]}
    assert sum(1 for s in data["studies"]) == len(every)  # keys unique


def test_year_span_is_sane(data):
    assert data["year_min"] >= 1950
    assert data["year_max"] <= 2030


def test_generated_credits_is_a_complete_renderable_attribution(data, tmp_path):
    output = tmp_path / "CREDITS.md"
    text = write_credits_md(data, output)
    assert output.read_text(encoding="utf-8") == text
    assert "## The researchers" in text
    assert "| key | authors | year | venue | role | evidence | doi |" in text
    assert "parameter-source study" in text
