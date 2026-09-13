"""Parameter set, node registry, and baseline loading + DAG validation.

Every parameter row carries bib-key citations, a precision tier, a
population scope, and a unit pair that must map to a composition rule.
The DAG check rejects cycles before any compute.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass, replace
from pathlib import Path

from . import units
from .citations import parse_bib

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


@dataclass(frozen=True)
class Correlation:
    """A declared rank correlation between two parameter rows.

    Row shape: from_param,to_param,spearman,justification. The
    justification must cite a source for the DIRECTION or say
    `declared` outright — a bare number is rejected by the audit.
    """

    from_param: str
    to_param: str
    spearman: float
    justification: str = ""


def load_correlations(path: str | Path) -> list[Correlation]:
    """Read params/correlations.csv; comment lines start with #."""
    out: list[Correlation] = []
    with open(path, newline="", encoding="utf-8") as f:
        lines = [ln for ln in f if not ln.lstrip().startswith("#")]
    for row in csv.DictReader(lines):
        out.append(
            Correlation(
                from_param=row["from_param"].strip(),
                to_param=row["to_param"].strip(),
                spearman=float(row["spearman"]),
                justification=row.get("justification", "").strip(),
            )
        )
    return out


def spearman_matrix(params: "ParameterSet", correlations: list[Correlation]) -> list[list[float]] | None:
    """Map declared pairs onto the parameter-set row order.

    Returns None when no pair applies, so callers can skip the
    Iman-Conover pass entirely.
    """
    idx = {p.link: i for i, p in enumerate(params.parameters)}
    n = len(idx)
    mat = [[0.0] * n for _ in range(n)]
    for i in range(n):
        mat[i][i] = 1.0
    hit = False
    for c in correlations:
        a, b = idx.get(c.from_param), idx.get(c.to_param)
        if a is None or b is None:
            raise KeyError(
                f"correlation references unknown link(s): {c.from_param!r}, {c.to_param!r}"
            )
        mat[a][b] = c.spearman
        mat[b][a] = c.spearman
        hit = True
    return mat if hit else None


def load(path: str | Path, version: str | None = None) -> ParameterSet:
    path = Path(path)
    if version is None:
        vfile = path.parent / "VERSION"
        version = vfile.read_text().strip() if vfile.exists() else "unversioned"
    rows: list[Parameter] = []
    seen: set[str] = set()
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            p = Parameter(
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
            if not p.link or p.link in seen:
                raise ValueError(f"duplicate or empty parameter link {p.link!r}")
            # Admission contract: a row without its extraction tier,
            # citation, or studied population is missing metadata, not
            # support. Blank fields are refused here rather than flowing
            # into steps that would read as endorsed evidence.
            blank = [f for f in ("tier", "citation", "population_scope")
                     if not getattr(p, f).strip()]
            if blank:
                raise ValueError(
                    f"parameter {p.link!r} has blank support metadata: {', '.join(blank)}"
                )
            if not all(math.isfinite(v) for v in (p.point, p.low, p.high)):
                raise ValueError(f"parameter {p.link!r} has non-finite values")
            if not p.low <= p.point <= p.high:
                raise ValueError(f"parameter {p.link!r} point lies outside its band")
            seen.add(p.link)
            rows.append(p)
    _check_dag(rows)
    return ParameterSet(version=version, parameters=tuple(rows))


def load_nodes(path: str | Path) -> dict[str, units.Node]:
    nodes: dict[str, units.Node] = {}
    known_units = {value for name, value in vars(units).items() if name.isupper() and isinstance(value, str)}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            node = units.Node(
                name=row["node"],
                unit=row["unit"],
                description=row.get("description", ""),
            )
            if not node.name or node.name in nodes:
                raise ValueError(f"duplicate or empty node {node.name!r}")
            if node.unit not in known_units:
                raise ValueError(f"node {node.name!r} has unknown unit {node.unit!r}")
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
            if not base.outcome or base.outcome in out:
                raise ValueError(f"duplicate or empty baseline outcome {base.outcome!r}")
            if base.status not in ("verified", "pending"):
                raise ValueError(
                    f"baseline {base.outcome!r} has unknown status {base.status!r}; "
                    "expected 'verified' or 'pending'"
                )
            if base.value is not None and not math.isfinite(base.value):
                raise ValueError(f"baseline {base.outcome!r} has non-finite value")
            # Admission contract: a verified row is what count conversions
            # are built on, so it must pin its value and name its citation
            # and studied population before it can support anything.
            if base.status == "verified":
                missing = [name for name in ("citation", "population")
                           if not getattr(base, name)]
                if base.value is None:
                    missing.append("value")
                if missing:
                    raise ValueError(
                        f"verified baseline {base.outcome!r} is missing "
                        f"{', '.join(missing)}; pin them before computing counts"
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
