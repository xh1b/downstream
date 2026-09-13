#!/usr/bin/env python3
"""Build params/county_mortality.csv: Gamma-Poisson county mortality posteriors.

Consumes a validated CDC WONDER county export (see scripts/fetch_wonder.py)
under the strict CountyRateObservation contract, pools every county toward
the verified national baseline with the repo's declared prior strength
(place.py PRIOR_N: 2000 equivalent person-years for all-cause mortality),
and writes the posterior table the place layer consumes.

Every output row carries the complete provenance chain - the observation
(events, person-years, declared scope/window/citation) AND the national
prior (rate, unit, population, citation, copied from params/baselines.csv)
- so the loader can verify the chain end to end before applying anything.

Usage:
    uv run python scripts/build_county_mortality.py \
        --export validation/cdc_wonder_county_male_45_54_2015_2019.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from downstream.county_mortality import count_observations, parse_export
from downstream.county_rates import NationalRatePrior, poisson_gamma_posterior
from downstream.params import load_baselines

# The declared prior strength for county all-cause mortality pooling
# (place.py PRIOR_N["all_cause_mortality_annual"]). The Gamma-Poisson
# posterior replaces the w = n/(n+k) formula with the same intent: small
# counties shrink toward the national rate, large counties keep their
# own signal.
PRIOR_PERSON_YEARS = 2000.0

HEADER = ("key", "outcome", "population_scope", "time_window",
          "events", "person_years", "posterior_mean_rate",
          "prior_rate", "prior_unit", "prior_population", "prior_citation",
          "prior_person_years", "observation_citation")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--export", required=True, help="validated WONDER county export CSV")
    ap.add_argument("--metadata", default=None,
                    help="export sidecar JSON (default: <export>.metadata.json)")
    ap.add_argument("--params", default=str(ROOT / "params"))
    ap.add_argument("--out", default=None,
                    help="default: params/county_mortality.csv")
    ap.add_argument("--estimate-prior-k", action="store_true",
                    help="method-of-moments empirical-Bayes estimate of the prior "
                         "strength from this export; prints a report and writes nothing")
    args = ap.parse_args()

    metadata_path = (Path(args.metadata) if args.metadata
                     else Path(args.export).with_suffix(".metadata.json"))
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    baselines = load_baselines(Path(args.params) / "baselines.csv")
    base = baselines.get("all_cause_mortality_annual")
    if base is None or base.status != "verified" or base.value is None:
        raise SystemExit("no verified all_cause_mortality_annual national baseline")
    if base.unit != "deaths_per_person_year":
        raise SystemExit(f"national baseline unit {base.unit!r} is not a rate")

    parsed = parse_export(args.export, metadata=metadata)
    observations = count_observations(parsed)

    if args.estimate_prior_k:
        from downstream.county_rates import empirical_bayes_prior_person_years
        report = empirical_bayes_prior_person_years(observations, base.value)
        print(json.dumps({
            **report,
            "declared_prior_person_years": PRIOR_PERSON_YEARS,
            "note": "method-of-moments EB: Gamma prior matched to the between-county "
                    "mean/variance of true rates after Poisson-noise subtraction; "
                    "the declared k stays a choice the report informs, not a number "
                    "this flag imposes",
        }, indent=2))
        return 0

    prior = NationalRatePrior(
        outcome="all_cause_mortality_annual",
        rate=base.value,
        population_scope=(
            f"county residents, {metadata['sex'].lower()}, ages {metadata['age']}; "
            f"cause: {metadata['cause']}"
        ),
        time_window=f"{min(metadata['years'])}-{max(metadata['years'])}",
        citation=base.citation,
    )

    parsed = parse_export(args.export, metadata=metadata)
    observations = count_observations(parsed)
    rows = []
    for obs in observations:
        posterior = poisson_gamma_posterior(obs, prior, PRIOR_PERSON_YEARS, draws=2, seed=1901)
        rows.append({
            "key": obs.key,
            "outcome": obs.outcome,
            "population_scope": obs.population_scope,
            "time_window": obs.time_window,
            "events": obs.events,
            "person_years": obs.person_years,
            "posterior_mean_rate": f"{posterior['posterior']['mean_rate']:.9f}",
            "prior_rate": prior.rate,
            "prior_unit": base.unit,
            "prior_population": base.population,
            "prior_citation": prior.citation,
            "prior_person_years": PRIOR_PERSON_YEARS,
            "observation_citation": obs.citation,
        })

    out = Path(args.out or str(Path(args.params) / "county_mortality.csv"))
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=HEADER)
        writer.writeheader()
        writer.writerows(rows)

    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    provenance = {
        "source_table": str(Path(args.export).name),
        "metadata_sidecar": metadata_path.name,
        "built_at": stamp,
        "rows": len(rows),
        "prior": {
            "outcome": prior.outcome,
            "rate": prior.rate,
            "person_years": PRIOR_PERSON_YEARS,
            "declared_by": "place.py PRIOR_N['all_cause_mortality_annual']",
            "national_baseline_population": base.population,
            "national_baseline_citation": base.citation,
        },
        "method": "Gamma-Poisson posterior per county; posterior_mean_rate = "
                  "(prior_rate * prior_person_years + events) / "
                  "(prior_person_years + person_years)",
        "suppression": "counties with <=9 deaths are absent from the export and "
                       "therefore from this table; never reconstructed",
    }
    out.with_suffix(".provenance.json").write_text(
        json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out} ({len(rows)} county posteriors)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
