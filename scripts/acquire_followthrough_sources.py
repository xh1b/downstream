"""Acquire public reference data with immutable local files and hash provenance.

This is a source-download CLI, not parameter admission. Raw public data are
gitignored; the manifest is reviewable and sufficient to re-fetch the files.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "cps2024": ("https://www2.census.gov/programs-surveys/cps/datasets/2024/supp/jan24pub.zip", "jan24pub.zip"),
    "cps2024_dictionary": ("https://www2.census.gov/programs-surveys/cps/techdocs/cpsjan24.pdf", "cpsjan24.pdf"),
    "oreopoulos2008": ("https://poverty.ucdavis.edu/sites/main/files/file-attachments/stevens_2008jole.pdf", "oreopoulos2008.pdf"),
    "sullivan2007": ("https://www.nber.org/system/files/working_papers/w13626/w13626.pdf", "sullivan2007.pdf"),
    "browning2011": ("https://www.vive.dk/media/pure/yxd91ozg/2078384", "browning2011.pdf"),
    "eliason2009": ("https://citeseerx.ist.psu.edu/document?doi=4ac77bd406711c5906c0b113650198430b8fae35&repid=rep1&type=pdf", "eliason2009.pdf"),
}


def acquire(source: str, output: Path) -> dict:
    url, filename = SOURCES[source]
    target = output / filename
    output.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        request = Request(url, headers={"User-Agent": "downstream-public-research/0.5"})
        content = urlopen(request, timeout=60).read()
        if not content.startswith((b"%PDF", b"PK")):
            raise ValueError(f"{source}: expected PDF or ZIP, received another content type")
        with target.open("xb") as handle:
            handle.write(content)
    content = target.read_bytes()
    return {"source_id": source, "url": url, "path": str(target.relative_to(ROOT)),
            "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content),
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "status": "acquired_not_parameter_admitted"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", nargs="+", choices=tuple(SOURCES))
    args = parser.parse_args()
    manifest = ROOT / "validation" / "followthrough_sources.json"
    existing = json.loads(manifest.read_text()) if manifest.exists() else {"sources": {}}
    for source in args.sources:
        row = acquire(source, ROOT / "data" / "followthrough")
        previous = existing["sources"].get(source)
        if previous and previous["sha256"] != row["sha256"]:
            raise ValueError(f"{source}: immutable acquired source hash changed")
        existing["sources"][source] = previous or row
        manifest.write_text(json.dumps(existing, indent=2) + "\n")
        print(source, row["bytes"], row["sha256"], flush=True)


if __name__ == "__main__":
    main()
