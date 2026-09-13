"""Generational transmission: one parent->child edge, walked recursively.

An intergenerational walk is ONE admitted relationship — parent outcome
to child adult outcome — applied at every generation. The repo never
extracts a separate parent->grandchild coefficient: the transmission
edge is admitted once (child_earnings->grandchild_earnings), and each
further generation re-applies the relationship, with the evidence
support for THAT step carried alongside it (the US IGE literature
anchors the first step; the Swedish multi-generation register studies
anchor the repetition beyond it).

Two facts are distinct and both declared per step:

- the COMPOSITION KIND: how a parent shift maps into the child outcome
  (earnings composes in GAP space — grandchild gap = 1 - IGE*(1 - child
  gap) — never as level products);
- the RELATIONSHIP id: steps sharing one id are a single edge unrolled
  across generations, so their parameter bands must be identical. The
  unrolled rows in parameters.csv are a presentation choice; this
  registry is the single source of truth for what the relationship is,
  and the audit fails if the unrolled copies drift apart.

Outcomes without an admitted transmission row are listed in
BLOCKED_CANDIDATES with the extraction that would admit the walk:
one row per outcome, then every generation follows by recursion.
"""

from __future__ import annotations

from dataclasses import dataclass

from .ledger import CHAIN_CAUSAL_ROLES, CHAIN_KINDS, DIRECT, Ledger, start
from .params import ParameterSet

GEN_LABELS = ("child", "grandchild", "greatgrandchild")


def generation_label(index: int) -> str:
    """1-based generation label: child, grandchild, greatgrandchild, ..."""
    if index < 1:
        raise ValueError(f"generation index must be >= 1, got {index}")
    if index <= len(GEN_LABELS):
        return GEN_LABELS[index - 1]
    return "great" * (index - 2) + "grandchild"


@dataclass(frozen=True)
class TransmissionStep:
    """One unrolled application of a transmission relationship."""

    link: str           # the admitted parameter row for this step
    kind: str           # ledger composition kind (e.g. GAP)
    relationship: str   # steps sharing an id are ONE edge unrolled
    support: tuple[str, ...]  # bib keys licensing THIS step's repetition


@dataclass(frozen=True)
class Transmission:
    """A walkable outcome: gen-2 entry + the recursive transmission edge."""

    outcome: str              # display name, e.g. "earnings"
    unit: str                 # ledger unit carried through the walk
    entry: str                # displacement->child_X link (generation 2)
    steps: tuple[TransmissionStep, ...]  # generations 3, 4, ...
    entry_label: str = ""     # label of the generation-2 ledger ("" = outcome)

    @property
    def depth(self) -> int:
        return 1 + len(self.steps)


EARNINGS = Transmission(
    outcome="earnings",
    unit="gap_multiplier",
    entry="displacement->child_earnings",
    entry_label="child_earnings",
    steps=(
        TransmissionStep(
            link="child_earnings->grandchild_earnings",
            kind="gap",
            relationship="ige_earnings",
            support=("solon1992", "corak2013", "chetty2014"),
        ),
        TransmissionStep(
            link="grandchild_earnings->greatgrandchild_earnings",
            kind="gap",
            relationship="ige_earnings",
            support=("lindahl2015", "adermon2018"),
        ),
    ),
)

ACHIEVEMENT = Transmission(
    outcome="achievement",
    unit="sd_delta",
    entry="displacement_event->child_achievement_sd",
    entry_label="child_achievement_sd",
    steps=(
        TransmissionStep(
            link="child_achievement_sd->grandchild_achievement_sd",
            kind="linear_shift",
            relationship="skill_persistence",
            support=("blackdevereuxsalvanes2009",),
        ),
    ),
)

TRANSMISSIONS = (EARNINGS, ACHIEVEMENT)

# Outcomes with an admitted generation-2 displacement estimate but no
# admitted transmission row: the walk is ONE extraction away. These are
# declared, visible skeleton — never silently extrapolated. Landed walks
# (earnings, achievement) are in TRANSMISSIONS above, not here.
BLOCKED_CANDIDATES = (
    {
        "outcome": "education_years",
        "entry": None,
        "missing": "the transmission row itself LANDED (v1.44: "
                   "child_education_years->grandchild_education_years, "
                   "0.296 [0.255, 0.337], lindahl2015 Table 2); what is "
                   "still missing is the gen-2 entry — no "
                   "displacement->child_education_years edge exists (the "
                   "hs_completion/college rows are probability-scale and "
                   "cannot bridge without a declared conversion)",
        "note": "walk exists the moment an admitted entry lands",
    },
    {
        "outcome": "adult_depression",
        "entry": "displacement_event->adult_depression_cesd",
        "missing": "parent depression -> child depression row: candidate "
                   "coefficients live in the parental-depression "
                   "meta-analyses (Connell & Goodman 2002; Goodman et al. "
                   "2011; Sutherland et al. 2022 meta-regression), but none "
                   "was verifiable from a primary source at landing time "
                   "(2026-09-14) — full-text pass queued",
        "note": "two blockers: the meta-analytic association is reported "
                "in SD units while the entry row is scale01 (0-1 CESD "
                "index), so the walk needs the index SD or a same-scale "
                "transmission; verify the coefficient from the actual "
                "meta-analysis text before pinning anything",
    },
    {
        "outcome": "divorce",
        "entry": "displacement->divorce_hazard",
        "missing": "parental divorce -> child own-divorce row (gruber2004 "
                   "documents the own-divorce effect; needs full-text "
                   "pinning as its own row)",
        "note": "also needs a conditional composition kind: only the "
                "share of marriages that actually dissolve transmit",
    },
)


