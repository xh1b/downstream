"""Model validation, stage by stage.

V0 — internal consistency (runs offline, always):
    The direct child estimate (Oreopoulos 2008) must agree, within
    bands, with the IGE-composed path (father shock x transmission
    band). Two independent literatures landing on the same number is
    the model's cheapest falsification test.

V1 — historical retrodiction (scaffolded, data plugs pending):
    China-shock commuting zones. The model must reproduce the MEASURED
    marriage / fertility / child-poverty / mortality deltas in exposed
    CZs (Autor, Dorn & Hanson 2019 + follow-ups) from exposure inputs,
    without fitting to them.

V2 — out-of-sample back-tests (designed, not built):
    NAFTA shocks, the 2008-09 auto crisis, BRAC base closures.

V3 — prospective pre-registered forecasting (designed, not built):
    Published forecasts with proper scoring rules before outcomes are
    known; misses published.
"""

from __future__ import annotations

import csv
from pathlib import Path

from .children import CHILD_DIRECT, GRANDCHILD
from .ledger import DIRECT, GAP, chain
from .params import ParameterSet
from .worker import WORKER_EARNINGS

VALIDATION_DIR = Path(__file__).resolve().parents[2] / "validation"


def internal_consistency(params: ParameterSet) -> dict:
    """V0: direct child effect vs IGE-composed path.

    IGE path: father gap 0.80 (JLS band) -> child gap =
    1 - IGE * (1 - father_gap). If the bands do not overlap, one of the
    two literatures is misread and the model must stop.
    """
    father = chain(
        params,
        links=[WORKER_EARNINGS],
        label="father_gap",
        unit="gap_multiplier",
        kinds=[DIRECT],
    )
    ige = params.by_link(GRANDCHILD)
    composed = father.apply(GAP, ige, label="child_via_ige")

    direct = params.by_link(CHILD_DIRECT)
    overlap = not (composed.high < direct.low or direct.high < composed.low)

    return {
        "check": "V0 internal consistency: direct child effect vs IGE-composed path",
        "direct": {
            "point": direct.point,
            "low": direct.low,
            "high": direct.high,
            "citation": direct.citation,
        },
        "ige_composed": {
            "point": round(composed.point, 4),
            "low": round(composed.low, 4),
            "high": round(composed.high, 4),
            "transmission": ige.citation,
        },
        "bands_overlap": overlap,
        "pass": overlap,
    }


def v1_targets() -> dict:
    """The transcribed ADH 2019 measured CZ coefficients (V1 targets).

    Loaded from validation/adh2019_measured_coefficients.csv — measured
    outcomes per percentage-point trade shock. These are the numbers
    the retrodiction must reproduce WITHOUT tuning. The exposure
    bridge (shock -> displaced workers, ADH Table 2 employment
    effects) is still pending; until it lands, this reports the
    measured side only.
    """
    path = VALIDATION_DIR / "adh2019_measured_coefficients.csv"
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(line for line in f if not line.startswith("#")):
            rows.append(row)
    return {
        "targets": rows,
        "count": len(rows),
        "source": "validation/adh2019_measured_coefficients.csv",
        "exposure_bridge": "pending: ADH Table 2 employment effects (shock -> displaced workers)",
        "status": (
            "measured side transcribed (full text, autor2019); "
            "retrodiction scoring starts when the exposure bridge lands"
        ),
    }


def v1_backtest_spec() -> dict:
    """The China-shock retrodiction target and the exact data it needs."""
    return {
        "stage": "V1 retrodiction",
        "target": (
            "Reproduce measured 1990-2014 deltas in trade-exposed US "
            "commuting zones: marriage rates, nonmarital fertility, child "
            "poverty, prime-age mortality (Autor, Dorn & Hanson 2019; "
            "Autor et al. 2020)"
        ),
        "inputs_needed": [
            "CZ-level import-exposure shock (ADH published instrument)",
            "CZ demographic baselines (Census/ACS tables)",
            "measured outcome deltas (published tables; transcribed with citations)",
        ],
        "design": (
            "Feed exposure through the model's family/mortality streams; "
            "compare modeled vs measured deltas per CZ tercile. Pass rule: "
            "modeled point inside the measured 95% CI for a majority of "
            "terciles and no sign flips. No parameter may be tuned to "
            "pass; a miss is published."
        ),
        "status": "scaffolded - data plugs pending (see docs/QUEUED_EXTRACTIONS.md)",
    }


def run(params: ParameterSet) -> dict:
    return {
        "v0_internal_consistency": internal_consistency(params),
        "v1_backtest": v1_backtest_spec(),
        "v1_targets": v1_targets(),
    }
