# @ref:test-receiving-adapter
# Method: @link:doc-receiving-community-0-4.
# Implementation: @link:code-receiving-community; @link:code-employer.
# @tag:receiving @tag:testing
"""Receiving estimates need source-specific shares, denominators and endpoint windows."""
from copy import deepcopy
from dataclasses import replace
from decimal import Decimal, localcontext
import json
import math

import pytest

from downstream.cli import main
from downstream.params import load_all
from downstream.receiving_community import TOTAL, VIOLENT, receiving_comparison


@pytest.fixture(scope="module")
def params():
    return load_all()["params"]


def example(model="light_miller_2018", *, counts=False, baseline=True):
    violent = model == "light_miller_2018"
    exposure = {"margin": "undocumented_residents" if violent else "valid_residence_permit_residents",
        "response_window": "annual_one_year_lag" if violent else "ten_year_endpoint_difference",
        "unit": "resident_counts" if counts else "population_share_fraction",
        "population": "synthetic receiving population", "source": "supplied share scenario"}
    if counts:
        exposure.update(reference_immigrants=200, post_immigrants=220,
                        reference_total_population=10000, post_total_population=10000)
    else:
        exposure.update(reference_share=.02, post_share=.022, post_population_for_counts=10000)
    payload = {"model": model, "exposure": exposure}
    if baseline:
        payload["baseline"] = {"outcome": "violent_crime" if violent else "total_crime",
            "rate": 300, "unit": "incidents_per_100000_residents", "window": "annual_endpoint_rate",
            "population": exposure["population"], "source": "synthetic fixed annual baseline"}
    return payload


def test_light_source_is_semi_log_per_percentage_point_not_stock_elasticity(params):
    result = receiving_comparison(params, example())
    delta_pp = (.022-.02)*100
    assert result["exposure"]["applied_shift"] == pytest.approx(.2)
    assert result["rate_ratio"]["point"] == pytest.approx(math.exp(-.12*delta_pp))
    assert result["rate_ratio"]["point"] != pytest.approx(1.1**-.12)
    assert result["rate_ratio"]["low"] <= result["rate_ratio"]["point"] <= result["rate_ratio"]["high"] < 1
    assert result["percent_rate_change"]["point"] == pytest.approx(100*math.expm1(-.12*delta_pp))
    assert result["rate_projection"]["exposure_minus_reference"]["point"] == pytest.approx(300*math.expm1(-.12*delta_pp))
    assert result["endpoint_incident_difference"]["point"] == pytest.approx(30*math.expm1(-.12*delta_pp))
    assert not result["eligible_for_public_headline"]
    assert result["source"]["causal_role"] == "conditional_fixed_effects_association"


def test_bianchi_log_share_ratio_retains_null_uncertainty_and_source_version(params):
    result = receiving_comparison(params, example("bianchi_2010"))
    assert result["rate_ratio"]["point"] == pytest.approx(1.1**.105)
    assert result["rate_ratio"]["low"] < 1 < result["rate_ratio"]["high"]
    assert result["endpoint_incident_difference"]["low"] < 0 < result["endpoint_incident_difference"]["high"]
    assert result["source"]["tier"] == "canonical"
    assert result["source"]["response_window"] == "ten_year_endpoint_difference"
    assert "annual_endpoint" in result["endpoint_incident_difference"]["unit"]


@pytest.mark.parametrize("model", ["light_miller_2018", "bianchi_2010"])
def test_counts_match_shares_and_reference_null_is_exact(params, model):
    share = example(model)
    counts = example(model, counts=True)
    assert receiving_comparison(params, share)["rate_ratio"] == receiving_comparison(params, counts)["rate_ratio"]
    counts["exposure"].update(post_immigrants=400, post_total_population=20000)
    null = receiving_comparison(params, counts)
    assert null["rate_ratio"] == {"point": 1, "low": 1, "high": 1, "unit": "rate_ratio"}
    assert all(value == 0 for value in null["percent_rate_change"].values())
    assert null["endpoint_incident_difference"]["point"] == 0


