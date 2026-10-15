# @ref:test-source-reextraction
# Method: @link:doc-citing.
# Implementation: @link:code-params.
# @tag:evidence @tag:testing
import math

import pytest

from downstream.params import load_all


def test_source_offset_four_five_uses_its_own_column_standard_error():
    row = load_all()["params"].by_link("earnings_shock->mortality_offsets_4_5")
    assert row.low == pytest.approx(math.exp(.240 - 1.96 * .138), abs=5e-5)
    assert row.high == pytest.approx(math.exp(.240 + 1.96 * .138), abs=5e-5)
    assert row.low < 1 < row.high
    assert "SE 0.138" in row.notes
    assert "born 1930-1959" in row.population_scope
