"""Parameter set loading and DAG validation.

Every parameter row carries its citation, precision tier, and
population scope. The DAG check rejects cycles before any compute.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


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


@dataclass(frozen=True)
class ParameterSet:
    version: str
    parameters: tuple[Parameter, ...]

    def by_link(self, link: str) -> Parameter:
        for p in self.parameters:
            if p.link == link:
                return p
        raise KeyError(f"unknown link {link!r}")


def load(path: str | Path, version: str = "v0") -> ParameterSet:
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
                )
            )
    _check_dag(rows)
    return ParameterSet(version=version, parameters=tuple(rows))


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
