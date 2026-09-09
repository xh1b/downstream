"""The explanation object: a computed claim with its full derivation.

This is the contract between the model and every surface that renders
it (CLI today, web later). It exists so that no renderer ever has to
re-derive WHY a number is what it is — the why travels WITH the
number, structured:

  claim     the headline, always with a band and a population
  steps     the cited chain that produced it, with contribution shares
  drivers   which parameters dominate the REMAINING uncertainty (Sobol)
  blocked   outcomes we refused to compute, and the exact missing input
  falsify   what evidence would confirm or break the claim

Hard rules (enforced by tests and by render.py):
- no naked point estimates: every number ships with its band
- every step carries at least one citation key
- blocked items always name the fix
- claims say "modeled" — the model's output is never passed off as
  a measurement
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .children import child_line
from .params import ParameterSet


@dataclass
class Step:
    label: str
    sentence: str
    params: tuple[float, float, float]   # point, low, high as applied
    before: tuple[float, float, float]
    after: tuple[float, float, float]
    citations: list[str]
    tier: str
    population: str
    contribution: float                  # share of total log-effect

    def as_dict(self) -> dict:
        return {
            "label": self.label,
            "sentence": self.sentence,
            "param": _r3(self.params),
            "before": _r3(self.before),
            "after": _r3(self.after),
            "citations": self.citations,
            "tier": self.tier,
            "population": self.population,
            "contribution_share": round(self.contribution, 3),
        }


@dataclass
class Explanation:
    claim: str
    outcome: str
    unit: str
    value: tuple[float, float, float]    # point, low, high
    horizon: str
    population: str
    steps: list[Step] = field(default_factory=list)
    drivers: list[dict] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    blocked: list[dict] = field(default_factory=list)
    falsify: list[str] = field(default_factory=list)
    parameter_set_version: str = ""
    monte_carlo: dict | None = None

    def as_dict(self) -> dict:
        return {
            "claim": self.claim,
            "outcome": self.outcome,
            "unit": self.unit,
            "value": _r3(self.value),
            "horizon": self.horizon,
            "population": self.population,
            "steps": [s.as_dict() for s in self.steps],
            "drivers": self.drivers,
            "assumptions": self.assumptions,
            "blocked": self.blocked,
            "falsify": self.falsify,
            "parameter_set_version": self.parameter_set_version,
            "monte_carlo": self.monte_carlo,
        }


def explain_child_line(params: ParameterSet, draws: int = 4000, seed: int = 1901) -> Explanation:
    """Worked explanation: what happens to the earnings line of a
    displaced father's family, three generations out."""
    from .mc import simulate

    child = child_line(params)

    steps: list[Step] = []
    prev = (1.0, 1.0, 1.0)
    contributions: list[float] = []
    for ledger, readable in (
        (child["child"], "the child's adult earnings"),
        (child["grandchild"], "the grandchild's adult earnings"),
        (child["greatgrandchild"], "the great-grandchild's adult earnings"),
    ):
        s = ledger.steps[-1]
        effect = math.log(max(ledger.point, 1e-9)) - math.log(max(prev[0], 1e-9))
        contributions.append(effect)
        steps.append(
            Step(
                label=s.link,
                sentence=_step_sentence(s.link, prev[0], ledger.point),
                params=(s.param[0], s.param[1], s.param[2]),
                before=prev,
                after=(ledger.point, ledger.low, ledger.high),
                citations=s.citation.split(";"),
                tier=s.tier,
                population=_population_for(params, s.link),
                contribution=effect,
            )
        )
        prev = (ledger.point, ledger.low, ledger.high)

    total = sum(abs(e) for e in contributions) or 1.0
    for st, effect in zip(steps, contributions):
        # share of the TOTAL MOVEMENT in the line (positive; signed
        # log-shares cancel across gap-space steps and mislead)
        st.contribution = abs(effect) / total

    from .sensitivity import sobol_indices

    def _compute(ps: ParameterSet) -> float:
        return child_line(ps)["grandchild"].point

    sob = sobol_indices(params, _compute, _load_nodes(), base=128, seed=seed)

    return Explanation(
        claim=(
            "For families where a displaced father takes the average "
            "long-run earnings hit, the model traces the earnings line "
            "through children and grandchildren"
        ),
        outcome="grandchild_earnings",
        unit="gap_multiplier",
        value=(child["grandchild"].point, child["grandchild"].low, child["grandchild"].high),
        horizon="adult outcomes, one and two generations after the shock",
        population="children of US-style displaced tradable workers",
        steps=steps,
        drivers=_driver_sentences(sob)[:3],
        assumptions=[
            "transmission repeats the same IGE band across generations",
            "independent causes of one outcome are reported side by side, not composed",
            "US-centric parameter population applied to US-style exposures",
        ],
        falsify=[
            "long-run panels of displaced-worker children NOT showing "
            "an earnings gap would break the first step (Oreopoulos "
            "2008 is a 39,000-pair quasi-experiment; it would take "
            "comparable contrary evidence to overturn)",
            "a null in 3-generation persistence data would collapse the "
            "great-grandchild layer (weakest-identified)",
        ],
        parameter_set_version=params.version,
        monte_carlo=simulate(
            params, _compute, draws=draws, seed=seed, nodes=_load_nodes()
        ),
    )


def _step_sentence(link: str, before: float, after: float) -> str:
    delta_pct = (after - before) * 100
    if "child_earnings" in link and "grandchild" not in link:
        return (
            f"Children of displaced fathers earn about {abs(delta_pct):.0f}% "
            "less as adults (firm-closure quasi-experiment, 39k father-son pairs)."
        )
    if "grandchild" in link and "greatgrandchild" not in link:
        return (
            f"That gap transmits to the grandchild at roughly half strength: "
            f"a further {abs(delta_pct):.1f}% down (intergenerational earnings "
            "elasticity, US mobility literature)."
        )
    return (
        f"The line continues one more generation at the same transmission "
        f"strength: a further {abs(delta_pct):.1f}% down (weakest-identified layer)."
    )


def _population_for(params: ParameterSet, link: str) -> str:
    try:
        return params.by_link(link).population_scope
    except KeyError:
        return ""


def _driver_sentences(sob: dict) -> list[dict]:
    out = []
    for row in sob["indices"][:3]:
        share = max(row["S_total"], 0.0)
        if share < 0.01:
            continue  # below 1% is estimator noise at our base sizes
        out.append(
            {
                "link": row["link"],
                "share_of_uncertainty": share,
                "sentence": (
                    f"{row['link']} drives about {share * 100:.0f}% of the "
                    "remaining range — pinning it down is where more "
                    "evidence would help most."
                ),
            }
        )
    return out


def _load_nodes() -> dict:
    from .params import default_dir, load_nodes

    return load_nodes(default_dir() / "nodes.csv")


def _r3(t: tuple[float, float, float]) -> tuple[float, float, float]:
    return tuple(round(v, 4) for v in t)
