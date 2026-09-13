"""Deterministic ledger computation with explicit composition semantics.

A Ledger tracks ONE quantity through its cited steps. Composition is
per-step and typed:

  level        value * param            — plain multiplier on a level
  gap          1 - param * (1 - value)  — transmission gap propagation (IGE)
  gap_log_elastic  value ** param       — finite-change mapping for a constant
                                          log elasticity; the shipped gap rule
                                          is its first-order Taylor expansion
                                          at value=1. Declared ensemble
                                          alternate ONLY (variants), never a
                                          chain-invitable default.
  direct       param IS the new value   — directly estimated effect on this outcome
  rate         recorded only            — rate ratio, applied to a baseline at the
                                          count boundary (never chained)

Every step records its citation. Ranges propagate so the published band
always brackets the point. Bands widen, never shrink.
"""

from __future__ import annotations

from dataclasses import dataclass

from .params import Parameter

LEVEL = "level"
GAP = "gap"
GAP_LOG = "gap_log_elastic"
GAP_SCALE = "gap_scale"
LINEAR_SHIFT = "linear_shift"
DIRECT = "direct"
RATE = "rate"


@dataclass(frozen=True)
class Step:
    link: str
    kind: str
    citation: str
    tier: str
    param: tuple[float, float, float]  # point, low, high
    value: tuple[float, float, float]  # point, low, high AFTER the step
    causal_role: str = "unspecified"
    population_scope: str = ""  # studied population of the source estimate
    evidence_role: str = ""  # applicability role (admitted/conditional/structural/boundary)

    def as_dict(self) -> dict:
        return {
            "link": self.link,
            "kind": self.kind,
            "citation": self.citation,
            "tier": self.tier,
            "param_point": self.param[0],
            "param_low": self.param[1],
            "param_high": self.param[2],
            "value_point": self.value[0],
            "value_low": self.value[1],
            "value_high": self.value[2],
            "causal_role": self.causal_role,
            "population_scope": self.population_scope,
            "evidence_role": self.evidence_role,
        }


@dataclass(frozen=True)
class Ledger:
    """A value with its full audit trail."""

    label: str
    unit: str
    point: float
    low: float
    high: float
    steps: tuple[Step, ...]

    def _step(self, kind: str, p: Parameter, causal_role: str = "unspecified") -> Step:
        if kind == LEVEL:
            corners = [x * y for x in (self.low, self.high) for y in (p.low, p.high)]
            v = (self.point * p.point, min(corners), max(corners))
        elif kind == GAP:
            corners = [1 - t * (1 - x) for x in (self.low, self.high) for t in (p.low, p.high)]
            v = (1 - p.point * (1 - self.point), min(corners), max(corners))
        elif kind == GAP_LOG:
            # Finite-change mapping for a constant log elasticity: the
            # incoming multiplier raised to the transmission power. The
            # shipped GAP rule is this map's first-order Taylor expansion
            # at value=1; for 0 <= value <= 1 and 0 <= t <= 1 it retains
            # no more than GAP (equality at 0 and 1). Neither expression
            # identifies an intervention response, so this kind exists
            # for the declared ensemble alternate (variants.py) with the
            # same structural_transmission_assumption causal role — it is
            # deliberately absent from CHAIN_KINDS.
            if min(self.point, self.low, self.high) < 0 or min(p.point, p.low, p.high) < 0:
                raise ValueError(
                    "gap_log_elastic composition needs a non-negative incoming "
                    "value and transmission band; a fractional power of a "
                    "negative base is undefined here"
                )
            corners = [x ** t for x in (self.low, self.high) for t in (p.low, p.high)]
            v = (self.point ** p.point, min(corners), max(corners))
        elif kind == GAP_SCALE:
            # A same-place contrast can scale the *loss* from a direct
            # displacement effect while leaving a null displacement effect
            # at its counterfactual value.  This is deliberately distinct
            # from GAP: it is not an intergenerational transmission claim.
            corners = [1 - m * (1 - x) for x in (self.low, self.high)
                       for m in (p.low, p.high)]
            v = (1 - p.point * (1 - self.point), min(corners), max(corners))
        elif kind == LINEAR_SHIFT:
            # Standardized-shift transmission: the child outcome moves a
            # constant slope times the parent shift, both in the same
            # additive scale (sd_delta). A correlation between standardized
            # outcomes is exactly this slope. Like GAP it is a structural
            # transmission assumption — the shipped correlation estimates
            # carry their authors' own no-causal-interpretation caveats —
            # not an identified intervention response.
            corners = [t * x for x in (self.low, self.high) for t in (p.low, p.high)]
            v = (p.point * self.point, min(corners), max(corners))
        elif kind == DIRECT:
            v = (p.point, p.low, p.high)
        elif kind == RATE:
            # A rate ratio REPLACES the tracked value (it applies to a
            # baseline at the boundary); recorded, never chained.
            v = (p.point, p.low, p.high)
        else:
            raise ValueError(f"unknown composition kind {kind!r}")
        return Step(
            link=p.link,
            kind=kind,
            citation=p.citation,
            tier=p.tier,
            param=(p.point, p.low, p.high),
            value=v,
            causal_role=causal_role,
            population_scope=p.population_scope,
            evidence_role=p.evidence_role,
        )

    def apply(self, kind: str, param: Parameter, label: str = "", causal_role: str = "unspecified") -> "Ledger":
        step = self._step(kind, param, causal_role)
        point, low, high = step.value
        if low > high:  # bands only widen; ordering is an invariant
            low, high = high, low
        return Ledger(
            label=label or param.to_node,
            unit=self.unit,
            point=point,
            low=low,
            high=high,
            steps=self.steps + (step,),
        )


