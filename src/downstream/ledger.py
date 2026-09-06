"""Deterministic downstream ledger computation.

Auditable by construction: every step applies exactly one cited
parameter and records the citation alongside the result. Ranges
propagate multiplicatively from parameter low/high — a canonical-tier
parameter can only widen a band, never narrow it.
"""

from __future__ import annotations

from dataclasses import dataclass

from .params import Parameter, ParameterSet


@dataclass(frozen=True)
class Step:
    link: str
    citation: str
    tier: str
    point: float
    low: float
    high: float

    def as_dict(self) -> dict:
        return {
            "link": self.link,
            "citation": self.citation,
            "tier": self.tier,
            "point": self.point,
            "low": self.low,
            "high": self.high,
        }


@dataclass(frozen=True)
class Ledger:
    """A value with its full audit trail."""

    label: str
    point: float
    low: float
    high: float
    steps: tuple[Step, ...]

    def apply(self, param: Parameter, label: str = "") -> "Ledger":
        return Ledger(
            label=label or param.to_node,
            point=self.point * param.point,
            low=self.low * param.low,
            high=self.high * param.high,
            steps=self.steps
            + (
                Step(
                    link=param.link,
                    citation=param.citation,
                    tier=param.tier,
                    point=param.point,
                    low=param.low,
                    high=param.high,
                ),
            ),
        )


def chain(
    params: ParameterSet,
    links: list[str],
    base: float,
    label: str,
) -> Ledger:
    """Apply a named chain of parameters to a base value."""
    ledger = Ledger(label=label, point=base, low=base, high=base, steps=())
    for link in links:
        ledger = ledger.apply(params.by_link(link), label=link.split("->")[-1])
    return ledger


def standard_family_daughter(
    params: ParameterSet,
    wage_multiplier: float = 0.80,
) -> dict:
    """Worked example: the standard family (2 parents, 3 children).

    Returns the daughter's modeled adult-earnings multiplier with the
    full citation trail. Vignette framing: probability/range, never a
    deterministic person claim.
    """
    daughter = chain(
        params,
        links=[
            "displacement->earnings",
            "children_earnings->adult_earnings",
            "child_adult_earnings->grandchild_earnings",
        ],
        base=wage_multiplier,
        label="grandchild_earnings",
    )
    return {
        "daughter_line_earnings_multiplier": {
            "point": round(daughter.point, 3),
            "low": round(daughter.low, 3),
            "high": round(daughter.high, 3),
        },
        "steps": [s.as_dict() for s in daughter.steps],
    }
