"""Study-level random-effects synthesis, separate from parameter admission.

This is deliberately a small, auditable evidence layer: it will combine only
like-for-like estimates with supplied standard errors.  It never turns a
summary band in ``parameters.csv`` into pseudo-study data, and it does not
claim target-population transport without target covariates.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path


# Two-sided 95% Student-t critical values, indexed by degrees of freedom.
# A small explicit table avoids presenting a normal 1.96 interval as valid
# for a two-study synthesis.  df > 30 is already close to the normal limit.
_T975 = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447,
    7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179,
    13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101,
    19: 2.093, 20: 2.086, 21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064,
    25: 2.060, 26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042,
}


def _t975(df: int) -> float:
    return _T975.get(df, 1.96)


@dataclass(frozen=True)
class StudyEstimate:
    link: str
    study_id: str
    point: float
    standard_error: float
    scale: str
    population_scope: str
    design: str
    time_horizon: str
    citation: str = ""
    source_url: str = ""
    treatment: str = ""
    comparison: str = ""
    outcome_definition: str = ""
    overlap_group: str = ""


REQUIRED_COLUMNS = (
    "link", "study_id", "point", "standard_error", "scale",
    "population_scope", "design", "time_horizon", "citation",
)


def load_study_estimates(path: str | Path) -> tuple[StudyEstimate, ...]:
    """Read a source-extracted study-level estimate CSV.

    ``scale`` must encode the comparable estimand and transformation, e.g.
    ``log_odds_ratio`` or ``risk_difference_per_person_year``.  Rows with
    differing scales intentionally cannot be pooled.
    """
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(line for line in handle if not line.lstrip().startswith("#"))
        if reader.fieldnames is None or any(c not in reader.fieldnames for c in REQUIRED_COLUMNS):
            raise ValueError(f"study estimate CSV requires columns {REQUIRED_COLUMNS}")
        rows = []
        for raw in reader:
            try:
                row = StudyEstimate(
                    link=raw["link"].strip(), study_id=raw["study_id"].strip(),
                    point=float(raw["point"]), standard_error=float(raw["standard_error"]),
                    scale=raw["scale"].strip(), population_scope=raw["population_scope"].strip(),
                    design=raw["design"].strip(), time_horizon=raw["time_horizon"].strip(),
                    citation=raw["citation"].strip(), source_url=raw.get("source_url", "").strip(),
                    treatment=raw.get("treatment", "").strip(), comparison=raw.get("comparison", "").strip(),
                    outcome_definition=raw.get("outcome_definition", "").strip(),
                    overlap_group=raw.get("overlap_group", "").strip(),
                )
            except (TypeError, ValueError) as exc:
                raise ValueError(f"invalid study estimate row {raw!r}") from exc
            if not row.link or not row.study_id or not row.scale or not row.citation:
                raise ValueError("study estimate link, study_id, scale, and citation are required")
            # population_scope/design/time_horizon are the compatibility
            # keys; a blank field must not pool as "identical" to another
            # blank field.
            blank = [name for name in ("population_scope", "design", "time_horizon")
                     if not getattr(row, name)]
            if blank:
                raise ValueError(
                    f"study estimate {row.study_id!r} has blank compatibility metadata: "
                    f"{', '.join(blank)}"
                )
            if not all(math.isfinite(v) for v in (row.point, row.standard_error)) or row.standard_error <= 0:
                raise ValueError(f"study estimate {row.study_id!r} must have finite point and positive standard_error")
            rows.append(row)
    keys = [(r.link, r.study_id) for r in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate (link, study_id) in study estimate CSV")
    return tuple(rows)


def random_effects(rows: list[StudyEstimate]) -> dict:
    """DerSimonian--Laird random-effects synthesis on one exact scale.

    This is an evidence-screening and heterogeneity diagnostic, not a causal
    transport posterior.  The prediction interval describes a new *study on
    this same scale*, not an automatically valid estimate for a new geography
    or population.
    """
    if len(rows) < 2:
        raise ValueError("random-effects synthesis needs at least two study estimates")
    scales = {r.scale for r in rows}
    links = {r.link for r in rows}
    populations = {r.population_scope for r in rows}
    horizons = {r.time_horizon for r in rows}
    treatments = {r.treatment for r in rows if r.treatment}
    comparisons = {r.comparison for r in rows if r.comparison}
    definitions = {r.outcome_definition for r in rows if r.outcome_definition}
    overlap_groups = [r.overlap_group for r in rows if r.overlap_group]
    if len(scales) != 1 or len(links) != 1:
        raise ValueError("pool only one link and one identical estimand scale at a time")
    # Programmatic rows bypass the loader, so the pooling path re-checks
    # the compatibility fields it groups on.
    blank = [name for name in ("population_scope", "design", "time_horizon")
             if any(not getattr(r, name) for r in rows)]
    if blank:
        raise ValueError(
            "blank compatibility metadata cannot establish like-for-like pooling: "
            f"{' ,'.join(sorted(set(blank)))}"
        )
    if len(populations) != 1 or len(horizons) != 1:
        raise ValueError("pool only studies with identical population_scope and time_horizon")
    if any(len(x) > 1 for x in (treatments, comparisons, definitions)):
        raise ValueError("pool only studies with identical declared treatment, comparison, and outcome definition")
    if len(overlap_groups) != len(set(overlap_groups)):
        raise ValueError("overlapping study samples require an explicit dependence model; do not pool duplicate overlap_group rows")
    weights = [1 / r.standard_error**2 for r in rows]
    w_sum = sum(weights)
    fixed = sum(w * r.point for w, r in zip(weights, rows)) / w_sum
    q = sum(w * (r.point - fixed)**2 for w, r in zip(weights, rows))
    df = len(rows) - 1
    c = w_sum - sum(w*w for w in weights) / w_sum
    tau2 = max(0.0, (q - df) / c) if c > 0 else 0.0
    re_weights = [1 / (r.standard_error**2 + tau2) for r in rows]
    re_w_sum = sum(re_weights)
    mean = sum(w * r.point for w, r in zip(re_weights, rows)) / re_w_sum
    se = math.sqrt(1 / re_w_sum)
    # Hartung--Knapp's residual scale acknowledges that tau² is estimated.
    # It is a sensitivity output, not a promise of calibrated coverage with
    # very few or dependent studies.
    hk_scale = sum(w * (r.point - mean) ** 2 for w, r in zip(re_weights, rows)) / df
    hk_se = math.sqrt(hk_scale / re_w_sum)
    hk_critical = _t975(df)
    prediction_se = math.sqrt(tau2 + se**2)
    return {
        "link": rows[0].link,
        "scale": rows[0].scale,
        "studies": len(rows),
        "fixed_effect": {"mean": fixed, "standard_error": math.sqrt(1 / w_sum)},
        "random_effects": {
            "mean": mean, "standard_error": se, "ci95": [mean - 1.96*se, mean + 1.96*se],
            "hartung_knapp_sensitivity": {
                "ci95": [mean - hk_critical * hk_se, mean + hk_critical * hk_se],
                "standard_error": hk_se,
                "degrees_of_freedom": df,
                "critical_value": hk_critical,
                "note": "Hartung-Knapp residual-scale sensitivity; do not treat it as reliable under unmodeled overlap or incompatible studies",
            },
            "tau2": tau2, "i2_percent": max(0.0, (q - df) / q * 100) if q > 0 else 0.0,
            "prediction_interval95": [mean - 1.96*prediction_se, mean + 1.96*prediction_se],
        },
        "heterogeneity": {"Q": q, "df": df},
        "study_metadata": [
            {"study_id": r.study_id, "population_scope": r.population_scope,
             "design": r.design, "time_horizon": r.time_horizon,
             "citation": r.citation, "source_url": r.source_url,
             "treatment": r.treatment, "comparison": r.comparison,
             "outcome_definition": r.outcome_definition, "overlap_group": r.overlap_group}
            for r in rows
        ],
        "compatibility": {
            "population_scope": rows[0].population_scope,
            "time_horizon": rows[0].time_horizon,
            "treatment": next(iter(treatments), None),
            "comparison": next(iter(comparisons), None),
            "outcome_definition": next(iter(definitions), None),
            "overlap": "no declared overlapping groups" if not overlap_groups else "declared groups are distinct",
            "missing_metadata": [name for name, values in (("treatment", treatments), ("comparison", comparisons), ("outcome_definition", definitions)) if not values],
        },
        "admission": "not admitted to parameters.csv; requires estimand, timing, and target-population review",
        "transport_note": "prediction interval is across comparable studies, not a transported target-population posterior",
    }


def synthesize(rows: tuple[StudyEstimate, ...], link: str | None = None) -> dict:
    """Synthesize eligible same-scale groups, refusing singleton groups."""
    groups: dict[tuple[str, str, str, str], list[StudyEstimate]] = {}
    for row in rows:
        if link is None or row.link == link:
            groups.setdefault((row.link, row.scale, row.population_scope, row.time_horizon), []).append(row)
    if link is not None and not groups:
        raise KeyError(f"no study estimates for link {link!r}")
    reports, blocked = [], []
    for (group_link, scale, population_scope, time_horizon), group in sorted(groups.items()):
        if len(group) < 2:
            blocked.append({"link": group_link, "scale": scale, "population_scope": population_scope,
                            "time_horizon": time_horizon, "reason": "needs at least two compatible studies"})
        else:
            reports.append(random_effects(group))
    return {"reports": reports, "blocked": blocked,
            "method": "DerSimonian-Laird random-effects; source-extracted compatible estimates only; plug-in intervals are sensitivity outputs, not small-study-safe intervals"}
