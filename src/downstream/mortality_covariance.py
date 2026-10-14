"""Unknown-covariance diagnostics for additive log-odds coefficients.

This module never admits a mortality response or converts coefficients to deaths.
It uses only marginal standard errors; no covariance is inferred.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from collections.abc import Mapping, Sequence


def _finite(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite number")
    try:
        value = float(value)
    except OverflowError as exc:
        raise ValueError(f"{label} must be a finite number") from exc
    if not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    return value


def linear_se_bounds(standard_errors: Sequence[float],
                     weights: Sequence[float] | None = None) -> dict:
    """Sharp SE extrema over all PSD covariance matrices with this diagonal.

    For lengths l_i = |weight_i| * SE_i, the upper bound is sum(l_i),
    and the lower bound is max(0, max(l_i) - sum(other l_i)). A Gram
    representation proves attainability: align all vectors for the maximum;
    oppose the longest or form a closed polygon for the minimum. Each bound
    concerns one linear contrast, not simultaneous extrema of many contrasts.
    """
    errors = list(standard_errors)
    if not errors:
        raise ValueError("at least one marginal standard error is required")
    coefficients = [1.0] * len(errors) if weights is None else list(weights)
    if len(coefficients) != len(errors):
        raise ValueError("weights and standard errors must have the same length")
    lengths = []
    for index, (error, weight) in enumerate(zip(errors, coefficients, strict=True)):
        error = _finite(error, f"standard_errors[{index}]")
        if error < 0:
            raise ValueError("standard errors must be nonnegative")
        weight = _finite(weight, f"weights[{index}]")
        lengths.append(_finite(abs(weight) * error, "weighted standard error"))
    longest = max(lengths)
    longest_index = lengths.index(longest)
    try:
        others = math.fsum(length for index, length in enumerate(lengths)
                           if index != longest_index)
        upper = math.fsum(lengths)
    except OverflowError as exc:
        raise ValueError("standard-error bounds exceed finite numeric range") from exc
    return {"lower": max(0.0, longest - others), "upper": upper,
            "scope": "One linear contrast; all PSD covariance matrices with the supplied diagonal.",
            "covariance_assumed": False}


@dataclass(frozen=True)
class AdditiveCoefficient:
    name: str
    estimate: float
    standard_error: float | None

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("coefficient name must be a nonempty string")
        _finite(self.estimate, "estimate")
        if self.standard_error is not None and _finite(self.standard_error, "standard_error") < 0:
            raise ValueError("standard_error must be nonnegative")


def additive_phase_diagnostic(components: Sequence[AdditiveCoefficient],
                              weights: Mapping[str, float], *, critical_value=1.96) -> dict:
    """Report a phase point plus covariance-free marginal precision bounds.

    Missing active SEs withhold the bounds and envelope. An outer normal
    approximation envelope is a diagnostic under the stated approximation,
    not a reported source interval, a simultaneous band or admission criterion.
    """
    components = list(components)
    if not components or any(not isinstance(c, AdditiveCoefficient) for c in components):
        raise ValueError("components must contain AdditiveCoefficient records")
    by_name = {c.name: c for c in components}
    if len(by_name) != len(components):
        raise ValueError("component names must be unique")
    if not isinstance(weights, Mapping) or not weights or set(weights) - by_name.keys():
        raise ValueError("weights must name known components")
    z = _finite(critical_value, "critical_value")
    if z <= 0:
        raise ValueError("critical_value must be positive")
    active = [(by_name[name], _finite(weight, f"weight:{name}"))
              for name, weight in weights.items()]
    active = [(component, weight) for component, weight in active if weight != 0]
    if not active:
        raise ValueError("at least one nonzero weight is required")
    try:
        point = _finite(math.fsum(component.estimate * weight for component, weight in active),
                        "phase total")
    except OverflowError as exc:
        raise ValueError("phase total exceeds finite numeric range") from exc
    result = {"point": point, "unit": "additive_log_odds", "eligible_for_model_admission": False,
              "components": [{"name": c.name, "estimate": c.estimate,
                              "standard_error": c.standard_error, "weight": weight}
                             for c, weight in active]}
    missing = [c.name for c, _ in active if c.standard_error is None]
    if missing:
        result.update(uncertainty_available=False, missing_standard_errors=missing,
                      reason="Active component marginal standard errors are missing; no bounds inferred.")
        return result
    bounds = linear_se_bounds([c.standard_error for c, _ in active],
                              [weight for _, weight in active])
    width = _finite(z * bounds["upper"], "normal approximation envelope width")
    result.update(uncertainty_available=True, standard_error_bounds=bounds,
                  normal_approximation_outer_envelope={
                      "low": _finite(point - width, "envelope lower endpoint"),
                      "high": _finite(point + width, "envelope upper endpoint"),
                      "critical_value": z,
                      "interpretation": "Contains point +/- critical_value * SE for every compatible covariance; requires a normal approximation. Not a simultaneous band or source-reported interval."})
    return result
