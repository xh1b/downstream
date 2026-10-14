#!/usr/bin/env python3
"""Build a self-contained local reference explorer from current engine output."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def build() -> str:
    from downstream.params import load_all
    from downstream.scenario import ScenarioInput, compute_counts

    parts = load_all(ROOT / "params")
    result = compute_counts(parts["params"], parts["baselines"], ScenarioInput(
        1000, label="Fixed national reference; exposure scaling only"))
    payload = {"reference_exposure": 1000, "result": result}
    directory = ROOT / "examples" / "calculator"
    template = (directory / "template.html").read_text()
    return (template.replace("/* CALCULATOR_STYLE */", (directory / "style.css").read_text())
            .replace("/* CALCULATOR_DATA */", json.dumps(payload, sort_keys=True, indent=2,
                                                        allow_nan=False).replace("<", "\\u003c"))
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
