#!/usr/bin/env python3
"""Build a self-contained local reference explorer from current engine output."""
from __future__ import annotations

import argparse
import hashlib
import math
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def build() -> str:
    from downstream.params import load_all
    from downstream.scenario import ScenarioInput, compute_counts
    from downstream.study_library import load_library
    from downstream.worker import mortality_profile

    parts = load_all(ROOT / "params")
    result = compute_counts(parts["params"], parts["baselines"], ScenarioInput(
        1000, label="Fixed national reference; exposure scaling only"))
    directory = ROOT / "examples" / "calculator"
    phases = [{"phase": phase, "label": label, "point": p.point, "low": p.low, "high": p.high,
               "citation": p.citation, "population_scope": p.population_scope}
              for (phase, p), label in zip(mortality_profile(parts["params"]).items(),
                                           ("0", "+1", "+2–3", "+4–5", "+6…"))]
    original = parts["params"].by_link("displacement->child_earnings")
    presets = {"overall": {"point": original.point, "low": original.low, "high": original.high,
                           "source": {"citation": original.citation, "notes": original.notes,
                                      "population_scope": original.population_scope}}}
    library = load_library(ROOT / "params" / "study_estimates.csv")
    for q in range(1, 5):
        row = library[f"oreopoulos2008_q{q}"]
        beta, se = row["point"], row["standard_error"]
        presets[f"q{q}"] = {"point": math.exp(beta), "low": math.exp(beta - 1.96 * se),
                            "high": math.exp(beta + 1.96 * se), "source": row}
    payload = {"result": result, "phases": phases, "child_presets": presets,
               "browser_math_sha256": hashlib.sha256((directory / "math.js").read_bytes()).hexdigest(),
               "defaults": {"workers": 1000, "years": 20,
                            "rate": parts["baselines"]["all_cause_mortality_annual"].value,
                            "children": 2, "gap": original.point,
                            "earnings": parts["baselines"]["median_male_lifetime_earnings"].value}}
    template = (directory / "template.html").read_text()
    return (template.replace("/* CALCULATOR_STYLE */", (directory / "style.css").read_text())
            .replace("/* CALCULATOR_DATA */", json.dumps(payload, sort_keys=True, indent=2,
                                                        allow_nan=False).replace("<", "\\u003c"))
            .replace("/* CALCULATOR_MATH */", (directory / "math.js").read_text())
            .replace("/* CALCULATOR_APP */", (directory / "app.js").read_text()))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if generated HTML is stale")
    args = parser.parse_args()
    path = ROOT / "examples" / "calculator" / "index.html"
    expected = build()
    if args.check:
        if not path.exists() or path.read_text() != expected:
            print("Calculator HTML is stale; run scripts/build_calculator_prototype.py")
            return 1
        print("Calculator HTML matches current engine and authored UI inputs")
    else:
        path.write_text(expected)
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
