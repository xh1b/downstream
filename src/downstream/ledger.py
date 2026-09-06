"""Deterministic ledger computation with explicit composition semantics.

A Ledger tracks ONE quantity through its cited steps. Composition is
per-step and typed:

  level        value * param            — plain multiplier on a level
  gap          1 - param * (1 - value)  — transmission gap propagation (IGE)
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

    def _step(self, kind: str, p: Parameter) -> Step:
        if kind == LEVEL:
            v = (self.point * p.point, self.low * p.low, self.high * p.high)
        elif kind == GAP:
            v = (
                1 - p.point * (1 - self.point),
                1 - p.high * (1 - self.low),
                1 - p.low * (1 - self.high),
            )
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
        )

    def apply(self, kind: str, param: Parameter, label: str = "") -> "Ledger":
        step = self._step(kind, param)
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


def chain(params, links: list[str], label: str, unit: str, kinds: list[str]) -> Ledger:
    """Apply named links with an explicit composition kind per link."""
    if len(links) != len(kinds):
        raise ValueError("links and kinds must be the same length")
    ledger = start(label, unit)
    for link, kind in zip(links, kinds):
        ledger = ledger.apply(kind, params.by_link(link), label=link.split("->")[-1])
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
