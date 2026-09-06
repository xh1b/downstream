"""Proper scoring rules for the validation program.

A published forecast must be scored against what happened. These are
the rules (Gneiting & Raftery 2007):

- CRPS — the continuous ranked probability score of a sample-based
  predictive distribution. Lower is better; CRPS of a point forecast
  equals absolute error; CRPS of the observation itself (degenerate)
  is 0.
- Coverage — the share of observations falling inside a published
  band. A 90% band that covers 60% of outcomes is overconfident,
  whatever its citations say.
- PIT — probability integral transform values for calibration curves.

Used by the V1 retrodiction and V3 prospective stages.
"""

from __future__ import annotations

import math


def crps_sample(samples: list[float], observed: float) -> float:
    """CRPS from a predictive sample: E|X-y| - 0.5 E|X-X'|.

    The standard sample-based estimator of the ensemble-forecasting
    literature (hersbach2000); sorted O(n log n) second term."""
    if not samples:
        raise ValueError("empty forecast sample")
    s = sorted(samples)
    n = len(s)
    term1 = sum(abs(x - observed) for x in s) / n
    # sum_i sum_j |X_i - X_j| (ordered pairs) via the rank identity:
    # sorted x gives sum_{i<j} (x_j - x_i) * 2 = sum_i x_i * 2(2i-n+1)
    weights = [2 * (2 * i - n + 1) for i in range(n)]
    term2 = sum(w * x for w, x in zip(weights, s)) / (n * n)
    return term1 - 0.5 * term2


def coverage(bands: list[tuple[float, float]], observed: list[float]) -> float:
    """Share of observations inside their published [lo, hi] bands."""
    if len(bands) != len(observed):
        raise ValueError("bands and observations must pair up")
    hits = sum(1 for (lo, hi), y in zip(bands, observed) if lo <= y <= hi)
    return hits / len(observed)


def pit(samples: list[float], observed: float) -> float:
    """PIT value of an observation under a sample-based forecast
    (midpoint convention so ties behave). Uniform PIT = calibrated."""
    s = sorted(samples)
    n = len(s)
    below = sum(1 for x in s if x < observed)
    equal = sum(1 for x in s if x == observed)
    return (below + 0.5 * equal) / n


def calibration_table(pits: list[float], bins: int = 10) -> list[dict]:
    """Counts per PIT bin — the raw material for a reliability curve."""
    if bins < 2:
        raise ValueError("need >= 2 bins")
    table = []
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        count = sum(1 for p in pits if (lo <= p < hi) or (b == bins - 1 and p == 1.0))
        table.append({"bin": [round(lo, 2), round(hi, 2)], "count": count})
    return table


def crps_of_point(point: float, observed: float) -> float:
    """Sanity anchor: CRPS of a degenerate (point) forecast."""
    return abs(point - observed)
