"""Consumer acceptance must preserve normalization, scope and shared comparisons."""
import copy
import math

import pytest

from downstream.consumer import mix_expected, scale_outcome
from scripts.build_consumer_fixtures import build


@pytest.fixture(scope="module")
def pack():
    return build()


def test_fractional_display_keeps_native_precision_and_parameter_values(pack):
    source = pack["fixtures"]["national"]["result"]["modeled"]["excess_deaths"]
    scaled = pack["expected_display_values"]["0.125"]["excess_deaths"]
    native = pack["fixtures"]["fractional"]["result"]["modeled"]["excess_deaths"]
    assert scaled["point"] == pytest.approx(native["point"])
    assert 0 < scaled["point"] < .004
    a, b = source["sensitivity"], scaled["sensitivity"]
    factor = .125 / 1000
    assert b["reference_point"] == pytest.approx(a["reference_point"] * factor)
    assert b["variance_attribution"]["output_variance"] == pytest.approx(
        a["variance_attribution"]["output_variance"] * factor**2)
    assert b["variance_attribution"]["blocks"] == a["variance_attribution"]["blocks"]
    for left, right in zip(a["effect_drivers"], b["effect_drivers"]):
        assert left["input_value"] == right["input_value"]
        assert left["citation"] == right["citation"]
        assert left["supported_range"]["input_low"] == right["supported_range"]["input_low"]
        assert right["effect_removed"]["point"] == pytest.approx(left["effect_removed"]["point"] * factor)
        assert right["supported_range"]["endpoint_span"] == pytest.approx(
            left["supported_range"]["endpoint_span"] * factor)
    assert source["point"] > scaled["point"]


def test_zero_and_large_exposure_scale_only_result_statistics(pack):
    for workers in (0, 1_000_000):
        for key, row in pack["expected_display_values"][str(workers)].items():
            source = pack["fixtures"]["national"]["result"]["modeled"][key]
            assert row["point"] == pytest.approx(source["point"] * workers / 1000)
            assert row["baseline"] == source["baseline"]
            assert row["applicability"] == source["applicability"]
            assert row["parameter_interval_90"]["p05"] == pytest.approx(
                source["parameter_interval_90"]["p05"] * workers / 1000)
            if workers == 0:
                assert not row["sensitivity"]["variance_attribution"]["available"]


def test_persistence_mixture_uses_both_components_in_every_variant(pack):
    county = pack["fixtures"]["county_17043"]["result"]["modeled"]["excess_deaths"]
    national = pack["fixtures"]["national"]["result"]["modeled"]["excess_deaths"]
    mixed = pack["mixtures"]["county_national"]["expected"]["excess_deaths"]
    for name in ("source_profile", "no_sustained_excess"):
        for stat in ("point", "low", "high"):
            expected = sum(w*r["persistence_sensitivity"]["variants"][name][stat]
                           for w, r in [(.6, county), (.4, national)])
            assert mixed["persistence_sensitivity"]["variants"][name][stat] == pytest.approx(expected)
    assert mixed["point"] != pytest.approx(county["point"])
    assert mixed["baseline"] != county["baseline"]
    late = "earnings_shock->mortality_sustained"
    assert mixed["effect_removal_points"][late] == pytest.approx(
        mixed["persistence_sensitivity"]["variants"]["no_sustained_excess"]["point"])
    assert not mixed["parameter_interval_90"]["available"]
    assert not mixed["variance_attribution"]["available"]
    for key, expected in mixed["supported_endpoint_points"].items():
        assert expected["available"]
        for bound in ("low", "high"):
            values = []
            for source in (county, national):
                driver = next(d for d in source["sensitivity"]["effect_drivers"] if d["input_id"] == key)
                values.append(driver["supported_range"][f"at_input_{bound}"]["point"])
            assert expected[f"at_input_{bound}"] == pytest.approx(.6*values[0]+.4*values[1])


def test_partial_review_and_missing_outcomes_cannot_become_headline_or_zero(pack):
    reviewed = pack["fixtures"]["synthetic_reviewed"]["result"]
    assert all(row["applicability"]["eligible_for_public_headline"] for row in reviewed["modeled"].values())
    assert all(not row["eligible_for_public_headline"] for row in
               pack["mixtures"]["partly_reviewed"]["expected"].values())
    for row in pack["mixtures"]["partly_blocked"]["expected"].values():
        assert row["available"] is False
        assert "point" not in row
    national = pack["fixtures"]["national"]["result"]
    blocked = pack["fixtures"]["blocked_demographics"]["result"]
    assert mix_expected([national, blocked], [1, 0], "excess_deaths")["available"]


def test_explicit_fallback_and_negative_child_valuation_are_preserved(pack):
    fallback = pack["fixtures"]["unsupported_county"]
    assert fallback["requested_place"] == "72127"
    assert fallback["resolved_place"] == "national"
    assert fallback["fallback_reason"]
    child = pack["fixtures"]["beneficial_child"]["result"]["modeled"]["child_lifetime_earnings_lost_usd"]
    assert child["point"] < 0
    assert scale_outcome(child, .5)["point"] < 0
    value = pack["fixtures"]["valuation"]["result"]["child_valuation"]["projections"]["constant_career_gap"]
    scaled = scale_outcome(value, .5)
    assert scaled["point"] == value["point"] / 2
    assert scaled["annual_schedules_per_worker_family"] == value["annual_schedules_per_worker_family"]


@pytest.mark.parametrize("factor", [-1, True, math.inf, math.nan])
def test_invalid_display_factors_fail(factor):
    with pytest.raises(ValueError):
        scale_outcome({"point": 1}, factor)


@pytest.mark.parametrize("weights", [[], [.5], [.2, .2], [-.1, 1.1], [True, 0], [math.nan, 0]])
def test_invalid_mixture_weights_fail(pack, weights):
    result = pack["fixtures"]["national"]["result"]
    with pytest.raises(ValueError):
        mix_expected([result, result], weights, "excess_deaths")


def test_mixtures_refuse_unlike_units_and_absent_comparisons(pack):
    source = pack["fixtures"]["national"]["result"]
    other = copy.deepcopy(source)
    other["modeled"]["excess_deaths"]["unit"] = "jobs"
    with pytest.raises(ValueError, match="unlike"):
        mix_expected([source, other], [.5, .5], "excess_deaths")
    other["modeled"]["excess_deaths"]["unit"] = "deaths"
    other["modeled"]["excess_deaths"].pop("persistence_sensitivity")
    mixed = mix_expected([source, other], [.5, .5], "excess_deaths")
    assert not mixed["persistence_sensitivity"]["available"]
