"""Structural-variant ensemble: named alternate composition assumptions.

The model's composition choices (side-by-side parallel streams, flat
IGE transmission across generations) are ASSUMPTIONS, not citations.
Plan #9: run the named alternates as a declared ensemble and publish
the spread. A reader who rejects an assumption can read the number
their assumption produces; a reader who accepts the baseline can see
what it costs them.

Every variant is DECLARED (named, documented, deterministic). None
may be silently substituted for the baseline: the ensemble output
carries all variants side by side, and the baseline row always
equals the shipped model's output (trap-pinned).

Variants (v1):
- baseline              the shipped composition (SPEC §4-5)
- parallel_gap_additive divorce + family-size streams combined
                        gap-additively via ledger.combine_parallel,
                        then composed with the direct child gap —
                        the additivity assumption the literature does
                        not license (SPEC §4), priced here
- ige_decay_half        grandchild transmission decays: t2 = t^0.5
- ige_decay_power       grandchild transmission strengthens: t2 = t^1.5
  (both decay shapes are geometric re-parameterizations of the SAME
  cited IGE band — declared assumption alternates, not new evidence)
"""

from __future__ import annotations

from dataclasses import replace

from .children import CHILD_DIRECT, GRANDCHILD, child_line
from .ledger import DIRECT, GAP, combine_parallel, start
from .params import ParameterSet

VARIANT_IDS = ("baseline", "parallel_gap_additive", "ige_decay_half", "ige_decay_power")


def _with_transmission(params: ParameterSet, link: str, exponent: float) -> ParameterSet:
    """Re-parameterize a transmission link as t^exponent (geometric)."""
    p = params.by_link(link)
    q = replace(p, point=p.point**exponent, low=p.low**exponent, high=p.high**exponent)
    rows = tuple(q if r.link == link else r for r in params.parameters)
    return ParameterSet(version=f"{params.version}-variant", parameters=rows)


def _parallel_additive_child(params: ParameterSet) -> dict:
    """Direct + divorce + family-size gaps combined additively in gap space.

    The additivity assumption is DECLARED here and nowhere else: the
    shipped model reports these streams side by side precisely because
    the literature does not license the combination (SPEC §4).
    """
    divorce = params.by_link("divorce->child_earnings")
    fam = params.by_link("family_size->child_earnings")
    fam_compounded = start("family", "gap_multiplier")
    fam_compounded = fam_compounded.apply("level", fam, label="family_size")
    parallel = combine_parallel(
        [
            start("divorce", "gap_multiplier").apply(DIRECT, divorce, label="divorce"),
            fam_compounded,
        ],
        label="parallel_streams",
    )
    direct = params.by_link(CHILD_DIRECT)
    # gap-additive: child gap = direct gap + parallel gaps, floored at 0
    point = max(0.0, 1 - ((1 - direct.point) + (1 - parallel.point)))
    low = max(0.0, 1 - ((1 - direct.high) + (1 - parallel.low)))
    high = max(0.0, 1 - ((1 - direct.low) + (1 - parallel.high)))
    child = start("child_earnings", "gap_multiplier")
    child = replace(child, point=round(point, 4), low=round(low, 4), high=round(high, 4))
    grand = child.apply(GAP, params.by_link(GRANDCHILD), label="grandchild")
    return {"child": child, "grandchild": grand}


def run_ensemble(params: ParameterSet) -> dict:
    """All named variants side by side, with the spread published."""
    rows = []

    def _row(name: str, description: str, child, grand) -> None:
        rows.append(
            {
                "variant": name,
                "description": description,
                "child_gap": {"point": round(child.point, 4), "low": round(child.low, 4), "high": round(child.high, 4)},
                "grandchild_gap": {"point": round(grand.point, 4), "low": round(grand.low, 4), "high": round(grand.high, 4)},
            }
        )

    base = child_line(params)
    _row(
        "baseline",
        "the shipped composition (SPEC 4-5): direct child effect, flat IGE",
        base["child"], base["grandchild"],
    )

    pa = _parallel_additive_child(params)
    _row(
        "parallel_gap_additive",
        "direct + divorce + family-size gaps added in gap space (declared "
        "additivity; the literature does not license it — SPEC 4)",
        pa["child"], pa["grandchild"],
    )

    for name, expo, desc in (
        ("ige_decay_half", 0.5, "grandchild transmission t^0.5 (persistence decays)"),
        ("ige_decay_power", 1.5, "grandchild transmission t^1.5 (persistence strengthens)"),
    ):
        v = _with_transmission(params, GRANDCHILD, expo)
        line = child_line(v)
        _row(name, f"{desc}; declared assumption alternate, not new evidence", line["child"], line["grandchild"])

    child_pts = [r["child_gap"]["point"] for r in rows]
    grand_pts = [r["grandchild_gap"]["point"] for r in rows]
    return {
        "experiment": "structural_variant_ensemble",
        "parameter_set_version": params.version,
        "variants": rows,
        "spread": {
            "child_point_min": round(min(child_pts), 4),
            "child_point_max": round(max(child_pts), 4),
            "grandchild_point_min": round(min(grand_pts), 4),
            "grandchild_point_max": round(max(grand_pts), 4),
        },
        "note": (
            "Composition-assumption alternates, declared and priced. The "
            "baseline row equals the shipped model. No variant is ever "
            "silently substituted; the spread IS the result."
        ),
    }
