# @ref:test-artifact-checks
# Implementation: @link:script-artifact-checks; @link:script-build-calculator.
"""Freshness permits measured arithmetic noise, never changed inputs or markup."""
import math

import pytest

from scripts.artifact_checks import same_json
from scripts.build_calculator import same_html


def step(value, count):
    for _ in range(count):
        value = math.nextafter(value, math.inf)
    return value


def test_measured_roundoff_is_bounded_without_changing_either_input():
    left = {"computed": [3.8120118124581133], "source_hash": "original"}
    right = {"computed": [3.8120118124581204], "source_hash": "original"}
    assert same_json(left, right)
    assert left["computed"] == [3.8120118124581133]
    assert right["computed"] == [3.8120118124581204]
    assert same_json(1.0, step(1.0, 32))
    assert not same_json(1.0, step(1.0, 33))


@pytest.mark.parametrize("left,right", [
    (0.0, math.ulp(0.0)), (1, 1.0), (True, 1),
    ([1.0], [1.0, 2.0]), ({"x": 1}, {"y": 1}),
    ({"source_hash": "a"}, {"source_hash": "b"}),
    (1.0, 1.00000001), (math.nan, math.nan), (math.inf, math.inf),
])
def test_changed_structure_metadata_and_real_numeric_drift_fail(left, right):
    assert not same_json(left, right)


def test_calculator_compares_only_its_json_payload_with_the_float_allowance():
    def html(number):
        return '<main>A</main><script id="engine-data" type="application/json">' + str(number) + '</script><script>authored()</script>'
    assert same_html(html(1.0), html(step(1.0, 16)))
    assert not same_html(html(1.0), html(1.01))
    assert not same_html(html(1.0).replace('authored()', 'changed()'), html(1.0))
    assert not same_html(html(1.0).replace('<main>A', '<main>B'), html(1.0))
    assert not same_html(html(1.0).replace('1.0</script>', 'invalid</script>'), html(1.0))
    assert not same_html('no embedded data', html(1.0))
