"""Immutable local forecast registrations and separate outcome scoring.

A local timestamp is not proof of public preregistration. Publish the
registration hash to an independent timestamped archive before outcomes.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path


def _date(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("forecast dates must include a timezone")
    return parsed


def register(path, proposal, *, now=None):
    """Freeze a forecast before its outcome window begins; never overwrite."""
    now = now or datetime.now(timezone.utc)
    required = ("event_id", "event_source", "population", "outcome", "unit",
                "measurement_source", "measurement_rule", "exposure_bridge_source",
                "algo_version", "outcome_window_start", "outcome_window_end")
    for key in required:
        if not isinstance(proposal.get(key), str) or not proposal[key].strip():
            raise ValueError(f"{key} is required")
    start, end = (_date(proposal[k]) for k in ("outcome_window_start", "outcome_window_end"))
    if not now < start < end:
        raise ValueError("registration must precede the entire outcome window")
    prediction = proposal["prediction"]
    vals = [prediction[k] for k in ("low", "point", "high")]
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in vals):
        raise ValueError("prediction must contain finite numbers")
    if not vals[0] <= vals[1] <= vals[2]:
        raise ValueError("prediction envelope must contain the point")
    record = {"schema": "downstream-forecast/1", "registered_at": now.isoformat(),
              "proposal": proposal, "scoring_rule": "absolute error and support-envelope coverage",
              "timestamp_status": "local only; independent timestamp required"}
    digest = hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()
    record["sha256"] = digest
    with Path(path).open("x") as f:
        json.dump(record, f, indent=2)
        f.write("\n")
    return record


def score(record, measured, *, unit, source, now=None):
    record = dict(record)
    digest = record.pop("sha256")
    if hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest() != digest:
        raise ValueError("forecast registration was modified")
    proposal = record["proposal"]
    if (now or datetime.now(timezone.utc)) < _date(proposal["outcome_window_end"]):
        raise ValueError("outcome window is not complete")
    if unit != proposal["unit"] or not source:
        raise ValueError("measurement needs matching units and a source")
    if isinstance(measured, bool) or not isinstance(measured, (int, float)) or not math.isfinite(measured):
        raise ValueError("measurement must be finite")
    pred = proposal["prediction"]
    return {"registration_sha256": digest, "measured": measured, "unit": unit, "source": source,
            "absolute_error": abs(measured-pred["point"]),
            "covered": pred["low"] <= measured <= pred["high"],
            "interpretation": "Coverage of a support envelope, not calibrated probabilistic coverage"}
