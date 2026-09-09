"""Reproduce GAO-05-138 Appendix II's civilian-job exposure inventory.

These are base jobs, not estimates of community spillovers. Created jobs
are redevelopment counts and cannot score a causal service-job multiplier.
"""
from __future__ import annotations

import csv
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.request import urlopen

SOURCE = "https://www.gao.gov/assets/a245059.html"


class _Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def parse(raw: bytes):
    parser = _Text()
    parser.feed(raw.decode("utf-8"))
    text = " ".join(parser.parts)
    pattern = (r"Major base:\s*(.*?);\s*BRAC round:\s*(\d{4});\s*"
               r"Estimated jobs lost:\s*([\d,]+);\s*Estimated jobs created:\s*([\d,]+);\s*"
               r"Recovery \(percent\):\s*([\d,]+)\.")
    rows = [dict(base=" ".join(name.split()), round=int(year),
                 civilian_jobs_lost=int(lost.replace(",", "")),
                 redevelopment_jobs_created=int(created.replace(",", "")),
                 recovery_percent=int(recovery.replace(",", "")))
            for name, year, lost, created, recovery in re.findall(pattern, text)]
    if (len(rows), sum(r['civilian_jobs_lost'] for r in rows),
            sum(r['redevelopment_jobs_created'] for r in rows)) != (73, 129649, 92921):
        raise ValueError("GAO Table 3 row count or published totals do not reconcile")
    return rows


def build(destination, source_file=None):
    if source_file:
        raw = Path(source_file).read_bytes()
    else:
        with urlopen(SOURCE, timeout=60) as response:
            raw = response.read()
    rows = parse(raw)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    path = destination / "brac_gao05138_civilian_jobs.csv"
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    provenance = {"source": SOURCE, "table": "Appendix II, Table 3",
                  "as_of": "2003-10-31", "source_sha256": hashlib.sha256(raw).hexdigest(),
                  "capture": "saved accessible-text excerpt" if source_file else "HTTP HTML response",
                  "rows": len(rows), "civilian_jobs_lost": 129649,
                  "redevelopment_jobs_created": 92921,
                  "limitation": "Base civilian jobs only. Not a measured causal community spillover.",
                  "validation_status": "exposure inventory only; geography/window alignment and causal measured side still required"}
    path.with_suffix(".provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    return provenance


if __name__ == "__main__":
    import argparse
    cli = argparse.ArgumentParser()
    cli.add_argument("--out", required=True)
    cli.add_argument("--input", help="saved accessible text or HTML when direct download is unavailable")
    args = cli.parse_args()
    print(json.dumps(build(args.out, args.input), indent=2))
