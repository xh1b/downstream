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
            for field in ("link", "source_locator", "population_scope", "time_horizon", "scale", "design", "citation", "overlap_group",
                          "treatment", "comparison", "outcome_definition", "standard_error_method"):
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


def require_contrast(row: dict, **expected: str) -> None:
    """Admit a source coefficient only for the scale/window/population it serves."""
    mismatches = [key for key, value in expected.items() if row.get(key) != value]
    if mismatches:
        raise ValueError(f"incompatible source contrast {row.get('study_id')}: {', '.join(mismatches)}")
