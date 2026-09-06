"""downstream CLI.

    downstream family --params params/parameters.csv
    downstream compute --links displacement->earnings --base 1.0
"""

from __future__ import annotations

import argparse
import json
import sys

from .ledger import standard_family_daughter
from .mc import simulate_chain
from .params import load


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="downstream")
    sub = parser.add_subparsers(dest="cmd", required=True)

    family = sub.add_parser("family", help="standard-family vignette")
    family.add_argument("--params", default="params/parameters.csv")
    family.add_argument("--wage-multiplier", type=float, default=0.80)

    sim = sub.add_parser("simulate", help="Monte Carlo over a chain")
    sim.add_argument("--params", default="params/parameters.csv")
    sim.add_argument("--links", required=True)
    sim.add_argument("--base", type=float, default=1.0)
    sim.add_argument("--draws", type=int, default=10_000)

    args = parser.parse_args(argv)
    if args.cmd == "family":
        params = load(args.params)
        out = standard_family_daughter(params, wage_multiplier=args.wage_multiplier)
        json.dump(out, sys.stdout, indent=2)
        print()
        return 0
    if args.cmd == "simulate":
        params = load(args.params)
        links = args.links.split(",")
        out = simulate_chain(params, links, base=args.base, label="chain", draws=args.draws)
        json.dump(out, sys.stdout, indent=2)
        print()
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
