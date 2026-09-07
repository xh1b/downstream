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




def _load_csv(name: str) -> list[dict]:
    path = VALIDATION_DIR / name
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


def v1_retrodict(params: ParameterSet) -> dict:
    """The V1 unit-level retrodiction scorecard: model vs ADH measured.

    Protocol (no tuning, exposure only):
    - bridge: 1pp import shock displaces 2.52pp [1.74, 3.30] of
      working-age adults from manufacturing (ADH T1 col10);
    - model side: the S&vW mortality stream (sustained + peak) applied
      to the displaced pool against ADH's reported 1990 death rates
      (CDC-derived, transcribed in the bridge file);
    - bands: exact interval arithmetic — excess deaths are monotone
      increasing in every input, so the corner values are the band;
    - measured side: ADH T5 male-female differential, 4.27 (SE 3.54)
      per 100k adults per pp shock.

    Verdicts are coverage statements, both directions. Scope caveats
    publish: S&vW identifies high-seniority MEN; the bridge displaces
    adults 18-39 of both sexes; the measured outcome is a male-female
    DIFFERENTIAL (female response small per ADH T A4). Two variants
    bound the scope question: all-adults (pooled death rate) and
    all-male (declared assumption: every lost mfg job is a man's).

    Outcomes with no non-circular model path are named as refusals:
    ADH is the only source for the marriage/fertility/poverty
    coefficients, so scoring the model against numbers only ADH
    supplies would be circular. That refusal is a result.
    """
    bridge = {r["quantity"]: r for r in _load_csv("adh2019_exposure_bridge.csv")}
    b = bridge["mfg_employment_share_change_per_pp"]
    # displaced workers per 100k adults per 1pp shock = |pp| * 1000
    n_point = abs(float(b["point"])) * 1000
    n_lo = abs(float(b["high"])) * 1000
    n_hi = abs(float(b["low"])) * 1000

    m_all = (float(bridge["male_death_rate_1990_per100k"]["point"] or 0)
             + float(bridge["female_death_rate_1990_per100k"]["point"] or 0)) / 2 / 100_000
    m_male = float(bridge["male_death_rate_1990_per100k"]["point"]) / 100_000

    sust = params.by_link("earnings_shock->mortality_sustained")
    peak = params.by_link("earnings_shock->mortality_peak")
    WINDOW = 10.0  # ADH measure decadal changes

    def excess(n: float, m: float, s, pk) -> float:
        return n * m * ((s - 1) * WINDOW + (pk - 1))

    scored = []
    for label, m, caveat in (
        ("all_adults", m_all, "displaced pool mixed-sex, pooled death rate"),
        ("all_male", m_male, "declared assumption: every lost mfg job is a man's"),
    ):
        point = excess(n_point, m, sust.point, peak.point)
        lo = excess(n_lo, m, sust.low, peak.low)
        hi = excess(n_hi, m, sust.high, peak.high)
        measured, mse = 4.27, 3.54
        scored.append({
            "variant": label,
            "scope_caveat": caveat,
            "modeled_excess_deaths_per100k": {"point": round(point, 2), "low": round(lo, 2), "high": round(hi, 2)},
            "measured_differential_per100k": {"point": measured, "ci95": [round(measured - 1.96 * mse, 2), round(measured + 1.96 * mse, 2)]},
            "measured_inside_modeled_band": lo <= measured <= hi,
            "modeled_point_inside_measured_ci": (measured - 1.96 * mse) <= point <= (measured + 1.96 * mse),
        })

    # --- divorce stream (non-circular: rege2007/charles2004, not ADH) ---
    # additional divorces per 100k adults over W years =
    #   N_displaced x married_share x divorce_5y_baseline x (hazard_ratio - 1)
    # linearization of the cumulative hazard (declared approximation:
    # valid for small cumulative probabilities), scaled W/5.
    divorce = params.by_link("displacement->divorce_hazard")
    married_share = float(bridge["married_share_women_1839_1990"]["point"])
    women_share = float(bridge["women_share_adults_1839"]["point"])
    d_measured, d_se = 0.28, 0.15
    d_rows = []
    for window in (5.0, 10.0):
        def d_excess(n: float, hr: float) -> float:
            return n * married_share * 0.1045 * (hr - 1) * (window / 5.0) / women_share / 1000.0

        pt = d_excess(n_point, divorce.point)
        lo = d_excess(n_lo, divorce.low)
        hi = d_excess(n_hi, divorce.high)
        d_rows.append({
            "window_years": window,
            "modeled_pp_women": {"point": round(pt, 4), "low": round(lo, 4), "high": round(hi, 4)},
            "measured_pp_women": {"point": d_measured, "ci95": [round(d_measured - 1.96 * d_se, 4), round(d_measured + 1.96 * d_se, 4)]},
            "measured_inside_modeled_band": lo <= d_measured <= hi,
            "modeled_point_inside_measured_ci": (d_measured - 1.96 * d_se) <= pt <= (d_measured + 1.96 * d_se),
            "assumptions": [
                "cumulative hazard linearized in the rate ratio (declared approximation, small-p)",
                "married_share incidence from ADH T6 1990 level (transcribed, cited)",
                "one exposed marriage per married displaced worker",
            ],
        })

    refusals = [
        {"outcome": r["outcome"], "reason": "circular: ADH is the only source for this coefficient; the model has no independent path (no marriage/fertility/poverty parameter outside ADH)"}
        for r in v1_targets()["targets"]
        if r["outcome"] not in {"male_female_mort_diff_total", "widowed_divorced_separated_pp"}
    ]

    return {
        "stage": "V1 retrodiction — unit-level scorecard (per 1pp shock, per 100k adults)",
        "bridge": {"displaced_per_100k": {"point": n_point, "low": n_lo, "high": n_hi}, "source": "ADH T1 col10 (validation/adh2019_exposure_bridge.csv)"},
        "window_years": WINDOW,
        "scored": scored,
        "scored_divorce": {
            "stream": "displacement->divorce_hazard (rege2007; charles2004) + census divorce_5y_cumulative baseline",
            "windows": d_rows,
        },
        "refusals": refusals,
        "honesty": (
            "No parameter was tuned to pass. Bands are exact interval "
            "arithmetic on monotone paths. The scored outcome carries three "
            "scope caveats (S&vW men-only identification, mixed-sex bridge, "
            "differential-vs-level measurement) — published, not netted out."
        ),
    }


def run(params: ParameterSet) -> dict:
    return {
        "v0_internal_consistency": internal_consistency(params),
        "v1_backtest": v1_backtest_spec(),
        "v1_targets": v1_targets(),
        "v1_retrodict": v1_retrodict(params),
    }
