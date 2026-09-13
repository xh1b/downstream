"""downstream CLI.

    downstream family                          standard-family vignette
    downstream scenario --workers 1000         modeled counts for an exposure
    downstream explain                         the child-line claim, explained
    downstream sensitivity --outcome grandchild
    downstream simulate --links a,b --kinds direct,gap
    downstream audit                           parameter/citation/DAG checks
    downstream validate                        V0 consistency + V1 target
    downstream citations                       citation coverage report
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .audit import audit, summary
from .explanation import explain_child_line
from .mc import simulate_chain
from .params import ParameterSet, default_dir, load_all
from .render import load_citations, render_text
from .scenario import ScenarioInput, compute_counts
from .snapshot import dumps as snapshot_dumps
from .snapshot import write as snapshot_write
from .sensitivity import sobol_indices
from .validate import run as validate_run
from .vignette import standard_family

DEFAULT_PARAMS_DIR = str(default_dir())


def _dump(obj) -> None:
    json.dump(obj, sys.stdout, indent=2)
    print()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="downstream")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("family", help="standard-family vignette")
    p.add_argument("--params", default=DEFAULT_PARAMS_DIR)
    p.add_argument("--wage-multiplier", type=float, default=0.80)
    p.add_argument("--children", type=int, default=3)
    p.add_argument("--place", default=None, metavar="KEY",
                   help="places.csv key — applies shrunk baselines + the mobility modifier")

    p = sub.add_parser("scenario", help="modeled counts for a displacement exposure")
    p.add_argument("--params", default=DEFAULT_PARAMS_DIR)
    p.add_argument("--workers", type=float, required=True)
    p.add_argument("--children", type=int, default=2)
    p.add_argument("--tradable-share", type=float, default=1.0)
    p.add_argument("--net-tradable-jobs-lost", type=float, default=None,
                   help="documented net metro-level loss of tradable jobs; required for local service jobs")
    p.add_argument("--wage-multiplier", type=float, default=None)
    p.add_argument("--exposure-years", type=float, default=20.0)
    p.add_argument("--mortality-method", choices=["odds_survival", "legacy_additive"], default="odds_survival")
    p.add_argument("--mortality-timing", choices=["source_profile", "source_aligned", "immediate_sustained"], default="source_profile",
                   help="source_profile follows extracted source offsets; other choices are legacy/sensitivity assumptions")
    p.add_argument("--mortality-profile", default=None,
                   help="verified demographic mortality profile id from mortality_profiles.csv")
    p.add_argument("--mortality-mix", default=None, metavar="PROFILE:WEIGHT,...",
                   help="declared demographic mix; weights must sum to one")
    p.add_argument("--place-application", choices=["initial_only", "legacy_repeated"], default="initial_only")
    p.add_argument("--draws", type=int, default=2_000,
                   help="parameter-only Monte Carlo draws for count intervals (minimum 2)")
    p.add_argument("--seed", type=int, default=1901)
    p.add_argument("--strict", action="store_true", help="fail on missing baselines")
    p.add_argument("--place", default=None, metavar="KEY",
                   help="places.csv key — applies shrunk baselines + the mobility modifier")

    p = sub.add_parser("forecast-register", help="freeze a prospective forecast locally")
    p.add_argument("--params", default=DEFAULT_PARAMS_DIR)
    p.add_argument("--input", required=True)
    p.add_argument("--out", required=True)

    p = sub.add_parser("forecast-score", help="score a completed registered forecast")
    p.add_argument("--params", default=DEFAULT_PARAMS_DIR)
    p.add_argument("--input", required=True)
    p.add_argument("--measured", type=float, required=True)
    p.add_argument("--unit", required=True)
    p.add_argument("--source", required=True)

    p = sub.add_parser("synthesize", help="random-effects synthesis of source-extracted, same-scale study estimates")
    p.add_argument("--params", default=DEFAULT_PARAMS_DIR)
    p.add_argument("--input", required=True, help="CSV with study_id, link, point, standard_error, scale, and scope metadata")
    p.add_argument("--link", default=None, help="optional link id to synthesize")
    p.add_argument("--compare-params", action="store_true",
                   help="add a read-only manual-review comparison to the shipped parameter row")

    p = sub.add_parser("county-posterior", help="Gamma-Poisson county event/person-time rate posterior")
    p.add_argument("--params", default=DEFAULT_PARAMS_DIR)
    p.add_argument("--input", required=True, help="CSV with county event counts and person-years")
    p.add_argument("--key", required=True)
    p.add_argument("--outcome", required=True)
    p.add_argument("--time-window", required=True)
    p.add_argument("--national-rate", required=True, type=float)
    p.add_argument("--national-population-scope", required=True,
                   help="must exactly match the county input's population_scope")
    p.add_argument("--national-citation", required=True,
                   help="locator for the national rate and matching window")
    p.add_argument("--prior-person-years", required=True, type=float)
    p.add_argument("--draws", default=10_000, type=int)
    p.add_argument("--seed", default=1901, type=int)

    p = sub.add_parser("county-wonder-posterior", help="posterior directly from a validated CDC WONDER county export")
    p.add_argument("--params", default=DEFAULT_PARAMS_DIR)
    p.add_argument("--export", required=True, help="tab-delimited county WONDER export")
    p.add_argument("--metadata", required=True, help="JSON saved query metadata")
    p.add_argument("--key", required=True)
    p.add_argument("--national-rate", required=True, type=float)
    p.add_argument("--prior-person-years", required=True, type=float)
    p.add_argument("--draws", default=10_000, type=int)
    p.add_argument("--seed", default=1901, type=int)

    p = sub.add_parser("bundle", help="export a pinned standalone engine and data directory")
    p.add_argument("--params", default=DEFAULT_PARAMS_DIR)
    p.add_argument("--out", required=True)

    p = sub.add_parser("policy", help="compare baseline and policy exposure assumptions")
    p.add_argument("--params", default=DEFAULT_PARAMS_DIR)
    p.add_argument("--input", required=True, help="JSON with baseline and policy cases")

    p = sub.add_parser("entity", help="modeled impacts from documented entity exposure")
    p.add_argument("--params", default=DEFAULT_PARAMS_DIR)
    p.add_argument("--input", required=True, help="JSON documented exposure or warehouse row")
    p.add_argument("--input-format", choices=["exposure", "warehouse"], default="exposure")
    p.add_argument("--children", type=int, default=2)
    p.add_argument("--exposure-years", type=float, default=20.0)
    p.add_argument("--tradable-share", type=float, default=1.0)
    p.add_argument("--mortality-profile", default=None,
                   help="verified demographic mortality profile id from mortality_profiles.csv")
    p.add_argument("--mortality-mix", default=None, metavar="PROFILE:WEIGHT,...",
                   help="declared demographic mix; weights must sum to one")
    p.add_argument("--place", default=None)

    p = sub.add_parser("explain", help="walk a claim from headline to citations")
    p.add_argument("--params", default=DEFAULT_PARAMS_DIR)
    p.add_argument("--draws", type=int, default=4000)
    p.add_argument("--text", action="store_true", help="plain-language rendering")

    p = sub.add_parser("sensitivity", help="Sobol decomposition of an outcome")
    p.add_argument("--place", default=None, metavar="KEY")
    p.add_argument("--params", default=DEFAULT_PARAMS_DIR)
    p.add_argument("--outcome", default="grandchild", choices=["grandchild", "child"])
    p.add_argument("--base", type=int, default=128)
    p.add_argument("--seed", type=int, default=1901)
    p.add_argument("--ci", type=int, default=None, metavar="REPS",
                   help="report S_total with seed-replicate spread over REPS designs")
    p.add_argument("--dependent-blocks", action="store_true",
                   help="attribute declared correlated inputs as joint blocks instead of dropping their dependence")

    p = sub.add_parser("knobs", help="knob experiments (sweep a parameter / rank what is worth pinning)")
    p.add_argument("--place", default=None, metavar="KEY")
    p.add_argument("--params", default=DEFAULT_PARAMS_DIR)
    p.add_argument("--action", required=True, choices=["sweep", "voi"])
    p.add_argument("--link", default=None, help="knob link id (sweep)")
    p.add_argument("--values", default=None, help="comma-separated knob values (sweep)")
    p.add_argument("--workers", type=float, default=1000.0)
    p.add_argument("--children", type=int, default=2)
    p.add_argument("--exposure-years", type=float, default=20.0)
    p.add_argument("--outcome", default="grandchild", choices=["grandchild", "child", "excess_deaths"])
    p.add_argument("--shrink", type=float, default=0.5)
    p.add_argument("--draws", type=int, default=2000)
    p.add_argument("--seed", type=int, default=1901)

    p = sub.add_parser("simulate", help="Monte Carlo over a link chain")
    p.add_argument("--place", default=None, metavar="KEY")
    p.add_argument("--params", default=DEFAULT_PARAMS_DIR)
    target = p.add_mutually_exclusive_group(required=True)
    target.add_argument("--links", help="comma-separated link ids")
    target.add_argument("--outcome", choices=["child", "grandchild"])
    p.add_argument("--kinds", default=None, help="comma-separated: level|gap|direct per link")
    p.add_argument("--base", type=float, default=1.0)
    p.add_argument("--draws", type=int, default=10_000)
    p.add_argument("--seed", type=int, default=1901)

    p = sub.add_parser("infer", help="exact moments, log-space shares, closure coverage")
    p.add_argument("--params", default=DEFAULT_PARAMS_DIR)
    p.add_argument("--links", default=None, help="comma-separated link ids (chain analysis)")
    p.add_argument("--kinds", default=None, help="comma-separated: level|gap|direct per link")
    p.add_argument("--outcome", default=None, choices=["grandchild", "child"],
                   help="built-in child-line chains instead of --links")
    p.add_argument("--action", default="chain", choices=["chain", "shares", "closure", "agree", "stress"])
    p.add_argument("--rho", type=float, default=0.3, help="stress correlation (stress action)")
    p.add_argument("--stress-links", default=None, help="comma-separated block to correlate (stress)")
    p.add_argument("--draws", type=int, default=20000)
    p.add_argument("--trials", type=int, default=400)
    p.add_argument("--seed", type=int, default=1901)

    p = sub.add_parser("ensemble", help="structural-variant ensemble (plan #9)")
    p.add_argument("--params", default=DEFAULT_PARAMS_DIR)

    p = sub.add_parser(
        "place",
        help="place-resolved baselines + mobility modifier for one geography",
    )
    p.add_argument("--params", default=DEFAULT_PARAMS_DIR)
    p.add_argument("--key", required=True, help="places.csv key (e.g. 'national' or a FIPS)")

    p = sub.add_parser("audit", help="parameter/citation/DAG checks")
    p.add_argument("--params", default=DEFAULT_PARAMS_DIR)

    p = sub.add_parser(
        "export",
        help="version-stamped parameter_set.json snapshot (consumed by production; refuses while audit has ERRORs)",
    )
    p.add_argument("--params", default=DEFAULT_PARAMS_DIR)
    p.add_argument("--out", default=None, help="write to a file instead of stdout")

    p = sub.add_parser("validate", help="V0 internal consistency + V1 target")
    p.add_argument("--params", default=DEFAULT_PARAMS_DIR)

    p = sub.add_parser("citations", help="citation coverage report")
    p.add_argument("--params", default=DEFAULT_PARAMS_DIR)

    p = sub.add_parser("credits", help="the computed collective behind the model")
    p.add_argument("--params", default=DEFAULT_PARAMS_DIR)
    p.add_argument("--write", action="store_true", help="regenerate CREDITS.md")

    args = parser.parse_args(argv)
    parts = load_all(args.params)
    params = parts["params"]

    sampling_places = None
    if args.cmd in {"sensitivity", "knobs", "simulate"}:
        if args.place:
            from .place import load_places, place_json

            sampling_places = load_places(Path(args.params) / "places.csv")
            if not sampling_places:
                parser.error(f"places.csv absent under {args.params}")
            if args.place not in sampling_places:
                parser.error(f"unknown place {args.place!r}")
        if args.cmd == "simulate" and args.links and args.place:
            parser.error("--place requires --outcome; arbitrary link chains have no place composition")

    def sampling_child(ps):
        from .children import child_line
        from .place import modifier_parameter

        modifier = (modifier_parameter(ps, sampling_places, args.place)["parameter"]
                    if sampling_places else None)
        return child_line(ps, place_modifier=modifier)[args.outcome].point

    def dump_sampling(out):
        if sampling_places:
            out["place"] = place_json(sampling_places, parts["baselines"], args.place, params)
            out["place_uncertainty"] = (
                "Mobility gamma is recomputed on every parameter draw; place measurements "
                "and pooling weights are fixed. Multiplicative child-line composition "
                "is a declared modeling assumption."
            )
        _dump(out)

    if args.cmd == "family":
        places = None
        if args.place:
            from .place import load_places

            places = load_places(Path(args.params) / "places.csv")
            if not places:
                raise SystemExit(f"places.csv absent under {args.params} — cannot resolve --place {args.place!r}")
        _dump(standard_family(
            params, wage_multiplier=args.wage_multiplier, n_children=args.children,
            places=places, place_key=args.place,
        ))
        return 0

    if args.cmd == "synthesize":
        from .synthesis import load_study_estimates, synthesize

        out = synthesize(load_study_estimates(args.input), args.link)
        if args.compare_params:
            from .admission import compare_synthesis_to_parameter

            out["parameter_comparisons"] = [
                compare_synthesis_to_parameter(params, report, parts["nodes"])
                for report in out["reports"]
            ]
        _dump(out)
        return 0

    if args.cmd == "county-posterior":
        from .county_rates import NationalRatePrior, load_county_rates, poisson_gamma_posterior

        matches = [r for r in load_county_rates(args.input)
                   if (r.key, r.outcome, r.time_window) == (args.key, args.outcome, args.time_window)]
        if not matches:
            parser.error("no county observation matches --key, --outcome, and --time-window")
        prior = NationalRatePrior(args.outcome, args.national_rate,
                                  args.national_population_scope, args.time_window,
                                  args.national_citation)
        _dump(poisson_gamma_posterior(matches[0], prior, args.prior_person_years,
                                      draws=args.draws, seed=args.seed))
        return 0

    if args.cmd == "county-wonder-posterior":
        from .county_mortality import count_observations, parse_export
        from .county_rates import NationalRatePrior, poisson_gamma_posterior

        try:
            metadata = json.loads(Path(args.metadata).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            parser.error(f"invalid WONDER metadata JSON: {exc}")
        parsed = parse_export(args.export, metadata=metadata)
        matches = [r for r in count_observations(parsed) if r.key == args.key]
        if not matches:
            parser.error("county was absent or suppressed in the validated WONDER export")
        prior = NationalRatePrior(matches[0].outcome, args.national_rate,
                                  matches[0].population_scope, matches[0].time_window,
                                  parsed["query"].get("citation") or parsed["query"]["source_url"])
        out = poisson_gamma_posterior(matches[0], prior, args.prior_person_years,
                                      draws=args.draws, seed=args.seed)
        out["wonder_export"] = {"source_sha256": parsed["source_sha256"],
                                 "suppressed_count": parsed["suppressed_count"],
                                 "query": parsed["query"]}
        _dump(out)
        return 0

    if args.cmd == "scenario":
        places = None
        if args.place:
            from .place import load_places

            places = load_places(Path(args.params) / "places.csv")
            if not places:
                raise SystemExit(f"places.csv absent under {args.params} — cannot resolve --place {args.place!r}")
        from .scenario import sample_counts
        mortality_profiles = None
        mortality_mix = None
        if args.mortality_mix:
            try:
                mortality_mix = {item.split(":", 1)[0]: float(item.split(":", 1)[1])
                                 for item in args.mortality_mix.split(",")}
            except (IndexError, ValueError) as exc:
                parser.error(f"invalid --mortality-mix; use profile:weight,... ({exc})")
        if args.mortality_profile or mortality_mix:
            from .mortality_profiles import load_profiles
            mortality_profiles = load_profiles(Path(args.params) / "mortality_profiles.csv")
        out = sample_counts(
            params,
            parts["baselines"],
            ScenarioInput(
                displaced_workers=args.workers,
                n_children=args.children,
                tradable_share=args.tradable_share,
                net_tradable_jobs_lost=args.net_tradable_jobs_lost,
                wage_multiplier=args.wage_multiplier,
                exposure_years=args.exposure_years,
                mortality_method=args.mortality_method,
                mortality_timing=args.mortality_timing,
                mortality_profile=args.mortality_profile,
                mortality_mix=mortality_mix,
                place_application=args.place_application,
            ),
            strict=args.strict,
            places=places,
            place_key=args.place,
            mortality_profiles=mortality_profiles,
            draws=args.draws,
            seed=args.seed,
            nodes=parts["nodes"],
            params_dir=Path(args.params),
        )
        _dump(out)
        return 0

    if args.cmd == "policy":
        from .policy import PolicyCase, compare_policies
        from .place import load_places
        try:
            payload = json.loads(Path(args.input).read_text())
            before = PolicyCase.from_dict(payload["baseline"])
            after = PolicyCase.from_dict(payload["policy"])
            out = compare_policies(params, parts["baselines"], before, after,
                                   places=load_places(Path(args.params) / "places.csv"))
        except (OSError, ValueError, TypeError, KeyError) as exc:
            parser.error(str(exc))
        _dump(out)
        return 0

    if args.cmd == "entity":
        from .employer import DocumentedExposure, compute_entity_counts
        from .place import load_places

        try:
            payload = json.loads(Path(args.input).read_text())
            adapter = (DocumentedExposure.from_warehouse if args.input_format == "warehouse"
                       else DocumentedExposure)
            exposure = adapter(**payload)
        except (OSError, ValueError, TypeError) as exc:
            parser.error(str(exc))
        places = load_places(Path(args.params) / "places.csv") if args.place else None
        if args.place and (not places or args.place not in places):
            parser.error(f"cannot resolve place {args.place!r}")
        mortality_profiles = None
        mortality_mix = None
        if args.mortality_mix:
            try:
                mortality_mix = {item.split(":", 1)[0]: float(item.split(":", 1)[1])
                                 for item in args.mortality_mix.split(",")}
            except (IndexError, ValueError) as exc:
                parser.error(f"invalid --mortality-mix; use profile:weight,... ({exc})")
        if args.mortality_profile or mortality_mix:
            from .mortality_profiles import load_profiles
            mortality_profiles = load_profiles(Path(args.params) / "mortality_profiles.csv")
        try:
            result = compute_entity_counts(
                params, parts["baselines"], exposure,
                ScenarioInput(0, n_children=args.children, exposure_years=args.exposure_years,
                              tradable_share=args.tradable_share,
                              mortality_profile=args.mortality_profile,
                              mortality_mix=mortality_mix),
                places=places, place_key=args.place,
                mortality_profiles=mortality_profiles,
            )
        except (ValueError, TypeError) as exc:
            parser.error(str(exc))
        _dump(result)
        return 0

    if args.cmd == "explain":
        exp = explain_child_line(params, draws=args.draws)
        if args.text:
            load_citations(parts["bib"])
            print(render_text(exp))
        else:
            _dump(exp.as_dict())
        return 0

    if args.cmd == "sensitivity":
        outcome_fn = sampling_child
        if args.ci and args.dependent_blocks:
            parser.error("--ci is currently available for classical independent Sobol only")
        if args.dependent_blocks:
            from .params import load_correlations
            from .sensitivity import correlated_block_sobol

            dump_sampling(
                correlated_block_sobol(
                    params, outcome_fn, parts["nodes"],
                    load_correlations(Path(args.params) / "correlations.csv"),
                    base=args.base, seed=args.seed,
                )
            )
        elif args.ci:
            from .sensitivity import sobol_ci

            dump_sampling(
                sobol_ci(
                    params,
                    outcome_fn,
                    parts["nodes"],
                    base=args.base,
                    seed=args.seed,
                    replicates=args.ci,
                )
            )
        else:
            dump_sampling(
                sobol_indices(
                    params,
                    outcome_fn,
                    parts["nodes"],
                    base=args.base,
                    seed=args.seed,
                )
            )
        return 0

    if args.cmd == "knobs":
        from .knobs import sweep as knob_sweep
        from .knobs import value_of_information

        # NOTE: do NOT re-import ScenarioInput here — a function-local
        # import makes the name local to all of main(), and the
        # `scenario` branch above then dies with UnboundLocalError
        # (caught by the CLI smoke trap, 2026-09-07).
        scenario = ScenarioInput(
            displaced_workers=args.workers,
            n_children=args.children,
            exposure_years=args.exposure_years,
            label="knob-sweep",
        )
        if args.action == "sweep":
            if not args.link or not args.values:
                print("knobs sweep needs --link and --values", file=sys.stderr)
                return 2
            try:
                values = [float(v) for v in args.values.split(",")]
            except ValueError as exc:
                parser.error(f"invalid --values: {exc}")
            dump_sampling(knob_sweep(params, parts["baselines"], scenario, args.link, values, places=sampling_places, place_key=args.place))
            return 0
        # voi: rank which knob is worth narrowing next
        if args.outcome == "excess_deaths":
            def outcome_fn(ps: ParameterSet) -> float:
                out = compute_counts(ps, parts["baselines"], scenario, places=sampling_places, place_key=args.place)
                return out["modeled"]["excess_deaths"]["point"]
        else:
            outcome_fn = sampling_child
        dump_sampling(
            value_of_information(
                params,
                outcome_fn,
                parts["nodes"],
                draws=args.draws,
                seed=args.seed,
                shrink=args.shrink,
                params_dir=Path(args.params),
            )
        )
        return 0

    if args.cmd == "simulate":
        if args.outcome:
            from .mc import simulate

            if args.kinds or args.base != 1.0:
                parser.error("--kinds and --base apply only to --links")
            out = simulate(params, sampling_child, draws=args.draws, seed=args.seed,
                           nodes=parts["nodes"], params_dir=Path(args.params))
            out["outcome"] = args.outcome
            dump_sampling(out)
            return 0
        if not args.kinds:
            parser.error("--kinds is required with --links; arbitrary chains have no safe default composition")
        links = args.links.split(",")
        kinds = args.kinds.split(",")
        try:
            out = simulate_chain(
                params,
                links,
                base=args.base,
                label="chain",
                draws=args.draws,
                seed=args.seed,
                kinds=kinds,
                nodes=parts["nodes"],
            )
        except (KeyError, ValueError) as exc:
            parser.error(str(exc))
        _dump(out)
        return 0

    if args.cmd == "infer":
        from .inference import (
            analytic_chain,
            analytic_vs_mc,
            closure_coverage,
            logspace_variance_shares,
        )

        if args.outcome:
            from .children import CHILD_DIRECT, GRANDCHILD

            links = [CHILD_DIRECT, GRANDCHILD]
            kinds = ["direct", "gap"]
        else:
            if not args.links:
                print("infer needs --links or --outcome", file=sys.stderr)
                return 2
            if not args.kinds:
                print("infer --links requires --kinds; arbitrary chains have no safe default composition", file=sys.stderr)
                return 2
            links = args.links.split(",")
            kinds = args.kinds.split(",")

        from .ledger import validate_chain
        try:
            validate_chain(params, links, kinds, parts["nodes"])
        except (KeyError, ValueError) as exc:
            parser.error(str(exc))

        if args.action == "chain":
            _dump(analytic_chain(params, links, kinds, parts["nodes"]))
        elif args.action == "shares":
            _dump(logspace_variance_shares(params, links, parts["nodes"], kinds=kinds))
        elif args.action == "closure":
            def outcome_fn(ps: ParameterSet) -> float:
                from .ledger import chain as lchain

                return lchain(ps, links, label="x", unit="gap_multiplier", kinds=kinds).point

            _dump(
                closure_coverage(
                    params, outcome_fn, parts["nodes"],
                    trials=args.trials, draws=min(args.draws, 5000), seed=args.seed,
                )
            )
        elif args.action == "stress":
            from .inference import correlation_stress

            if not args.stress_links:
                print("stress needs --stress-links", file=sys.stderr)
                return 2
            block = [link for link in args.stress_links.split(",") if link]

            def outcome_fn(ps: ParameterSet) -> float:
                from .ledger import chain as lchain

                return lchain(ps, links, label="x", unit="gap_multiplier", kinds=kinds).point

            _dump(
                correlation_stress(
                    params, outcome_fn, parts["nodes"], block,
                    rho=args.rho, draws=min(args.draws, 5000),
                    trials=args.trials, seed=args.seed,
                )
            )
        else:  # agree
            def outcome_fn(ps: ParameterSet) -> float:
                from .ledger import chain as lchain

                return lchain(ps, links, label="x", unit="gap_multiplier", kinds=kinds).point

            analytic = analytic_chain(params, links, kinds, parts["nodes"])
            _dump(analytic_vs_mc(params, outcome_fn, analytic, parts["nodes"],
                                 draws=args.draws, seed=args.seed))
        return 0

    if args.cmd == "ensemble":
        from .variants import run_ensemble

        _dump(run_ensemble(params))
        return 0

    if args.cmd in {"forecast-register", "forecast-score"}:
        from .forecast_registry import register, score
        payload = json.loads(Path(args.input).read_text())
        if args.cmd == "forecast-register":
            _dump(register(args.out, payload))
        else:
            _dump(score(payload, args.measured, unit=args.unit, source=args.source))
        return 0

    if args.cmd == "bundle":
        from .bundle import export_bundle
        _dump(export_bundle(args.out, args.params))
        return 0

    if args.cmd == "export":
        if args.out:
            n = snapshot_write(args.out, args.params)
            print(f"wrote {args.out}: {n} parameters", file=sys.stderr)
        else:
            print(snapshot_dumps(args.params), end="")
        return 0

    if args.cmd == "audit":
        findings = audit(args.params)
        s = summary(findings)
        _dump({"summary": s, "findings": [f.as_dict() for f in findings]})
        return 0 if s["pass"] else 1

    if args.cmd == "validate":
        _dump(validate_run(params))
        return 0 if validate_run(params)["v0_internal_consistency"]["pass"] else 1

    if args.cmd == "place":
        from .place import load_places, place_json

        places = load_places(Path(args.params) / "places.csv")
        _dump(place_json(places, parts["baselines"], args.key, params))
        return 0

    if args.cmd == "citations":
        bib = parts["bib"]
        used: dict[str, list[str]] = {}
        for pr in params.parameters:
            for k in pr.citation_keys:
                used.setdefault(k, []).append(pr.link)
        rows = []
        for key, entry in sorted(bib.items()):
            rows.append(
                {
                    "key": key,
                    "cite": entry.cite(),
                    "title": entry.title,
                    "evidence": entry.evidence,
                    "used_by": used.get(key, []),
                }
            )
        _dump(
            {
                "bib_entries": len(bib),
                "cited": len(used),
                "uncited": sorted(set(bib) - set(used)),
                "entries": rows,
            }
        )
        return 0

    if args.cmd == "credits":
        from .credits import attribution_sentences, collect, write_credits_md
        from pathlib import Path as _P

        data = collect(parts["bib"], _P(args.params))
        if args.write:
            text = write_credits_md(data, _P(args.params).parent / "CREDITS.md")
            print(text.splitlines()[2])
            print("written: CREDITS.md")
        else:
            _dump(
                {
                    "attribution": attribution_sentences(data),
                    "studies": data["bib_entries"],
                    "researchers": len(data["researchers"]),
                }
            )
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
