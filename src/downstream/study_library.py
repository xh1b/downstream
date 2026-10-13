"""Hash-pinned source contrasts; distinct from pooled or transported effects."""
from __future__ import annotations

import csv
import math
from pathlib import Path
import re

from .params import default_dir


def load_library(path: Path | None = None) -> dict[str, dict]:
    path = path or default_dir() / "study_estimates.csv"
    out = {}
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            key = row["study_id"]
            if key in out:
                raise ValueError("duplicate source contrast")
            if not re.fullmatch(r"[0-9a-f]{64}", row["source_sha256"]):
                raise ValueError("source contrast requires SHA-256")
            for field in ("source_locator", "population_scope", "time_horizon", "scale", "design", "citation", "overlap_group"):
                if not row[field].strip():
                    raise ValueError(f"source contrast requires {field}")
            for field in ("point", "standard_error"):
                row[field] = float(row[field])
                if not math.isfinite(row[field]):
                    raise ValueError("source contrast must be finite")
            if row["standard_error"] <= 0:
                raise ValueError("source contrast requires positive standard error")
            out[key] = row
    if not out:
        raise ValueError("source contrast library is empty")
    return out
