"""v1.27 pins: per-parameter distributions + first citable correlations.

What this file hunts:
- a declared dist on a row whose band is NOT SE-derived: the dist
  column exists only for reported 95% CIs; a rounding band, a
  cross-study spread, or an evidence-widened band (CITING 4: bands
  never shrink) carries no shape information, and claiming one
  manufactures precision the paper never reported
- the audit letting an unknown dist token through, or a lognormal
  on a non-positive band
- a correlation whose magnitude is presented as extracted: the
  papers report no sampling covariance, so the -0.5 couplings must
  carry `declared` in the justification
- a correlation row referencing a link that does not exist, or a
  matrix that is not PSD
- Iman-Conover silently changing marginals: the induced coupling
  must reorder draws only — every marginal distribution survives
- the sampler stamp lying: once declared correlations apply, the
  output must say `lhs+iman-conover`, not plain `lhs`
- mc.simulate reading correlations.csv when told not to
  (use_declared_correlations=False must give raw LHS)
"""
import math
import random

import pytest

from downstream.audit import audit
from downstream.distributions import (
    KNOWN_DISTS,
    LOGNORMAL,
    NORMAL,
    apply_rank_correlation,
    dist_for,
    lhs_matrix,
    plan,
    sample_unit_interval,
)
from downstream.params import (
    default_dir,
    load,
    load_correlations,
    load_nodes,
    spearman_matrix,
)

PARAMS_DIR = default_dir()
PARAMS = load(PARAMS_DIR / "parameters.csv")
NODES = load_nodes(PARAMS_DIR / "nodes.csv")


def test_version_is_v127():
    assert (PARAMS_DIR / "VERSION").read_text().strip() == "v1.41"


# --- declared per-parameter distributions -------------------------------

SE_CI_NORMAL = [
    "unemployment_rate->property_crime",
    "family_income_shock->child_achievement_sd",
    "eviction_order->emergency_shelter_use",
    "eitc_exposure->adult_earnings_early",
    "male_earnings->marital_fertility",
    "male_job_loss_rate->child_maltreatment",
    "wage_ratio->household_ipv",
    "import_shock->non_displaced_wage_spillover",
    "import_shock->gop_win_probability",
    "import_shock->radical_right_vote_share",
    "displacement->college_enrollment",
    "displacement->parental_income_shortrun",
    "displacement->grade_retention_hazard",
    "eviction_order->eviction_earnings_response",
    "household_ipv->child_internalizing_sd",
    "household_ipv->child_externalizing_sd",
    "unemployment_status->mental_health_sd",
]
SE_CI_LOGNORMAL = [
    "earnings_shock->mortality_peak",
    "earnings_shock->mortality_sustained",
    "displacement->infant_birth_weight",
]


def test_ci_rows_declare_their_shape():
    for link in SE_CI_NORMAL:
        p = PARAMS.by_link(link)
        assert p.dist == "normal", link
    for link in SE_CI_LOGNORMAL:
        p = PARAMS.by_link(link)
        assert p.dist == "lognormal", link


def test_declared_band_rows_do_not_claim_a_shape():
    # Bands built by hand (rounding band, cross-study spread, widened)
    # must NOT declare a distribution — flat-in-band is the honest shape.
    for link in [
        "displacement->worker_earnings",  # cross-study spread
        "displacement->divorce_hazard",  # spread, widened
        "child_earnings->grandchild_earnings",  # IGE band
        "foreclosure_order->house_price_gap",  # +/-25% rounding band
        "local_unemp_shock->household_ipv",  # exp() spec-range band
        "household_hardship->household_ipv",  # declared +/-25% band
        "displacement->child_earnings",  # evidence-WIDENED CI band
        "youth_wages->youth_crime",  # rounding band
    ]:
        assert PARAMS.by_link(link).dist == "", link


def test_declared_dist_overrides_the_unit_default():
    p = PARAMS.by_link("import_shock->gop_win_probability")
    assert dist_for(p, "percent_delta") == NORMAL
    p2 = PARAMS.by_link("earnings_shock->mortality_peak")
    assert dist_for(p2, "rate_ratio") == LOGNORMAL


def test_unknown_dist_token_is_rejected():
    p = PARAMS.by_link("import_shock->gop_win_probability")
    with pytest.raises(ValueError):
        sample_unit_interval("cauchy", 0.5, p.low, p.high, point=p.point)
    assert "cauchy" not in KNOWN_DISTS


