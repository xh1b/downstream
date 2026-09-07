"""Traps for the V1 panel retrodiction.

Each trap names the defect it hunts:
- stacked terciles without period demeaning (confounded comparison
  flips the sign — caught in development)
- a panel verdict being flippable by code instead of evidence
- the extract silently shrinking (rows dropped)
- the earnings sign bug (a gap multiplier below 1 is a LOSS; the
  modeled change must be negative)
- slope scoring drifting from the pinned state
"""

from __future__ import annotations

import csv

from downstream.params import load_all
from downstream.validate import VALIDATION_DIR, v1_panel

P = v1_panel(load_all()["params"])
DIVORCE = [t for t in P["tercile_tests"] if t["outcome"].startswith("widowed")]
EARN = [t for t in P["tercile_tests"] if t["outcome"].startswith("male p25")][0]


def test_panel_extract_rowcount():
    rows = list(csv.DictReader(
        line for line in (VALIDATION_DIR / "adh_cz_panel.csv").read_text().splitlines()
        if not line.startswith("#")
    ))
    assert len(rows) == 1444
    assert "d_impuschm_p9cen" in rows[0]


def test_divorce_pooled_pass_state_pinned():
    t = [x for x in DIVORCE if x["exposure"].startswith("pooled")][0]
    assert t["sign_agreement"] is True
    assert t["measured_inside_modeled_band"] is True


def test_divorce_male_shock_pass_state_pinned():
    t = [x for x in DIVORCE if x["exposure"].startswith("male-specific")][0]
    assert t["sign_agreement"] is True
    assert t["measured_inside_modeled_band"] is True
    # the closest-exposure row: measured and model point within 2% of
    # each other — if this drifts, the extract or slope changed
    assert abs(t["measured_gap_pp"] - t["modeled_gap_pp"]["point"]) < 0.002


def test_earnings_row_sign_and_undershoot_pinned():
    t = EARN
    m = t["modeled_gap_usd"]
    # sign: a gap multiplier below 1 is a LOSS — modeled change negative
    assert m["point"] < 0 and m["low"] <= m["point"] <= m["high"]
    assert t["sign_agreement"] is True
    # undershoot: measured fall ~5x the incidence-weighted composition —
    # the wage-spillover evidence. Pinned: flippable only by evidence.
    assert t["measured_inside_modeled_band"] is False
    assert t["measured_gap_usd"] < 3 * m["point"]


def test_undemeaned_terciles_flip_sign():
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
    assert s["pit"] == 1.0
    assert 0.15 < s["crps"] < 0.20
    assert s["model_slope_pp_per_pp"]["p50"] < s["observed_slope"]


def test_panel_deterministic():
    assert v1_panel(load_all()["params"]) == P
