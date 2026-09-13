"""Family-stream outcomes: divorce, IPV transmission, family size.

Parallel streams are reported SIDE BY SIDE with the displacement path.
They are never silently composed into the child-earnings line —
The structural ensemble offers a separate, explicitly assumed additive view.
"""

from __future__ import annotations

from .ledger import DIRECT, LEVEL, Ledger, start
from .params import ParameterSet

DIVORCE = "displacement->divorce_hazard"
FAMILY_SIZE = "family_size->child_earnings"
IPV_DAUGHTER = "ipv_exposure->daughter_violence_odds"


def divorce_hazard(params: ParameterSet) -> Ledger:
    """Relative divorce hazard after displacement (rate ratio)."""
    return start("divorce_hazard", "rate_ratio").apply(DIRECT, params.by_link(DIVORCE))


def daughter_violence_odds(params: ParameterSet) -> Ledger:
    """Adult partner-violence odds for exposed daughters.

    Upstream household_ipv incidence is NOT yet parameterized
    (Aizer 2010 extraction queued) — this outcome is structurally
    placed but not computable end to end. The scenario layer reports
    it as blocked rather than inventing a producer.
    """
    p = params.by_link(IPV_DAUGHTER)
    ledger = start("daughter_violence_odds", "odds_ratio").apply(DIRECT, p)
    return ledger


def family_size_penalty(params: ParameterSet, n_children: int) -> Ledger:
    """Per-child education/earnings penalty, applied per additional child.

    Assumption: linear in (n_children - 1) applications of the BDS
    2005 per-child row. The band compounds and widens with family size.
    """
    if n_children < 1:
        raise ValueError("n_children must be >= 1")
    ledger = start("family_size_penalty", "gap_multiplier")
    p = params.by_link(FAMILY_SIZE)
    for _ in range(n_children - 1):
        ledger = ledger.apply(LEVEL, p)
    return ledger


# NOTE: there is deliberately no "combined child gap" helper. The
# divorce and family-size rows are conditional or per-child effects on
# DIFFERENT margins than the direct displacement effect; composing them
# would need incidence weights and an additivity assumption the
# literature does not license. The vignette reports streams side by
# side; a combined view is future work with its own cited derivation.
