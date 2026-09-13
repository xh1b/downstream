"""Child and grandchild lines.

Primary path: the DIRECT Oreopoulos estimate on children of displaced
fathers. The IGE links then propagate the child gap into the
grandchild and great-grandchild gaps in GAP SPACE — never as level
products. The generational walk is driven by the transmissions
registry (one admitted parent->child relationship applied
recursively, per-step evidence support declared alongside it), not by
separately declared per-generation parameters.
"""

from __future__ import annotations

from .ledger import GAP_SCALE
from .params import Parameter, ParameterSet
from .transmissions import EARNINGS, walk

CHILD_DIRECT = "displacement->child_earnings"
GRANDCHILD = "child_earnings->grandchild_earnings"
GREATGRANDCHILD = "grandchild_earnings->greatgrandchild_earnings"


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

    # A place modifier on the child generation propagates through the
    # walk (it rewrites the ledger before the next step composes from
    # it); the legacy_repeated descendant modifiers are post-hoc and
    # deliberately do NOT propagate.
    def hook(ledger, generation: int):
        if place_modifier is not None and generation == 1:
            return ledger.apply(GAP_SCALE, place_modifier,
                                causal_role="exploratory_place_effect_modifier")
        return ledger

    walked = walk(params, EARNINGS, hook=hook)
    if place_modifier is not None and place_application == "legacy_repeated":
        for gen in ("grandchild", "greatgrandchild"):
            walked[gen] = walked[gen].apply(
                GAP_SCALE, place_modifier,
                causal_role="exploratory_place_effect_modifier")
    return {
        **walked,
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
