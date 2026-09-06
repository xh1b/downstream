"""The downstream audit.

Static checks over the parameter set, node registry, baselines, and
bibliography. Every finding names the file and the fix. The audit
exits nonzero on any ERROR; WARN items are honest-gaps reporting.

Run: downstream audit   (or python -m downstream.audit)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .citations import parse_bib
from .params import VALID_TIERS, load, load_all
from . import units

ERROR = "ERROR"
WARN = "WARN"
INFO = "INFO"


@dataclass
class Finding:
    severity: str
    check: str
    message: str

    def as_dict(self) -> dict:
        return {"severity": self.severity, "check": self.check, "message": self.message}


def audit(params_dir: str | Path | None = None) -> list[Finding]:
    d = Path(params_dir) if params_dir else Path(__file__).resolve().parents[2] / "params"
    findings: list[Finding] = []

    try:
        params = load(d / "parameters.csv")
    except Exception as e:  # cycle or parse failure is itself a finding
        findings.append(Finding(ERROR, "dag", f"parameters.csv failed to load: {e}"))
        return findings

    parts = load_all(d)
    nodes: dict = parts["nodes"]
    baselines: dict = parts["baselines"]
    bib: dict = parts["bib"]

    if params.version == "unversioned":
        findings.append(Finding(WARN, "version", "params/VERSION missing; outputs stamp 'unversioned'"))

    seen_links: set[str] = set()
    cited_keys: set[str] = set()

    for p in params.parameters:
        where = f"parameters.csv:{p.link}"
        if p.link in seen_links:
            findings.append(Finding(ERROR, "duplicate-link", f"{where}: duplicate link id"))
        seen_links.add(p.link)

        if not (p.low <= p.point <= p.high):
            findings.append(
                Finding(ERROR, "band", f"{where}: point {p.point} outside [{p.low}, {p.high}]")
            )

        if p.tier not in VALID_TIERS:
            findings.append(
                Finding(ERROR, "tier", f"{where}: tier {p.tier!r} not in {sorted(VALID_TIERS)}")
            )

        keys = p.citation_keys
        if not keys:
            findings.append(Finding(ERROR, "citation", f"{where}: no citation keys"))
        for k in keys:
            cited_keys.add(k)
            if k not in bib:
                findings.append(
                    Finding(ERROR, "citation", f"{where}: bib key {k!r} not in references.bib")
                )

        for node_name in (p.from_node, p.to_node):
            if node_name not in nodes:
                findings.append(
                    Finding(ERROR, "node", f"{where}: node {node_name!r} not in nodes.csv")
                )
        if p.from_node in nodes and p.to_node in nodes:
            fu, tu = nodes[p.from_node].unit, nodes[p.to_node].unit
            if units.composition_for(fu, tu) is None:
                findings.append(
                    Finding(
                        ERROR,
                        "units",
                        f"{where}: no composition rule for {fu} -> {tu}",
                    )
                )
            # The Moretti-shape guard: a level ratio under 1.0 would
            # silently shrink counts; level ratios are "jobs per job".
            if tu == units.LEVEL_RATIO and p.point < 1.0:
                findings.append(
                    Finding(
                        ERROR,
                        "level-ratio-shape",
                        f"{where}: level_ratio point {p.point} < 1.0 — levels are "
                        "counts-per-count; a fraction here is almost always the "
                        "v0 multiplier bug",
                    )
                )

        # Tier/evidence consistency: the tier claims how the number was read.
        if p.tier == "EXACT":
            for k in keys:
                if k in bib and bib[k].evidence not in ("fulltext-table", "fulltext"):
                    findings.append(
                        Finding(
                            ERROR,
                            "tier-evidence",
                            f"{where}: tier EXACT but {k} evidence={bib[k].evidence!r}; "
                            "pin the full-text table reference or drop the tier",
                        )
                    )
        if p.tier == "EXACT-abstract":
            for k in keys:
                if k in bib and bib[k].evidence not in ("abstract", "results", "fulltext-table", "fulltext"):
                    findings.append(
                        Finding(
                            ERROR,
                            "tier-evidence",
                            f"{where}: tier EXACT-abstract but {k} evidence={bib[k].evidence!r}",
                        )
                    )

    # Orphan detection: from_node that is neither an entry point nor produced.
    entry_nodes = {"displacement_event", "family_size", "school_spending", "youth_wages"}
    produced = {p.to_node for p in params.parameters}
    for p in params.parameters:
        if p.from_node not in produced and p.from_node not in entry_nodes:
            findings.append(
                Finding(
                    WARN,
                    "orphan",
                    f"parameters.csv:{p.link}: from_node {p.from_node!r} has no producer "
                    "and is not an entry node; upstream extraction must be queued in "
                    "docs/QUEUED_EXTRACTIONS.md",
                )
            )

    for key, entry in bib.items():
        if key not in cited_keys:
            findings.append(
                Finding(WARN, "uncited-bib", f"references.bib:{key}: cited nowhere ({entry.cite()})")
            )

    # Baselines: verified rows need value + citation; pending rows are listed.
    for name, b in baselines.items():
        if b.status == "verified":
            if b.value is None or not b.citation:
                findings.append(
                    Finding(
                        ERROR,
                        "baseline",
                        f"baselines.csv:{name}: status=verified but value/citation missing",
                    )
                )
        elif b.status == "pending":
            findings.append(
                Finding(
                    INFO,
                    "baseline",
                    f"baselines.csv:{name}: pending — count conversions blocked until pinned",
                )
            )
        else:
            findings.append(
                Finding(ERROR, "baseline", f"baselines.csv:{name}: unknown status {b.status!r}")
            )

    return findings


def summary(findings: list[Finding]) -> dict:
    counts = {ERROR: 0, WARN: 0, INFO: 0}
    for f in findings:
        counts[f.severity] += 1
    return {
        "errors": counts[ERROR],
        "warnings": counts[WARN],
        "info": counts[INFO],
        "pass": counts[ERROR] == 0,
    }


if __name__ == "__main__":
    import json
    import sys

    fs = audit()
    print(json.dumps({"summary": summary(fs), "findings": [f.as_dict() for f in fs]}, indent=2))
    sys.exit(0 if summary(fs)["pass"] else 1)
