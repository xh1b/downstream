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
import math
from pathlib import Path

from .children import CHILD_DIRECT, GRANDCHILD
from .ledger import DIRECT, GAP, chain
from .params import ParameterSet, data_dir
from .worker import WORKER_EARNINGS
from .mortality import excess_deaths

VALIDATION_DIR = data_dir("validation")


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


# ---------------------------------------------------------------------------
# V2 — out-of-sample back-tests (PRE-REGISTERED at v1.27, sources pending).
#
# The clinical-trials rule: outcome definitions and scoring rules are
# registered in code BEFORE the event data lands, and the trap tests pin
# them. A bridge/measured file landing later cannot change what counts as
# a pass; a miss is published, never refitted.
#
# Structural finding recorded up front (2026-09-09 source sweep): none of
# the three events carries a published DISPLACEMENT-COUNT bridge (shock
# units -> displaced workers), the input every scored stream needs. V1
# had one (ADH's own Table 1 employment regression). Until each event's
# bridge lands, scoring is blocked BY DESIGN — fabricating exposure from
# secondary prose would be exactly the overclaim the honesty architecture
# exists to prevent.
# ---------------------------------------------------------------------------

V2_EVENT_IDS = ("nafta", "auto_crisis", "brac")

V2_SCORED_STREAMS = (
    {"outcome": "excess_deaths_per100k", "links": ["earnings_shock->mortality_sustained", "earnings_shock->mortality_peak"]},
    {"outcome": "additional_divorces_per100k_women", "links": ["displacement->divorce_hazard"]},
    {"outcome": "local_service_jobs_per_displaced", "links": ["displacement->local_service_jobs"]},
)


def _v2_event_specs() -> list[dict]:
    """The three held-out events: what scores, and what blocks it."""
    return [
        {
            "id": "nafta",
            "description": (
                "NAFTA tariff cuts 1990-2000; wage growth by industry and "
                "locality exposure (Hakobyan & McLaren, REStat 98(4):728-741, "
                "2016; NBER w16535)"
            ),
            "shock_unit": "percentage points of local/industry tariff cut (Mexican import competition)",
            "exposure_bridge": {
                "file": "validation/nafta_exposure_bridge.csv",
                "needs": (
                    "displaced workers per unit of local tariff cut. The H&M "
                    "design measures wage growth of workers in exposed "
                    "industries and localities; it does not estimate "
                    "displacement counts, and the ADH import-penetration "
                    "bridge does not transfer to tariff units. Queued as an "
                    "extraction target."
                ),
                "sources": ["Hakobyan & McLaren 2016 (w16535, open PDF) — wage-growth measured side"],
            },
            "measured_outcomes": {
                "file": "validation/nafta_measured_coefficients.csv",
                "needs": "H&M wage-growth coefficients with SEs (blue-collar, service workers in affected localities; anticipatory adjustment)",
            },
            "window_semantics": "1990-2000 decadal wage growth (matches the model's decadal-window convention; declared at pre-registration)",
            "registered_scored_streams": [s["outcome"] for s in V2_SCORED_STREAMS],
            "status": "blocked: displacement bridge missing (H&M estimate no displacement counts)",
        },
        {
            "id": "auto_crisis",
            "description": (
                "2008-09 auto crisis: auto manufacturing + dealerships shed "
                ">600k jobs Dec 2007-Jun 2009 (BLS); GM/Chrysler bankruptcies "
                "concentrated in Michigan/Ohio/Indiana"
            ),
            "shock_unit": "count of auto-industry jobs lost (BLS descriptive counts, published)",
            "exposure_bridge": {
                "file": "validation/auto_crisis_exposure_bridge.csv",
                "needs": (
                    "county-level displaced workers (BLS CES/CPS counts are "
                    "national; a county bridge needs the local distribution, "
                    "e.g. WARN filings or QCEW county detail)"
                ),
                "sources": ["BLS CES descriptive counts (national totals)"],
            },
            "measured_outcomes": {
                "file": "validation/auto_crisis_measured_coefficients.csv",
                "needs": (
                    "published quasi-experimental local-outcome estimates for "
                    "the auto shock. 2026-09-09 sweep found none: the crisis "
                    "overlaps the Great Recession, so an event-specific causal "
                    "estimate does not exist. Record the honest refusal unless "
                    "a source surfaces."
                ),
                "sources": [],
            },
            "window_semantics": "acute shock 2008-2009; scored windows pre-registered at 3y and 5y",
            "registered_scored_streams": [s["outcome"] for s in V2_SCORED_STREAMS],
            "status": "blocked: county displacement bridge + quasi-experimental measured side both unidentified",
        },
        {
            "id": "brac",
            "description": (
                "BRAC base closures 1988-1995 rounds: ~100+ closures, civilian "
                "job cuts per community published (GAO-05-138 app. II; GAO/NSIAD-99-36)"
            ),
            "shock_unit": "count of displaced DoD CIVILIAN workers per community (published)",
            "exposure_bridge": {
                "file": "validation/brac_exposure_bridge.csv",
                "needs": (
                    "civilian jobs lost per BRAC community (GAO Appendix II: "
                    "Civilian Jobs Lost and Created at Major BRAC Locations). "
                    "GAO Table 3 inventory landed (73 bases); county and window alignment pending."
                ),
                "sources": ["GAO-05-138 (open HTML)", "GAO/NSIAD-99-36 (open HTML)"],
            },
            "measured_outcomes": {
                "file": "validation/brac_measured_coefficients.csv",
                "needs": (
                    "Hooker & Knetter (Economic Inquiry 39(4):583-598, 2001; "
                    "NBER w6941): county employment/income effects of "
                    "closures — the civilian closure 'looks more like a "
                    "plant closure'. WP is a scanned image (no text layer); "
                    "the published version is paywalled. Path: OCR the WP "
                    "with the repo's GLM-OCR stack, or secure the published "
                    "tables. RAND MR-667 (Dardia et al., open PDF) covers "
                    "three California closures as cross-checks."
                ),
                "sources": [
                    "Hooker & Knetter 2001 (Economic Inquiry 39(4):583-598; NBER w6941 — scanned, needs OCR)",
                    "Dardia, McCarthy, Malkin & Vernez 1996 (RAND MR-667, open PDF) — cross-checks",
                ],
            },
            "window_semantics": "closures phased over 2-6 years; scored windows pre-registered at 5y and 10y post-round",
            "registered_scored_streams": [s["outcome"] for s in V2_SCORED_STREAMS],
            "status": "blocked: county/window bridge alignment + causal measured side; GAO Table 3 inventory landed",
        },
    ]


