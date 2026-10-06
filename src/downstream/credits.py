"""The credits engine: who built this model?

The model's authority is borrowed, and the loans are itemized. Every
parameter traces to named researchers; the methodology traces to named
statisticians. This module computes the collective from references.bib
— the "incorporates the work of N researchers" claim is machine-
generated and therefore always exact and reproducible, an attribution index, not a count of independently verified researchers.

Roles (derived from where a key is cited):
  parameter   — cited by params/parameters.csv (the evidence base)
  baseline    — named in params/baselines.csv
  methodology — modeling/verification craft (LHS, Sobol, scoring...)
  context     — in references.bib, shaping the framing and honesty rows
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .citations import BibEntry
from .params import default_dir


@dataclass
class Researcher:
    name: str          # "Surname, Initials" as parsed
    surname: str
    entries: list[str]  # bib keys


def _clean_latex(s: str) -> str:
    s = re.sub(r"\{\\['`^\"=.](\w)\}", r"\1", s)
    s = s.replace("\\'", "").replace("\\`", "")
    return s.replace("{", "").replace("}", "").strip()


def parse_authors(field: str) -> list[str]:
    """BibTeX author field -> normalized person/org names.

    Splits on ' and '. Braced groups are corporate authors and stay
    whole ('{World Bank}'). 'others' is dropped (et al. carries no
    name to credit).
    """
    names: list[str] = []
    depth, start, raw_names = 0, 0, []
    for i, char in enumerate(field):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        elif depth == 0 and field.startswith(" and ", i):
            raw_names.append(field[start:i])
            start = i + 5
    raw_names.append(field[start:])
    for raw in raw_names:
        raw = _clean_latex(raw)
        name = raw.strip()
        if not name or name.lower() == "others":
            continue
        names.append(re.sub(r"\s+", " ", name))
    return names


def _surname(name: str) -> str:
    # "Surname, Initials" form first; else last token ("Sobol', Ilya M." hits the comma form)
    if "," in name:
        return name.split(",")[0].strip()
    parts = name.split()
    return parts[-1] if parts else name


def collect(bib: dict[str, BibEntry], params_dir: Path | None = None) -> dict:
    d = Path(params_dir) if params_dir else default_dir()

    parameter_keys: set[str] = set()
    import csv as _csv

    with open(d / "parameters.csv", newline="", encoding="utf-8") as f:
        for row in _csv.DictReader(f):
            for k in row["citation"].split(";"):
                if k.strip():
                    parameter_keys.add(k.strip())

    baseline_keys: set[str] = set()
    with open(d / "baselines.csv", newline="", encoding="utf-8") as f:
        for row in _csv.DictReader(f):
            if row["outcome"].startswith("#"):
                continue
            for k in row["citation"].split(";"):
                if k.strip():
                    baseline_keys.add(k.strip())

    researchers: dict[str, Researcher] = {}
    studies = []
    for key, entry in bib.items():
        for name in parse_authors(entry.fields.get("author", "")):
            sur = _surname(name)
            # Full names distinguish unrelated authors with a common surname.
            aliases = {"Autor, David": "Autor, David H.", "Hanson, Gordon": "Hanson, Gordon H.",
                       "Conover, W. J.": "Conover, William J.", "Sullivan, Daniel": "Sullivan, Daniel G."}
            name = aliases.get(name, name)
            identity = re.sub(r"[^\w]", "", name).casefold()
            r = researchers.setdefault(identity, Researcher(name=name, surname=sur, entries=[]))
            if key not in r.entries:
                r.entries.append(key)

    def role(key: str) -> str:
        if key in parameter_keys:
            return "parameter"
        if key in baseline_keys:
            return "baseline"
        if key in {
            "mckay1979", "iman1982", "saltelli2002", "sobol2001",
            "hersbach2000", "gneiting2007", "gigerenzer2002",
        }:
            return "methodology"
        return "context"

    years = [int(e.year) for e in bib.values() if e.year.isdigit()]

    studies = [
        {
            "key": key,
            "title": entry.title,
            "year": entry.year,
            "authors": parse_authors(entry.fields.get("author", "")),
            "venue": entry.fields.get("journal", entry.fields.get("publisher", "")),
            "evidence": entry.evidence,
            "role": role(key),
            "doi": entry.fields.get("doi", ""),
        }
        for key, entry in sorted(bib.items())
    ]

    return {
        "bib_entries": len(bib),
        "studies": studies,
        "researchers": sorted(
            ({"name": r.name, "surname": r.surname, "entries": r.entries} for r in researchers.values()),
            key=lambda x: x["surname"].lower(),
        ),
        "parameter_keys": sorted(parameter_keys),
        "baseline_keys": sorted(baseline_keys),
        "year_min": min(years) if years else None,
        "year_max": max(years) if years else None,
    }


def attribution_sentences(data: dict) -> list[str]:
    """The computed claims — every public surface must use THESE
    numbers, never a rounded-up paraphrase."""
    n_studies = data["bib_entries"]
    n_researchers = len(data["researchers"])
    param_studies = {s["key"] for s in data["studies"] if s["role"] == "parameter"}
    param_researchers = {
        r["name"]
        for r in data["researchers"]
        if set(r["entries"]) & param_studies
    }
    years = f'{data["year_min"]}-{data["year_max"]}'
    return [
        (
            f"The bibliography contains {n_studies} sources and {n_researchers} named "
            f"author records (people and organizations), {years}."
        ),
        (
            f"The parameters cite {len(param_studies)} sources with "
            f"{len(param_researchers)} named author records; these are not counts of independent research teams."
        ),
        (
            "The bibliography includes research, methods and context sources; inclusion does not establish peer review or independent validation. Modeled numbers carry their cited inputs and declared structural assumptions."
        ),
    ]


def write_credits_md(data: dict, path: Path) -> str:
    sents = attribution_sentences(data)
    lines = [
        "# CREDITS — the collective this model is built from",
        "",
        "> Generated by `downstream credits --write`. Do not edit by hand;",
        "> the numbers are computed from params/references.bib.",
        "",
        "## The claim, computed",
        "",
    ]
    lines += [f"- {s}" for s in sents]
    lines += ["", "## The researchers", ""]
    param_studies = {s["key"] for s in data["studies"] if s["role"] == "parameter"}
    for r in data["researchers"]:
        marked = [f"{k}*" for k in r["entries"] if k in param_studies]
        rest = [k for k in r["entries"] if k not in param_studies]
        lines.append(f"- **{r['name']}** — {', '.join(marked + rest)}")
    lines += [
        "",
        "\\* parameter-source study (its estimate is inside the model).",
        "",
        "## The studies",
        "",
        "| key | authors | year | venue | role | evidence | doi |",
        "|:---|:---|:---|:---|:---|:---|:---|",
    ]
    for s in data["studies"]:
        auth = "; ".join(s["authors"][:3]) + (" et al." if len(s["authors"]) > 3 else "")
        lines.append(
            f"| {s['key']} | {auth} | {s['year']} | {s['venue']} | {s['role']} | "
            f"{s['evidence']} | {s['doi'] or '-'} |"
        )
    text = "\n".join(lines) + "\n"
    path.write_text(text, encoding="utf-8")
    return text


def update_readme_attribution(data, path):
    """Refresh the bounded generated attribution block in the README."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    block = "<!-- BEGIN GENERATED ATTRIBUTION -->\n" + "\n\n".join(attribution_sentences(data)) + "\n\nSee [CREDITS.md](CREDITS.md) for the complete attribution record.\n<!-- END GENERATED ATTRIBUTION -->"
    pattern = r"<!-- BEGIN GENERATED ATTRIBUTION -->.*?<!-- END GENERATED ATTRIBUTION -->"
    if re.search(pattern, text, re.S):
        text = re.sub(pattern, lambda _: block, text, flags=re.S)
    else:
        text = re.sub(r"The parameter set \(v1\.48\).*?full credit record\.", lambda _: block, text, flags=re.S)
    path.write_text(text, encoding="utf-8")