def test_lognormal_stays_in_band_and_centers_on_the_point():
    p = PARAMS.by_link("earnings_shock->mortality_peak")
    rng = random.Random(5)
    vals = []
    for _ in range(2000):
        vals.append(sample_unit_interval(LOGNORMAL, rng.random(), p.low, p.high, point=p.point))
        assert p.low <= vals[-1] <= p.high
    # median near the reported point (clamping piles the tails at the edges)
    vals.sort()
    assert vals[1000] == pytest.approx(p.point, rel=0.02)


def test_normal_centers_on_the_point_not_the_midpoint():
    # mental_health_sd's band is a ROUNDED reported CI: midpoint 0.505,
    # point 0.51 — the sampled center must be the reported point.
    p = PARAMS.by_link("unemployment_status->mental_health_sd")
    rng = random.Random(6)
    vals = [sample_unit_interval(NORMAL, rng.random(), p.low, p.high, point=p.point) for _ in range(2000)]
    vals.sort()
    assert vals[1000] == pytest.approx(p.point, abs=0.01)
    for v in vals:
        assert p.low <= v <= p.high


def test_lognormal_on_nonpositive_band_fails_loudly():
    with pytest.raises(ValueError):
        sample_unit_interval(LOGNORMAL, 0.5, -1.0, 2.0, point=0.5)


def test_sample_without_point_keeps_the_old_centers():
    # back-compat: no point -> normal centers on the midpoint,
    # lognormal on the geometric mean
    v = sample_unit_interval(LOGNORMAL, 0.5, 1.5, 2.0)
    assert v == pytest.approx(math.sqrt(1.5 * 2.0), abs=1e-9)
    assert sample_unit_interval(NORMAL, 0.5, 1.15, 2.0) == pytest.approx(1.575, abs=1e-9)


# --- correlations loader ------------------------------------------------


def test_correlations_load():
    rows = load_correlations(PARAMS_DIR / "correlations.csv")
    links = {(r.from_param, r.to_param): r.spearman for r in rows}
    assert links[("displacement->worker_earnings", "earnings_shock->mortality_peak")] == -0.5
    assert links[("displacement->worker_earnings", "earnings_shock->mortality_sustained")] == -0.5
    for r in rows:
        assert "declared" in r.justification.lower()


def test_spearman_matrix_maps_pairs_onto_row_order():
    rows = load_correlations(PARAMS_DIR / "correlations.csv")
    mat = spearman_matrix(PARAMS, rows)
    assert mat is not None
    i = [p.link for p in PARAMS.parameters].index("displacement->worker_earnings")
    j = [p.link for p in PARAMS.parameters].index("earnings_shock->mortality_peak")
    assert mat[i][j] == -0.5 and mat[j][i] == -0.5
    for k in range(len(mat)):
        assert mat[k][k] == 1.0


def test_spearman_matrix_none_when_no_pairs(tmp_path):
    empty = tmp_path / "correlations.csv"
    empty.write_text("from_param,to_param,spearman,justification\n")
    rows = load_correlations(empty)
    assert spearman_matrix(PARAMS, rows) is None


def test_spearman_matrix_unknown_link_raises():
    rows = [type(load_correlations(PARAMS_DIR / "correlations.csv")[0])(
        "nope->link", "earnings_shock->mortality_peak", -0.5, "x"
    )]
    with pytest.raises(KeyError):
        spearman_matrix(PARAMS, rows)


def test_correlations_matrix_is_psd():
    from downstream.distributions import _cholesky

    rows = load_correlations(PARAMS_DIR / "correlations.csv")
    mat = spearman_matrix(PARAMS, rows)
    assert mat is not None
    _cholesky(mat)  # raises on non-PSD


# --- mc.simulate applies declared correlations -------------------------


def test_simulate_stamps_iman_conover_and_is_reproducible():
    from downstream.mc import simulate

    def compute(ps):
        return sum(pp.point for pp in ps.parameters)

    a = simulate(PARAMS, compute, draws=300, seed=11)
    b = simulate(PARAMS, compute, draws=300, seed=11)
    assert a == b
    assert a["sampler"] == "lhs+iman-conover"
    assert a["correlations_applied"] == 2
    assert a["parameter_set_version"] == "v1.41-sampled"


def test_simulate_can_opt_out_of_declared_correlations():
    from downstream.mc import simulate

    def compute(ps):
        return sum(pp.point for pp in ps.parameters)

    a = simulate(PARAMS, compute, draws=300, seed=11, use_declared_correlations=False)
    assert a["sampler"] == "lhs"
    assert a["correlations_applied"] == 0


