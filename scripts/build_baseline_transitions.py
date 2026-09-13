#!/usr/bin/env python3
"""R2 baseline artifact: weighted 2021->2022 employment/earnings transitions.

First baseline-transition artifact for the research plan's R2 milestone
(docs/LIFE_COURSE_RESEARCH_PLAN.md). Estimates ordinary (no-event)
December-to-December employment-state transitions and earnings changes
for prime-age workers from the redesigned SIPP public-use files, within
the January 2021 - December 2022 longitudinal span.

Design (all choices declared in docs/BASELINE_TRANSITION_R2_2026-09-14.md):
- Persons: FINYR2 > 0 in the calendar-2023 longitudinal weights release
  (the span Jan 2021 - Dec 2022), age 25-54 at December 2021, present in
  both pu2021 and pu2022 December records with RIN_UNIV = 1 and a valid
  RMESR at both dates.
- Employment state (2021 SIPP Data Dictionary, RMESR):
  E = {1,2,3,4,5} with a job (whole or part of the month),
  U = {6,7} no job, on layoff or looking,
  N = {8} no job, no layoff and no looking.
- Weights: FINYR2 person longitudinal weight. Nominal dollars; the
  2021->2022 comparison carries an inflation caveat, not a deflation.
- Held-out check: persons are split by a stable hash of their key; cell
  shares estimated on half A are compared with observed shares on half B.

Outputs land in validation/sipp/r2_transitions/. Deterministic; stdlib
only (Census advises column-selected streaming reads).
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data" / "sipp"
OUT = REPO / "validation" / "sipp" / "r2_transitions"

PU2021 = DATA / "2021" / "pu2021.csv.gz"
PU2022 = DATA / "2022" / "pu2022.csv.gz"
WEIGHTS = DATA / "2023" / "lgtwgt2023yr2.csv"

EMPLOYED = {"1", "2", "3", "4", "5"}
UNEMPLOYED = {"6", "7"}
NILF = {"8"}
STATES = ("E", "U", "N")
AGE_BANDS = ((25, 34), (35, 44), (45, 54))
BASE_COLS = ("SSUID", "PNUM", "SPANEL", "MONTHCODE")


def state(rmesr: str) -> str | None:
    if rmesr in EMPLOYED:
        return "E"
    if rmesr in UNEMPLOYED:
        return "U"
    if rmesr in NILF:
        return "N"
    return None


def age_band(age: float) -> str | None:
    for lo, hi in AGE_BANDS:
        if lo <= age <= hi:
            return f"{lo}-{hi}"
    return None


def half_of(key: tuple[str, str, str]) -> str:
    digest = hashlib.md5("".join(key).encode()).hexdigest()
    return "A" if int(digest[:8], 16) % 2 == 0 else "B"


def load_weights() -> dict[tuple[str, str, str], float]:
    weights: dict[tuple[str, str, str], float] = {}
    with open(WEIGHTS, newline="") as fh:
        for row in csv.DictReader(fh, delimiter="|"):
            row = {k.lower(): v for k, v in row.items()}
            w = float(row["finyr2"])
            if w > 0:
                weights[(row["ssuid"], row["pnum"], row["spanel"])] = w
    return weights


def stream_december(path: Path, columns: tuple[str, ...],
                    wanted: set[tuple[str, str, str]] | None = None,
                    prime_only: bool = False) -> dict[tuple[str, str, str], dict[str, str]]:
    """One streaming pass over a pu file; December rows only.

    prime_only filters on 25 <= TAGE_EHC <= 54 while scanning (used for
    the 2021 pass, where age defines the sample); wanted filters on
    known keys (used for the 2022 pass and the 2021 earnings pass).
    """
    out: dict[tuple[str, str, str], dict[str, str]] = {}
    with gzip.open(path, "rt") as fh:
        header = fh.readline().rstrip("\n").split("|")
        ix = [header.index(c) for c in columns]
        i_month = ix[columns.index("MONTHCODE")]
        i_univ = ix[columns.index("RIN_UNIV")] if "RIN_UNIV" in columns else None
        i_age = ix[columns.index("TAGE_EHC")] if "TAGE_EHC" in columns else None
        i_key = (ix[0], ix[1], ix[2])
        for line in fh:
            parts = line.rstrip("\n").split("|")
            if parts[i_month] != "12" or (i_univ is not None and parts[i_univ] != "1"):
                continue
            if i_age is not None and age_band(float(parts[i_age])) is None:
                continue
            key = (parts[i_key[0]], parts[i_key[1]], parts[i_key[2]])
            if wanted is not None and key not in wanted:
                continue
            out[key] = {c: parts[i] for c, i in zip(columns, ix, strict=True)}
    return out


def weighted_median(values: list[float], weights: list[float]) -> float:
    order = sorted(range(len(values)), key=lambda i: values[i])
    total = sum(weights)
    acc = 0.0
    for i in order:
        acc += weights[i]
        if acc >= 0.5 * total:
            return values[i]
    return values[-1]


def write_csv(path: Path, rows: list[dict]) -> None:
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    weights = load_weights()
    print(f"longitudinal span weights (FINYR2 > 0): {len(weights)}", flush=True)

    cols21 = BASE_COLS + ("RMESR", "TAGE_EHC", "ESEX")
    cols22 = BASE_COLS + ("RMESR", "TPEARN")

    base21 = stream_december(PU2021, cols21, prime_only=True)
    print(f"prime-age Dec-2021 in-universe persons: {len(base21)}", flush=True)

    span_persons = {k for k in weights if k in base21}
    print(f"of those, in the Jan2021-Dec2022 weighted span: {len(span_persons)}", flush=True)

    dec22 = stream_december(PU2022, cols22, wanted=span_persons)
    print(f"Dec-2022 in-universe records matched: {len(dec22)}", flush=True)

    linked = [k for k in span_persons if k in dec22 and state(dec22[k]["RMESR"])]
    unmatched = len(span_persons) - len(linked)
    print(f"linked valid transitions: {len(linked)} (dropped {unmatched})", flush=True)

    cols_earn = BASE_COLS + ("TPEARN",)
    dec21_earn = stream_december(PU2021, cols_earn, wanted=set(linked))

    rows = []
    for key in linked:
        b, d = base21[key], dec22[key]
        e21 = dec21_earn[key]["TPEARN"]
        e22 = d["TPEARN"]
        rows.append({
            "half": half_of(key),
            "sex": "male" if b["ESEX"] == "1" else "female",
            "age_band": age_band(float(b["TAGE_EHC"])),
            "origin": state(b["RMESR"]),
            "dest": state(d["RMESR"]),
            "weight": weights[key],
            "earn21": float(e21) if e21 else None,
            "earn22": float(e22) if e22 else None,
        })

    # Cell accumulators: exact cell (sex, age, origin) plus marginals with
    # "all" sentinels, all four computed per row in one pass.
    def cells_for(sex: str, age: str) -> tuple[tuple[str, str], ...]:
        return ((sex, age), (sex, "all"), ("all", age), ("all", "all"))

    trans = defaultdict(lambda: defaultdict(float))
    trans_n = defaultdict(int)
    for r in rows:
        for sex, age in cells_for(r["sex"], r["age_band"]):
            cell = (sex, age, r["origin"])
            trans[cell][r["dest"]] += r["weight"]
            trans_n[cell] += 1

    emp_rows = []
    for cell in sorted(trans, key=str):
        total = sum(trans[cell].values())
        row = {
            "sex": cell[0], "age_band": cell[1], "origin": cell[2],
            "n_persons": trans_n[cell], "weight": round(total, 3),
        }
        for dest in STATES:
            row[f"to_{dest}"] = round(trans[cell][dest] / total, 6)
        emp_rows.append(row)
    write_csv(OUT / "employment_transitions_2021_2022.csv", emp_rows)

    earn_acc = defaultdict(list)
    for r in rows:
        if r["origin"] == "E" and r["dest"] == "E" and r["earn21"] and r["earn22"]:
            for sex, age in cells_for(r["sex"], r["age_band"]):
                earn_acc[(sex, age)].append(r)

    earn_rows = []
    for cell in sorted(earn_acc, key=str):
        persons = earn_acc[cell]
        w = [p["weight"] for p in persons]
        v21 = [p["earn21"] for p in persons]
        v22 = [p["earn22"] for p in persons]
        paired = [(p["earn21"], p["earn22"], p["weight"]) for p in persons if p["earn21"] > 0]
        ratios = [b / a for a, b, _ in paired]
        wr = [wt for _, _, wt in paired]
        gains = sum(p["weight"] for p in persons if p["earn22"] > p["earn21"])
        earn_rows.append({
            "sex": cell[0], "age_band": cell[1], "origin_dest": "E|E",
            "n_persons": len(persons),
            "median_dec2021_tpearn": round(weighted_median(v21, w), 2),
            "median_dec2022_tpearn": round(weighted_median(v22, w), 2),
            "median_ratio": round(weighted_median(ratios, wr), 4),
            "share_gain": round(gains / sum(w), 6),
        })
    write_csv(OUT / "earnings_transitions_2021_2022.csv", earn_rows)

    # Held-out calibration: estimate on half A, evaluate on half B.
    calib_train = defaultdict(lambda: defaultdict(float))
    calib_hold = defaultdict(lambda: defaultdict(float))
    for r in rows:
        target = calib_train if r["half"] == "A" else calib_hold
        cell = (r["sex"], r["age_band"], r["origin"])
        target[cell][r["dest"]] += r["weight"]
    calibration = []
    for cell in sorted(calib_train, key=str):
        total_train = sum(calib_train[cell].values())
        total_hold = sum(calib_hold[cell].values())
        if total_hold == 0:
            continue
        for dest in STATES:
            pred = calib_train[cell][dest] / total_train
            obs = calib_hold[cell][dest] / total_hold
            calibration.append({
                "cell": "|".join(cell), "dest": dest,
                "train_share": round(pred, 6),
                "heldout_share": round(obs, 6),
                "abs_diff": round(abs(pred - obs), 6),
            })

    coverage = {
        "span": "January 2021 - December 2022 (FINYR2, calendar-2023 weights release)",
        "weight_population": len(weights),
        "prime_age_dec2021_in_universe": len(base21),
        "in_weighted_span": len(span_persons),
        "linked_transitions": len(rows),
        "dropped_2022": unmatched,
        "state_definition": {
            "E": "RMESR in 1-5 (with a job, whole or part of month)",
            "U": "RMESR in 6-7 (no job, on layoff or looking)",
            "N": "RMESR 8 (no job, no layoff and no looking)",
        },
        "heldout_calibration_cells": len(calibration),
        "heldout_max_abs_diff": round(max(c["abs_diff"] for c in calibration), 6),
        "heldout_mean_abs_diff": round(
            sum(c["abs_diff"] for c in calibration) / len(calibration), 6),
        "note": (
            "Longitudinal weights cover persons present through the span; "
            "attrition between surveys is absorbed by the Census weight "
            "construction and is not separately re-modeled here. Nominal "
            "dollars; 2021->2022 earnings changes carry an inflation caveat."
        ),
    }
    with open(OUT / "coverage_and_calibration.json", "w") as fh:
        json.dump({"coverage": coverage, "calibration": calibration}, fh, indent=2)

    print(f"wrote {OUT / 'employment_transitions_2021_2022.csv'}")
    print(f"wrote {OUT / 'earnings_transitions_2021_2022.csv'}")
    print(f"wrote {OUT / 'coverage_and_calibration.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
