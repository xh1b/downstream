"""The reusable consumer API rejects overflow and retains explicit unknowns."""
import pytest

from downstream.consumer import mix_expected, scale_outcome


def packet(row, outcome="excess_deaths"):
    return {"modeled": {outcome: row}, "exposure": {"displaced_workers": 1000}}


def row():
    return {"point": 10.0, "low": 5.0, "high": 15.0, "unit": "deaths",
            "applicability": {"eligible_for_public_headline": False},
            "source": {"coefficient": 1.5},
            "components": {"follow_up_years": 20, "method": "odds_survival", "timing": "source_profile"}}


@pytest.mark.parametrize("factor", ["1", None, {}, 10**400, 1e308])
def test_invalid_or_overflowing_scale_is_explicit(factor):
    with pytest.raises(ValueError):
        scale_outcome(row(), factor)


def test_scalar_source_data_and_original_result_are_retained():
    original = row()
    scaled = scale_outcome(original, .125)
    assert scaled["point"] == 1.25
    assert scaled["source"] == original["source"]
    assert original["point"] == 10


@pytest.mark.parametrize("weights", ["1", None, [10**400], [True]])
def test_malformed_weights_are_explicit(weights):
    with pytest.raises(ValueError):
        mix_expected([packet(row())], weights, "excess_deaths")


def test_legacy_result_does_not_invent_sensitivity():
    result = mix_expected([packet(row())], [1], "excess_deaths")
    assert result["point"] == 10
    assert not result["effect_removal_points"]["available"]
    assert not result["supported_endpoint_points"]["available"]
    assert not result["parameter_interval_90"]["available"]


def test_mixture_refuses_nonfinite_source_output():
    source = row()
    source["point"] = float("inf")
    with pytest.raises(ValueError, match="finite numeric"):
        mix_expected([packet(source)], [1], "excess_deaths")


def test_large_factor_does_not_overflow_a_finite_variance_result():
    source = row()
    source.update(point=1e-308, low=1e-308, high=1e-308)
    source["sensitivity"] = {"reference_point": 1e-308, "effect_drivers": [],
                             "variance_attribution": {"available": True, "output_variance": 1e-308}}
    result = scale_outcome(source, 1e308)
    assert result["point"] == pytest.approx(1)
    assert result["sensitivity"]["variance_attribution"]["output_variance"] == pytest.approx(1e308)


def test_component_scope_and_identity_are_preserved_without_first_component_inheritance():
    first, second = row(), row()
    first["baseline"] = {"population": "county"}
    second["baseline"] = {"population": "national"}
    results = [{**packet(first, "deaths"), "input_content_sha256": "first"},
               {**packet(second, "deaths"), "input_content_sha256": "second"}]
    mixed = mix_expected(results, [.25, .75], "deaths")
    assert [r["weight"] for r in mixed["components"]] == [.25, .75]
    assert [r["source_identity"]["input_content_sha256"] for r in mixed["components"]] == ["first", "second"]
    assert [r["outcome_context"]["baseline"]["population"] for r in mixed["components"]] == ["county", "national"]
    mixed["components"][0]["outcome_context"]["baseline"]["population"] = "changed"
    assert first["baseline"]["population"] == "county"


@pytest.mark.parametrize("bad", ["reviewed", 1, None])
def test_truthy_values_do_not_create_reviewed_mixture_eligibility(bad):
    source = row()
    source["applicability"]["eligible_for_public_headline"] = bad
    with pytest.raises(ValueError, match="Boolean headline eligibility"):
        mix_expected([packet(source, "deaths")], [1], "deaths")


@pytest.mark.parametrize("value", ["10", True, None])
def test_scaling_refuses_non_numeric_output(value):
    source = row()
    source["point"] = value
    with pytest.raises(ValueError, match="finite numeric"):
        scale_outcome(source, 2)


def test_normalize_mixture_then_scale_all_comparisons():
    from scripts.build_consumer_fixtures import build
    fixtures = build()["fixtures"]
    mixed = mix_expected([fixtures["national"]["result"], fixtures["county_17043"]["result"]], [.4, .6], "excess_deaths")
    scaled = scale_outcome(mixed, .25)
    assert scaled["point"] == pytest.approx(mixed["point"]*.25)
    assert not scaled["parameter_interval_90"]["available"]
    assert scaled["components"] == mixed["components"]
    assert scaled["persistence_sensitivity"]["source_minus_no_sustained_point"] == pytest.approx(mixed["persistence_sensitivity"]["source_minus_no_sustained_point"]*.25)
    assert scaled["effect_removal_points"] == pytest.approx({k:v*.25 for k,v in mixed["effect_removal_points"].items()})
    for key, endpoint in mixed["supported_endpoint_points"].items():
        for bound in ("at_input_low", "at_input_high"):
            assert scaled["supported_endpoint_points"][key][bound] == pytest.approx(endpoint[bound]*.25)


def test_mixtures_require_a_common_known_denominator_and_mortality_contract():
    a, b = packet(row()), packet(row())
    b["exposure"]["displaced_workers"] = 1
    with pytest.raises(ValueError, match="bases differ"):
        mix_expected([a,b], [.5,.5], "excess_deaths")
    del b["exposure"]
    assert not mix_expected([a,b], [.5,.5], "excess_deaths")["available"]
    b = packet(row())
    b["modeled"]["excess_deaths"]["components"]["follow_up_years"] = 10
    with pytest.raises(ValueError, match="follow-up/method/timing differs"):
        mix_expected([a,b], [.5,.5], "excess_deaths")
    del b["modeled"]["excess_deaths"]["components"]
    assert not mix_expected([a,b], [.5,.5], "excess_deaths")["available"]


def test_blocked_mixture_remains_unavailable_after_display_scaling():
    unavailable = {"available": False, "reason": "blocked"}
    assert scale_outcome(unavailable, 2) == unavailable