def start(label: str, unit: str, value: float = 1.0) -> Ledger:
    return Ledger(label=label, unit=unit, point=value, low=value, high=value, steps=())


# Only these links have a defensible in-ledger composition.  Most parameter
# rows are boundary coefficients (rates, elasticities, or counts) and must be
# applied by their named boundary adapter, not invited into an arbitrary chain.
CHAIN_KINDS = {
    "displacement->worker_earnings": DIRECT,
    "displacement->child_earnings": DIRECT,
    "child_earnings->grandchild_earnings": GAP,
    "grandchild_earnings->greatgrandchild_earnings": GAP,
    "displacement_event->child_achievement_sd": DIRECT,
    "child_achievement_sd->grandchild_achievement_sd": LINEAR_SHIFT,
    "child_education_years->grandchild_education_years": LINEAR_SHIFT,
}

# Composition has a different epistemic status from its arithmetic. These
# roles travel with public ledgers so clients cannot relabel a persistence
# coefficient as a separately identified intervention response.
CHAIN_CAUSAL_ROLES = {
    "displacement->worker_earnings": "direct_displacement_estimate",
    "displacement->child_earnings": "direct_displacement_estimate",
    "child_earnings->grandchild_earnings": "structural_transmission_assumption",
    "grandchild_earnings->greatgrandchild_earnings": "structural_transmission_assumption",
    "displacement_event->child_achievement_sd": "direct_displacement_estimate",
    "child_achievement_sd->grandchild_achievement_sd": "structural_transmission_assumption",
    "child_education_years->grandchild_education_years": "structural_transmission_assumption",
}


def validate_chain(params, links: list[str], kinds: list[str], nodes: dict) -> None:
    """Refuse links that lack an explicit, context-safe chain operation."""
    if len(links) != len(kinds):
        raise ValueError("links and kinds must be the same length")
    previous = None
    for link, kind in zip(links, kinds):
        parameter = params.by_link(link)
        if parameter.evidence_role == "boundary":
            raise ValueError(
                f"chain link {link!r} is evidence_role=boundary: it informs a "
                "separate input type and cannot start from generic worker displacement"
            )
        expected = CHAIN_KINDS.get(link)
        if expected is None:
            raise ValueError(
                f"chain link {link!r} is boundary-applied and cannot be used in an arbitrary chain"
            )
        if expected != kind:
            raise ValueError(
                f"chain link {link!r} requires {expected!r} composition from its units, not {kind!r}"
            )
        if previous is not None and previous.to_node != parameter.from_node:
            raise ValueError(
                f"disconnected chain: {previous.link!r} ends at {previous.to_node!r}, "
                f"but {link!r} starts at {parameter.from_node!r}"
            )
        previous = parameter


def chain(params, links: list[str], label: str, unit: str, kinds: list[str], nodes: dict | None = None,
          base: float = 1.0) -> Ledger:
    """Apply named links with an explicit composition kind per link."""
    if len(links) != len(kinds):
        raise ValueError("links and kinds must be the same length")
    if nodes is not None:
        validate_chain(params, links, kinds, nodes)
    ledger = start(label, unit, value=base)
    for link, kind in zip(links, kinds):
        ledger = ledger.apply(kind, params.by_link(link), label=link.split("->")[-1],
                              # Generic callers can use this arithmetic helper
                              # without claiming that their synthetic links are
                              # part of the shipped causal graph.  Production
                              # chains pass nodes and are validated above.
                              causal_role=CHAIN_CAUSAL_ROLES.get(link, "unspecified"))
    return ledger


def combine_parallel(gaps: list[Ledger], label: str) -> Ledger:
    """Combine independent causes of one gap outcome.

    ASSUMPTION (declared, not derived): independent causes add in gap
    space, floored at zero. Never use this silently — the vignette
    reports parallel streams side by side by default.
    """
    point_gap = sum(1 - g.point for g in gaps)
    low_gap = sum(1 - g.low for g in gaps)
    high_gap = sum(1 - g.high for g in gaps)
    steps: tuple[Step, ...] = ()
    for g in gaps:
        steps += g.steps
    floor = 0.0

    def clamp(v: float) -> float:
        return max(floor, 1 - v)

    return Ledger(
        label=label,
        unit=gaps[0].unit if gaps else "gap_multiplier",
        point=clamp(point_gap),
        low=clamp(low_gap),
        high=clamp(high_gap),
        steps=steps,
    )
