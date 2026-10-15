# @ref:script-analyze-mortality-covariance
# Method: @link:doc-mortality-covariance-0-4.
# Implementation: @link:code-mortality-covariance.
# @tag:mortality
"""Inspect available Table 4 additive components without admitting a profile."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


def report():
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "src"))
    from downstream.mortality_covariance import AdditiveCoefficient, additive_phase_diagnostic

    # Visual transcription: available author manuscript PDF page 35, Table 4 col 1.
    # No values come from the working-paper Table 5 or its direct odds phases.
    components = [AdditiveCoefficient(name, estimate, error) for name, estimate, error in [
        ("main_16_plus", .131, .054), ("added_1", .716, .199),
        ("added_2_3", .559, .147), ("added_4_5", .198, .147),
        ("added_6_10", .057, .094), ("added_11_15", -.066, .081)]]
    phase_names = [("1 year after displacement year", "added_1"),
                   ("2-3 years after displacement year", "added_2_3"),
                   ("4-5 years after displacement year", "added_4_5"),
                   ("6-10 years after displacement year", "added_6_10"),
                   ("11-15 years after displacement year", "added_11_15"),
                   ("16+ years after displacement", None)]
    phases = {}
    for label, addition in phase_names:
        weights = {"main_16_plus": 1}
        if addition:
            weights[addition] = 1
        phases[label] = additive_phase_diagnostic(components, weights)
    return {
        "schema": "downstream-additive-covariance-diagnostic/1",
        "status": "source-manuscript precision diagnostic; not admitted as a model profile",
        "source": {
            "url": "https://www.movingforwardnetwork.com/wp-content/uploads/2023/04/Sullivan_Job-Displacement-and-Mortality_2009.pdf",
            "sha256": "1f31b9c02bc20d22fbdf5f2e86e655646ee3f5ae62b31f3b15549dffa0c4dd55",
            "locator": "PDF page 35 (one-based), Table 4, column 1; visually checked 2026-10-15",
            "version": "Available 2009 author-manuscript copy; not a freshly verified publisher version of record",
            "population": "Male birth cohorts 1930-1959; stable employment 1974-1979; 1979 tenure >=6 years; employer employment >=50; no further PA labor-market presence restriction",
            "reference_category": "Manufacturing job; the separate nonmanufacturing interaction is not included",
        },
        "phases": phases,
        "limitations": [
            "No coefficient covariance was supplied or inferred.",
            "These are additive log-odds totals, not probability differences or working-paper direct phase coefficients.",
            "Printed timing labels are retained; no mapping onto production follow-up years is assumed.",
            "SE bounds are sharp for one contrast at a time; different phase minima need not be jointly attainable.",
            "Normal approximation envelopes are marginal diagnostics, not a simultaneous band or source-reported confidence intervals.",
            "These calculations do not bound nonlinear cumulative deaths, establish transport, or authorize admission.",
        ],
        "implementation_sha256": {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                                  for name in ["src/downstream/mortality_covariance.py",
                                               "scripts/analyze_mortality_covariance.py"]},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = json.dumps(report(), indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(output)
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
