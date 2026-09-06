"""Parameter set, node registry, and baseline loading + DAG validation.

Every parameter row carries bib-key citations, a precision tier, a
population scope, and a unit pair that must map to a composition rule.
The DAG check rejects cycles before any compute.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, replace
from pathlib import Path

from . import units
from .citations import BibEntry, parse_bib

VALID_TIERS = {"EXACT", "EXACT-abstract", "EXACT-results", "canonical"}


@dataclass(frozen=True)
class Parameter:
    link: str
    from_node: str
    to_node: str
    point: float
    low: float
    high: float
    tier: str
    citation: str
    population_scope: str
    notes: str = ""
    dist: str = ""  # optional declared distribution; unit decides the default

    @property
    def citation_keys(self) -> list[str]:
        return [k.strip() for k in self.citation.split(";") if k.strip()]


@dataclass(frozen=True)
class ParameterSet:
    version: str
    parameters: tuple[Parameter, ...]

    def by_link(self, link: str) -> Parameter:
        for p in self.parameters:
            if p.link == link:
                return p
        raise KeyError(f"unknown link {link!r}")

    def with_param(self, link: str, point: float) -> "ParameterSet":
        """A copy with one parameter's point estimate overridden.

        Used by Monte Carlo sampling. The version degrades to a
        sampled marker (never accumulating): sampled outputs are not
        published as v-pinned.
        """
        base_version = self.version.split("-sampled")[0]
        rows = [replace(p, point=point) if p.link == link else p for p in self.parameters]
        return ParameterSet(version=f"{base_version}-sampled", parameters=tuple(rows))


@dataclass(frozen=True)
class Baseline:
    outcome: str
    unit: str
    population: str
    value: float | None
    citation: str
    source: str
    status: str
    notes: str = ""


def load(path: str | Path, version: str | None = None) -> ParameterSet:
    path = Path(path)
    if version is None:
        vfile = path.parent / "VERSION"
        version = vfile.read_text().strip() if vfile.exists() else "unversioned"
    rows: list[Parameter] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(
                Parameter(
                    link=row["link"],
                    from_node=row["from_node"],
                    to_node=row["to_node"],
                    point=float(row["point"]),
                    low=float(row["low"]),
                    high=float(row["high"]),
                    tier=row["tier"],
                    citation=row["citation"],
                    population_scope=row["population_scope"],
                    notes=row.get("notes", ""),
                    dist=row.get("dist", ""),
                )
            )
    _check_dag(rows)
    return ParameterSet(version=version, parameters=tuple(rows))


def load_nodes(path: str | Path) -> dict[str, units.Node]:
    nodes: dict[str, units.Node] = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            node = units.Node(
                name=row["node"],
                unit=row["unit"],
                description=row.get("description", ""),
            )
            nodes[node.name] = node
    return nodes


def load_baselines(path: str | Path) -> dict[str, Baseline]:
    out: dict[str, Baseline] = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["outcome"].startswith("#"):
                continue
            value = float(row["value"]) if row["value"].strip() else None
            base = Baseline(
                outcome=row["outcome"],
                unit=row["unit"],
                population=row["population"],
                value=value,
                citation=row["citation"].strip(),
                source=row["source"].strip(),
                status=row["status"].strip(),
                notes=row.get("notes", ""),
            )
            out[base.outcome] = base
    return out


def default_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "params"


def load_all(params_dir: str | Path | None = None):
    """Load the shipped parameter set + nodes + baselines + bibliography."""
    d = Path(params_dir) if params_dir else default_dir()
    return {
        "params": load(d / "parameters.csv"),
        "nodes": load_nodes(d / "nodes.csv"),
        "baselines": load_baselines(d / "baselines.csv"),
        "bib": parse_bib(d / "references.bib"),
    }


def _check_dag(rows: list[Parameter]) -> None:
    edges: dict[str, list[str]] = {}
    for r in rows:
        edges.setdefault(r.from_node, []).append(r.to_node)
    seen: set[str] = set()
    done: set[str] = set()

    def visit(node: str) -> None:
        if node in done:
            return
        if node in seen:
            raise ValueError(f"parameter DAG has a cycle at {node!r}")
        seen.add(node)
        for nxt in edges.get(node, []):
            visit(nxt)
        seen.discard(node)
        done.add(node)

    for start in list(edges):
        visit(start)
