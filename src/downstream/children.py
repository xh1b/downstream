"""Child and grandchild lines.

Primary path: the DIRECT Oreopoulos estimate on children of displaced
fathers. The IGE links then propagate the child gap into the
grandchild and great-grandchild gaps in GAP SPACE — never as level
products. A great-grandchild layer repeats the IGE band and carries the
weakest-identification honesty statement.
"""

from __future__ import annotations

from .ledger import DIRECT, GAP, LEVEL, Ledger, start
from .params import Parameter, ParameterSet

CHILD_DIRECT = "displacement->child_earnings"
GRANDCHILD = "child_earnings->grandchild_earnings"
GREATGRANDCHILD = "grandchild_earnings->greatgrandchild_earnings"


def child_earnings(params: ParameterSet) -> Ledger:
    return start("child_earnings", "gap_multiplier").apply(DIRECT, params.by_link(CHILD_DIRECT))


def grandchild_earnings(child: Ledger, params: ParameterSet) -> Ledger:
    return child.apply(GAP, params.by_link(GRANDCHILD))


def greatgrandchild_earnings(grandchild: Ledger, params: ParameterSet) -> Ledger:
    return grandchild.apply(GAP, params.by_link(GREATGRANDCHILD))


def child_line(params: ParameterSet, place_modifier: Parameter | None = None,
               place_application: str = "initial_only") -> dict:
    """The full three-generation line with the honest-weakness marker.

    place_modifier (optional): the place-resolved Chetty-Hendren
    mobility multiplier (built by place.modifier_parameter). It composes
    MULTIPLICATIVELY with the chain — a declared modeling assumption,
    applied once to the initial child, then transmitted in gap space.
    legacy_repeated reproduces the old extra descendant modifiers. None = the national
    median-county baseline (multiplier 1.0), the shipped framing.
    """
    if place_application not in {"initial_only", "legacy_repeated"}:
        raise ValueError("unknown place_application")
    child = child_earnings(params)
    if place_modifier is not None:
        child = child.apply(LEVEL, place_modifier)
    grandchild = grandchild_earnings(child, params)
    greatgrandchild = greatgrandchild_earnings(grandchild, params)
    if place_modifier is not None and place_application == "legacy_repeated":
        grandchild = grandchild.apply(LEVEL, place_modifier)
        greatgrandchild = greatgrandchild.apply(LEVEL, place_modifier)
    return {
        "child": child,
        "grandchild": grandchild,
        "greatgrandchild": greatgrandchild,
        "weakest_identified": "greatgrandchild",
        "honesty": (
            "The great-grandchild layer is the weakest-identified layer "
            "in this model: it repeats the IGE band beyond the "
            "literature's identification core. Lindahl et al. 2015 shows "
            "persistence survives conditioning on the middle generation, "
            "so the effect is non-zero — but its size is the least "
            "certain number here."
        ),
    }