def test_induced_negative_coupling_moves_the_two_mortality_rows_together():
    """THE coherence property: deep-loss earnings draws must pair with
    big mortality responses. Compare rank agreement between the
    earnings multiplier and the sustained-mortality multiplier under
    the landed matrix (rho=-0.5 pair) vs independent LHS."""
    links = ["displacement->worker_earnings", "earnings_shock->mortality_sustained"]

    def sampled_values(spearman):
        dp = plan(PARAMS, NODES, 600, 21, spearman=spearman)
        a, b = [], []
        for k in range(600):
            row = dp.u[k]
            for j, p in enumerate(PARAMS.parameters):
                lo, hi = sorted((p.low, p.high))
                v = sample_unit_interval(dp.dists[j], row[j], lo, hi, point=p.point)
                if p.link == links[0]:
                    a.append(v)
                elif p.link == links[1]:
                    b.append(v)
        return a, b

    def rank_corr(a, b):
        n = len(a)
        ra = {v: r for r, v in enumerate(sorted(a))}
        rb = {v: r for r, v in enumerate(sorted(b))}
        ma = sum(ra[v] for v in a) / n
        mb = sum(rb[v] for v in b) / n
        cov = sum((ra[x] - ma) * (rb[y] - mb) for x, y in zip(a, b))
        va = math.sqrt(sum((ra[x] - ma) ** 2 for x in a))
        vb = math.sqrt(sum((rb[y] - mb) ** 2 for y in b))
        return cov / (va * vb)

    ind_a, ind_b = sampled_values(None)
    landed = load_correlations(PARAMS_DIR / "correlations.csv")
    dep_a, dep_b = sampled_values(spearman_matrix(PARAMS, landed))
    rho_ind = rank_corr(ind_a, ind_b)
    rho_dep = rank_corr(dep_a, dep_b)
    assert rho_dep < -0.35, rho_dep
    assert rho_dep < rho_ind - 0.2, (rho_dep, rho_ind)


def test_marginals_survive_induction_on_the_landed_matrix():
    rows = load_correlations(PARAMS_DIR / "correlations.csv")
    rng = random.Random(13)
    u = lhs_matrix(len(PARAMS.parameters), 500, rng)
    mat = spearman_matrix(PARAMS, rows)
    assert mat is not None
    out = apply_rank_correlation(u, mat)
    for j in range(len(PARAMS.parameters)):
        assert sorted(row[j] for row in out) == sorted(row[j] for row in u)


# --- audit traps --------------------------------------------------------


def test_audit_rejects_unknown_dist_token():
    # simulate the defect: declare an unknown token on a row
    import csv as _csv
    import io
    import pathlib
    import tempfile

    s = open(PARAMS_DIR / "parameters.csv").read()
    rows = list(_csv.reader(s.splitlines()))
    di = rows[0].index("dist")
    for r in rows[1:]:
        if r[0] == "foreclosure_order->house_price_gap":
            r[di] = "truncated-beta"
    buf = io.StringIO()
    _csv.writer(buf, lineterminator="\n").writerows(rows)
    d = pathlib.Path(tempfile.mkdtemp())
    (d / "parameters.csv").write_text(buf.getvalue())
    for name in ("nodes.csv", "baselines.csv", "references.bib", "doi_review.json", "correlations.csv"):
        try:
            (d / name).write_text(open(PARAMS_DIR / name).read())
        except OSError:
            pass
    (d / "VERSION").write_text("v1.33")
    findings = audit(d)
    errors = [f.message for f in findings if f.severity == "ERROR" and f.check == "dist"]
    assert any("truncated-beta" in m for m in errors), errors


def test_audit_warns_on_an_assembled_band_claiming_a_ci_shape():
    # the rounding-band row declaring `normal` is a WARN, not an ERROR:
    # the shape mismatch is a smell (band was assembled), caught loudly
    import csv as _csv
    import io
    import pathlib
    import tempfile

    s = open(PARAMS_DIR / "parameters.csv").read()
    rows = list(_csv.reader(s.splitlines()))
    di = rows[0].index("dist")
    for r in rows[1:]:
        if r[0] == "local_unemp_shock->household_ipv":  # exp() spec-range band
            r[di] = "normal"
    buf = io.StringIO()
    _csv.writer(buf, lineterminator="\n").writerows(rows)
    d = pathlib.Path(tempfile.mkdtemp())
    (d / "parameters.csv").write_text(buf.getvalue())
    for name in ("nodes.csv", "baselines.csv", "references.bib", "doi_review.json", "correlations.csv"):
        try:
            (d / name).write_text(open(PARAMS_DIR / name).read())
        except OSError:
            pass
    (d / "VERSION").write_text("v1.33")
    findings = audit(d)
    warns = [f.message for f in findings if f.severity == "WARN" and f.check == "dist"]
    assert any("local_unemp_shock->household_ipv" in m for m in warns), warns
