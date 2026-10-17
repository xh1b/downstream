# @ref:code-receiving-community
# Rationale: @link:paper-receiving.
# Software contract: @link:doc-receiving-community-0-4.
# Verification: @link:test-receiving-community; @link:test-receiving-adapter.
# @tag:receiving
"""Source-specific receiving-community share scenarios, separate from displacement."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
import math

from . import __version__
from .params import ParameterSet

VIOLENT = "undocumented_share_change_pp->receiving_violent_crime_log_rate"
TOTAL = "regular_immigrant_share_ratio->receiving_total_crime_rate"
MODELS = {
    "light_miller_2018": {
        "link": VIOLENT, "margin": "undocumented_residents", "outcome": "violent_crime",
        "response_window": "annual_one_year_lag", "exposure_scale": "percentage_point_change",
        "source_citation": "lightmiller2018", "causal_role": "conditional_fixed_effects_association",
    },
    "bianchi_2010": {
        "link": TOTAL, "margin": "valid_residence_permit_residents", "outcome": "total_crime",
        "response_window": "ten_year_endpoint_difference", "exposure_scale": "log_share_ratio",
        "source_citation": "bianchibuonannopinotti2012", "causal_role": "conditional_iv_source_estimate",
    },
}


def _number(value, name, *, positive=False, maximum=None):
    if (isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0
            or value > float("1.7976931348623157e308") or not math.isfinite(value)
            or (positive and value == 0) or (maximum is not None and value > maximum)):
        raise ValueError(f"{name} must be a finite {'positive' if positive else 'nonnegative'} number"
                         + (f" no greater than {maximum}" if maximum is not None else ""))
    return float(value)


def _text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty string")
    return value


def _fields(value, required, optional, name):
    if not isinstance(value, dict) or not required <= value.keys() or value.keys() - required - optional:
        raise ValueError(f"{name} requires {sorted(required)} and only optional {sorted(optional)}")


def _hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def receiving_comparison(params: ParameterSet, payload: dict) -> dict:
    """Apply one source contrast, retaining signed rate and endpoint-count changes.

    A model is selected explicitly; undocumented and regular-resident margins,
    percentage-point changes and log share ratios are never interchanged.
    """
    _fields(payload, {"model", "exposure"}, {"baseline", "transport_assumption"}, "receiving scenario")
    payload = deepcopy(payload)
    model = payload["model"]
    if not isinstance(model, str) or model not in MODELS:
        raise ValueError(f"model must be one of {sorted(MODELS)}")
    spec = MODELS[model]
    exposure = payload["exposure"]
    common = {"margin", "response_window", "unit", "population", "source"}
    if not isinstance(exposure, dict):
        raise ValueError("exposure must supply source-specific population shares, not displaced workers")
    unit = exposure.get("unit")
    if unit == "population_share_fraction":
        _fields(exposure, common | {"reference_share", "post_share"},
                {"post_population_for_counts"}, "share exposure")
        reference = _number(exposure["reference_share"], "reference_share", maximum=1)
        post = _number(exposure["post_share"], "post_share", maximum=1)
        population = (_number(exposure["post_population_for_counts"], "post_population_for_counts", positive=True)
                      if "post_population_for_counts" in exposure else None)
    elif unit == "resident_counts":
        _fields(exposure, common | {"reference_immigrants", "post_immigrants",
                "reference_total_population", "post_total_population"}, set(), "resident-count exposure")
        before = _number(exposure["reference_total_population"], "reference_total_population", positive=True)
        population = _number(exposure["post_total_population"], "post_total_population", positive=True)
        reference = _number(exposure["reference_immigrants"], "reference_immigrants", maximum=before) / before
        post = _number(exposure["post_immigrants"], "post_immigrants", maximum=population) / population
    else:
        raise ValueError("exposure unit must be population_share_fraction or resident_counts; no worker-to-inflow conversion exists")
    for name in ("population", "source"):
        _text(exposure[name], f"exposure.{name}")
    if exposure["margin"] != spec["margin"]:
        raise ValueError(f"{model} requires margin {spec['margin']}; other immigrant/work-access margins are not interchangeable")
    if exposure["response_window"] != spec["response_window"]:
        raise ValueError(f"{model} requires response_window {spec['response_window']}; no annualization or cumulative extrapolation is admitted")
    if "transport_assumption" in payload:
        _text(payload["transport_assumption"], "transport_assumption")
    if model == "light_miller_2018":
        delta = (post - reference) * 100
    else:
        if reference == 0 or post == 0:
            raise ValueError("log-share source requires strictly positive reference and post shares")
        difference = post - reference
        # Near equality, separately rounded logarithms can erase a real
        # signed shift. A bounded relative difference is safe for log1p;
        # distant ratios retain log subtraction to avoid ratio overflow.
        delta = (math.log1p(difference / reference)
                 if abs(difference) <= reference / 2
                 else math.log(post) - math.log(reference))
    parameter = params.by_link(spec["link"])
    if (parameter.citation_keys != [spec["source_citation"]] or parameter.evidence_role != "conditional"
            or (parameter.from_node, parameter.to_node) != tuple(spec["link"].split("->"))):
        raise ValueError("receiving parameter must preserve its source citation and conditional role")

    def response(coefficient):
        log_response = coefficient * delta
        try:
            ratio = math.exp(log_response)
            difference = math.expm1(log_response)
        except OverflowError as exc:
            raise ValueError("receiving response overflows; use a finite supported scenario") from exc
        if not math.isfinite(ratio) or not math.isfinite(difference):
            raise ValueError("receiving response overflows; supplied shift lies outside a finite scenario")
        return ratio, difference

    point_ratio, point_delta = response(parameter.point)
    edges = [response(b) for b in (parameter.low, parameter.high)]
    ratios = {"point": point_ratio, "low": min(x[0] for x in edges), "high": max(x[0] for x in edges)}
    changes = {"point": point_delta, "low": min(x[1] for x in edges), "high": max(x[1] for x in edges)}
    result = {
        "schema": "downstream-receiving-community/1", "engine_version": __version__,
        "parameter_set_version": params.version, "input": payload, "input_content_sha256": _hash(payload),
        "coefficient_content_sha256": _hash(asdict(parameter)), "model": model,
        "eligible_for_public_headline": False, "applicability": {
            "status": "conditional_source_scenario", "target_transport": "unreviewed",
            "reason": "Correct source units do not establish transport to this population or an H-1B replacement scenario."},
        "exposure": {"reference_share": reference, "post_share": post, "applied_shift": delta,
                     "applied_shift_unit": spec["exposure_scale"], "post_population_for_counts": population},
        "outcome": spec["outcome"], "rate_ratio": {**ratios, "unit": "rate_ratio"},
        "percent_rate_change": {k: 100*v for k, v in changes.items()},
        "source": {**asdict(parameter), "causal_role": spec["causal_role"],
                   "response_window": spec["response_window"]},
        "rate_projection": {"available": False, "reason": "No matched annual endpoint baseline rate supplied."},
        "endpoint_incident_difference": {"available": False,
            "reason": "Requires both a matched annual endpoint baseline and explicit post population."},
        "uncertainty_scope": "Transformed coefficient support at fixed supplied shares/baseline; not target transport or future incident-count uncertainty.",
        "retransformation_assumption": "Exponentiating the predicted log-rate change gives an arithmetic rate/count ratio only if the residual retransformation factor is unchanged between scenarios.",
        "limitations": [
            "No displaced-worker count is converted into arrivals or immigrant shares.",
            "This is an annual endpoint RATE contrast; years of follow-up cannot be multiplied into cumulative crimes.",
            "Violent crime overlaps total crime; these source-population contrasts must not be added.",
            "Work-banned asylum, regular-resident and undocumented margins are distinct; none labels all migrants.",
            "Rents, wages, health, trust, voting and other receiving-community channels remain unmodeled, not zero.",
            "Finite-change mapping assumes the source slope applies over the supplied shift; no supported target shift range is identified here.",
            "Arithmetic rate/count projections assume the residual retransformation factor remains unchanged; this factor is not estimated by this adapter.",
        ],
    }
    if "baseline" in payload:
        baseline = payload["baseline"]
        _fields(baseline, {"outcome", "rate", "unit", "window", "population", "source"}, set(), "baseline")
        if baseline["outcome"] != spec["outcome"] or baseline["unit"] != "incidents_per_100000_residents":
            raise ValueError("baseline must match the source outcome in incidents_per_100000_residents")
        if baseline["window"] != "annual_endpoint_rate" or baseline["population"] != exposure["population"]:
            raise ValueError("baseline must match the supplied population and annual endpoint window")
        _text(baseline["source"], "baseline.source")
        rate = _number(baseline["rate"], "baseline.rate")
        result["rate_projection"] = {"available": True, "baseline": baseline,
            "with_exposure": {k: rate*v for k, v in ratios.items()},
            "exposure_minus_reference": {k: rate*v for k, v in changes.items()},
            "unit": "incidents_per_100000_residents_per_annual_endpoint"}
        if population is not None:
            result["endpoint_incident_difference"] = {"available": True,
                **{k: rate*(population/100000)*v for k, v in changes.items()},
                "unit": "incidents_at_annual_endpoint", "comparison_population": population,
                "interpretation": "Both rate scenarios use the same supplied post population; not a cumulative count or an effect of population growth alone."}
    # Refuse overflow in rate/count projections too; never emit nonfinite JSON.
    _hash(result)
    return result
