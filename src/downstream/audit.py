"""The downstream audit.

Static checks over the parameter set, node registry, baselines, and
bibliography. Every finding names the file and the fix. The audit
exits nonzero on any ERROR; WARN items are honest-gaps reporting.

Division of labor: admission contracts (duplicate links, blank support
metadata, out-of-band points, unknown statuses) are enforced by the
loaders in params.py and place.py, which refuse the file outright. By
the time the audit sees a row it is syntactically admissible, so the
checks here cover only cross-file semantics a single-file loader cannot
know: tier-vs-evidence consistency, distribution shape, unit
composition, the citation graph, and correlation-matrix validity.

Run: downstream audit   (or python -m downstream.audit)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from .distributions import KNOWN_DISTS, _cholesky
from .params import (
    VALID_TIERS,
    load,
    load_all,
    load_correlations,
    spearman_matrix,
)
from .place import MOBILITY_MODIFIER_LINK, load_places
from .transmissions import transmission_findings
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

    try:
        parts = load_all(d)
    except Exception as e:  # refusal at admission is a finding, not a crash
        findings.append(Finding(ERROR, "inputs", f"parameter inputs failed to load: {e}"))
        return findings
    nodes: dict = parts["nodes"]
    baselines: dict = parts["baselines"]
    bib: dict = parts["bib"]

    if params.version == "unversioned":
        findings.append(Finding(WARN, "version", "params/VERSION missing; outputs stamp 'unversioned'"))

    cited_keys: set[str] = set()

    for p in params.parameters:
        where = f"parameters.csv:{p.link}"
        # Duplicate links, blank citations, and out-of-band points were
        # refused by params.load before this loop; nothing re-checks them.
        if p.tier not in VALID_TIERS:
            findings.append(
                Finding(ERROR, "tier", f"{where}: tier {p.tier!r} not in {sorted(VALID_TIERS)}")
            )

        # citation_keys is nonempty by admission: load refuses blank
        # citations, so every key here is a nonempty string.
        keys = p.citation_keys
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

        # Declared distribution shape (v1.27): a row claiming a CI shape
        # must have a band that shape can produce. A declared band
        # (rounding band, cross-study spread, evidence-widened band) is
        # expected to declare NOTHING — the dist column exists only for
        # SE-derived CIs.
        if p.dist:
            if p.dist not in KNOWN_DISTS:
                findings.append(
                    Finding(ERROR, "dist", f"{where}: dist {p.dist!r} not in {sorted(KNOWN_DISTS)}")
                )
            elif p.dist in ("lognormal", "loguniform"):
                if p.low <= 0 or p.high <= 0:
                    findings.append(
                        Finding(
                            ERROR,
                            "dist",
                            f"{where}: dist {p.dist} needs positive band edges, got [{p.low}, {p.high}]",
                        )
                    )
                elif p.dist == "lognormal":
                    geo = math.sqrt(p.low * p.high)
                    if abs(math.log(p.point) - math.log(geo)) > 0.01 + 1e-9:
                        findings.append(
                            Finding(
                                WARN,
                                "dist",
                                f"{where}: dist lognormal but the point is not the band's "
                                f"geometric mean ({p.point} vs {geo:.4g}) — an exp(beta +/- 1.96 SE) "
                                "band centers on the point; a mismatch means the band was not "
                                "built that way",
                            )
                        )
            elif p.dist == "normal":
                mid = (p.low + p.high) / 2
                if abs(p.point - mid) > max(0.005 * abs(p.point), 0.005) + 1e-9:
                    findings.append(
                        Finding(
                            WARN,
                            "dist",
                            f"{where}: dist normal but the point is not the band's midpoint "
                            f"({p.point} vs {mid:.4g}) — the sampling centers on the point and "
                            "truncates at the band; an off-midpoint band usually means it was "
                            "widened or assembled, not SE-derived",
                        )
                    )

    # Orphan detection: from_node that is neither an entry point nor produced.
    entry_nodes = {
        "displacement_event",
        "family_size",
        "school_spending",
        "youth_wages",
        "neighborhood_exposure",
        "unconditional_income",
        "youth_crime_conviction_share",
        "youth_violent_crime_conviction_share",
        # The receiving-community exposure: like displacement_event, a
        # scenario entry, not something the displacement DAG produces.
        "immigrant_influx",
        # v1.47 divorce-transmission stream: the node's own description
        # declares it an entry population ("married-worker couples
        # followed over the displacement window"); completing the
        # declaration its landing missed.
        "married_cohort",
        # Boundary-applied study inputs: they are deliberately not produced
        # by the displacement DAG and must not drown real audit warnings.
        "wage_ratio", "import_shock_per_worker", "family_income_shock",
        "unemployment_rate", "eitc_exposure", "male_earnings_pc",
        "male_mass_layoff_rate", "eviction_order", "foreclosure_order",
        "local_unemp_shock", "household_hardship", "couple_unemployment",
        "unemployment_status",
    }
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
                Finding(INFO, "uncited-bib", f"references.bib:{key}: cited nowhere ({entry.cite()})")
            )

    # Baselines: load_baselines guarantees the status is 'verified' or
    # 'pending' and that verified rows carry value, citation, and
    # population — anything else is refused at admission. The audit's
    # remaining job here is listing pending rows as honest gaps.
    for name, b in baselines.items():
        if b.status == "pending":
            findings.append(
                Finding(
                    INFO,
                    "baseline",
                    f"baselines.csv:{name}: pending — count conversions blocked until pinned",
                )
            )

    # Place-resolved plug (params/places.csv, optional): rows need
    # citations, the national fallback row is required when the file
    # exists, and a rate without its precision n would make the
    # pooling weight a guess — flagged as an honest gap, not applied.
    try:
        places = load_places(d / "places.csv")
    except Exception as e:
        places = {}
        findings.append(Finding(ERROR, "places", f"places.csv failed to load: {e}"))
    if places:
        if "national" not in places:
            findings.append(
                Finding(
                    ERROR,
                    "places",
                    "places.csv: no 'national' row — county shrinkage pools "
                    "toward it; add the row with its citation",
                )
            )
        for key, pl in places.items():
            prow = f"places.csv:{key}"
            # load_places guarantees a known level and finite nonnegative
            # precision counts; it does not require a citation, so blank
            # citations still reach this check.
            if not pl.citation:
                findings.append(Finding(ERROR, "places", f"{prow}: no citation"))
            if pl.mortality_rate is not None and pl.mortality_n is None:
                findings.append(
                    Finding(
                        WARN,
                        "places",
                        f"{prow}: mortality_rate without mortality_n — pooling "
                        "weight would be a guess; the outcome stays national "
                        "until the n lands",
                    )
                )
            if pl.divorce_rate is not None and pl.divorce_n is None:
                findings.append(
                    Finding(
                        WARN,
                        "places",
                        f"{prow}: divorce_rate without divorce_n — pooling "
                        "weight would be a guess; the outcome stays national "
                        "until the n lands",
                    )
                )
        if MOBILITY_MODIFIER_LINK not in {p.link for p in params.parameters}:
            findings.append(
                Finding(
                    WARN,
                    "places",
                    f"mobility modifier {MOBILITY_MODIFIER_LINK!r} not extracted "
                    "yet — child-outcome place modifiers blocked until the "
                    "Chetty & Hendren 2018 row lands",
                )
            )

    # Generational transmission registry: unrolled copies of one
    # relationship must agree band-for-band, boundary roles cannot walk,
    # and every per-step support key must exist in the bibliography.
    for check, message in transmission_findings(params, bib):
        findings.append(Finding(ERROR, check, message))

    # Declared correlations: pairs must reference real links, the matrix
    # must be a valid correlation matrix, and every row must carry a
    # justification — a citable source for the direction, or the word
    # `declared` for a modeling-choice magnitude.
    corr_path = d / "correlations.csv"
    if corr_path.exists():
        try:
            correlations = load_correlations(corr_path)
        except Exception as e:
            correlations = []
            findings.append(Finding(ERROR, "correlation", f"correlations.csv failed to load: {e}"))
        links = {p.link for p in params.parameters}
        for c in correlations:
            crow = f"correlations.csv:{c.from_param}->{c.to_param}"
            if c.from_param not in links or c.to_param not in links:
                findings.append(
                    Finding(
                        ERROR,
                        "correlation",
                        f"{crow}: references unknown link(s) {c.from_param!r}, {c.to_param!r}",
                    )
                )
            if not (-1.0 < c.spearman < 1.0):
                findings.append(
                    Finding(
                        ERROR,
                        "correlation",
                        f"{crow}: spearman {c.spearman} outside (-1, 1) — +/-1 forces a "
                        "functional relationship between parameters, which no evidence here supports",
                    )
                )
            if not c.justification:
                findings.append(Finding(ERROR, "correlation", f"{crow}: no justification"))
            elif "declared" not in c.justification.lower() and not any(
                k in c.justification for k in links
            ):
                # Neither a declared-magnitude marker nor a scope anchor.
                has_scope = any(w in c.justification.lower() for w in ("citable", "direction"))
                if not has_scope:
                    findings.append(
                        Finding(
                            ERROR,
                            "correlation",
                            f"{crow}: justification must name a citable basis or say 'declared'",
                        )
                    )
        if correlations:
            try:
                mat = spearman_matrix(params, correlations)
                assert mat is not None
                _cholesky(mat)  # raises on non-PSD
            except Exception as e:
                findings.append(
                    Finding(ERROR, "correlation", f"correlations.csv: matrix not PSD/loadable: {e}")
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
