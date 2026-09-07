"""Traps for the V1 panel retrodiction.

Each trap names the defect it hunts:
- stacked terciles without period demeaning (the confounded
  comparison flips the sign — the exact bug caught in development)
- the panel pass being flippable by code instead of evidence
- the extract silently shrinking (rows dropped)
- slope scoring drifting from the pinned state
"""

from __future__ import annotations

import csv
from pathlib import Path

from downstream.params import load_all
from downstream.validate import VALIDATION_DIR, v1_panel

P = v1_panel(load_all()["params"])


def test_panel_extract_rowcount():
    rows = list(csv.DictReader(
        line for line in (VALIDATION_DIR / "adh_cz_panel.csv").read_text().splitlines()
        if not line.startswith("#")
    ))
    assert len(rows) == 1444


def test_tercile_pass_state_pinned():
    t = P["tercile_test"]
    assert t["sign_agreement"] is True
    assert t["measured_inside_modeled_band"] is True
    assert 0.04 < t["modeled_gap_pp"]["low"] < t["measured_gap_pp"] < t["modeled_gap_pp"]["high"] < 0.3


def test_undemeaned_terciles_flip_sign():
    # the trap that justifies the demeaning: raw stacked terciles are
    # confounded by period composition and flip the measured gap negative
    rows = []
    with open(VALIDATION_DIR / "adh_cz_panel.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(line for line in f if not line.startswith("#")):
            if row["d_impusch_p9"] and row["d_sh_fem1839_widdivsep"]:
                rows.append((float(row["d_impusch_p9"]), float(row["d_sh_fem1839_widdivsep"])))
    rows.sort()
    k = len(rows) // 3
    raw_gap = sum(v for _, v in rows[-k:]) / k - sum(v for _, v in rows[:k]) / k
    assert raw_gap < 0, (
        "the un-demeaned stacked gap used to be negative (period confounding); "
        "if it is now positive the data or extract changed — re-examine before "
        "trusting the demeaned pass"
    )


def test_slope_scoring_state_pinned():
    s = P["slope_scoring"]
    assert s["pit"] == 1.0  # observed slope sits above the model mass: undershoot
    assert 0.15 < s["crps"] < 0.20
    assert s["model_slope_pp_per_pp"]["p50"] < s["observed_slope"]


def test_panel_deterministic():
    assert v1_panel(load_all()["params"]) == P
