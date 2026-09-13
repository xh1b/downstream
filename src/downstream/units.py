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
SD_DELTA = "sd_delta"          # change in standard-deviation units (achievement scales)
LIFE_YEARS = "life_years"      # life-expectancy change in years
LOG_ELASTICITY = "log_elasticity"  # elasticity of ln(outcome); signed, samples linear
USD = "usd"
PROB = "probability"
PERCENTILE = "percentile"      # a rank in 0-100 (Chetty-Hendren kfr scale)
EDU_YEARS = "edu_years"        # additional years of educational attainment (akee2010)
PERCENT = "percent"            # a LEVEL share expressed in percentage points (damm2014)
SCALE01 = "scale01"            # a 0-1 symptom index (CESD), NOT a probability


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
    (GAP, ODDS_RATIO): "rate",           # mortality odds, recorded before risk conversion
    (GAP, RATE_RATIO): "rate",           # earnings shock -> mortality
    (PERSONS, RATE_RATIO): "rate",       # displacement -> divorce hazard
    (RATE_RATIO, GAP): "direct",         # divorce -> child_earnings (parallel stream)
    (COUNT, GAP): "direct",              # family_size -> child_earnings (parallel stream)
    (GAP, GAP): "gap",                   # IGE links (child -> grandchild -> great-grandchild)
    (SD_DELTA, SD_DELTA): "sd_linear",   # standardized-shift transmission walk
                                         # (parent achievement -> grandchild achievement);
                                         # structural assumption, carried caveats on the row
    (RATE_RATIO, ODDS_RATIO): "direct",  # ipv -> daughter odds (dangling upstream)
    (PERSONS, LEVEL_RATIO): "level_ratio",
    (GAP, PERCENT_DELTA): "elasticity",
    (GAP, LOG_ELASTICITY): "elasticity",  # wage_ratio -> ln(IPV) elasticity (aizer2010)
    # Boundary-applied COEFFICIENTS: per-unit responses estimated on an
    # external shock ($1k). They apply to a baseline at the count
    # boundary (like "rate") and must NEVER be chained — the response
    # size depends on the shock magnitude, which is not carried by a
    # chain step.
    (USD, PERCENT_DELTA): "rate",   # import_shock -> local wage spillover (adh2013)
    (USD, SD_DELTA): "rate",        # family income -> child achievement (dahl2012)
    (RATE_RATIO, SD_DELTA): "rate", # IPV exposure -> child SD outcomes (evans2008) - boundary
                                    # coefficient like dahl2012: the d contrast is per exposed-vs-not,
                                    # never chained
    (PERSONS, SD_DELTA): "rate",    # displacement -> spouse mental health (marcus2013) - boundary
                                    # exposure contrast like evans2008: the SD delta is per
                                    # exposed-vs-not, never chained
    (USD, LIFE_YEARS): "rate",      # family income -> life expectancy (chetty2016)
    (PERCENT_DELTA, PERCENT_DELTA): "rate",  # unemployment pp -> property crime % (raphael2001)
    (RATE_RATIO, RATE_RATIO): "rate",  # unemployment shock -> IPV incidence (schneider2016) - boundary
                                       # coefficient: multiplier per unit of the shock (doubling = 2.0),
                                       # never chained
    (USD, USD): "rate",             # EITC $1k exposure -> adult annual earnings (bastian2018)
    (PERCENTILE, GAP): "level",     # neighborhood exposure -> child-outcomes modifier
                                    # (place multiplier 1 + dose*gamma*gap/100; boundary
                                    # coefficient like the others: applies a county gap
                                    # vs the national row, never chained from a node level)
    (USD, EDU_YEARS): "rate",       # unconditional income -> education years (akee2010) -
                                    # per-treatment boundary coefficient: the paper's dose is
                                    # four years of ~$4k/y transfer, never a per-dollar chain
    (USD, PROB): "rate",            # unconditional income -> crime entry (akee2010) - the
                                    # probit marginal effects are exposure contrasts, boundary
                                    # applied like the rest
    (PERCENT, PROB): "rate",        # area youth conviction share -> child conviction prob
                                    # (damm2014) - per-1pp boundary coefficient: each 1pp of
                                    # the area share adds the row's probability points; the
                                    # share is a LEVEL, never chained from a crime-count delta
    (PERSONS, PROB): "rate",        # maternal displacement -> child education probabilities
                                    # (brand2014) - LEVEL exposure contrasts from PSM TT
                                    # matching, boundary applied like akee2010/damm2014,
                                    # never chained
    (PERSONS, SCALE01): "rate",     # maternal displacement -> young-adult CESD index
                                    # (brand2014) - LEVEL exposure contrast on the 0-1
                                    # symptom scale, boundary applied, never chained
    (PERSONS, LOG_ELASTICITY): "rate",  # husband displacement -> wife participation
                                    # elasticity (halla2020) - the AWE elasticity is
                                    # defined w.r.t. the husband's 5-year earnings loss
                                    # (-21..-24%); boundary coefficient, never chained
}


def composition_for(from_unit: str, to_unit: str) -> str | None:
    return COMPOSITION.get((from_unit, to_unit))
