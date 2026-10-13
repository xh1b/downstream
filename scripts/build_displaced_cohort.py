"""Reproduce a frozen CPS January-2024 long-tenured displacement reference cohort.

Age and household structure are measured at interview, not retrospectively at
job loss. Survey weights describe the reference population, not an H-1B cohort.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
# One-based inclusive positions, Census January-2024 dictionary.
FIELDS = {"PRTAGE": (122, 123), "PESEX": (129, 130), "PEMARITL": (125, 126),
          "PESD2": (1003, 1004), "PESD3": (1005, 1006),
          "PRSDIND": (1019, 1020), "PTSD18TN": (1217, 1220),
          "PRDISPWK": (1221, 1222), "PWSUPWGT": (1191, 1200),
          "PRCHLD": (633, 634), "PRNMCHLD": (635, 636),
          "PRSLWKLY": (1128, 1133)}


def decode(line: str) -> dict[str, int]:
    if len(line.rstrip("\r\n")) < 1222:
        raise ValueError("truncated CPS supplement record")
    out = {}
    for name, (a, b) in FIELDS.items():
        value = float(line[a-1:b])
        if not math.isfinite(value) or not value.is_integer():
            raise ValueError(f"invalid integral CPS field {name}")
        out[name] = int(value)
    return out


def weighted_median(pairs):
    if not pairs:
        return None
    total = sum(w for _, w in pairs)
    cumulative = 0.0
    for value, weight in sorted(pairs):
        cumulative += weight
        if cumulative >= total / 2:
            return value


def summarize(rows, minimum_tenure=3):
    selected = [r for r in rows if r["PRDISPWK"] == 1 and r["PESD3"] in (1, 2, 3) and
                r["PTSD18TN"] >= minimum_tenure * 100 and r["PWSUPWGT"] > 0]
    if not selected:
        raise ValueError("no eligible displaced workers")
    summaries = {name: defaultdict(float) for name in
                 ("sex_age", "industry_lost_job", "reason", "tenure", "marital_status",
                  "own_children_under_18", "own_child_age_categories")}
    ages, earnings = [], []
    total = 0.0
    for r in selected:
        w = r["PWSUPWGT"] / 10000
        total += w
        age = r["PRTAGE"]
        band = "20-24" if age < 25 else "25-34" if age < 35 else "35-44" if age < 45 else "45-54" if age < 55 else "55-64" if age < 65 else "65+"
        sex = {1: "Male", 2: "Female"}.get(r["PESEX"], "unknown")
        summaries["sex_age"][f"{sex}:{band}"] += w
        summaries["industry_lost_job"][str(r["PRSDIND"])] += w
        summaries["reason"][str(r["PESD2"])] += w
        summaries["tenure"]["3-5" if r["PTSD18TN"] < 600 else "6-9" if r["PTSD18TN"] < 1000 else "10+"] += w
        for field, source in (("marital_status", "PEMARITL"),
                              ("own_children_under_18", "PRNMCHLD"),
                              ("own_child_age_categories", "PRCHLD")):
            summaries[field][str(r[source]) if r[source] >= 0 else "not_in_universe_or_missing"] += w
        ages.append((age, w))
        if r["PRSLWKLY"] >= 0:
            earnings.append((r["PRSLWKLY"] / 100, w))
    return {"schema": "downstream-reference-cohort/1", "dataset": "CPS January 2024 displacement supplement",
            "inclusion": f"PRDISPWK=1; known loss year PESD3 in 1,2,3; lost-job tenure PTSD18TN/100 >= {minimum_tenure}; positive PWSUPWGT/10000",
            "displacement_years": "2021-2023", "interview_date": "2024-01",
            "raw_sample_n": len(selected), "weighted_workers": total,
            "age_median_at_interview": weighted_median(ages),
            "lost_job_weekly_earnings_median_nominal": weighted_median(earnings),
            "earnings_observed_weight_share": sum(w for _, w in earnings)/total,
            "weighted_counts": {name: dict(sorted(values.items())) for name, values in summaries.items()},
            "sex_age_shares": {key: value/total for key, value in sorted(summaries["sex_age"].items())},
            "limitations": ["Reference cohort, not an identified H-1B-displacement population.",
                            "Interview age and family structure may differ from those at displacement; no retrospective child ages are invented.",
                            "Public ages are topcoded from 80; earnings are topcoded/allocated and in nominal lost-job dollars.",
                            "Unknown/NIU family responses are retained, never assigned zero children.",
                            "Survey sampling variance is not inferred from an ordinary random-sample formula.",
                            "The BLS >=3-year tenure definition differs from the source mortality study's stable-employment restrictions."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--minimum-tenure", type=int, choices=(3, 6), default=3)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    raw = ROOT / "data/followthrough/jan24pub.zip"
    manifest = json.loads((ROOT / "validation/followthrough_sources.json").read_text())
    digest = hashlib.sha256(raw.read_bytes()).hexdigest()
    if digest != manifest["sources"]["cps2024"]["sha256"]:
        raise ValueError("CPS input does not match pinned source")
    with ZipFile(raw) as archive, archive.open("jan24pub.dat") as handle:
        result = summarize((decode(line.decode("ascii")) for line in handle), args.minimum_tenure)
    result["provenance"] = {"sha256": digest, "source_url": manifest["sources"]["cps2024"]["url"],
                            "dictionary_sha256": manifest["sources"]["cps2024_dictionary"]["sha256"]}
    # Independent published benchmark; tolerance reflects rounded thousands,
    # not a fitted multiplier. The 6-year subset has no published total here.
    if args.minimum_tenure == 3:
        measured = result["weighted_workers"]
        result["published_total_check"] = {"published_workers": 2578000,
            "difference": measured-2578000, "tolerance": 1000,
            "pass": abs(measured-2578000) <= 1000,
            "source": "https://www.bls.gov/news.release/archives/disp_08292024.pdf"}
        if not result["published_total_check"]["pass"]:
            raise ValueError(f"CPS/BLS total mismatch: {measured}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as handle:
        json.dump(result, handle, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps({k: v for k, v in result.items() if k in
                      ("weighted_workers", "raw_sample_n", "published_total_check")}))


if __name__ == "__main__":
    main()
