"""Fail CI when measured line or branch coverage regresses below the floor."""
from __future__ import annotations

import json
from pathlib import Path
import sys

MIN_LINE = 95.0
MIN_BRANCH = 90.0


def main(argv: list[str] | None = None) -> int:
    path = Path((argv or sys.argv[1:])[0] if (argv or sys.argv[1:]) else "coverage.json")
    totals = json.loads(path.read_text(encoding="utf-8"))["totals"]
    line = float(totals["percent_statements_covered"])
    branch = float(totals["percent_branches_covered"])
    print(f"coverage: lines={line:.1f}% (min {MIN_LINE:.1f}%), branches={branch:.1f}% (min {MIN_BRANCH:.1f}%)")
    return 0 if line >= MIN_LINE and branch >= MIN_BRANCH else 1


if __name__ == "__main__":
    raise SystemExit(main())
