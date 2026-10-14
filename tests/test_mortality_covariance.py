"""Unknown covariance bounds must follow PSD geometry, not independence guesses."""
import importlib.util
import json
import math
from pathlib import Path
import random

import pytest

from downstream.mortality_covariance import (
    AdditiveCoefficient, additive_phase_diagnostic, linear_se_bounds,
)


def test_two_component_bounds_are_attained_by_psd_rank_one_covariances():
    a, b = .054, .199
    bounds = linear_se_bounds([a, b])
    assert bounds["lower"] == pytest.approx(.145)
    assert bounds["upper"] == pytest.approx(.253)
    for rho, endpoint in [(-1, "lower"), (1, "upper")]:
        # [[a^2, rho*a*b], [rho*a*b,b^2]] has nonnegative diagonal,
        # zero determinant and the supplied diagonal: a valid PSD witness.
        variance = a * a + b * b + 2 * rho * a * b
        assert math.sqrt(variance) == pytest.approx(bounds[endpoint])
    assert not bounds["covariance_assumed"]


def test_polygon_lower_extremum_can_be_zero_without_zero_marginal_errors():
    bounds = linear_se_bounds([1, 1, 1])
    assert bounds["lower"] == 0
    assert bounds["upper"] == 3
    # Three unit vectors 120 degrees apart give Gram correlations -1/2,
    # eigenvalues (0,1.5,1.5), and zero variance for their sum.
    assert 3 + 2 * 3 * (-.5) == bounds["lower"] ** 2


def test_general_signed_weights_zero_errors_and_permutation():
    bounds = linear_se_bounds([2, 3, 0], [-2, .5, 99])
    assert bounds["lower"] == 2.5
    assert bounds["upper"] == 5.5
    assert linear_se_bounds([0, 3, 2], [99, .5, -2]) == bounds
    assert linear_se_bounds([.054]) == linear_se_bounds([.054, 0])
    assert linear_se_bounds([0, 0])["upper"] == 0


def test_bounds_contain_random_psd_gram_covariances():
    rng = random.Random(1901)
    for _ in range(100):
        errors = [rng.uniform(0, 1) for _ in range(6)]
        weights = [rng.uniform(-2, 2) for _ in errors]
        vectors = []
        for error in errors:
            vector = [rng.gauss(0, 1) for _ in range(3)]
            norm = math.hypot(*vector)
            vectors.append([x * error / norm for x in vector])
        # A Gram covariance built from these vectors is PSD by construction.
        actual = math.hypot(*(math.fsum(weight * vector[axis]
                             for weight, vector in zip(weights, vectors, strict=True))
                             for axis in range(3)))
        bounds = linear_se_bounds(errors, weights)
        assert bounds["lower"] - 1e-12 <= actual <= bounds["upper"] + 1e-12


@pytest.mark.parametrize("errors,weights", [([], None), ([1], []), ([-1], None),
    ([True], None), ([None], None), ([math.nan], None), ([math.inf], None),
    ([1], [False]), ([1], [math.nan]), ([1e308, 1e308], None), ([1e308], [2])])
def test_invalid_bound_inputs_are_rejected(errors, weights):
    with pytest.raises(ValueError):
        linear_se_bounds(errors, weights)


def test_additive_total_keeps_sign_and_uses_sum_not_se_of_added_component():
    values = [AdditiveCoefficient("main", .131, .054),
              AdditiveCoefficient("added", -.066, .081)]
    report = additive_phase_diagnostic(values, {"main": 1, "added": 1})
    assert report["point"] == pytest.approx(.065)
    assert report["standard_error_bounds"]["lower"] == pytest.approx(.027)
    assert report["standard_error_bounds"]["upper"] == pytest.approx(.135)
    envelope = report["normal_approximation_outer_envelope"]
    assert envelope["low"] == pytest.approx(.065 - 1.96 * .135)
    assert envelope["high"] == pytest.approx(.065 + 1.96 * .135)
    assert report["unit"] == "additive_log_odds"
    assert report["eligible_for_model_admission"] is False
    json.dumps(report, allow_nan=False)


def test_missing_active_se_withholds_uncertainty_and_ignores_inactive_gap():
    values = [AdditiveCoefficient("main", .131, .054), AdditiveCoefficient("added", .716, None)]
    report = additive_phase_diagnostic(values, {"main": 1, "added": 1})
    assert report["point"] == pytest.approx(.847)
    assert not report["uncertainty_available"]
    assert report["missing_standard_errors"] == ["added"]
    assert "standard_error_bounds" not in report
    assert "normal_approximation_outer_envelope" not in report
    assert additive_phase_diagnostic(values, {"main": 1, "added": 0})["uncertainty_available"]


@pytest.mark.parametrize("name,point,se", [("", 0, 0), (1, 0, 0), ("x", True, 0),
    ("x", math.nan, 0), ("x", 0, -1), ("x", 0, math.inf), ("x", 0, False)])
def test_invalid_components(name, point, se):
    with pytest.raises(ValueError):
        AdditiveCoefficient(name, point, se)


@pytest.mark.parametrize("weights,z", [({}, 1.96), ({"missing": 1}, 1.96),
    ({"main": 0}, 1.96), ({"main": True}, 1.96), ({"main": 1}, 0),
    ({"main": 1}, math.inf), ({"main": 1}, False)])
def test_invalid_phase_contracts(weights, z):
    with pytest.raises(ValueError):
        additive_phase_diagnostic([AdditiveCoefficient("main", .131, .054)],
                                  weights, critical_value=z)
    with pytest.raises(ValueError, match="unique"):
        additive_phase_diagnostic([AdditiveCoefficient("x", 0, 0)] * 2, {"x": 1})


def test_nonfinite_computation_and_empty_component_contracts():
    with pytest.raises(ValueError, match="finite"):
        AdditiveCoefficient("x", 10 ** 1000, 1)
    for components in ([], [object()]):
        with pytest.raises(ValueError, match="components"):
            additive_phase_diagnostic(components, {"x": 1})
    with pytest.raises(ValueError, match="range"):
        additive_phase_diagnostic([AdditiveCoefficient("x", 1e308, 1),
                                   AdditiveCoefficient("y", 1e308, 1)], {"x": 1, "y": 1})
    with pytest.raises(ValueError, match="finite"):
        additive_phase_diagnostic([AdditiveCoefficient("x", 1, 1e308)], {"x": 1})


def test_source_diagnostic_is_reproducible_and_separate_from_admitted_parameters():
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location("covariance_report",
                                                root / "scripts/analyze_mortality_covariance.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.report()
    rows = list(result["phases"].values())
    assert [row["point"] for row in rows] == pytest.approx([.847, .690, .329, .188, .065, .131])
    assert [row["standard_error_bounds"]["lower"] for row in rows] == pytest.approx(
        [.145, .093, .093, .040, .027, .054])
    assert [row["standard_error_bounds"]["upper"] for row in rows] == pytest.approx(
        [.253, .201, .201, .148, .135, .054])
    assert "manufacturing" in result["source"]["reference_category"].lower()
    assert "manuscript" in result["source"]["version"]
    assert result == module.report()
    assert all(not row["eligible_for_model_admission"] for row in rows)
    json.dumps(result, allow_nan=False)
