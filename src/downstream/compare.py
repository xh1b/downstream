"""Deterministic, field-complete comparison of saved calculations and parameters."""
from __future__ import annotations

import csv
import io
import json
import math
from pathlib import Path

SCHEMA = "downstream-comparison/1"
IDENTIFIERS = ("link", "key", "outcome", "name", "id", "label", "profile_id")
QUALIFIERS = ("exposure", "population", "unit", "variant", "method", "time_window", "tercile")


def _segment(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _flatten(value, path: str = "") -> dict:
    """JSON-pointer paths; named list records survive insertion and reordering."""
    if isinstance(value, dict):
        result = {}
        for key, child in sorted(value.items()):
            result.update(_flatten(child, f"{path}/{_segment(key)}"))
        return result if value else {path: {}}
    if isinstance(value, list):
        identity = None
        if value and all(isinstance(row, dict) for row in value):
            for key in IDENTIFIERS:
                names = [row.get(key) for row in value]
                if all(isinstance(name, str) and name for name in names):
                    exposures = [row.get("exposure") for row in value]
                    if key == "outcome" and all(isinstance(name, str) and name for name in exposures):
                        if len(set(zip(names, exposures))) == len(names):
                            identity = (key, "exposure")
                            break
                    if len(set(names)) == len(names):
                        identity = (key,)
                        break
                    if key in {"link", "key", "id", "profile_id"}:
                        raise ValueError(f"duplicate {key} identifiers at {path}")
                    for qualifier in QUALIFIERS:
                        qualified = [row.get(qualifier) for row in value]
                        if all(isinstance(name, str) and name for name in qualified):
                            if len(set(zip(names, qualified))) == len(names):
                                identity = (key, qualifier)
                                break
                    if identity:
                        break
        result = {}
        for index, child in enumerate(value):
            if identity and len(identity) == 1:
                name = f"{identity[0]}={child[identity[0]]}"
            elif identity:
                name = json.dumps({key: child[key] for key in identity}, sort_keys=True,
                                  ensure_ascii=False, separators=(",", ":"))
            else:
                name = str(index)
            result.update(_flatten(child, f"{path}/{_segment(name)}"))
        return result if value else {path: []}
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"non-finite value at {path}")
    return {path: value}


def load_documents(path: str | Path) -> dict:
    """Read one JSON result or a directory of named JSON results."""
    path = Path(path)
    if path.is_dir():
        documents = {p.stem: json.loads(p.read_text(encoding="utf-8"))
                     for p in sorted(path.glob("*.json"))}
        if not documents:
            raise ValueError(f"no JSON results in {path}")
        return documents
    # Identical root name lets differently named files compare by their fields.
    return {"result": json.loads(path.read_text(encoding="utf-8"))}


def _number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def compare_documents(before: dict, after: dict, before_label: str, after_label: str) -> dict:
    old, new = _flatten(before), _flatten(after)
    rows = []
    counts = dict.fromkeys(("changed", "added", "removed", "unchanged"), 0)
    for path in sorted(old.keys() | new.keys()):
        a, b = old.get(path), new.get(path)
        if path not in old:
            status = "added"
        elif path not in new:
            status = "removed"
        elif type(a) is type(b) and a == b or _number(a) and _number(b) and a == b:
            status = "unchanged"
        else:
            status = "changed"
        delta = b - a if _number(a) and _number(b) else None
        percent = 100 * delta / abs(a) if delta is not None and a != 0 else None
        if (delta is not None and not math.isfinite(delta)) or (
            percent is not None and not math.isfinite(percent)
        ):
            raise ValueError(f"numeric difference overflow at {path}")
        counts[status] += 1
        rows.append({"path": path, "status": status, "before": a, "after": b,
                     "delta": delta, "percent_change": percent})
    return {"schema": SCHEMA, "before_label": before_label, "after_label": after_label,
            "summary": counts, "rows": rows}


def _display(value) -> str:
    if value is None:
        return "null"
    return json.dumps(value, ensure_ascii=False, allow_nan=False)


def render_comparison(report: dict, format: str = "markdown", changes_only: bool = False) -> str:
    rows = [row for row in report["rows"] if not changes_only or row["status"] != "unchanged"]
    if format == "json":
        return json.dumps({**report, "rows": rows}, indent=2, allow_nan=False) + "\n"
    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(("path", "status", "before", "after", "delta", "percent_change"))
        for row in rows:
            writer.writerow((row["path"], row["status"], _display(row["before"]),
                             _display(row["after"]), row["delta"], row["percent_change"]))
        return output.getvalue()
    if format != "markdown":
        raise ValueError(f"unknown comparison format: {format}")

    def cell(value):
        # Keep untrusted result strings inert in Markdown/HTML summaries.
        return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(
            ">", "&gt;").replace("|", "&#124;").replace("`", "&#96;").replace(
            "\r", " ").replace("\n", " ")

    lines = [f"# Version comparison: {cell(report['before_label'])} → {cell(report['after_label'])}",
             "", ", ".join(f"{count} {status}" for status, count in report["summary"].items()),
             "", "Delta = after − before. Percent = 100 × delta / |before|; undefined at zero.",
             "Values include calculation outputs, inputs, and provenance; paths identify each field.",
             "", "| Field | Status | Before | After | Delta | Change (%) |",
             "| --- | --- | --- | --- | --- | --- |"]
    for row in rows:
        values = (row["path"], row["status"], _display(row["before"]), _display(row["after"]),
                  "—" if row["delta"] is None else _display(row["delta"]),
                  "—" if row["percent_change"] is None else _display(row["percent_change"]))
        lines.append("| " + " | ".join(cell(value) for value in values) + " |")
    return "\n".join(lines) + "\n"
