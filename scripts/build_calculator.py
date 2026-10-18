#!/usr/bin/env python3
# @ref:script-build-calculator
# Method: @link:doc-calculator.
# Implementation: @link:code-params; @link:code-scenario; @link:code-study-library;
# @link:calculator-template; @link:calculator-math; @link:calculator-app.
# Verification: @link:test-calculator; @link:test-calculator-server.
# @tag:calculator
"""Build the calculator page from current engine output."""
from __future__ import annotations

import argparse
import hashlib
import math
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
from scripts.artifact_checks import same_json  # noqa: E402


def same_html(saved: str, expected: str) -> bool:
    """Keep authored HTML exact; compare only embedded result floats by ULP."""
    marker = '<script id="engine-data" type="application/json">'
    saved_head, found, saved_tail = saved.partition(marker)
    expected_head, _, expected_tail = expected.partition(marker)
    if not found or saved_head != expected_head:
        return False
    saved_json, found, saved_end = saved_tail.partition('</script>')
    expected_json, _, expected_end = expected_tail.partition('</script>')
    if not found or saved_end != expected_end:
        return False
    try:
        return same_json(json.loads(saved_json), json.loads(expected_json))
    except ValueError:
        return False


def build() -> str:
    from downstream.params import load_all
    from downstream.scenario import ScenarioInput, compute_counts
    from downstream.study_library import load_library
    from downstream.worker import mortality_profile

    parts = load_all(ROOT / "params")
    result = compute_counts(parts["params"], parts["baselines"], ScenarioInput(
        1000, label="National source reference"))
    directory = ROOT / "calculator"
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
    def embedded_source(name):
        # Repeated inline assets cite their authored anchor rather than defining it again.
        return (directory / name).read_text().replace("@ref:", "@link:")

    template = embedded_source("template.html")
    return (template.replace("/* CALCULATOR_STYLE */", embedded_source("style.css"))
            .replace("/* CALCULATOR_DATA */", json.dumps(payload, sort_keys=True, indent=2,
                                                        allow_nan=False).replace("<", "\\u003c"))
            .replace("/* CALCULATOR_MATH */", embedded_source("math.js"))
            .replace("/* CALCULATOR_APP */", embedded_source("app.js")))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if generated HTML is stale")
    args = parser.parse_args()
    path = ROOT / "calculator" / "index.html"
    expected = build()
    if args.check:
        if not path.exists() or not same_html(path.read_text(), expected):
            print("Calculator HTML is stale; run scripts/build_calculator.py")
            return 1
        print("Calculator HTML matches current engine and authored UI inputs")
    else:
        path.write_text(expected)
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