def test_changing_total_population_is_not_silently_ignored(params):
    payload = example("bianchi_2010", counts=True)
    payload["exposure"].update(post_immigrants=200, post_total_population=20000)
    result = receiving_comparison(params, payload)
    assert result["exposure"]["post_share"] == .01
    assert result["rate_ratio"]["point"] == pytest.approx(.5**.105)
    assert result["endpoint_incident_difference"]["comparison_population"] == 20000
    assert result["endpoint_incident_difference"]["point"] == pytest.approx(60*(.5**.105-1))


def test_signed_outflow_reverses_interval_order_and_does_not_clip(params):
    payload = example()
    payload["exposure"]["post_share"] = .01
    result = receiving_comparison(params, payload)
    assert 1 < result["rate_ratio"]["low"] <= result["rate_ratio"]["point"] <= result["rate_ratio"]["high"]
    assert result["endpoint_incident_difference"]["point"] > 0


def test_small_effect_survives_when_ratio_rounds_to_one(params):
    payload = example()
    payload["exposure"]["post_share"] = math.nextafter(.02, 1)
    result = receiving_comparison(params, payload)
    assert result["rate_ratio"]["point"] == 1
    assert result["percent_rate_change"]["point"] < 0
    assert result["rate_projection"]["exposure_minus_reference"]["point"] < 0


def test_missing_baseline_or_post_population_is_unavailable_not_zero(params):
    payload = example(baseline=False)
    result = receiving_comparison(params, payload)
    assert not result["rate_projection"]["available"]
    assert not result["endpoint_incident_difference"]["available"]
    assert "point" not in result["endpoint_incident_difference"]
    payload = example()
    del payload["exposure"]["post_population_for_counts"]
    result = receiving_comparison(params, payload)
    assert result["rate_projection"]["available"]
    assert not result["endpoint_incident_difference"]["available"]


@pytest.mark.parametrize("change", [
    {"reference_share": True}, {"post_share": math.nan}, {"post_share": math.inf},
    {"post_share": -1}, {"post_share": 2.2}, {"post_share": 10**400},
    {"unit": "workers"}, {"margin": "all_immigrants"}, {"margin": "asylum_work_banned"},
    {"response_window": "five_year_cumulative"}, {"source": ""},
    {"post_population_for_counts": 0}, {"population": ""}, {"arrivals": 200},
])
def test_invalid_or_unsupported_exposure_refused(params, change):
    payload = example()
    payload["exposure"].update(change)
    with pytest.raises(ValueError):
        receiving_comparison(params, payload)


@pytest.mark.parametrize("change", [
    {"outcome": "total_crime"}, {"unit": "prob_per_person"}, {"rate": True},
    {"rate": -1}, {"rate": math.nan}, {"population": "another population"},
    {"window": "ten_year_cumulative"}, {"source": ""}, {"rate": 1.7e308},
])
def test_baseline_contract_and_nonfinite_projection_refusal(params, change):
    payload = example()
    payload["baseline"].update(change)
    if change == {"rate": 1.7e308}:
        payload["exposure"]["post_share"] = 0  # positive response makes rate overflow
    with pytest.raises(ValueError):
        receiving_comparison(params, payload)


def test_zero_log_share_and_inconsistent_counts_refused(params):
    payload = example("bianchi_2010")
    payload["exposure"]["post_share"] = 0
    with pytest.raises(ValueError, match="strictly positive"):
        receiving_comparison(params, payload)
    payload = example(counts=True)
    payload["exposure"]["post_immigrants"] = 10001
    with pytest.raises(ValueError):
        receiving_comparison(params, payload)
    payload["exposure"]["post_immigrants"] = 200
    payload["exposure"]["reference_total_population"] = 0
    with pytest.raises(ValueError):
        receiving_comparison(params, payload)


def test_worker_exposure_and_other_unsupported_inputs_do_not_create_arrivals(params):
    for payload in [None, {}, {"model": "unknown", "exposure": {}},
                    {"model": "light_miller_2018", "exposure": []},
                    {**example(), "displaced_workers": 100},
                    {**example(), "transport_assumption": ""}]:
        with pytest.raises(ValueError):
            receiving_comparison(params, payload)


