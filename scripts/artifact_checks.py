# @ref:script-artifact-checks
# Contract: @link:development-tooling. Verification: @link:test-artifact-checks.
"""Compare generated results across libm implementations without rounding data."""
from __future__ import annotations

import math


def same_json(left, right):
    """Require exact structure/metadata; allow at most 32 ULP for finite floats.

    Zero remains exact. Source hashes still bind every authored model input.
    The allowance covers measured libm differences amplified by subtraction;
    it is a freshness comparison, never a transform of exported results.
    """
    if type(left) is not type(right):
        return False
    if isinstance(left, float):
        if not (math.isfinite(left) and math.isfinite(right)):
            return False
        if left == 0 or right == 0:
            return left == right
        return abs(left - right) <= 32 * max(math.ulp(left), math.ulp(right))
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(same_json(v, right[k]) for k, v in left.items())
    if isinstance(left, list):
        return len(left) == len(right) and all(same_json(a, b) for a, b in zip(left, right))
    return left == right
