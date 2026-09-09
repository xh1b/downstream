"""Manual-review report for synthesized evidence versus a shipped parameter.

The report is intentionally read-only.  A pooled estimate can be statistically
sound yet causally incompatible with a graph edge, so no CLI path writes
``parameters.csv`` from this module.
"""

from __future__ import annotations

import math

from .params import ParameterSet


_EXPECTED_LOG_SCALE = {
    "odds_ratio": "log_odds_ratio",
    "rate_ratio": "log_rate_ratio",
    "level_ratio": "log_level_ratio",
}


def compare_synthesis_to_parameter(params: ParameterSet, report: dict, nodes: dict) -> dict:
    """Compare a same-scale synthesis with its declared parameter link.

    Only ratio nodes have a mechanical log-scale comparison. Other effects are
    returned as manual-review-only because a multiplier, gap, standardized
    effect, and risk difference cannot safely be equated by convenience.
    """
    link = report["link"]
    parameter = params.by_link(link)
    unit = nodes[parameter.to_node].unit
    expected_scale = _EXPECTED_LOG_SCALE.get(unit)
    output = {
        "link": link,
        "parameter": {"point": parameter.point, "low": parameter.low, "high": parameter.high,
                      "to_unit": unit, "citation": parameter.citation},
        "synthesis": {"scale": report["scale"], "studies": report["studies"],
                      "random_effects": report["random_effects"]},
        "automatic_admission": False,
    }
    if expected_scale is None:
        output.update({
            "compatible_scale": False,
            "review_status": "manual",
            "reason": "no lossless generic transform exists for this target unit",
        })
        return output
    if report["scale"] != expected_scale:
        output.update({
            "compatible_scale": False,
            "review_status": "manual",
            "reason": f"expected {expected_scale!r} for {unit}, got {report['scale']!r}",
        })
        return output
    point = math.log(parameter.point)
    # The existing row may itself be one of the synthesized studies, so this
    # standardized difference is descriptive only, never a significance test.
    se = (math.log(parameter.high) - math.log(parameter.low)) / 3.92
    pooled = report["random_effects"]
    delta = pooled["mean"] - point
    descriptive_z = delta / math.sqrt(se**2 + pooled["standard_error"]**2)
    output.update({
        "compatible_scale": True,
        "review_status": "manual: estimand, timing, target population, and study-overlap review required",
        "parameter_log_scale": {"point": point, "approx_standard_error": se},
        "pooled_minus_parameter_log_scale": delta,
        "descriptive_standardized_difference": descriptive_z,
        "warning": "not a hypothesis test: the shipped row can overlap the pooled study set",
    })
    return output
