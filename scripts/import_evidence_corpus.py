#!/usr/bin/env python3
"""Import locally acquired PDFs into the reproducible evidence registry.

This is a mechanical import, not evidence extraction.  Each record is marked
``unreviewed`` until a researcher records the estimand, uncertainty, scope,
and graph-overlap decision under docs/CITING.md.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
from pathlib import Path


FIELDS = (
    "corpus_id",
    "source_url",
    "sha256",
    "pages",
    "text_extractable",
    "retrieval_status",
    "screening_status",
    "import_status",
    "local_filename",
)

# The first acquisition wave used descriptive filenames before we standardized
# on NBER working-paper identifiers.  Keep their immutable retrieval routes in
# the registry rather than degrading those rows to local-only files.
DESCRIPTIVE_SOURCES = {
    "bhuller2016_incarceration_recidivism_employment": "https://www.nber.org/system/files/working_papers/w22648/w22648.pdf",
    "bhuller2018_incarceration_spillovers": "https://www.nber.org/system/files/working_papers/w24227/w24227.pdf",
    "black2005_birth_weight_adult_outcomes": "https://www.nber.org/system/files/working_papers/w11796/w11796.pdf",
    "butikofer2023_parental_mental_health": "https://www.nber.org/system/files/working_papers/w31446/w31446.pdf",
    "cabral2020_school_shootings": "https://www.nber.org/system/files/working_papers/w28311/w28311.pdf",
    "case2003_childhood_health_circumstance": "https://www.nber.org/system/files/working_papers/w9788/w9788.pdf",
    "case2010_early_life_health": "https://www.nber.org/system/files/working_papers/w15637/w15637.pdf",
    "chetty2015_moving_to_opportunity": "https://www.nber.org/system/files/working_papers/w21156/w21156.pdf",
    "chetty2016_childhood_environment_gender_gaps": "https://www.nber.org/system/files/working_papers/w21936/w21936.pdf",
    "chettyhendren2016_childhood_exposure": "https://www.nber.org/system/files/working_papers/w23001/w23001.pdf",
    "deryugina2014_katrina_economic_impact": "https://www.nber.org/system/files/working_papers/w20713/w20713.pdf",
    "deryugina2018_katrina_mortality": "https://www.nber.org/system/files/working_papers/w24822/w24822.pdf",
    "dobbie2018_parental_incarceration": "https://www.nber.org/system/files/working_papers/w24186/w24186.pdf",
    "dobkin2016_hospital_admissions": "https://www.nber.org/system/files/working_papers/w22288/w22288.pdf",
    "coile2004_health_shocks_couples": "https://www.nber.org/system/files/working_papers/w10810/w10810.pdf",
    "collinson2025_eviction_children": "https://www.nber.org/system/files/working_papers/w33659/w33659.pdf",
    "currie2007_childhood_mental_health_human_capital": "https://www.nber.org/system/files/working_papers/w13217/w13217.pdf",
    "deshpande2019_disability_financial_distress": "https://www.nber.org/system/files/working_papers/w25642/w25642.pdf",
    "garces2000_head_start_long_term": "https://www.nber.org/system/files/working_papers/w8054/w8054.pdf",
    "gensowski2018_childhood_polio": "https://www.nber.org/system/files/working_papers/w24753/w24753.pdf",
    "gruber2000_unilateral_divorce": "https://www.nber.org/system/files/working_papers/w7968/w7968.pdf",
    "humphries2019_eviction_poverty": "https://www.nber.org/system/files/working_papers/w26139/w26139.pdf",
    "isen2014_clean_air_act": "https://www.nber.org/system/files/working_papers/w19858/w19858.pdf",
    "johnston2025_divorce_family_arrangements": "https://www.nber.org/system/files/working_papers/w33776/w33776.pdf",
    "lochner2001_education_crime": "https://www.nber.org/system/files/working_papers/w8605/w8605.pdf",
}


def nber_url(stem: str) -> str:
    """Return the stable NBER PDF address when the local filename is wNNNNN."""
    if stem.startswith("w") and stem[1:].isdigit():
        return f"https://www.nber.org/system/files/working_papers/{stem}/{stem}.pdf"
    return DESCRIPTIVE_SOURCES.get(stem, "")


def pages(path: Path) -> int:
    result = subprocess.run(
        ["pdfinfo", str(path)], capture_output=True, text=True, check=True
    )
    for line in result.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    raise ValueError(f"pdfinfo reported no page count for {path}")


def text_extractable(path: Path) -> bool:
    result = subprocess.run(
        ["pdftotext", "-f", "1", "-l", "1", str(path), "-"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and bool(result.stdout.strip())


def screened_ids(findings: Path | None) -> set[str]:
    if findings is None or not findings.exists():
        return set()
    with findings.open(newline="", encoding="utf-8") as handle:
        return {row["corpus_id"] for row in csv.DictReader(handle)}


def build_rows(corpus: Path, screened: set[str] | None = None) -> list[dict[str, str]]:
    screened = screened or set()
    rows: list[dict[str, str]] = []
    for paper in sorted(corpus.glob("*.pdf")):
        digest = hashlib.sha256(paper.read_bytes()).hexdigest()
        rows.append(
            {
                "corpus_id": paper.stem,
                "source_url": nber_url(paper.stem),
                "sha256": digest,
                "pages": str(pages(paper)),
                "text_extractable": str(text_extractable(paper)).lower(),
                "retrieval_status": "verified_pdf",
                "screening_status": "screened" if paper.stem in screened else "unreviewed",
                "import_status": "finding_recorded" if paper.stem in screened else "acquired",
                "local_filename": paper.name,
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--findings", type=Path)
    args = parser.parse_args()
    rows = build_rows(args.corpus, screened_ids(args.findings))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"imported {len(rows)} PDFs into {args.output}")


if __name__ == "__main__":
    main()
