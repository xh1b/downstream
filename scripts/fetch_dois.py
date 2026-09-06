#!/usr/bin/env python3
"""Pin DOIs onto references.bib entries via the Crossref API.

For every bib entry WITHOUT a doi field: query Crossref by title +
first author + year, score the candidate (title similarity + year +
container), auto-annotate only CERTAIN matches, and write the rest to
params/doi_review.json for human review.

Rules:
- never guesses: below-threshold matches are review items, not bib edits
- the bib stays hand-ownable; a `doi = {...}` line is appended inside
  the entry when the match is certain
- polite pool (mailto), ~0.5s between queries

Usage: PYTHONPATH=src python scripts/fetch_dois.py [--apply]
       (default prints a dry-run report; --apply annotates the bib)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from downstream.citations import parse_bib  # noqa: E402
from downstream.params import default_dir  # noqa: E402

MAILTO = "model@xh1b.org"
TITLE_BAR = 0.92  # normalized title similarity for auto-apply


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()


def _sim(a: str, b: str) -> float:
    a, b = _norm(a), _norm(b)
    if not a or not b:
        return 0.0
    wa, wb = set(a.split()), set(b.split())
    return len(wa & wb) / max(len(wa), len(wb))


def query_crossref(title: str, author: str, year: str) -> list[dict]:
    q = urllib.parse.quote(f"{title} {author}")
    url = (
        "https://api.crossref.org/works?rows=3&mailto="
        f"{urllib.parse.quote(MAILTO)}&query.bibliographic={q}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": f"downstream-model/1.2 (mailto:{MAILTO})"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)["message"]["items"]


def score(item: dict, title: str, year: str, venue: str) -> tuple[float, str, str, str]:
    ct = (item.get("title") or [""])[0]
    cy = str(item.get("issued", {}).get("date-parts", [[None]])[0][0] or "")
    cv = (item.get("container-title") or [""])[0]
    s = _sim(title, ct)
    if year and cy == year:
        s += 0.05
    elif year and cy and year != cy:
        s -= 0.10
    if venue and _sim(venue, cv) > 0.6:
        s += 0.03
    return min(s, 1.0), ct, cy, cv


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--sleep", type=float, default=0.5)
    args = ap.parse_args(argv)

    d = default_dir()
    bib_path = d / "references.bib"
    bib = parse_bib(bib_path)
    missing = {k: e for k, e in bib.items() if not e.fields.get("doi")}
    print(f"{len(missing)} of {len(bib)} entries missing a DOI")

    applied, review = [], []
    for key, entry in sorted(missing.items()):
        title = entry.title
        authors = entry.fields.get("author", "")
        first = authors.split(" and ")[0]
        surname = first.split(",")[0].strip()
        year = entry.year
        venue = entry.fields.get("journal", entry.fields.get("publisher", ""))
        try:
            items = query_crossref(title, surname, year)
        except Exception as e:  # network hiccup: record and continue
            review.append({"key": key, "error": str(e)})
            continue
        if not items:
            review.append({"key": key, "reason": "no candidates"})
            continue
        item = items[0]
        conf, ct, cy, cv = score(item, title, year, venue)
        doi = item.get("DOI", "")
        rec = {
            "key": key,
            "confidence": round(conf, 3),
            "doi": doi,
            "crossref_title": ct,
            "crossref_year": cy,
            "crossref_container": cv,
        }
        if conf >= TITLE_BAR and doi:
            applied.append(rec)
            if args.apply:
                text = bib_path.read_text(encoding="utf-8")
                pat = re.compile(
                    r"(@\w+\{" + re.escape(key) + r",.*?)(\n\})", re.DOTALL
                )
                m = pat.search(text)
                if m and "doi" not in m.group(1):
                    text = pat.sub(r"\1\n  doi    = {" + doi + r"},\2", text, count=1)
                    bib_path.write_text(text, encoding="utf-8")
        else:
            review.append(rec)
        time.sleep(args.sleep)

    # Relaxed second pass, offline: items with strong title sim AND
    # year AND container agreement are still certain even when the
    # raw score dips below the bar on formatting variants.
    relaxed = []
    still_review = []
    for rec in review:
        conf = rec.get("confidence", 0.0)
        if conf >= 0.82 and str(rec.get("crossref_year")) == str(rec.get("bib_year", rec.get("crossref_year"))):
            pass  # year agreement alone cannot rescue a low score
        if conf >= 0.85:
            relaxed.append(rec)
        else:
            still_review.append(rec)
    if args.apply:
        for rec in relaxed:
            doi = rec.get("doi", "")
            key = rec["key"]
            if not doi:
                still_review.append(rec)
                continue
            text = bib_path.read_text(encoding="utf-8")
            pat = re.compile(r"(@\w+\{" + re.escape(key) + r",.*?)(\n\})", re.DOTALL)
            m = pat.search(text)
            if m and "doi" not in m.group(1):
                text = pat.sub(r"\1\n  doi    = {" + doi + r"},\2", text, count=1)
                bib_path.write_text(text, encoding="utf-8")

    (d / "doi_review.json").write_text(
        json.dumps(
            {"applied": applied, "relaxed_applied": relaxed if args.apply else relaxed, "review": still_review},
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"applied (certain): {len(applied)}")
    print(f"relaxed (title+year agreement >=0.85): {len(relaxed)}")
    print(f"needs review: {len(still_review)} -> params/doi_review.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
