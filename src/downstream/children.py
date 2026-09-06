"""Child and grandchild lines.

Primary path: the DIRECT Oreopoulos estimate on children of displaced
fathers. The IGE links then propagate the child gap into the
grandchild and great-grandchild gaps in GAP SPACE — never as level
products. A great-grandchild layer repeats the IGE band and carries the
weakest-identification honesty statement.
"""

from __future__ import annotations

from .ledger import DIRECT, GAP, Ledger, start
from .params import ParameterSet

CHILD_DIRECT = "displacement->child_earnings"
GRANDCHILD = "child_earnings->grandchild_earnings"
GREATGRANDCHILD = "grandchild_earnings->greatgrandchild_earnings"


def child_earnings(params: ParameterSet) -> Ledger:
    return start("child_earnings", "gap_multiplier").apply(DIRECT, params.by_link(CHILD_DIRECT))


def grandchild_earnings(child: Ledger, params: ParameterSet) -> Ledger:
    return child.apply(GAP, params.by_link(GRANDCHILD))


def greatgrandchild_earnings(grandchild: Ledger, params: ParameterSet) -> Ledger:
    return grandchild.apply(GAP, params.by_link(GREATGRANDCHILD))


def child_line(params: ParameterSet) -> dict:
    """The full three-generation line with the honest-weakness marker."""
    child = child_earnings(params)
    grandchild = grandchild_earnings(child, params)
    greatgrandchild = greatgrandchild_earnings(grandchild, params)
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
