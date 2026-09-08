"""Version-stamped parameter-set snapshot export.

The downstream repo is LOCAL-ONLY (owner decision 2026-09-06): production
never imports this engine. It consumes the exported snapshot instead —
pinned in the parent repo together with an engine snapshot, one version
stamp end to end (params VERSION == snapshot version == cached
algo_version == page display, ENTITY_ANALYSIS.md §3).

Determinism: the snapshot carries NO timestamps. Same params tree + same
version = same bytes; provenance is anchored by the consuming side and by
the git commit of the exported file.

The export refuses to build while `downstream audit` reports ERRORs — a
broken parameter set must never ship as a pinned artifact. WARNs (staging
area, uncited bib entries) do not block: they are the standing state of a
living queue.
"""

from __future__ import annotations

import json
from pathlib import Path

from .audit import ERROR, audit
from .params import default_dir, load_all

SCHEMA = "downstream-parameter-set/1"


def build(params_dir: str | Path | None = None) -> dict:
    """The full export document for the parameter set."""
    d = Path(params_dir) if params_dir else default_dir()
    all_ = load_all(d)
    params = all_["params"]
    nodes = all_["nodes"]
    baselines = all_["baselines"]
    bib = all_["bib"]

    blocking = [f for f in audit(d) if f.severity == ERROR]
    if blocking:
        lines = "\n".join(f"  - [{f.check}] {f.message}" for f in blocking)
        raise ValueError(f"audit errors block export ({len(blocking)}):\n{lines}")

    cited: set[str] = set()
    for p in params.parameters:
        cited.update(p.citation_keys)
    return {
        "schema": SCHEMA,
        "version": params.version,
        "parameters": [
            {
                "link": p.link,
                "from_node": p.from_node,
                "to_node": p.to_node,
                "point": p.point,
                "low": p.low,
                "high": p.high,
                "tier": p.tier,
                "citation": p.citation,
                "population_scope": p.population_scope,
                "notes": p.notes,
                "dist": p.dist,
            }
            for p in params.parameters
        ],
        "nodes": [
            {"name": n.name, "unit": n.unit, "description": n.description}
            for n in nodes.values()
        ],
        "baselines": [
            {
                "outcome": b.outcome,
                "unit": b.unit,
                "population": b.population,
                "value": b.value,
                "citation": b.citation,
                "source": b.source,
                "status": b.status,
                "notes": b.notes,
            }
            for b in baselines.values()
        ],
        "citations": {
            key: {
                "evidence": bib[key].evidence,
                "year": bib[key].year,
                "title": bib[key].title,
                "doi": bib[key].fields.get("doi", ""),
            }
            for key in sorted(cited)
        },
    }


def dumps(params_dir: str | Path | None = None) -> str:
    return json.dumps(build(params_dir), indent=2, sort_keys=False) + "\n"


def write(path: str | Path, params_dir: str | Path | None = None) -> int:
    """Write the snapshot; returns the parameter-row count."""
    doc = build(params_dir)
    Path(path).write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return len(doc["parameters"])
