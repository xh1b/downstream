# @ref:script-build-consumer-fixtures
# Method: @link:doc-consumer-fixtures-0-4.
# Implementation: @link:code-consumer; @link:code-county-rates; @link:code-mortality-profiles.
# @tag:consumer
"""Build offline acceptance fixtures for normalized and mixed model consumers."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from downstream.consumer import mix_expected, scale_outcome  # noqa: E402


def build():
    sys.path.insert(0, str(ROOT / "src"))
    from downstream import __version__
    from downstream.county_rates import load_county_mortality_posteriors
    from downstream.mortality_profiles import load_profiles
    from downstream.params import load_all
    from downstream.place import load_places
    from downstream.scenario import ScenarioInput, compute_counts, sample_counts

    directory = ROOT / "params"
    parts = load_all(directory)
    places = load_places(directory / "places.csv")
    county = load_county_mortality_posteriors(directory / "county_mortality.csv")
    profiles = load_profiles(directory / "mortality_profiles.csv")
    fixtures = {}

    def add(name, scenario, *, requested_place="national", sample=False):
        resolved = requested_place if requested_place in places else "national"
        options = dict(places=places, place_key=resolved, mortality_profiles=profiles,
                       county_mortality=county, params_dir=directory)
        public = (sample_counts(parts["params"], parts["baselines"], scenario,
                                draws=128, seed=1901, nodes=parts["nodes"],
                                sensitivity_base=128, **options) if sample
                  else compute_counts(parts["params"], parts["baselines"], scenario, **options))
        # Precision at the display boundary matters for fractional exposure.
        raw = compute_counts(parts["params"], parts["baselines"], scenario, _raw=True, **options)
        for key, row in public["modeled"].items():
            for stat in ("point", "low", "high"):
                row[stat] = raw["modeled"][key][stat]
        for row in public["modeled"].values():
            if row.get("persistence_sensitivity", {}).get("available"):
                sampled = row["persistence_sensitivity"]
                raw_p = raw["modeled"]["excess_deaths"]["persistence_sensitivity"]
                for variant, values in raw_p["variants"].items():
                    for stat in ("point", "low", "high"):
                        sampled["variants"][variant][stat] = values[stat]
                sampled["source_minus_no_sustained_point"] = raw_p["source_minus_no_sustained_point"]
                sampled["structural_point_range"] = raw_p["structural_point_range"]
        entry = {"scenario": asdict(scenario), "requested_place": requested_place,
                 "resolved_place": resolved, "fallback_reason": None if resolved == requested_place
                 else "Requested county has no place coverage; explicit national reference used.",
                 "normalization_workers": scenario.displaced_workers,
                 "precision": "Raw engine totals with public applicability, provenance and sensitivity.",
                 "result": public}
        fixtures[name] = entry
        return public

    national = add("national", ScenarioInput(1000.0), sample=True)
    local = add("county_17043", ScenarioInput(1000.0), requested_place="17043")
    add("unsupported_county", ScenarioInput(1000.0), requested_place="72127")
    add("zero", ScenarioInput(0.0))
    add("fractional", ScenarioInput(.125))
    add("beneficial_child", ScenarioInput(1000.0, child_income_quartile=3,
                                         income_rank_definition="Synthetic fixture assumes source-matched rank; not target evidence."))
    add("valuation", ScenarioInput(1000.0, child_profiles=[{"age_at_displacement": 12, "sex": "Male"}]*2,
                                   real_discount_rate=.03, valuation_year=2026))
    target = {"sex": "Male", "age": "45-54 years", "worker_tenure": "high-tenure",
              "geography": "United States", "calendar_window": "2015-2019",
              "exposure_type": "firm closure", "children_sex": "Male"}
    decisions = {key: {"status": "reviewed", "reviewer": "synthetic fixture",
                      "rationale": "Fixture only; not a real transport review.", "citations": "synthetic"}
                 for key in ("excess_deaths", "child_lifetime_earnings_lost_usd")}
    reviewed = add("synthetic_reviewed", ScenarioInput(1000.0, target_population=target,
                         applicability_decisions=decisions,
                         child_profiles=[{"age_at_displacement": 12, "sex": "Male"}]*2,
                         income_rank_definition="synthetic source-matched rank"))
    blocked = add("blocked_demographics", ScenarioInput(1000.0, target_population={**target, "sex": "Female"}))
    scaled = {str(n): {key: scale_outcome(row, n/1000) for key, row in national["modeled"].items()}
              for n in (0, .125, 250, 1000, 1_000_000)}
    mixtures = {}
    for name, results, weights in [("county_national", [local, national], [.6, .4]),
                                    ("partly_reviewed", [reviewed, national], [.5, .5]),
                                    ("partly_blocked", [local, blocked], [.5, .5])]:
        mixtures[name] = {"weights": weights,
                          "expected": {key: mix_expected(results, weights, key)
                                       for key in ("excess_deaths", "child_lifetime_earnings_lost_usd")}}
    files = (sorted((ROOT / "src/downstream").glob("*.py")) + sorted(directory.glob("*"))
             + [ROOT / "scripts/build_consumer_fixtures.py"])
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in files if p.is_file()}
    return {"schema": "downstream-consumer-fixtures/1", "engine_version": __version__,
            "parameter_set_version": parts["params"].version,
            "source_files_sha256": hashes,
            "source_content_sha256": hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest(),
            "fixture_sampling": "128 draws/base, seed 1901; contract fixtures, not precision-qualified research intervals.",
            "fixtures": fixtures, "expected_display_values": scaled, "mixtures": mixtures}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "validation/consumer_fixtures_0_4.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, allow_nan=False) + "\n"
    if args.check:
        if args.out.read_text() != rendered:
            parser.error("consumer fixtures differ; regenerate on the intended fixed candidate")
    else:
        args.out.write_text(rendered)
    print(args.out)


if __name__ == "__main__":
    main()
