"""Child and grandchild lines.

Primary path: the DIRECT Oreopoulos estimate on children of displaced
fathers. The IGE links then propagate the child gap into the
grandchild and great-grandchild gaps in GAP SPACE — never as level
products. A great-grandchild layer repeats the IGE band and carries the
weakest-identification honesty statement.
"""

from __future__ import annotations

from .ledger import CHAIN_CAUSAL_ROLES, DIRECT, GAP, GAP_SCALE, Ledger, start
from .params import Parameter, ParameterSet

CHILD_DIRECT = "displacement->child_earnings"
GRANDCHILD = "child_earnings->grandchild_earnings"
GREATGRANDCHILD = "grandchild_earnings->greatgrandchild_earnings"


def child_earnings(params: ParameterSet) -> Ledger:
    return start("child_earnings", "gap_multiplier").apply(
        DIRECT, params.by_link(CHILD_DIRECT), causal_role=CHAIN_CAUSAL_ROLES[CHILD_DIRECT]
    )


def grandchild_earnings(child: Ledger, params: ParameterSet) -> Ledger:
    return child.apply(GAP, params.by_link(GRANDCHILD), causal_role=CHAIN_CAUSAL_ROLES[GRANDCHILD])


def greatgrandchild_earnings(grandchild: Ledger, params: ParameterSet) -> Ledger:
    return grandchild.apply(GAP, params.by_link(GREATGRANDCHILD), causal_role=CHAIN_CAUSAL_ROLES[GREATGRANDCHILD])


def child_line(params: ParameterSet, place_modifier: Parameter | None = None,
               place_application: str = "initial_only") -> dict:
    """The full three-generation line with the honest-weakness marker.

    place_modifier (optional): the place-resolved Chetty-Hendren
    mobility loss modifier (built by place.modifier_parameter). It scales
    the direct displacement *loss* in a same-place contrast: ``1-M(1-g)``.
    Thus a null displacement effect (g=1) stays null at every place. This
    is exploratory structural bridging, not an identified interaction.
    legacy_repeated reproduces the old extra descendant modifiers. None = the national
    median-county baseline (multiplier 1.0), the shipped framing.
    """
    if place_application not in {"initial_only", "legacy_repeated"}:
        raise ValueError("unknown place_application")
    child = child_earnings(params)
    if place_modifier is not None:
        child = child.apply(GAP_SCALE, place_modifier, causal_role="exploratory_place_effect_modifier")
    grandchild = grandchild_earnings(child, params)
    greatgrandchild = greatgrandchild_earnings(grandchild, params)
    if place_modifier is not None and place_application == "legacy_repeated":
        grandchild = grandchild.apply(GAP_SCALE, place_modifier, causal_role="exploratory_place_effect_modifier")
        greatgrandchild = greatgrandchild.apply(GAP_SCALE, place_modifier, causal_role="exploratory_place_effect_modifier")
    return {
        "child": child,
        "grandchild": grandchild,
        "greatgrandchild": greatgrandchild,
        "evidence_status": {
            "child": {
                "status": "direct_estimate",
                "eligible_for_validated_direct_contrast": True,
                "reason": "direct displacement-to-child adult earnings estimate; transport still requires an applicability decision",
            },
            "grandchild": {
                "status": "structural_projection",
                "eligible_for_validated_direct_contrast": False,
                "reason": "combines a direct child estimate with an intergenerational persistence assumption; not an identified displacement intervention effect",
            },
            "greatgrandchild": {
                "status": "structural_projection",
                "eligible_for_validated_direct_contrast": False,
                "reason": "repeats an intergenerational persistence assumption beyond the identification core",
            },
        },
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
