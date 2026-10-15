# @ref:script-analyze-mortality-persistence
# Method: @link:doc-mortality-persistence-analysis-2026-10-14.
# Implementation: @link:code-mortality; @link:code-params; @link:code-scenario.
# @tag:mortality
"""Reproduce persistence arithmetic without changing admitted model inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys


def main():
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "src"))
    from downstream import __version__
    from downstream.mortality import excess_deaths_profile, odds_risk, rate_to_risk
    from downstream.params import load_all
    from downstream.scenario import ScenarioInput, sample_counts
    from downstream.worker import mortality_profile

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=root / "validation/mortality_persistence_analysis_20261014.json")
    args = parser.parse_args()
    parts = load_all(root / "params")
    profile = mortality_profile(parts["params"])
    odds = {phase: parameter.point for phase, parameter in profile.items()}
    alternative = {**odds, "offset_6_plus": 1.0}
    baseline_rate = parts["baselines"]["all_cause_mortality_annual"].value
    risk = rate_to_risk(baseline_rate)
    phases = ["displacement", "offset_1", "offsets_2_3", "offsets_2_3",
              "offsets_4_5", "offsets_4_5"] + ["offset_6_plus"] * 14

    def recurrence(annual_odds):
        reference_survivors = exposed_survivors = 1000.0
        path = []
        for year, ratio in enumerate(annual_odds, 1):
            reference_deaths = reference_survivors * risk
            exposed_deaths = exposed_survivors * odds_risk(risk, ratio)
            reference_survivors -= reference_deaths
            exposed_survivors -= exposed_deaths
            path.append({"follow_up_year": year,
                         "reference_deaths_in_year": reference_deaths,
                         "scenario_deaths_in_year": exposed_deaths,
                         "annual_death_count_difference": exposed_deaths - reference_deaths,
                         "reference_cumulative_deaths": 1000 - reference_survivors,
                         "scenario_cumulative_deaths": 1000 - exposed_survivors,
                         "cumulative_excess_deaths": reference_survivors - exposed_survivors})
        return path

    source_path = recurrence([odds[phase] for phase in phases])
    alternate_path = recurrence([alternative[phase] for phase in phases])
    for values, path in [(odds, source_path), (alternative, alternate_path)]:
        for row in path:
            expected = excess_deaths_profile(1000, risk, values, row["follow_up_year"])
            assert math.isclose(row["cumulative_excess_deaths"], expected, abs_tol=2e-12)
    assert source_path[:6] == alternate_path[:6]
    source = source_path[-1]["cumulative_excess_deaths"]
    alternate = alternate_path[-1]["cumulative_excess_deaths"]
    # Same working-paper sample, column 2's separate late phases. Point-only
    # diagnostic, not a new admitted response or an independent study.
    segmented_betas = [.983, .688, .555, .555, .249, .249] + [.179]*5 + [.065]*5 + [.153]*4
    segmented = recurrence([math.exp(beta) for beta in segmented_betas])
    sampled = sample_counts(parts["params"], parts["baselines"], ScenarioInput(1000),
                            nodes=parts["nodes"], params_dir=root / "params", draws=2000, seed=1901)
    hashes = {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in [
        "params/parameters.csv", "params/baselines.csv", "params/correlations.csv",
        "params/study_estimates.csv", "src/downstream/mortality.py",
        "src/downstream/mortality_robustness.py", "scripts/analyze_mortality_persistence.py"]}
    result = {
        "engine_version": __version__,
        "parameter_set_version": (root / "params/VERSION").read_text().strip(),
        "input_sha256": hashes,
        "scope": "Fixed national male 45-54 reference, 1000 workers, 20 years; no aging or target transport calibration.",
        "baseline_annual_rate": baseline_rate,
        "baseline_annual_probability": risk,
        "phases": [{"phase": phase, "odds_ratio": odds[phase],
                    "annual_risk_per_1000_survivors": 1000 * odds_risk(risk, odds[phase])}
                   for phase in odds],
        "source_path": source_path,
        "no_sustained_excess_path": alternate_path,
        "source_minus_alternative_at_year_20": source - alternate,
        "difference_as_fraction_of_source_excess": (source - alternate) / source,
        "source_excess_increase_over_alternative": source / alternate - 1,
        "late_log_odds_attenuation": [
            {"fraction_of_source_late_log_odds": fraction,
             "late_odds_ratio": math.exp(fraction * math.log(odds["offset_6_plus"])),
             "year_20_excess": excess_deaths_profile(1000, risk, {
                 **odds, "offset_6_plus": math.exp(fraction * math.log(odds["offset_6_plus"]))}, 20)}
            for fraction in [0, .25, .5, .75, 1]],
        "attenuation_status": "Unweighted diagnostic assumptions, not an identified transport distribution or bounds.",
        "working_paper_column_2_diagnostic": {
            "source": "Sullivan-von Wachter NBER WP13626 Table 5 column 2, PDF page 54",
            "url": "https://www.nber.org/system/files/working_papers/w13626/w13626.pdf",
            "source_sha256": "20617cbe3924c8b58f6d3888cb0a0ea26ca908d60486f4aad304398dd6ef9c8f",
            "annual_log_odds_coefficients": segmented_betas,
            "year_20_excess": segmented[-1]["cumulative_excess_deaths"],
            "status": "Point-only within-study check using fixed model baseline; no joint interval or production admission."},
        "paired_parameter_sampling": sampled["modeled"]["excess_deaths"]["persistence_sensitivity"],
        "sampling_exclusions": sampled["parameter_uncertainty"]["excluded"],
        "arithmetic_check": "Annual survivor recurrence agrees with production log-survival function at all 20 horizons within 2e-12 deaths.",
    }
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"source": source, "alternative": alternate, "difference": source-alternate,
                      "segmented_same_study": segmented[-1]["cumulative_excess_deaths"],
                      "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
