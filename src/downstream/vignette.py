"""The standard family: a fully cited worked vignette.

Standard family = employed father, mother, three children (ages 3, 7,
12), median county. Every number below is a modeled multiplier or rate
ratio with its citation trail. Vignette framing: probability/range for
a family of this type — NEVER a deterministic claim about a person.
"""

from __future__ import annotations

from .children import child_line
from .family import daughter_violence_odds, divorce_hazard
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
    places: dict | None = None,
    place_key: str | None = None,
) -> dict:
    from .scenario import ScenarioInput
    ScenarioInput(1, n_children=n_children, wage_multiplier=wage_multiplier)
    worker = worker_outcomes(params, wage_multiplier=wage_multiplier)
    modifier = None
    place_block: dict | None = None
    if places and place_key:
        from .place import modifier_parameter

        mp = modifier_parameter(params, places, place_key)
        modifier = mp["parameter"]
        place_block = {
            "key": place_key,
            "applied": modifier is not None,
            "reason": mp["modifier"].get("reason"),
            "mobility_percentile": mp["modifier"].get("mobility_percentile"),
            "national_percentile": mp["modifier"].get("national_percentile"),
        }
    line = child_line(params, place_modifier=modifier)

    divorce = divorce_hazard(params)
    daughter = daughter_violence_odds(params)
    # The standard family identifies a displaced tradable worker, not a job
    # class. Moretti's multipliers are class-specific (1.6 manufacturing,
    # ~5 high-tech) and the row's span crosses classes, so the community
    # stream stays visibly blocked here rather than borrowing a class.
    jobs = {
        "outcome": "local_service_jobs_lost",
        "blocked": (
            "requires a documented net tradable-job loss AND a declared job "
            "class (manufacturing or high_tech); the standard family does "
            "not identify either, and the published 1.6-5.0 span crosses "
            "job classes rather than describing uncertainty"
        ),
    }

    out = {
        "vignette": {
            "family": "standard family",
            "definition": (
                f"employed father, mother, {n_children} children"
                + (" (ages 3, 7, 12), " if n_children == DEFAULT_CHILDREN else " (ages unspecified), ")
                + 
                "median county; father displaced from a tradable job"
            ),
            "wage_multiplier": wage_multiplier,
            "n_children": n_children,
            "framing": (
                "modeled ranges for a family of this type; never a "
                "deterministic claim about a specific person"
            ),
        },
        "place": place_block,
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
            "family_size_penalty": {
                "outcome": "family_size_penalty",
                "blocked": (
                    "evidence_role=boundary: the per-extra-child row is a "
                    "family-size estimand, not a displacement consequence; "
                    "it stays outside the default displacement view"
                ),
            },
            "daughter_violence_odds": {
                **_ledger_dict(daughter),
                "blocked": (
                    "evidence_role=boundary: no admitted displacement-to-IPV "
                    "incidence edge exists (upstream household_ipv incidence "
                    "not yet parameterized; Aizer 2010 extraction queued)"
                ),
            },
        },
        "community_stream": jobs,
        "composition_notes": [
            "earnings and mortality are separate outcomes of one shock — not composed",
            "child line composes in GAP space for IGE links (1 - IGE*(1-gap))",
            "divorce stays a parallel conditional stream; the family-size "
            "and daughter-violence rows are boundary-only and visibly blocked; "
            "parallel streams are never composed silently",
            "great-grandchild layer carries the weakest-identification honesty statement",
        ],
    }
    if place_block is not None:
        out["composition_notes"].append(
            "place modifier scales the direct displacement loss in a same-place "
            "contrast — exploratory structural assumption, not an identified interaction"
        )
    return out


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
