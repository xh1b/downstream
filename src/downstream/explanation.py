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
    evidence_role: str = ""
    causal_role: str = ""

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
            "evidence_role": self.evidence_role, "causal_role": self.causal_role,
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
    projection_eligibility: dict = field(default_factory=dict)

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
            "projection_eligibility": self.projection_eligibility,
        }


def explain_child_line(params: ParameterSet, draws: int = 4000, seed: int = 1901, *, nodes=None, params_dir=None) -> Explanation:
    """Worked explanation: what happens to the earnings line of a
    displaced father's family, three generations out."""
    from .mc import simulate

    from pathlib import Path
    from .params import default_dir, load_nodes, load_correlations
    d = Path(params_dir) if params_dir is not None else default_dir()
    if nodes is None:
        nodes = load_nodes(d / "nodes.csv")
    child = child_line(params)

    steps: list[Step] = []
    prev = (1.0, 1.0, 1.0)
    contributions: list[float] = []
    for key in ("child", "grandchild"):
        ledger = child[key]
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
                contribution=effect, evidence_role=s.evidence_role, causal_role=s.causal_role,
            )
        )
        prev = (ledger.point, ledger.low, ledger.high)

    total = sum(abs(e) for e in contributions) or 1.0
    for st, effect in zip(steps, contributions):
        # share of the TOTAL MOVEMENT in the line (positive; signed
        # log-shares cancel across gap-space steps and mislead)
        st.contribution = abs(effect) / total

    from .sensitivity import correlated_block_sobol

    def _compute(ps: ParameterSet) -> float:
        return child_line(ps)["grandchild"].point

    correlations = load_correlations(d / "correlations.csv") if (d / "correlations.csv").exists() else []
    sob = correlated_block_sobol(params, _compute, nodes, correlations, base=128, seed=seed)

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
        population="illustrative transport of a Canadian father-son firm-closure estimate; grandchildren are structural projections",
        steps=steps,
        drivers=_driver_sentences(sob)[:3],
        assumptions=[
            "transmission repeats the same IGE band across generations",
            "independent causes of one outcome are reported side by side, not composed",
            "target population applicability has not been reviewed; the reference result is illustrative",
            "grandchild persistence is a structural projection, not an identified displacement effect",
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
        projection_eligibility=child["evidence_status"],
        monte_carlo=simulate(
            params, _compute, draws=draws, seed=seed, nodes=nodes, params_dir=d
        ),
    )


def _step_sentence(link: str, before: float, after: float) -> str:
    gap_pct = (1 - after) * 100
    if "grandchild" not in link:
        return (f"The modeled child earnings gap is {gap_pct:.2f}% below the no-displacement reference "
                "(Canadian father-son firm-closure estimate; transport is conditional).")
    attenuation = (after - before) * 100
    return (f"Structural persistence leaves a {gap_pct:.2f}% earnings gap below the no-displacement reference; "
            f"the gap narrows by {attenuation:.2f} percentage points from the preceding generation.")


def _population_for(params: ParameterSet, link: str) -> str:
    try:
        return params.by_link(link).population_scope
    except KeyError:
        return ""


def _driver_sentences(sob: dict) -> list[dict]:
    out = []
    for row in sob.get("indices", sob.get("blocks", []))[:3]:
        row = {**row, "link": row.get("link", ", ".join(row.get("links", [])))}
        share = max(row["S_total"], 0.0)
        if share < 0.01:
            continue  # below 1% is estimator noise at our base sizes
        out.append(
            {
                "link": row["link"],
                "share_of_uncertainty": share,
                "sentence": (
                    f"{row['link']} drives about {share * 100:.0f}% of the "
                    "parameter-induced variance in this sensitivity design — more "
                    "evidence would help most."
                ),
            }
        )
    return out


def _r3(t: tuple[float, float, float]) -> tuple[float, float, float]:
    return tuple(round(v, 4) for v in t)