def v2_events(params: ParameterSet) -> dict:
    """The pre-registered V2 registry: what will be scored, and what blocks it."""
    return {
        "stage": "V2 out-of-sample back-tests",
        "pre_registered": (
            "Outcome definitions and scoring rules registered in code at "
            f"{params.version} BEFORE any event data lands; trap tests pin "
            "them. A file landing later cannot change what counts as a pass."
        ),
        "scoring_rule": (
            "Same verdicts as V1: coverage statements in both directions "
            "(measured inside modeled band, modeled point inside measured "
            "CI) with no parameter tuning. Misses publish. Across-shock "
            "stability is reported (Lucas critique): the three events use "
            "the SAME frozen parameter set."
        ),
        "scored_streams": V2_SCORED_STREAMS,
        "events": _v2_event_specs(),
    }


_V2_SPECS = [
        {
            "id": "nafta",
            "description": (
                "NAFTA tariff cuts 1990-2000; wage growth by industry and "
                "locality exposure (Hakobyan & McLaren, REStat 98(4):728-741, "
                "2016; NBER w16535)"
            ),
            "shock_unit": "percentage points of local/industry tariff cut (Mexican import competition)",
            "exposure_bridge": {
                "file": "validation/nafta_exposure_bridge.csv",
                "needs": (
                    "displaced workers per unit of local tariff cut. H&M "
                    "measure wage growth, not displacement counts; the ADH "
                    "import-penetration bridge does not transfer to tariff "
                    "units. Queued as an extraction target."
                ),
                "sources": ["Hakobyan & McLaren 2016 (w16535, open PDF) — measured wage-growth side"],
            },
            "measured_outcomes": {
                "file": "validation/nafta_measured_coefficients.csv",
                "needs": "H&M wage-growth coefficients with SEs (blue-collar and service workers in affected localities; anticipatory adjustment recorded)",
            },
            "window_semantics": "1990-2000 decadal wage growth (matches the model's decadal window; declared at pre-registration)",
            "status": "blocked: displacement bridge (shock -> displaced workers) not estimable from H&M; extraction queued",
        },
        {
            "id": "auto_crisis",
            "description": (
                "2008-09 auto crisis: auto manufacturing and dealerships shed "
                ">600k jobs Dec 2007-Jun 2009 (BLS); GM/Chrysler bankruptcies "
                "concentrated in Michigan/Ohio/Indiana"
            ),
            "shock_unit": "count of auto-industry jobs lost (BLS descriptive counts, national)",
            "exposure_bridge": {
                "file": "validation/auto_crisis_exposure_bridge.csv",
                "needs": (
                    "county-level displaced workers. BLS CES/CPS counts are "
                    "national totals; a local bridge needs the county "
                    "distribution (WARN filings or QCEW county detail)."
                ),
                "sources": ["BLS CES descriptive counts (national)"],
            },
            "measured_outcomes": {
                "file": "validation/auto_crisis_measured_coefficients.csv",
                "needs": (
                    "published quasi-experimental local-outcome estimates. "
                    "2026-09-09 sweep found none: the crisis overlaps the "
                    "Great Recession, and no event-specific causal local "
                    "estimate surfaced. Record as an honest refusal unless a "
                    "source appears."
                ),
                "sources": [],
            },
            "window_semantics": "acute shock 2008-2009; scored windows pre-registered at 3y and 5y",
            "status": "blocked: county bridge + quasi-experimental measured side both unidentified",
        },
        {
            "id": "brac",
            "description": (
                "BRAC base closures, 1988-1995 rounds: civilian job cuts per "
                "community published (GAO-05-138 app. II; GAO/NSIAD-99-36)"
            ),
            "shock_unit": "count of displaced DoD civilian workers per community",
            "exposure_bridge": {
                "file": "validation/brac_exposure_bridge.csv",
                "needs": (
                    "civilian jobs lost per BRAC community (GAO app. II: "
                    "Civilian Jobs Lost and Created at Major BRAC Locations). "
                    "GAO Table 3 inventory landed (73 bases); county and window alignment pending."
                ),
                "sources": ["GAO-05-138 (open HTML)", "GAO/NSIAD-99-36 (open HTML)"],
            },
            "measured_outcomes": {
                "file": "validation/brac_measured_coefficients.csv",
                "needs": (
                    "Hooker & Knetter (Economic Inquiry 39(4):583-598, 2001; "
                    "NBER w6941): county employment/income effects — the "
                    "civilian closure 'looks more like a plant closure'. WP "
                    "PDF is a scanned image (no text layer); published "
                    "version paywalled. Path: OCR the WP or obtain the "
                    "published tables. RAND MR-667 (open PDF) is the "
                    "three-closure California cross-check."
                ),
                "sources": [
                    "Hooker & Knetter 2001 (NBER w6941 — scanned, needs OCR)",
                    "Dardia et al. 1996 (RAND MR-667, open PDF) — cross-checks",
                ],
            },
            "window_semantics": "closures phased over 2-6 years; scored windows pre-registered at 5y and 10y post-round",
            "status": "blocked: county/window bridge alignment + causal measured side; GAO Table 3 inventory landed",
        },
    ]




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
        # Must be the same odds-to-risk/survival kernel exposed by scenario.
        return excess_deaths(n, m, pk, s, WINDOW, method="odds_survival")

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
    - male p25 earnings vs pooled shock, DIRECT stream only
      (jacobson1993 et al., incidence-weighted; heavy scope caveats:
      JLS identifies high-tenure displaced workers, the p25 measures
      all men in the CZ) — the historical miss, retained
    - male p25 earnings, DIRECT + SPILLOVER composed (v1.17): the
      adh2013 spillover link (-0.822 log pts per $1k/worker on
      non-displaced noncollege wages) applied to the non-displaced
      share. Plus an aggregate cross-check of the composed model's
      implied total male wage response against ADH 2013 T6 col 2.
    """
    import csv as _csv
    import random as _random

    from .scoring import crps_sample, pit
    from .distributions import dist_for, sample_unit_interval

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
        hr = sample_unit_interval(
            dist_for(divorce, "rate_ratio"), rng.random(), divorce.low, divorce.high,
            point=divorce.point,
        )
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
    displaced_share = e_shock_gap * inc_factor  # bridge incidence at the tercile gap (data-fixed)

    def earn_gap(gap_mult: float) -> float:
        # earnings CHANGE (negative = fall): a gap multiplier below 1 is a
        # LOSS of (1 - mult), so the change is the negated loss.
        return -mean_level * (1 - gap_mult) * e_shock_gap * inc_factor

    earnings = {
        "outcome": "male p25 annual earnings change (USD, demeaned) — direct stream only",
        "exposure": "pooled shock (d_impusch_p9)",
        "stream": "displacement->worker_earnings (jacobson1993 et al.), incidence-weighted by displaced share of employed men",
        "cz_periods": n3,
        "shock_gap_pp": round(e_shock_gap, 4),
        "measured_gap_usd": round(e_gap, 2),
        "modeled_gap_usd": {"point": round(earn_gap(jls.point), 2), "low": round(earn_gap(jls.low), 2), "high": round(earn_gap(jls.high), 2)},
        "sign_agreement": (e_gap < 0) == (earn_gap(jls.point) < 0),
        "measured_inside_modeled_band": earn_gap(jls.low) <= e_gap <= earn_gap(jls.high),
        "status": (
            "historical miss RETAINED (v1.12 diagnosis row): undershoot ~4.8x. "
            "Kept published beside the composed row below — the miss is evidence, "
            "not something to overwrite."
        ),
        "scope_caveats": [
            "JLS identifies high-tenure displaced workers; p25 measures all CZ men (dilution biases the model magnitude UP)",
            "incidence uses mean CZ male employment share (declared, panel mean)",
            "p25 level baseline uses start-of-period panel mean",
        ],
    }

    # composed row (v1.17): direct displacement + the landed spillover link
    # (adh2013 T7PB col 6: -0.822 log pts per $1k/worker, NON-displaced
    # noncollege workers). The spillover coefficient is in the panel's
    # native exposure units ($1k/worker) — no pp conversion needed. It
    # applies to the NON-displaced share; log points convert exactly (exp),
    # not linearized. Channels compose additively in proportional change
    # (small-effect linearization, declared).
    spill = params.by_link("import_shock->non_displaced_wage_spillover")

    def prop_spill(coef: float) -> float:
        return math.exp(coef / 100.0 * e_shock_gap) - 1.0

    def earn_gap_composed(gap_mult: float, coef: float) -> float:
        prop = displaced_share * (gap_mult - 1.0) + (1.0 - displaced_share) * prop_spill(coef)
        return mean_level * prop

    comp_point = earn_gap_composed(jls.point, spill.point)
    comp_low = earn_gap_composed(jls.low, spill.low)
    comp_high = earn_gap_composed(jls.high, spill.high)
    earnings_composed = {
        "outcome": "male p25 annual earnings change (USD, demeaned) — direct + spillover composed",
        "exposure": "pooled shock (d_impusch_p9)",
        "stream": "displacement->worker_earnings (jacobson1993 et al.) + import_shock->non_displaced_wage_spillover (adh2013)",
        "cz_periods": n3,
        "shock_gap_pp": round(e_shock_gap, 4),
        "measured_gap_usd": round(e_gap, 2),
        "modeled_gap_usd": {"point": round(comp_point, 2), "low": round(comp_low, 2), "high": round(comp_high, 2)},
        "sign_agreement": (e_gap < 0) == (comp_point < 0),
        "measured_inside_modeled_band": comp_low <= e_gap <= comp_high,
        "gap_closure_share": round(1.0 - abs(e_gap - comp_point) / abs(e_gap - earnings["modeled_gap_usd"]["point"]), 4),
        "assumptions": [
            "channels additive in proportional change (small-effect linearization, declared)",
            "spillover applied to the non-displaced share (1 - displaced_share); displaced_share is data-fixed at the tercile gap",
            "log-point coefficient converted exactly (exp form), not linearized",
            "band corners exact interval arithmetic (loss monotone in both parameters)",
        ],
        "scope_caveats": [
            "the coefficient identifies NONmanufacturing noncollege workers; the p25 population includes manufacturing men whose wage response is deeper (ADH 2013 T7PB) — the composition is conservative on the spillover margin",
            "JLS high-tenure scope caveat inherited from the direct row",
        ],
    }

    # aggregate cross-check: the composed model's implied TOTAL male wage
    # response per $1k/worker vs ADH 2013 T6 col 2 (-0.892, SE 0.294) —
    # recorded on the spillover row notes for exactly this use.
    def total_response(gap_mult: float, coef: float) -> float:
        return 100.0 * earn_gap_composed(gap_mult, coef) / mean_level / e_shock_gap

    m_ci = [round(-0.892 - 1.96 * 0.294, 3), round(-0.892 + 1.96 * 0.294, 3)]
    wage_cross_check = {
        "check": "composed model implied TOTAL male wage response per $1k/worker vs ADH 2013 T6 col 2 (measured aggregate)",
        "model_logpts_per_1k": {
            "point": round(total_response(jls.point, spill.point), 3),
            "low": round(total_response(jls.low, spill.low), 3),
            "high": round(total_response(jls.high, spill.high), 3),
        },
        "measured_logpts_per_1k": {"point": -0.892, "se": 0.294, "ci95": m_ci},
        "model_point_inside_measured_ci": m_ci[0] <= total_response(jls.point, spill.point) <= m_ci[1],
        "measured_point_inside_model_band": total_response(jls.low, spill.low) <= -0.892 <= total_response(jls.high, spill.high),
        "note": (
            "The aggregate male wage response is reproduced within the measured "
            "CI, while the p25 row still undershoots — the residual is "
            "distributional (bottom-quartile wages fell more than the male "
            "mean), consistent with ADH 2013 note 39 (CZ-average wages "
            "understate composition-constant losses)."
        ),
    }

    observed_slope = 0.28  # ADH T6 col2, 2SLS, SE 0.15
    return {
        "stage": "V1 panel retrodiction (CZ terciles + slope scoring)",
        "panel": {"cz_periods": len(recs), "source": "openICPSR 116320-V2 extract (validation/adh_cz_panel.csv)"},
        "tercile_tests": [divorce_pooled, divorce_male, earnings, earnings_composed],
        "wage_response_cross_check": wage_cross_check,
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


def v2_backtest(event_id: str, params: ParameterSet) -> dict:
    """Score one held-out event through the pre-registered streams.

    Blocked BY DESIGN until the event's exposure bridge AND measured
    coefficients land (both files, transcribed with citations): the
    blocked dict names the missing sources instead of fabricating
    exposure. When both files exist, each registered stream gets the
    V1 verdict treatment: modeled band (exact interval arithmetic on
    the stream's monotone path) vs measured point + 95% CI, both
    directions reported.
    """
    event = next((e for e in _v2_event_specs() if e["id"] == event_id), None)
    if event is None:
        raise KeyError(f"unknown V2 event {event_id!r}; registered: {list(V2_EVENT_IDS)}")

    bridge_path = VALIDATION_DIR / Path(event["exposure_bridge"]["file"]).name
    measured_path = VALIDATION_DIR / Path(event["measured_outcomes"]["file"]).name
    if not bridge_path.exists() or not measured_path.exists():
        missing = []
        if not bridge_path.exists():
            missing.append(f"{bridge_path.name} (needs: {event['exposure_bridge']['needs']})")
        if not measured_path.exists():
            missing.append(f"{measured_path.name} (needs: {event['measured_outcomes']['needs']})")
        return {
            "event": event_id,
            "status": "blocked",
            "reason": "data plugs pending; scoring is registered but NOT run",
            "missing": missing,
            "registered_scored_streams": [s["outcome"] for s in V2_SCORED_STREAMS],
            "honesty": "No fabricated exposure, no fabricated measured side.",
        }

    bridge_rows = _load_csv(bridge_path.name)
    if any(not row.get("quantity", "").strip() for row in bridge_rows):
        return {
            "event": event["id"], "status": "blocked: malformed bridge quantity",
            "scored": [], "honesty": "Bridge rows must name their quantities.",
        }
    quantities = [row["quantity"] for row in bridge_rows]
    if len(set(quantities)) != len(quantities):
        return {
            "event": event["id"], "status": "blocked: duplicate bridge quantity",
            "scored": [], "honesty": "Duplicate bridge quantities are ambiguous.",
        }
    bridge = {r["quantity"]: r for r in bridge_rows}
    measured = _load_csv(measured_path.name)

    def number(quantity: str, field: str = "point") -> float:
        try:
            value = float(bridge[quantity][field])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"bridge lacks finite {quantity}.{field}") from exc
        if not math.isfinite(value):
            raise ValueError(f"bridge lacks finite {quantity}.{field}")
        return value

    try:
        n = abs(number("displaced_workers"))
        # Exposure bridges may report losses as negative changes or as positive
        # counts.  Magnitude endpoints must be ordered after abs() in either
        # convention; do not assume the signed-loss convention used by V1.
        n_lo, n_hi = sorted((abs(number("displaced_workers", "low")),
                             abs(number("displaced_workers", "high"))))
        window = number("window_years")
    except ValueError as exc:
        return {"event": event["id"], "status": f"blocked: {exc}", "scored": [],
                "honesty": "A score requires complete finite bridge inputs."}
    if window < 0:
        return {"event": event["id"], "status": "blocked: negative window_years",
                "scored": [], "honesty": "A score requires a nonnegative follow-up window."}

    sust = params.by_link("earnings_shock->mortality_sustained")
    peak = params.by_link("earnings_shock->mortality_peak")
    baseline_key = "baseline_mortality_per_person_year"
    if baseline_key not in bridge:
        return {
            "event": event["id"],
            "status": "blocked: bridge lacks cited baseline_mortality_per_person_year",
            "scored": [],
            "window_years": window,
            "honesty": "Mortality scoring requires a baseline probability; measured excess deaths cannot be reused as that baseline.",
        }
    try:
        baseline = number(baseline_key)
    except ValueError as exc:
        return {"event": event["id"], "status": f"blocked: {exc}", "scored": [],
                "window_years": window, "honesty": "Mortality scoring requires a finite baseline probability."}
    if not 0 <= baseline <= 1:
        return {"event": event["id"], "status": "blocked: invalid baseline_mortality_per_person_year",
                "scored": [], "window_years": window,
                "honesty": "Mortality scoring requires a baseline probability in [0, 1]."}

    def excess(n_: float, s: float, pk: float) -> float:
        return excess_deaths(n_, baseline, pk, s, window, method="odds_survival")

    scored = []
    for mrow in measured:
        if mrow["outcome"] != "excess_deaths_per100k":
            continue
        corners = [excess(n_, s, pk) for n_ in (n_lo, n_hi)
                   for s in (sust.low, sust.high) for pk in (peak.low, peak.high)]
        lo, hi = min(corners), max(corners)
        pt = excess(n, sust.point, peak.point)
        try:
            observed, mse = float(mrow["point"]), float(mrow["se"])
        except (KeyError, TypeError, ValueError):
            return {"event": event["id"], "status": "blocked: malformed measured outcome",
                    "scored": [], "window_years": window,
                    "honesty": "Measured outcome rows require finite point estimates and standard errors."}
        if not math.isfinite(observed) or not math.isfinite(mse) or mse < 0:
            return {"event": event["id"], "status": "blocked: malformed measured outcome",
                    "scored": [], "window_years": window,
                    "honesty": "Measured outcome rows require finite point estimates and nonnegative standard errors."}
        scored.append({
            "outcome": "excess_deaths_per100k",
            "modeled": {"point": round(pt, 2), "low": round(lo, 2), "high": round(hi, 2)},
            "measured": {"point": observed, "ci95": [round(observed - 1.96 * mse, 2), round(observed + 1.96 * mse, 2)]},
            "measured_inside_modeled_band": lo <= observed <= hi,
            "modeled_point_inside_measured_ci": (observed - 1.96 * mse) <= pt <= (observed + 1.96 * mse),
        })
    return {
        "event": event["id"],
        "status": "scored" if scored else "blocked: no scoreable measured outcome",
        "frozen_version": params.version,
        "scored": scored,
        "window_years": window,
        "honesty": "No parameter tuned to pass. Verdicts are coverage statements in both directions.",
    }


def run(params: ParameterSet) -> dict:
    return {
        "v0_internal_consistency": internal_consistency(params),
        "v1_backtest": v1_backtest_spec(),
        "v1_targets": v1_targets(),
        "v1_retrodict": v1_retrodict(params),
        "v1_panel": v1_panel(params),
        "v2_backtest": {
            "events": {eid: v2_backtest(eid, params) for eid in V2_EVENT_IDS},
            "registry": v2_events(params),
        },
    }
