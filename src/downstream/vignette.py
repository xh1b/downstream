"""The standard family: a fully cited worked vignette.

Standard family = employed father, mother, three children (ages 3, 7,
12), median county. Every number below is a modeled multiplier or rate
ratio with its citation trail. Vignette framing: probability/range for
a family of this type — NEVER a deterministic claim about a person.
"""

from __future__ import annotations

from .children import child_line
from .community import service_jobs_lost
from .family import daughter_violence_odds, divorce_hazard, family_size_penalty
from .params import ParameterSet
from .worker import worker_outcomes

DEFAULT_CHILDREN = 3


def _ledger_dict(ledger) -> dict:
    return {
        "label": ledger.label,
        "unit": ledger.unit,
        "point": round(ledger.point, 4),
        "low": round(ledger.low, 4),
        "high": round(ledger.high, 4),
        "steps": [s.as_dict() for s in ledger.steps],
    }


def standard_family(
    params: ParameterSet,
    wage_multiplier: float = 0.80,
    n_children: int = DEFAULT_CHILDREN,
) -> dict:
    worker = worker_outcomes(params, wage_multiplier=wage_multiplier)
    line = child_line(params)

    divorce = divorce_hazard(params)
    fam_penalty = family_size_penalty(params, n_children)
    daughter = daughter_violence_odds(params)
    jobs = service_jobs_lost(params, displaced_tradable=1)

    return {
        "vignette": {
            "family": "standard family",
            "definition": (
                "employed father, mother, three children (ages 3, 7, 12), "
                "median county; father displaced from a tradable job"
            ),
            "wage_multiplier": wage_multiplier,
            "n_children": n_children,
            "framing": (
                "modeled ranges for a family of this type; never a "
                "deterministic claim about a specific person"
            ),
        },
        "parameter_set_version": params.version,
        "worker_stream": {
            "earnings": _ledger_dict(worker["worker_earnings"]),
            "mortality_sustained": _ledger_dict(worker["mortality_sustained"]),
            "mortality_peak": _ledger_dict(worker["mortality_peak"]),
        },
        "children_stream": {
            "child": _ledger_dict(line["child"]),
            "grandchild": _ledger_dict(line["grandchild"]),
            "greatgrandchild": _ledger_dict(line["greatgrandchild"]),
            "weakest_identified": line["weakest_identified"],
            "honesty": line["honesty"],
        },
        "family_stream": {
            "divorce_hazard": _ledger_dict(divorce),
            "family_size_penalty": _ledger_dict(fam_penalty),
            "daughter_violence_odds": {
                **_ledger_dict(daughter),
                "blocked": (
                    "upstream household_ipv incidence not yet parameterized "
                    "(Aizer 2010 extraction queued)"
                ),
            },
        },
        "community_stream": jobs,
        "composition_notes": [
            "earnings and mortality are separate outcomes of one shock — not composed",
            "child line composes in GAP space for IGE links (1 - IGE*(1-gap))",
            "divorce and family-size streams reported side by side; "
            "parallel streams are never composed silently",
            "great-grandchild layer carries the weakest-identification honesty statement",
        ],
    }


# Back-compat wrapper for the original v0 surface.
def standard_family_daughter(params: ParameterSet, wage_multiplier: float = 0.80) -> dict:
    out = standard_family(params, wage_multiplier=wage_multiplier)
    gc = out["children_stream"]["grandchild"]
    return {
        "daughter_line_earnings_multiplier": {
            "point": gc["point"],
            "low": gc["low"],
            "high": gc["high"],
        },
        "steps": gc["steps"],
    }
