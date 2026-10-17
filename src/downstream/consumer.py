# @ref:code-consumer
# Rationale: @link:paper-consumer-transforms.
# Software contract: @link:doc-consumer-fixtures-0-4.
# Verification: @link:test-consumer-api; @link:test-consumer-fixtures.
# @tag:consumer
"""Checked display transforms for a fixed exposure basis and place mixtures.

These helpers retain input provenance; they do not estimate exposure or transport.
Joint mixture quantiles require a separate dependence model and are unavailable.
"""
from __future__ import annotations

import copy
import math


def _nonnegative_number(value):
    return (not isinstance(value, bool) and isinstance(value, (int, float))
            and 0 <= value <= float("1.7976931348623157e308") and math.isfinite(value))


def _finite_output(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("consumer transform exceeds finite numeric range")
    if isinstance(value, dict):
        for item in value.values():
            _finite_output(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _finite_output(item)
    return value


def _scale_fields(mapping, keys, factor):
    for key in keys:
        value = mapping[key]
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or abs(value) > float("1.7976931348623157e308") or not math.isfinite(value)):
            raise ValueError("outcome values must be finite numeric values")
        mapping[key] = value * factor


def _scale_experiment(experiment, factor):
    _scale_fields(experiment, ("point", "change_from_reference", "reference_minus_variant"), factor)


def scale_outcome(row, factor):
    """Expected numeric display contract; input metadata keeps its source basis."""
    if not _nonnegative_number(factor):
        raise ValueError("display factor must be finite and nonnegative")
    out = copy.deepcopy(row)
    if out.get("available") is False:
        return out
    if not {"point", "low", "high"} <= out.keys():
        raise ValueError("outcome requires point, low and high")
    _scale_fields(out, [key for key in ("point", "low", "high", "undiscounted_point",
                                       "sensitivity_reference_point") if key in out], factor)
    interval = out.get("parameter_interval_90")
    if interval and interval.get("available") is not False:
        _scale_fields(interval, ("p05", "p50", "p95", "mean"), factor)
    removals = out.get("effect_removal_points")
    if removals and removals.get("available") is not False:
        _scale_fields(removals, list(removals), factor)
    for endpoint in out.get("supported_endpoint_points", {}).values():
        if isinstance(endpoint, dict) and endpoint.get("available"):
            _scale_fields(endpoint, ("at_input_low", "at_input_high"), factor)
    sensitivity = out.get("sensitivity")
    if sensitivity:
        _scale_fields(sensitivity, ("reference_point",), factor)
        for driver in sensitivity["effect_drivers"]:
            _scale_experiment(driver["effect_removed"], factor)
            bounds = driver["supported_range"]
            for key in ("at_input_low", "at_input_high"):
                _scale_experiment(bounds[key], factor)
            _scale_fields(bounds, ("outcome_low", "outcome_high", "endpoint_span"), factor)
        variance = sensitivity["variance_attribution"]
        if variance.get("available"):
            if factor == 0:
                sensitivity["variance_attribution"] = {
                    "available": False, "reason": "Zero display exposure has zero variance; indices are undefined.",
                    "base": variance.get("base"), "seed": variance.get("seed")}
            else:
                _scale_fields(variance, ("output_variance",), factor)
                _scale_fields(variance, ("output_variance",), factor)
    persistence = out.get("persistence_sensitivity")
    if persistence and persistence.get("available"):
        for key, value in persistence["variants"].items():
            persistence["variants"][key] = scale_outcome(value, factor)
        _scale_fields(persistence, ("source_minus_no_sustained_point",), factor)
        if persistence.get("structural_point_range"):
            _scale_fields(persistence["structural_point_range"], ("low", "high"), factor)
        interval = persistence.get("source_minus_no_sustained_parameter_interval_90")
        if interval and interval.get("available") is not False:
            _scale_fields(interval, ("p05", "p50", "p95", "mean"), factor)
    return _finite_output(out)


def mix_expected(results, weights, outcome):
    """Point/declared-support expectations only; no invented joint quantiles."""
    if (not isinstance(weights, (list, tuple)) or not isinstance(results, (list, tuple))
            or not weights or len(weights) != len(results)
            or any(not _nonnegative_number(w) for w in weights)
            or not math.isclose(sum(weights), 1, abs_tol=1e-9, rel_tol=0)):
        raise ValueError("mixture weights must be nonnegative and sum to one")
    active = [(r, w) for r, w in zip(results, weights) if w > 0]
    if any(outcome not in r["modeled"] for r, _ in active):
        return {"available": False, "reason": "A positive-weight component blocks this outcome."}
    rows = [(r["modeled"][outcome], w) for r, w in active]
    for row, _ in rows:
        if (not isinstance(row.get("unit"), str) or not row["unit"].strip()
                or not isinstance(row.get("applicability"), dict)
                or type(row["applicability"].get("eligible_for_public_headline")) is not bool):
            raise ValueError("each outcome requires units and Boolean headline eligibility")
        for key in ("point", "low", "high"):
            value = row.get(key)
            if (isinstance(value, bool) or not isinstance(value, (int, float))
                    or abs(value) > float("1.7976931348623157e308") or not math.isfinite(value)):
                raise ValueError("outcome values must be finite numeric points and support endpoints")
    if len({r["unit"] for r, _ in rows}) != 1:
        raise ValueError("cannot mix unlike outcome units")
    denominators = [result.get("exposure", {}).get("displaced_workers") for result, _ in active]
    if any(value is None for value in denominators):
        return {"available": False, "reason": "A common displaced-worker basis is undeclared."}
    if any(not _nonnegative_number(value) for value in denominators):
        raise ValueError("component displaced-worker basis must be finite and nonnegative")
    if any(value != denominators[0] for value in denominators):
        raise ValueError("component displaced-worker bases differ; normalize before mixing")
    if outcome == "excess_deaths":
        contracts = [row.get("components", {}) for row, _ in rows]
        fields = ("follow_up_years", "method", "timing")
        if any(not isinstance(contract, dict) or not set(fields) <= contract.keys()
               or contract["follow_up_years"] is None
               or any(not isinstance(contract[key], str) or not contract[key].strip()
                      for key in ("method", "timing")) for contract in contracts):
            return {"available": False, "reason": "Common mortality follow-up/method/timing is undeclared."}
        if any(not _nonnegative_number(contract["follow_up_years"]) for contract in contracts):
            raise ValueError("mortality follow-up must be finite and nonnegative")
        if any(any(contract[key] != contracts[0][key] for key in fields) for contract in contracts):
            raise ValueError("component mortality follow-up/method/timing differs")
    out = {"available": True, "unit": rows[0][0]["unit"],
           "normalization_workers": denominators[0],
           **{k: sum(r[k]*w for r, w in rows) for k in ("point", "low", "high")},
           "eligible_for_public_headline": all(r["applicability"]["eligible_for_public_headline"]
                                              for r, _ in rows),
           "baseline": {"kind": "component-specific; no representative first-component baseline"},
           "parameter_interval_90": {"available": False, "reason": "Requires joint component draws."},
           "variance_attribution": {"available": False, "reason": "Requires a joint mixture calculation."},
           "support_scope": "Weighted Cartesian component support envelope, not a joint confidence interval."}
    out["components"] = [{
        "source_index": index, "weight": weight,
        "source_identity": {key: copy.deepcopy(result.get(key)) for key in (
            "engine_version", "parameter_set_version", "input_content_sha256", "exposure_input_sha256")},
        "source_context": {key: copy.deepcopy(result.get(key)) for key in (
            "subject", "place", "exposure", "exposure_provenance", "target_population",
            "child_applicability", "projection_eligibility", "assumptions", "uncertainty")},
        "outcome_context": {key: copy.deepcopy(result["modeled"][outcome].get(key))
                            for key in ("applicability", "baseline", "steps")},
    } for index, (result, weight) in enumerate(zip(results, weights)) if weight > 0]
    reports = [(r.get("persistence_sensitivity", {}), w) for r, w in rows]
    if all(p.get("available") for p, _ in reports):
        out["persistence_sensitivity"] = {
            "available": True,
            "variants": {name: {k: sum(p["variants"][name][k]*w for p, w in reports)
                                for k in ("point", "low", "high")}
                         for name in ("source_profile", "no_sustained_excess")},
            "source_minus_no_sustained_point": sum(p["source_minus_no_sustained_point"]*w
                                                   for p, w in reports)}
    else:
        out["persistence_sensitivity"] = {"available": False, "reason": "Not available in every component."}
    if not all(isinstance(r.get("sensitivity"), dict)
               and isinstance(r["sensitivity"].get("effect_drivers"), list)
               for r, _ in rows):
        out["effect_removal_points"] = {"available": False, "reason": "Per-component sensitivity reports are required."}
        out["supported_endpoint_points"] = {"available": False, "reason": "Per-component sensitivity reports are required."}
        return _finite_output(out)
    driver_maps = [{d["input_id"]: d for d in r["sensitivity"]["effect_drivers"]} for r, _ in rows]
    ids = sorted(set().union(*(set(d) for d in driver_maps)))
    out["effect_removal_points"] = {
        key: sum((d[key]["effect_removed"]["point"] if key in d
                  else r["sensitivity"]["reference_point"])*w
                 for (r, w), d in zip(rows, driver_maps)) for key in ids}
    out["sensitivity_reference_point"] = sum(r["sensitivity"]["reference_point"]*w for r, w in rows)
    out["supported_endpoint_points"] = {}
    for key in ids:
        declared = [d[key]["supported_range"] for d in driver_maps if key in d]
        if len({(d["input_low"], d["input_high"]) for d in declared}) != 1:
            out["supported_endpoint_points"][key] = {
                "available": False, "reason": "Component input endpoints differ; no shared input experiment."}
            continue
        points = {bound: sum((d[key]["supported_range"][f"at_input_{bound}"]["point"] if key in d
                              else r["sensitivity"]["reference_point"])*w
                             for (r, w), d in zip(rows, driver_maps)) for bound in ("low", "high")}
        out["supported_endpoint_points"][key] = {"available": True,
                                                "at_input_low": points["low"], "at_input_high": points["high"]}
    return _finite_output(out)


