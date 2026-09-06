"""Unit system for model nodes.

Units decide HOW a parameter may be applied. This is the guard that
keeps level ratios (Moretti's 5 service jobs per job) from ever being
multiplied into a gap chain — the v0 bug class the audit now rejects.
"""

from __future__ import annotations

from dataclasses import dataclass


# Node units
PERSONS = "persons"
COUNT = "count"
GAP = "gap_multiplier"        # deviation from 1.0 vs a counterfactual (1.0 = unharmed)
RATE_RATIO = "rate_ratio"     # relative rate vs counterfactual (applied to a baseline rate)
ODDS_RATIO = "odds_ratio"     # relative odds vs counterfactual
LEVEL_RATIO = "level_ratio"   # jobs per job, dollars per dollar: a LEVEL, never a chain link
PERCENT_DELTA = "percent_delta"
LOG_ELASTICITY = "log_elasticity"  # elasticity of ln(outcome); signed, samples linear
USD = "usd"
PROB = "probability"


@dataclass(frozen=True)
class Node:
    name: str
    unit: str
    description: str = ""


# How a parameter with (from_unit -> to_unit) may be applied.
#   level       : value * param            (plain multiplier on a level)
#   gap         : 1 - param*(1 - value)    (IGE / transmission gap propagation)
#   direct      : param IS the new value   (a directly estimated gap on the outcome)
#   rate        : baseline * param         (count conversion at the boundary)
#   level_ratio : n * param                (count conversion, additive in n)
#   elasticity  : pct_delta = param * pct_input
COMPOSITION = {
    (PERSONS, GAP): "level",             # displacement -> worker_earnings (JLS band)
    (GAP, RATE_RATIO): "rate",           # earnings shock -> mortality
    (PERSONS, RATE_RATIO): "rate",       # displacement -> divorce hazard
    (RATE_RATIO, GAP): "direct",         # divorce -> child_earnings (parallel stream)
    (COUNT, GAP): "direct",              # family_size -> child_earnings (parallel stream)
    (PERSONS, GAP): "level",             # direct displacement -> child_earnings
    (GAP, GAP): "gap",                   # IGE links (child -> grandchild -> great-grandchild)
    (RATE_RATIO, ODDS_RATIO): "direct",  # ipv -> daughter odds (dangling upstream)
    (PERSONS, LEVEL_RATIO): "level_ratio",
    (GAP, GAP): "gap",
    (GAP, PERCENT_DELTA): "elasticity",
    (GAP, LOG_ELASTICITY): "elasticity",  # wage_ratio -> ln(IPV) elasticity (aizer2010)
}


def composition_for(from_unit: str, to_unit: str) -> str | None:
    return COMPOSITION.get((from_unit, to_unit))
