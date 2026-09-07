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

    m_age = float(bridge["male_death_rate_2544_1999_2003_per_person"]["point"])
    scored = []
    for label, m, caveat in (
        ("all_adults", m_all, "displaced pool mixed-sex, pooled death rate"),
        ("all_male", m_male, "declared assumption: every lost mfg job is a man's"),
        ("all_male_age_matched", m_age, "WONDER 25-44 male pooled 1999-2003 (warehouse-pinned); closes the era/provenance caveat"),
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
        "window_semantics": (
            "CONFIRMED cumulative per-decade (deposit Readme: variables "
            "starting cum_mort measure cumulative per-decade mortality; all "
            "d_ outcomes are 10-year equivalent changes) — the model's "
            "window-multiplication is the correct comparison, not an annual "
            "rate change."
        ),
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




def v1_panel(params: ParameterSet) -> dict:
    """The V1 PANEL retrodiction: per-CZ exposure heterogeneity.

    Uses the authors' public-release CZ panel (openICPSR 116320-V2,
    CC BY 4.0; extract in validation/adh_cz_panel.csv). Tercile tests
    (within-period demeaned — raw stacked terciles are confounded by
    period composition and flip sign; trap-pinned) plus proper slope
    scoring. Exposure only, no tuning.

    Rows (all non-circular on the model side):
    - divorce vs pooled shock (rege2007 stream + census baseline)
    - divorce vs MALE-specific shock (d_impuschm_p9cen) — the stream
      is about displaced (mostly male) workers, so the male shock is
      the closer exposure
    - male p25 earnings vs pooled shock (JLS worker-earnings stream,
      incidence-weighted by displaced share of employed men; heavy
      scope caveats: JLS identifies high-tenure displaced workers,
      the p25 measures all men in the CZ)
    """
    import csv as _csv
    import random as _random

    from .scoring import crps_sample, pit

    rows = []
    with open(VALIDATION_DIR / "adh_cz_panel.csv", newline="", encoding="utf-8") as f:
        for row in _csv.DictReader(line for line in f if not line.startswith("#")):
            if row["d_impusch_p9"] and row["d_sh_fem1839_widdivsep"]:
                rows.append(row)
    if not rows:
        return {"stage": "V1 panel", "status": "blocked: panel file missing"}

    def fnum(row: dict, col: str) -> float | None:
        v = (row.get(col) or "").strip()
        return float(v) if v not in ("", "nan") else None

    recs = [
        {
            "shock": fnum(r, "d_impusch_p9"),
            "male_shock": fnum(r, "d_impuschm_p9cen"),
            "widdivsep": fnum(r, "d_sh_fem1839_widdivsep"),
            "p25": fnum(r, "d_inc1839m_p25"),
            "p25_level": fnum(r, "l_inc1839m_p25"),
            "emp_share": fnum(r, "l_sh_emp_age1839m"),
            "yr": r["yr"],
            "w": float(r["timepwt24"] or 0.0),
        }
        for r in rows
    ]

    def demean(col: str) -> None:
        for yr in {r["yr"] for r in recs}:
            sub = [r for r in recs if r["yr"] == yr and r.get(col) is not None]
            w = sum(r["w"] for r in sub) or 1.0
            m = sum(r[col] * r["w"] for r in sub) / w
            for r in sub:
                r[col] = r[col] - m

    for c in ("shock", "male_shock", "widdivsep", "p25"):
        demean(c)

    def tercile_gap(recs: list[dict], shock_col: str, out_col: str, weight_by_level: bool = False):
        use = [r for r in recs if r.get(shock_col) is not None and r.get(out_col) is not None]
        use.sort(key=lambda r: r[shock_col])
        k = len(use) // 3
        bottom, top = use[:k], use[-k:]

        def wgap(rs, col):
            if weight_by_level:
                ws = [r["w"] * (r["p25_level"] or 0.0) for r in rs]
                tot = sum(ws) or 1.0
                return sum(r[col] * w for r, w in zip(rs, ws)) / tot
            w = sum(r["w"] for r in rs) or 1.0
            return sum(r[col] * r["w"] for r in rs) / w

        return wgap(top, out_col) - wgap(bottom, out_col), wgap(top, shock_col) - wgap(bottom, shock_col), len(use)

    # --- model slopes ------------------------------------------------------
    divorce = params.by_link("displacement->divorce_hazard")
    rng = _random.Random(1901)
    slope_samples = []
    for _ in range(5000):
        n = rng.uniform(1740.0, 3300.0)
        hr = rng.uniform(divorce.low, divorce.high)
        slope_samples.append(n * 0.5305 * 0.1045 * (hr - 1) * 2.0 / (0.503 * 1000.0))
    slope_samples.sort()

    def q(p: float) -> float:
        return slope_samples[min(int(p * (len(slope_samples) - 1)), len(slope_samples) - 1)]

    jls = params.by_link("displacement->worker_earnings")

    # divorce vs pooled shock
    d_gap, d_shock_gap, n1 = tercile_gap(recs, "shock", "widdivsep")
    divorce_pooled = {
        "outcome": "widowed/divorced/separated share of women 18-39 (pp)",
        "exposure": "pooled shock (d_impusch_p9)",
        "cz_periods": n1,
        "shock_gap_pp": round(d_shock_gap, 4),
        "measured_gap_pp": round(d_gap, 4),
        "modeled_gap_pp": {"point": round(d_shock_gap * q(0.5), 4), "low": round(d_shock_gap * q(0.05), 4), "high": round(d_shock_gap * q(0.95), 4)},
        "sign_agreement": (d_gap > 0) == (d_shock_gap * q(0.5) > 0),
        "measured_inside_modeled_band": d_shock_gap * q(0.05) <= d_gap <= d_shock_gap * q(0.95),
    }

    # divorce vs male-specific shock (same model slope; the male shock
    # is pp of male-intensive employment exposure, closest to our stream)
    dm_gap, dm_shock_gap, n2 = tercile_gap(recs, "male_shock", "widdivsep")
    divorce_male = {
        "outcome": "widowed/divorced/separated share of women 18-39 (pp)",
        "exposure": "male-specific shock (d_impuschm_p9cen)",
        "cz_periods": n2,
        "shock_gap_pp": round(dm_shock_gap, 4),
        "measured_gap_pp": round(dm_gap, 4),
        "modeled_gap_pp": {"point": round(dm_shock_gap * q(0.5), 4), "low": round(dm_shock_gap * q(0.05), 4), "high": round(dm_shock_gap * q(0.95), 4)},
        "sign_agreement": (dm_gap > 0) == (dm_shock_gap * q(0.5) > 0),
        "measured_inside_modeled_band": dm_shock_gap * q(0.05) <= dm_gap <= dm_shock_gap * q(0.95),
        "caveat": "the male shock interacts import exposure with male industry-employment share; treating its pp as equivalent to the pooled shock's pp is a declared approximation",
    }

    # earnings p25 vs pooled shock (JLS stream, incidence-weighted)
    # model dollar gap = mean level x (1 - jls) x (shock_gap x 2.52%) / employed-men share
    usable = [r for r in recs if r["p25"] is not None and r["p25_level"] and r["emp_share"]]
    e_gap, e_shock_gap, n3 = tercile_gap(recs, "shock", "p25")
    mean_level = sum(r["p25_level"] * r["w"] for r in usable) / (sum(r["w"] for r in usable) or 1.0)
    mean_emp = sum(r["emp_share"] * r["w"] for r in usable) / (sum(r["w"] for r in usable) or 1.0) / 100.0
    inc_factor = 0.0252 / mean_emp

    def earn_gap(gap_mult: float) -> float:
        # earnings CHANGE (negative = fall): a gap multiplier below 1 is a
        # LOSS of (1 - mult), so the change is the negated loss.
        return -mean_level * (1 - gap_mult) * e_shock_gap * inc_factor

    earnings = {
        "outcome": "male p25 annual earnings change (USD, demeaned)",
        "exposure": "pooled shock (d_impusch_p9)",
        "stream": "displacement->worker_earnings (jacobson1993 et al.), incidence-weighted by displaced share of employed men",
        "cz_periods": n3,
        "shock_gap_pp": round(e_shock_gap, 4),
        "measured_gap_usd": round(e_gap, 2),
        "modeled_gap_usd": {"point": round(earn_gap(jls.point), 2), "low": round(earn_gap(jls.low), 2), "high": round(earn_gap(jls.high), 2)},
        "sign_agreement": (e_gap < 0) == (earn_gap(jls.point) < 0),
        "measured_inside_modeled_band": earn_gap(jls.low) <= e_gap <= earn_gap(jls.high),
        "scope_caveats": [
            "JLS identifies high-tenure displaced workers; p25 measures all CZ men (dilution biases the model magnitude UP)",
            "incidence uses mean CZ male employment share (declared, panel mean)",
            "p25 level baseline uses start-of-period panel mean",
        ],
    }

    observed_slope = 0.28  # ADH T6 col2, 2SLS, SE 0.15
    return {
        "stage": "V1 panel retrodiction (CZ terciles + slope scoring)",
        "panel": {"cz_periods": len(recs), "source": "openICPSR 116320-V2 extract (validation/adh_cz_panel.csv)"},
        "tercile_tests": [divorce_pooled, divorce_male, earnings],
        "slope_scoring": {
            "model_slope_pp_per_pp": {"p05": round(q(0.05), 4), "p50": round(q(0.5), 4), "p95": round(q(0.95), 4)},
            "observed_slope": observed_slope,
            "crps": round(crps_sample(slope_samples, observed_slope), 5),
            "pit": round(pit(slope_samples, observed_slope), 4),
            "note": (
                "CRPS in pp-of-women units against the published point "
                "estimate; PIT 1.0 means the observed slope sits above "
                "the model's central mass (the remarriage-margin "
                "undershoot, confirmed on panel terciles)."
            ),
        },
        "honesty": (
            "No tuning. The model slopes reuse the same cited bands as the "
            "unit scorecard; the panel adds exposure HETEROGENEITY, not new "
            "parameters. ICPSR deposit 116320 cited per its terms."
        ),
    }


def run(params: ParameterSet) -> dict:
    return {
        "v0_internal_consistency": internal_consistency(params),
        "v1_backtest": v1_backtest_spec(),
        "v1_targets": v1_targets(),
        "v1_retrodict": v1_retrodict(params),
        "v1_panel": v1_panel(params),
    }