def test_coefficient_null_and_source_metadata_contract(params):
    null = replace(params, parameters=tuple(replace(p, point=0, low=0, high=0)
                   if p.link == VIOLENT else p for p in params.parameters))
    assert receiving_comparison(null, example())["rate_ratio"]["point"] == 1
    for change in ({"citation": "wrong"}, {"evidence_role": "admitted"}, {"from_node": "wrong"}):
        bad = replace(params, parameters=tuple(replace(p, **change) if p.link == TOTAL else p
                                               for p in params.parameters))
        with pytest.raises(ValueError, match="source citation"):
            receiving_comparison(bad, example("bianchi_2010"))
    overflow = replace(params, parameters=tuple(replace(p, point=10000, low=10000, high=10000)
                        if p.link == TOTAL else p for p in params.parameters))
    with pytest.raises(ValueError, match="overflows"):
        receiving_comparison(overflow, example("bianchi_2010"))


def test_provenance_identity_and_caller_payload_preservation(params):
    payload = example()
    original = deepcopy(payload)
    first = receiving_comparison(params, payload)
    assert payload == original
    payload["exposure"]["source"] = "revised supplied scenario"
    second = receiving_comparison(params, payload)
    assert first["input"]["exposure"]["source"] == original["exposure"]["source"]
    assert first["input_content_sha256"] != second["input_content_sha256"]
    assert first["rate_ratio"] == second["rate_ratio"]
    assert first["coefficient_content_sha256"] == second["coefficient_content_sha256"]


def test_cli_and_old_link_migration(tmp_path, capsys):
    path = tmp_path / "receiving.json"
    path.write_text(json.dumps(example("bianchi_2010")))
    assert main(["receiving-community", "--input", str(path)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["model"] == "bianchi_2010"
    assert result["parameter_set_version"] == "v1.54"
    assert not result["eligible_for_public_headline"]
    with pytest.raises(SystemExit) as exc:
        main(["simulate", "--links", "immigrant_influx->receiving_violent_crime_rate",
              "--kinds", "gap_log_elastic", "--draws", "2"])
    assert exc.value.code == 2
    assert "retired" in capsys.readouterr().err


@pytest.mark.parametrize("direction", [0.0, 1.0])
def test_adjacent_bianchi_share_shift_survives_in_native_and_cli(params, direction, tmp_path, capsys):
    payload = example("bianchi_2010")
    reference = payload["exposure"]["reference_share"]
    post = math.nextafter(reference, direction)
    payload["exposure"]["post_share"] = post
    # Independent high-precision arithmetic on the actual binary inputs;
    # an absolute approximation tolerance would wrongly admit a zero here.
    with localcontext() as context:
        context.prec = 80
        expected_log = (Decimal.from_float(post) / Decimal.from_float(reference)).ln()
        expected_change = (Decimal.from_float(.105) * expected_log).exp() - 1
    expected_log, expected_change = float(expected_log), float(expected_change)
    native = receiving_comparison(params, payload)
    path = tmp_path / "adjacent-shares.json"
    path.write_text(json.dumps(payload))
    assert main(["receiving-community", "--input", str(path)]) == 0
    cli = json.loads(capsys.readouterr().out)
    for result in (native, cli):
        assert result["exposure"]["applied_shift"] != 0
        assert result["exposure"]["applied_shift"] == pytest.approx(expected_log, rel=1e-14, abs=0)
        assert result["percent_rate_change"]["point"] == pytest.approx(100*expected_change, rel=1e-14, abs=0)
        assert result["rate_projection"]["exposure_minus_reference"]["point"] == pytest.approx(300*expected_change, rel=1e-14, abs=0)
        assert result["endpoint_incident_difference"]["point"] == pytest.approx(30*expected_change, rel=1e-14, abs=0)
        assert math.copysign(1, result["endpoint_incident_difference"]["point"]) == math.copysign(1, post-reference)
        assert result["rate_ratio"]["point"] == 1  # the ratio can round; signed changes must survive


@pytest.mark.parametrize("reference,post", [(math.nextafter(0.0, 1.0), 1.0),
                                            (1.0, math.nextafter(0.0, 1.0))])
def test_extreme_bianchi_share_ratios_use_finite_log_difference_fallback(params, reference, post):
    payload = example("bianchi_2010", baseline=False)
    payload["exposure"].update(reference_share=reference, post_share=post)
    result = receiving_comparison(params, payload)
    assert result["exposure"]["applied_shift"] == math.log(post)-math.log(reference)
    assert all(math.isfinite(result["rate_ratio"][key]) for key in ("point", "low", "high"))
