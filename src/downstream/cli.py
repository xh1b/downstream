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
from .citations import parse_bib
from .explanation import explain_child_line
from .ledger import LEVEL
from .mc import simulate_chain
from .params import default_dir, load_all
from .render import load_citations, render_text
from .scenario import ScenarioInput, compute_counts
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

    p = sub.add_parser("scenario", help="modeled counts for a displacement exposure")
    p.add_argument("--params", default=DEFAULT_PARAMS_DIR)
    p.add_argument("--workers", type=float, required=True)
    p.add_argument("--children", type=int, default=2)
    p.add_argument("--tradable-share", type=float, default=1.0)
    p.add_argument("--wage-multiplier", type=float, default=None)
    p.add_argument("--exposure-years", type=float, default=20.0)
    p.add_argument("--strict", action="store_true", help="fail on missing baselines")

    p = sub.add_parser("explain", help="walk a claim from headline to citations")
    p.add_argument("--params", default=DEFAULT_PARAMS_DIR)
    p.add_argument("--draws", type=int, default=4000)
    p.add_argument("--text", action="store_true", help="plain-language rendering")

    p = sub.add_parser("sensitivity", help="Sobol decomposition of an outcome")
    p.add_argument("--params", default=DEFAULT_PARAMS_DIR)
    p.add_argument("--outcome", default="grandchild", choices=["grandchild", "child"])
    p.add_argument("--base", type=int, default=128)
    p.add_argument("--seed", type=int, default=1901)

    p = sub.add_parser("simulate", help="Monte Carlo over a link chain")
    p.add_argument("--params", default=DEFAULT_PARAMS_DIR)
    p.add_argument("--links", required=True, help="comma-separated link ids")
    p.add_argument("--kinds", default=None, help="comma-separated: level|gap|direct per link")
    p.add_argument("--base", type=float, default=1.0)
    p.add_argument("--draws", type=int, default=10_000)
    p.add_argument("--seed", type=int, default=1901)

    p = sub.add_parser("audit", help="parameter/citation/DAG checks")
    p.add_argument("--params", default=DEFAULT_PARAMS_DIR)

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

    if args.cmd == "family":
        _dump(standard_family(params, wage_multiplier=args.wage_multiplier, n_children=args.children))
        return 0

    if args.cmd == "scenario":
        out = compute_counts(
            params,
            parts["baselines"],
            ScenarioInput(
                displaced_workers=args.workers,
                n_children=args.children,
                tradable_share=args.tradable_share,
                wage_multiplier=args.wage_multiplier,
                exposure_years=args.exposure_years,
            ),
            strict=args.strict,
        )
        _dump(out)
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
        from .children import child_line

        outcome_fn = {
            "grandchild": lambda ps: child_line(ps)["grandchild"].point,
            "child": lambda ps: child_line(ps)["child"].point,
        }[args.outcome]
        _dump(
            sobol_indices(
                params,
                outcome_fn,
                parts["nodes"],
                base=args.base,
                seed=args.seed,
            )
        )
        return 0

    if args.cmd == "simulate":
        links = args.links.split(",")
        kinds = args.kinds.split(",") if args.kinds else [LEVEL] * len(links)
        out = simulate_chain(
            params,
            links,
            base=args.base,
            label="chain",
            draws=args.draws,
            seed=args.seed,
            kinds=kinds,
        )
        _dump(out)
        return 0

    if args.cmd == "audit":
        findings = audit(args.params)
        s = summary(findings)
        _dump({"summary": s, "findings": [f.as_dict() for f in findings]})
        return 0 if s["pass"] else 1

    if args.cmd == "validate":
        _dump(validate_run(params))
        return 0 if validate_run(params)["v0_internal_consistency"]["pass"] else 1

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