def validate_transmission(params: ParameterSet, t: Transmission) -> None:
    """Walk-time checks that never change what the admitted rows compose.

    Deliberately NOT here: boundary-role refusals, unrolled-copy drift,
    and support-key existence. Those are cross-row semantic findings and
    belong to the audit (see transmission_findings) — the walk composes
    whatever rows admission let through, exactly like the explicit
    per-generation composition it replaced.
    """
    params.by_link(t.entry)  # KeyError names the missing link
    if t.entry not in CHAIN_KINDS or CHAIN_KINDS[t.entry] != "direct":
        raise ValueError(
            f"transmission entry {t.entry!r} must be a chain-kind 'direct' link"
        )
    for step in t.steps:
        params.by_link(step.link)
        expected = CHAIN_KINDS.get(step.link)
        if expected is None:
            raise ValueError(
                f"transmission step {step.link!r} has no chain kind; composition "
                "must be admitted in ledger.CHAIN_KINDS before it can walk"
            )
        if expected != step.kind:
            raise ValueError(
                f"transmission step {step.link!r} requires {expected!r} "
                f"composition, not {step.kind!r}"
            )


def drift_relationships(params: ParameterSet) -> list[str]:
    """Relationship ids whose unrolled copies carry different bands.

    Steps sharing a relationship id are ONE edge unrolled across
    generations; if their rows disagree, one of them is wrong (or a
    third relationship should have been declared)."""
    drifted = []
    for t in TRANSMISSIONS:
        bands: dict[str, tuple] = {}
        for step in t.steps:
            p = params.by_link(step.link)
            band = (p.point, p.low, p.high)
            if step.relationship in bands and bands[step.relationship] != band:
                drifted.append(step.relationship)
            bands[step.relationship] = band
    return drifted


def transmission_findings(params: ParameterSet, bib: dict) -> list[tuple[str, str]]:
    """Audit findings for the registry: (check, message) tuples.

    Refusals at admission (unknown links, boundary roles) and semantic
    inconsistencies across unrolled copies (band drift, support keys
    missing from the bibliography) surface here, not at walk time.
    """
    findings: list[tuple[str, str]] = []
    try:
        load_transmissions(params)
    except Exception as e:
        findings.append(("transmission", f"transmission registry failed to load: {e}"))
        return findings
    for rel in drift_relationships(params):
        findings.append((
            "transmission-drift",
            f"transmission relationship {rel!r} is ONE edge unrolled, but its "
            "parameter rows disagree — pin them to the same band or declare "
            "separate relationships",
        ))
    for t in TRANSMISSIONS:
        for step in t.steps:
            for key in step.support:
                if key not in bib:
                    findings.append((
                        "transmission-support",
                        f"transmission step {step.link!r} cites {key!r}, "
                        "which is not in references.bib",
                    ))
    return findings


def walk(
    params: ParameterSet,
    t: Transmission,
    hook=None,
) -> dict[str, Ledger]:
    """Apply the entry, then the transmission edge at every generation.

    hook(prev_ledger, generation_index) may rewrite each generation's
    ledger in place in the walk (used for the exploratory place
    modifier); it must preserve the ledger's unit and band ordering.
    """
    validate_transmission(params, t)
    ledgers: dict[str, Ledger] = {}
    prev = start(t.entry_label or t.outcome, t.unit).apply(
        DIRECT, params.by_link(t.entry),
        causal_role=CHAIN_CAUSAL_ROLES[t.entry],
    )
    if hook is not None:
        prev = hook(prev, 1)
    ledgers[generation_label(1)] = prev
    for i, step in enumerate(t.steps, start=2):
        prev = prev.apply(
            step.kind, params.by_link(step.link),
            causal_role=CHAIN_CAUSAL_ROLES[step.link],
        )
        if hook is not None:
            prev = hook(prev, i)
        ledgers[generation_label(i)] = prev
    return ledgers


def load_transmissions(params: ParameterSet) -> tuple[Transmission, ...]:
    """Admit the declared walks or refuse loudly at load."""
    for t in TRANSMISSIONS:
        validate_transmission(params, t)
        entry = params.by_link(t.entry)
        if entry.evidence_role == "boundary":
            raise ValueError(
                f"transmission entry {t.entry!r} is evidence_role=boundary: "
                "a boundary coefficient cannot start an intergenerational walk"
            )
        for step in t.steps:
            p = params.by_link(step.link)
            if p.evidence_role == "boundary":
                raise ValueError(
                    f"transmission step {step.link!r} is evidence_role=boundary: "
                    "boundary coefficients are applied by named adapters, not walked"
                )
    return TRANSMISSIONS


def find_transmission(outcome: str) -> Transmission:
    """The declared walk for an outcome, or KeyError naming the gap."""
    for t in TRANSMISSIONS:
        if t.outcome == outcome:
            return t
    raise KeyError(
        f"no admitted transmission walk for outcome {outcome!r}; "
        f"walkable: {[t.outcome for t in TRANSMISSIONS]}"
    )


def describe(params: ParameterSet) -> dict:
    """The generational map: what walks, how far, on whose evidence —
    and what is one extraction away."""
    walks = []
    for t in load_transmissions(params):
        walks.append({
            "outcome": t.outcome,
            "unit": t.unit,
            "depth": t.depth,
            "generations": [generation_label(i) for i in range(1, t.depth + 1)],
            "entry": t.entry,
            "steps": [
                {
                    "link": s.link,
                    "kind": s.kind,
                    "relationship": s.relationship,
                    "support": list(s.support),
                }
                for s in t.steps
            ],
        })
    return {
        "walkable": walks,
        "blocked": [dict(b) for b in BLOCKED_CANDIDATES],
        "principle": (
            "one parent->child relationship per outcome, applied recursively; "
            "each step's evidence support is declared, never silently reused"
        ),
    }
