"""Knob experiments: turn a declared knob, measure what moves.

Two questions, two tools:

- `sweep` — set one parameter to each of a list of values (the knob
  PINNED: band collapsed onto the value) and recompute the scenario.
  Everything else keeps its band. The table shows how each modeled
  count responds to the knob, so a reader can see the model's local
  behavior without reading the engine.
- `value_of_information` — for each parameter, narrow its band by a
  factor around the point and re-run the Monte Carlo. The output band
  shrink that survives tells you which knob is WORTH turning. This is
  the extraction-queue ranker behind TODO plan #3/#4, computed instead
  of hand-waved.

Honesty rules (tested):

- Overridden parameter sets carry a `-knob` version marker. A knobbed
  run is an experiment, never a published parameter set.
- Unknown links and out-of-band pins fail loudly — a typo'd knob must
  not silently become a no-op.
- Pinning outside the parameter's own band is refused: a value the
  citations do not support cannot enter through the experiment door.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Callable

from .mc import simulate
from .params import ParameterSet
from .scenario import ScenarioInput, compute_counts


def with_band(
    params: ParameterSet,
    link: str,
    low: float,
    high: float,
    point: float | None = None,
) -> ParameterSet:
    """A copy with one parameter's band (and optionally point) overridden.

    Fails loudly if the link is unknown. Version is marked `-knob`.
    """
    base = params.by_link(link)  # KeyError with the link named if unknown
    if low > high:
        low, high = high, low
    p = replace(base, low=low, high=high)
    if point is not None:
        p = replace(p, point=point)
    rows = tuple(p if r.link == link else r for r in params.parameters)
    base_version = params.version.split("-sampled")[0].split("-knob")[0]
    return ParameterSet(version=f"{base_version}-knob", parameters=rows)


def pin(params: ParameterSet, link: str, value: float) -> ParameterSet:
    """Pin a knob exactly: point = low = high = value.

    The value must lie inside the parameter's current band — the band
    is what the citations license, and the experiment door does not
    widen it.
    """
    base = params.by_link(link)
    lo, hi = sorted((base.low, base.high))
    if not lo <= value <= hi:
        raise ValueError(
            f"cannot pin {link!r} to {value}: outside its cited band "
            f"[{lo}, {hi}]. Widen the band in params/parameters.csv "
            f"with a citation first."
        )
    return with_band(params, link, value, value, point=value)


def sweep(
    params: ParameterSet,
    baselines: dict,
    scenario: ScenarioInput,
    link: str,
    values: list[float],
) -> dict:
    """Scenario counts at each pinned value of one knob.

    Each row pins the knob (band collapsed) so the row's spread across
    values is the knob's effect, not sampling noise. The remaining
    parameters keep their bands; point arithmetic carries the row.
    """
    if not values:
        raise ValueError("sweep needs at least one value")
    rows = []
    first: dict | None = None
    for v in values:
        ps = pin(params, link, v)
        out = compute_counts(ps, baselines, scenario)
        flat = _flatten(out)
        if first is None:
            first = flat
        rows.append(
            {
                "knob": link,
                "value": v,
                "modeled": flat,
                "delta_vs_first": {
                    k: (round(flat[k] - first[k], 4) if isinstance(flat[k], (int, float)) else None)
                    for k in flat
                },
            }
        )
    return {
        "experiment": "sweep_1d",
        "knob": link,
        "parameter_set_version": params.version,
        "scenario": {
            "displaced_workers": scenario.displaced_workers,
            "n_children": scenario.n_children,
            "tradable_share": scenario.tradable_share,
            "exposure_years": scenario.exposure_years,
        },
        "rows": rows,
        "note": (
            "Knob pinned per row (band collapsed onto the value); "
            "point arithmetic. The knob value stays inside its cited "
            "band — the sweep cannot travel beyond the evidence."
        ),
    }


def value_of_information(
    params: ParameterSet,
    compute: Callable[[ParameterSet], float],
    nodes: dict,
    draws: int = 2_000,
    seed: int = 1901,
    shrink: float = 0.5,
) -> dict:
    """Rank parameters by how much narrowing each one buys.

    For every parameter: collapse its band halfway toward its point
    (`shrink=0.5` halves the band), re-run the LHS Monte Carlo on the
    same seed, and compare the p05-p95 width against the baseline run.
    The rank answers: which knob, turned next, removes the most output
    uncertainty? This is the Sobol ranking restated in OUTPUT units —
    band shrink, not variance share.
    """
    if not 0.0 < shrink <= 1.0:
        raise ValueError(f"shrink must be in (0, 1], got {shrink}")

    base = simulate(params, compute, draws=draws, seed=seed, nodes=nodes)
    base_width = base["p95"] - base["p05"]

    rows = []
    for p in params.parameters:
        lo, hi = sorted((p.low, p.high))
        if not lo <= p.point <= hi:
            raise ValueError(
                f"parameter {p.link!r} has point {p.point} outside its own "
                f"band [{lo}, {hi}] — fix params/parameters.csv"
            )
        if hi == lo:
            width_after = base_width  # already pinned; nothing to shrink
            rows.append(
                {
                    "link": p.link,
                    "band_before": [lo, hi],
                    "band_after": [lo, hi],
                    "p05": None,
                    "p95": None,
                    "width_after": None,
                    "width_reduction": 0.0,
                    "note": "already pinned (zero-width band)",
                }
            )
            continue
        nlo = p.point - (p.point - lo) * shrink
        nhi = p.point + (hi - p.point) * shrink
        ps = with_band(params, p.link, nlo, nhi)
        run = simulate(ps, compute, draws=draws, seed=seed, nodes=nodes)
        width_after = run["p95"] - run["p05"]
        rows.append(
            {
                "link": p.link,
                "band_before": [lo, hi],
                "band_after": [round(nlo, 6), round(nhi, 6)],
                "p05": run["p05"],
                "p95": run["p95"],
                "width_after": round(width_after, 4),
                "width_reduction": round(1 - width_after / base_width, 4) if base_width > 0 else 0.0,
            }
        )
    rows.sort(key=lambda r: -r["width_reduction"])
    return {
        "experiment": "value_of_information",
        "outcome_band_baseline": {"p05": base["p05"], "p95": base["p95"], "width": round(base_width, 4)},
        "draws": draws,
        "seed": seed,
        "shrink": shrink,
        "parameter_set_version": params.version,
        "rows": rows,
        "note": (
            "Width reduction = share of the p05-p95 output band removed "
            "by halving this parameter's band. Same seed across runs, so "
            "the comparison is paired. Ranks the extraction queue in "
            "output units."
        ),
    }


def _flatten(out: dict) -> dict:
    """Point values of the modeled counts + the tracked multipliers."""
    flat: dict = {}
    for key, val in out.get("modeled", {}).items():
        if isinstance(val, dict) and "point" in val:
            flat[key] = val["point"]
        else:
            flat[key] = val
    for key, val in out.get("multipliers", {}).items():
        flat[f"mult:{key}"] = val["point"]
    flat["blocked_count"] = len(out.get("blocked", []))
    return flat
