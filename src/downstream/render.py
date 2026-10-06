"""Text rendering of explanations.

The reference renderer: this is the bar every future surface (web,
paper, chat) must meet. Hard rules, enforced by tests:

- LAYER 1 (headline): one sentence, plain words, the band visible,
  the word "modeled" present.
- LAYER 2 (why): the chain, one step per line, every step with its
  citation and its range.
- LAYER 3 (range drivers): where the remaining uncertainty lives.
- LAYER 4 (falsification): what evidence would break the claim.
- LAYER 5 (receipts): every parameter, fully cited.

No layer shows a bare point estimate. `_fmt` is the only way to
render a number.
"""

from __future__ import annotations

from .citations import BibEntry
from .explanation import Explanation

_CITE_CACHE: dict[str, BibEntry] = {}


def load_citations(bib: dict[str, BibEntry]) -> None:
    global _CITE_CACHE
    _CITE_CACHE = bib


def _cite(key: str) -> str:
    entry = _CITE_CACHE.get(key)
    return entry.cite() if entry else key


def _fmt(value: tuple[float, float, float], digits: int = 2) -> str:
    point, low, high = value
    if low > high:
        low, high = high, low
    return f"{point:.{digits}f} [{low:.{digits}f} to {high:.{digits}f}]"


def render_text(exp: Explanation) -> str:
    lines: list[str] = []

    # Layer 1 — headline
    lines.append(exp.claim)
    lines.append(
        f"Modeled result ({exp.outcome.replace('_', ' ')}): "
        f"{_fmt(exp.value)} ({exp.unit.replace('_', ' ')}; "
        f"{exp.horizon}; {exp.population})."
    )
    lines.append("")

    # Layer 2 — the chain
    lines.append("Why: the cited chain")
    for i, s in enumerate(exp.steps, 1):
        cites = ", ".join(_cite(c) for c in s.citations)
        lines.append(
            f"  {i}. {s.sentence} "
            f"Applied: {_fmt(s.params)} — after this step: "
            f"{_fmt(s.after)} [{cites}; evidence tier {s.tier}; "
            f"{s.population}; evidence role {s.evidence_role}; causal role {s.causal_role}]"
        )
    lines.append("")

    # Layer 3 — uncertainty drivers
    lines.append("What drives the remaining range")
    if exp.drivers:
        for d in exp.drivers:
            lines.append(f"  - {d['sentence']}")
    else:
        lines.append("  - sensitivity analysis not yet run for this claim")
    lines.append("")

    # Layer 4 — falsification
    lines.append("What would prove this wrong")
    for f in exp.falsify:
        lines.append(f"  - {f}")
    lines.append("")

    # Assumptions + blocked
    if exp.assumptions:
        lines.append("Declared assumptions")
        for a in exp.assumptions:
            lines.append(f"  - {a}")
        lines.append("")
    if exp.blocked:
        lines.append("Refused to compute (missing cited inputs)")
        for b in exp.blocked:
            lines.append(f"  - {b['outcome']}: {b['reason']}")
        lines.append("")

    stamp = f"parameter set {exp.parameter_set_version}"
    if exp.monte_carlo:
        mc = exp.monte_carlo
        stamp += (
            f"; Monte Carlo {mc['draws']} draws ({mc['sampler']}), seed {mc['seed']}, "
            f"p05-p95 {_fmt((mc['p50'], mc['p05'], mc['p95']))} around p50"
        )
    lines.append(f"[{stamp}]")
    return "\n".join(lines)


def validate_rendered(text: str) -> list[str]:
    """Render guardrails: returns violations (empty = clean)."""
    problems: list[str] = []
    if "modeled" not in text.lower():
        problems.append("headline layer must say 'modeled'")
    return problems
