"""v1.29 pins: the place-resolved layer (shrinkage + mobility modifier).

What this file hunts:
- a unit bug at the place swap: a county value must replace the
  national baseline in the SAME unit and population — no conversion
  may happen in the loader (a county rate in per-100k silently
  entering a per-person-year chain is the classic fake-scale bug)
- pooling weight fabrication: a county value without its precision n
  must NOT be pooled — the outcome stays national with the reason
  stated; shrinkage with n <= 0 must return the national value
- the shrinkage math drifting: the empirical-Bayes weight w = n/(n+k)
  and its declared prior n values are pinned (k is a modeling choice;
  an empirical-Bayes estimator may replace k later, not the formula)
- modifier fabrication: before the Chetty-Hendren parameter row is
  extracted, the mobility modifier must report `blocked` naming the
  link — never an invented multiplier
- modifier math errors: gap-vs-median scaling, band direction
  following the gap sign, gap=0 -> exactly 1.0
- fallback silence: an unknown place key or a missing national row
  must fail loudly, not quietly degrade
"""
import json

import pytest

from downstream.audit import audit
from downstream.params import Baseline, Parameter, ParameterSet, load, default_dir
from downstream.place import (
    MOBILITY_MODIFIER_LINK,
    PRIOR_N,
    Place,
    load_places,
    mobility_modifier,
    national,
    place_baselines,
    shrink,
)

PARAMS_DIR = default_dir()
PARAMS = load(PARAMS_DIR / "parameters.csv")
NAT_RATE = 0.004944  # the verified all_cause_mortality_annual baseline


def _baseline_dict() -> dict[str, Baseline]:
    return {
        "all_cause_mortality_annual": Baseline(
            outcome="all_cause_mortality_annual",
            unit="deaths_per_person_year",
            population="US prime-age men (45-54)",
            value=NAT_RATE,
            citation="cdc_wonder D76 pooled 2015-2019",
            source="cdc_wonder",
            status="verified",
        ),
        "divorce_5y_cumulative": Baseline(
            outcome="divorce_5y_cumulative",
            unit="prob_per_marriage",
            population="US married couples 5y window",
            value=0.1045,
            citation="Census P70-125 Table 4",
            source="us_census_sipp",
            status="verified",
        ),
        "median_male_lifetime_earnings": Baseline(
            outcome="median_male_lifetime_earnings",
            unit="usd_2024",
            population="US men",
            value=2591418.0,
            citation="SSA CWHS Table 4.B6",
            source="ssa",
            status="verified",
        ),
    }


def _national_row() -> Place:
    return Place(
        key="national", name="United States", level="national",
        mobility_percentile=50.0, mobility_n=None,
        mortality_rate=None, mortality_n=None,
        divorce_rate=None, divorce_n=None,
        citation="national sources",
    )


def _philly(deaths_n: float | None = 2864.0) -> Place:
    return Place(
        key="42101", name="Philadelphia County PA", level="county",
        mobility_percentile=12.0, mobility_n=None,
        mortality_rate=0.006200, mortality_n=deaths_n,
        divorce_rate=None, divorce_n=None,
        citation="derived from cdc_wonder_d76_county 2015-2019",
    )


def _places(philly: Place | None = None) -> dict[str, Place]:
    d = {"national": _national_row()}
    if philly is not None:
        d[philly.key] = philly
    return d


def test_version_is_v129():
    assert (PARAMS_DIR / "VERSION").read_text().strip() == "v1.46"


# --- loader -------------------------------------------------------

def test_load_places_absent_file_is_empty_not_crash(tmp_path):
    assert load_places(tmp_path / "nope.csv") == {}


def test_load_places_parses_rows_and_skips_comments(tmp_path):
    csv = tmp_path / "places.csv"
    csv.write_text(
        "# header comment\n"
        "key,name,level,mobility_percentile,mobility_n,mortality_rate,"
        "mortality_n,divorce_rate,divorce_n,citation\n"
        "national,United States,national,,,,,,,nat source\n"
        "42101,Philadelphia County PA,county,12.0,,0.006200,2864,,,county source\n"
    )
    places = load_places(csv)
    assert set(places) == {"national", "42101"}
    assert places["42101"].mortality_rate == 0.006200
    assert places["42101"].mobility_percentile == 12.0
    assert places["national"].mortality_rate is None


def test_national_row_required():
    with pytest.raises(KeyError, match="no 'national' row"):
        national({})


def test_unknown_place_key_fails_loudly():
    with pytest.raises(KeyError):
        place_baselines(_places(), _baseline_dict(), "99999")
    with pytest.raises(KeyError):
        mobility_modifier(PARAMS, _places(), "99999")


# --- shrinkage ----------------------------------------------------

def test_shrink_formula_exact():
    v, w = shrink(0.006200, 2864.0, NAT_RATE, 2000.0)
    assert w == pytest.approx(2864.0 / 4864.0)
    assert v == pytest.approx((1 - w) * NAT_RATE + w * 0.006200)


def test_shrink_no_precision_n_returns_national():
    v, w = shrink(0.006200, None, NAT_RATE, 2000.0)
    assert v == NAT_RATE and w == 0.0
    v, w = shrink(0.006200, 0.0, NAT_RATE, 2000.0)
    assert v == NAT_RATE and w == 0.0


def test_shrink_n_equals_k_is_midpoint():
    v, w = shrink(0.006200, 2000.0, NAT_RATE, 2000.0)
    assert w == pytest.approx(0.5)
    assert v == pytest.approx((NAT_RATE + 0.006200) / 2)


def test_shrink_large_n_converges_to_county():
    v, w = shrink(0.006200, 200_000.0, NAT_RATE, 2000.0)
    assert w == pytest.approx(200_000.0 / 202_000.0)
    assert v == pytest.approx(0.006200, abs=2e-5)


def test_shrink_is_monotone_in_n():
    vals = [shrink(0.006200, n, NAT_RATE, 2000.0)[0] for n in (10, 100, 1000, 10000)]
    assert vals == sorted(vals)  # county > national: shrunk rises toward county


def test_prior_n_declared_per_outcome():
    assert PRIOR_N == {
        "all_cause_mortality_annual": 2000.0,
        "divorce_5y_cumulative": 200.0,
    }


# --- place_baselines ----------------------------------------------

def test_place_baselines_refuses_generic_mortality_pooling():
    out = place_baselines(_places(_philly()), _baseline_dict(), "42101")
    o = out["provenance"]["overrides"]["all_cause_mortality_annual"]
    assert o["applied"] is False
    assert "build params/county_mortality.csv" in o["reason"]
    b = out["baselines"]["all_cause_mortality_annual"]
    assert b.value == NAT_RATE


def test_place_baselines_without_n_stays_national():
    out = place_baselines(_places(_philly(deaths_n=None)), _baseline_dict(), "42101")
    o = out["provenance"]["overrides"]["all_cause_mortality_annual"]
    assert o["applied"] is False
    assert "build params/county_mortality.csv" in o["reason"]
    assert out["baselines"]["all_cause_mortality_annual"].value == NAT_RATE


def test_place_baselines_divorce_missing_stays_national():
    out = place_baselines(_places(_philly()), _baseline_dict(), "42101")
    o = out["provenance"]["overrides"]["divorce_5y_cumulative"]
    assert o["applied"] is False
    assert "no county value" in o["reason"]
    assert out["baselines"]["divorce_5y_cumulative"].value == 0.1045


def test_place_baselines_national_row_is_identity():
    out = place_baselines(_places(), _baseline_dict(), "national")
    assert out["baselines"]["all_cause_mortality_annual"].value == NAT_RATE
    assert all(
        o["applied"] is False for o in out["provenance"]["overrides"].values()
    )


def test_place_baselines_does_not_mutate_the_input():
    baselines = _baseline_dict()
    place_baselines(_places(_philly()), baselines, "42101")
    assert baselines["all_cause_mortality_annual"].value == NAT_RATE


def test_place_json_is_cli_round_trip():
    from downstream.place import place_json

    out = place_json(_places(_philly()), _baseline_dict(), "42101", PARAMS)
    json.dumps(out)  # raises on dataclass leakage
    assert out["baselines"]["all_cause_mortality_annual"]["value"]
    assert "mobility_modifier" in out
    # the compute path keeps real Baseline objects
    b = place_baselines(_places(_philly()), _baseline_dict(), "42101")
    assert isinstance(b["baselines"]["all_cause_mortality_annual"], Baseline)


# --- mobility modifier ---------------------------------------------

def test_modifier_landed_row_applies_with_citation():
    m = mobility_modifier(PARAMS, _places(_philly()), "42101")
    assert m["applied"] is True and m["blocked"] is False
    assert m["citation"] == "chettyhendren2018"


def _synthetic_ps(point: float = 0.001) -> ParameterSet:
    p = Parameter(
        link=MOBILITY_MODIFIER_LINK,
        from_node="neighborhood_exposure",
        to_node="child_outcomes_modifier",
        point=point, low=point / 2, high=point * 2,
        tier="canonical", citation="chettymclaren2018",
        population_scope="children of displaced workers",
    )
    # REPLACE the real row (by_link returns the first match — an
    # appended synthetic row would be shadowed by the landed one)
    rows = [p if r.link == MOBILITY_MODIFIER_LINK else r for r in PARAMS.parameters]
    return ParameterSet(version=PARAMS.version, parameters=tuple(rows))


def test_modifier_math_with_synthetic_row():
    m = mobility_modifier(_synthetic_ps(), _places(_philly()), "42101")
    assert m["applied"] is True
    # gap = 12 - 50 = -38; scale = 18/100
    assert m["multiplier"]["point"] == pytest.approx(1 + 0.18 * 0.001 * (-38))
    # negative gap: the LOW band comes from the HIGH parameter side
    assert m["multiplier"]["low"] == pytest.approx(1 + 0.18 * 0.002 * (-38))
    assert m["multiplier"]["high"] == pytest.approx(1 + 0.18 * 0.0005 * (-38))
    # band brackets the point
    assert m["multiplier"]["low"] <= m["multiplier"]["point"] <= m["multiplier"]["high"]


def test_modifier_at_national_reference_is_exactly_one():
    m = mobility_modifier(_synthetic_ps(), _places(_philly()), "national")
    assert m["applied"] is True
    assert m["multiplier"]["point"] == pytest.approx(1.0)
    assert m["multiplier"]["low"] == pytest.approx(1.0)
    assert m["multiplier"]["high"] == pytest.approx(1.0)


def test_modifier_below_reference_uses_the_real_row():
    ps = _synthetic_ps()
    m = mobility_modifier(ps, _places(_philly()), "42101")  # pct 12 vs national 50
    assert m["multiplier"]["point"] < 1.0  # below-national mobility hurts


def test_modifier_blocked_without_county_percentile():
    ps = _synthetic_ps()
    place = Place(
        key="01001", name="No Percentile County", level="county",
        mobility_percentile=None, mobility_n=None,
        mortality_rate=None, mortality_n=None,
        divorce_rate=None, divorce_n=None, citation="x",
    )
    # even with the link present, a missing county percentile blocks honestly
    m = mobility_modifier(ps, _places(place), "01001")
    assert m["applied"] is False
    assert "no mobility_percentile for '01001'" in m["reason"]


def test_modifier_blocked_without_national_percentile():
    ps = _synthetic_ps()
    nat = Place(
        key="national", name="United States", level="national",
        mobility_percentile=None, mobility_n=None,
        mortality_rate=None, mortality_n=None,
        divorce_rate=None, divorce_n=None, citation="x",
    )
    m = mobility_modifier(ps, {"national": nat}, "national")
    assert m["applied"] is False
    assert "national row has no mobility_percentile" in m["reason"]


# --- vignette unchanged ---------------------------------------------

def test_vignette_still_median_county_without_places():
    from downstream.vignette import standard_family

    out = standard_family(PARAMS)
    assert "median county" in out["vignette"]["definition"]


# --- audit -----------------------------------------------------------

def test_audit_flags_missing_national_row(tmp_path):
    d = tmp_path / "p"
    d.mkdir()
    import shutil

    for f in ("parameters.csv", "nodes.csv", "baselines.csv", "references.bib"):
        shutil.copy(PARAMS_DIR / f, d / f)
    (d / "places.csv").write_text(
        "key,name,level,mobility_percentile,mobility_n,mortality_rate,"
        "mortality_n,divorce_rate,divorce_n,citation\n"
        "42101,Philadelphia County PA,county,12.0,,0.006200,2864,,,src\n"
    )
    findings = audit(d)
    assert any(
        f.severity == "ERROR" and "no 'national' row" in f.message for f in findings
    )


def test_audit_flags_county_rate_without_n(tmp_path):
    d = tmp_path / "p"
    d.mkdir()
    import shutil

    for f in ("parameters.csv", "nodes.csv", "baselines.csv", "references.bib"):
        shutil.copy(PARAMS_DIR / f, d / f)
    (d / "places.csv").write_text(
        "key,name,level,mobility_percentile,mobility_n,mortality_rate,"
        "mortality_n,divorce_rate,divorce_n,citation\n"
        "national,United States,national,,,,,,,nat\n"
        "42101,Philadelphia County PA,county,12.0,,0.006200,,,,src\n"
    )
    findings = audit(d)
    assert any(
        f.severity == "WARN" and "mortality_n" in f.message for f in findings
    )


# --- v1.31 integration: the modifier + shrunk baselines in the
# --- vignette and scenario surfaces ----------------------------------

def test_modifier_parameter_is_derived_not_new():
    from downstream.place import modifier_parameter

    out = modifier_parameter(PARAMS, _places(_philly()), "42101")
    p = out["parameter"]
    mod = out["modifier"]
    assert p is not None
    assert p.link == "place:42101->child_outcomes_modifier"
    assert p.tier == "derived"
    assert p.citation == mod["citation"] == "chettyhendren2018"
    # the derived values ARE the modifier's multiplier — no new estimate
    assert p.point == mod["multiplier"]["point"]
    assert (p.low, p.high) == (mod["multiplier"]["low"], mod["multiplier"]["high"])
    # the declared assumption travels with the row
    assert "same-place contrast" in p.notes and "exploratory" in p.notes


def test_modifier_parameter_blocked_when_places_absent():
    from downstream.place import modifier_parameter

    out = modifier_parameter(PARAMS, {}, "42101")
    assert out["parameter"] is None
    assert out["modifier"]["applied"] is False


def test_legacy_child_line_repeats_multiplier():
    from downstream.children import CHILD_DIRECT, GRANDCHILD, child_line
    from downstream.place import modifier_parameter

    base = child_line(PARAMS)
    mp = modifier_parameter(PARAMS, _places(_philly()), "42101")
    line = child_line(PARAMS, place_modifier=mp["parameter"], place_application="legacy_repeated")
    m = mp["modifier"]["multiplier"]
    direct = PARAMS.by_link(CHILD_DIRECT).point
    ige = PARAMS.by_link(GRANDCHILD).point
    # child: the modifier scales the direct displacement loss, so a null
    # displacement effect would remain 1 at every place.
    assert line["child"].point == pytest.approx(1 - m["point"] * (1 - direct))
    # Grandchild: repeated loss scaling wraps the IGE propagation.
    expected_gc = 1 - m["point"] * ige * m["point"] * (1 - direct)
    assert line["grandchild"].point == pytest.approx(expected_gc, rel=1e-9)
    # every generation carries the step with its citation trail
    for gen in ("child", "grandchild", "greatgrandchild"):
        assert any(s.link == mp["parameter"].link for s in line[gen].steps)
        assert base[gen].point != line[gen].point


def test_child_line_without_modifier_is_unchanged():
    from downstream.children import child_line

    base = child_line(PARAMS)
    line = child_line(PARAMS, place_modifier=None)
    assert line["child"].point == base["child"].point
    assert len(line["child"].steps) == len(base["child"].steps)


def test_vignette_place_block_and_scaled_children():
    from downstream.vignette import standard_family

    out = standard_family(PARAMS, places=_places(_philly()), place_key="42101")
    assert out["place"]["applied"] is True and out["place"]["key"] == "42101"
    assert out["place"]["mobility_percentile"] == 12.0
    # ledger dicts round to 4 places — loose enough to survive rounding
    direct = PARAMS.by_link("displacement->child_earnings").point
    expected = 1 - modifier_for_place()["multiplier"]["point"] * (1 - direct)
    assert out["children_stream"]["child"]["point"] == pytest.approx(expected, abs=1e-3)
    assert any("same-place" in n and "exploratory" in n for n in out["composition_notes"])


def modifier_for_place():
    from downstream.place import modifier_parameter

    return modifier_parameter(PARAMS, _places(_philly()), "42101")["modifier"]


def test_vignette_without_place_is_back_compat():
    from downstream.vignette import standard_family

    out = standard_family(PARAMS)
    assert out["place"] is None
    # the worker/child numbers must be byte-identical to the old surface
    out2 = standard_family(PARAMS, places=_places(_philly()))  # no key: no-op
    assert out2["place"] is None
    assert out2["children_stream"]["child"]["point"] == out["children_stream"]["child"]["point"]


def test_vignette_unknown_place_key_fails_loudly():
    from downstream.vignette import standard_family

    with pytest.raises(KeyError):
        standard_family(PARAMS, places=_places(_philly()), place_key="99999")


def test_legacy_scenario_refuses_generic_county_mortality_baseline():
    from downstream.scenario import ScenarioInput, compute_counts

    base = compute_counts(
        PARAMS, _baseline_dict(), ScenarioInput(displaced_workers=1000, mortality_method="legacy_additive")
    )
    out = compute_counts(
        PARAMS, _baseline_dict(), ScenarioInput(displaced_workers=1000, mortality_method="legacy_additive"),
        places=_places(_philly()), place_key="42101",
    )
    # Generic county precision is not a likelihood denominator, so the
    # production scenario remains on the compatible national rate.
    assert out["modeled"]["excess_deaths"]["baseline"]["value"] == NAT_RATE
    ratio = out["modeled"]["excess_deaths"]["point"] / base["modeled"]["excess_deaths"]["point"]
    assert ratio == pytest.approx(1.0)
    ov = out["place"]["baseline_overrides"]["all_cause_mortality_annual"]
    assert ov["applied"] is False


def test_scenario_child_earnings_carry_the_modifier():
    from downstream.children import CHILD_DIRECT
    from downstream.scenario import ScenarioInput, compute_counts

    base = compute_counts(
        PARAMS, _baseline_dict(), ScenarioInput(displaced_workers=1000)
    )
    out = compute_counts(
        PARAMS, _baseline_dict(), ScenarioInput(displaced_workers=1000),
        places=_places(_philly()), place_key="42101",
    )
    m = modifier_for_place()["multiplier"]["point"]
    # Same-place contrast: place M scales the displacement loss itself.
    expected_ratio = m
    pc = out["modeled"]["child_lifetime_earnings_lost_usd"]["point"] / base["modeled"]["child_lifetime_earnings_lost_usd"]["point"]
    assert pc == pytest.approx(expected_ratio, rel=1e-3)
    assert out["place"]["modifier_applied"] is True


def test_same_place_modifier_has_zero_response_to_null_displacement():
    from dataclasses import replace
    from downstream.children import CHILD_DIRECT, child_line
    from downstream.place import modifier_parameter

    null_params = type(PARAMS)(PARAMS.version, tuple(
        replace(p, point=1.0, low=1.0, high=1.0) if p.link == CHILD_DIRECT else p
        for p in PARAMS.parameters
    ))
    modifier = modifier_parameter(null_params, _places(_philly()), "42101")["parameter"]
    assert child_line(null_params, place_modifier=modifier)["child"].point == 1.0


def test_scenario_place_untouched_without_key():
    from downstream.scenario import ScenarioInput, compute_counts

    base = compute_counts(PARAMS, _baseline_dict(), ScenarioInput(displaced_workers=1000))
    assert base["place"] is None


def test_cli_place_smoke():
    import subprocess
    import sys

    r = subprocess.run(
        [sys.executable, "-m", "downstream.cli", "family", "--place", "42101"],
        capture_output=True, text=True,
        env={**__import__("os").environ, "PYTHONPATH": "src"},
    )
    assert r.returncode == 0, r.stderr[-400:]
    out = json.loads(r.stdout)
    assert out["place"]["applied"] is True
    r2 = subprocess.run(
        [sys.executable, "-m", "downstream.cli", "scenario", "--workers", "500", "--place", "42101"],
        capture_output=True, text=True,
        env={**__import__("os").environ, "PYTHONPATH": "src"},
    )
    assert r2.returncode == 0, r2.stderr[-400:]
    assert json.loads(r2.stdout)["place"]["modifier_applied"] is True


# --- v1.36: county mortality posterior integration (strict contract) ---

def _county_mortality_table():
    from downstream.county_rates import load_county_mortality_posteriors

    return load_county_mortality_posteriors(PARAMS_DIR / "county_mortality.csv")


def test_county_mortality_posterior_table_loads_strictly():
    table = _county_mortality_table()
    assert len(table) == 2748
    autauga = table["01001"]
    assert autauga.outcome == "all_cause_mortality_annual"
    assert (autauga.events, autauga.person_years) == (115, 19096.0)
    # posterior mean = (prior_rate * prior_py + events) / (prior_py + person_years)
    expected = (0.004944 * 2000.0 + 115) / (2000.0 + 19096.0)
    assert autauga.posterior_mean_rate == pytest.approx(expected, abs=1e-9)


def test_county_mortality_loader_refuses_duplicates_and_blank_provenance(tmp_path):
    from downstream.county_rates import load_county_mortality_posteriors

    header = ("key,outcome,population_scope,time_window,events,person_years,"
              "posterior_mean_rate,prior_rate,prior_unit,prior_population,"
              "prior_citation,prior_person_years,observation_citation\n")
    good = ("01001,all_cause_mortality_annual,scope,2015-2019,115,19096,"
            "0.005919985,0.004944,deaths_per_person_year,pop,cite,2000,cite\n")
    with pytest.raises(ValueError, match="duplicate"):
        load_county_mortality_posteriors(_write(tmp_path, header + good + good))
    with pytest.raises(ValueError, match="blank provenance"):
        load_county_mortality_posteriors(
            _write(tmp_path, header + good.replace(",pop,", ",,")))
    with pytest.raises(ValueError, match="invalid counts"):
        load_county_mortality_posteriors(
            _write(tmp_path, header + good.replace("115,19096", "-1,19096")))


def _write(tmp_path, content):
    p = tmp_path / "county_mortality.csv"
    p.write_text(content)
    return p


def test_place_mortality_applies_strict_posterior_contract():
    from downstream.params import load_baselines

    places = load_places(PARAMS_DIR / "places.csv")
    # the real baseline table: the strict check compares the posterior's
    # prior chain against baselines.csv's exact value/population/citation
    baselines = load_baselines(PARAMS_DIR / "baselines.csv")
    out = place_baselines(places, baselines, "01001",
                          county_mortality=_county_mortality_table())
    override = out["provenance"]["overrides"]["all_cause_mortality_annual"]
    assert override["applied"] is True
    assert override["contract"] == "Gamma-Poisson posterior (strict events + person-years)"
    assert override["weight"] == pytest.approx(19096 / (2000 + 19096), abs=1e-6)
    county_baseline = out["baselines"]["all_cause_mortality_annual"]
    assert county_baseline.value == pytest.approx(0.005919985, abs=1e-9)
    assert county_baseline.unit == "deaths_per_person_year"
    assert "Gamma-Poisson posterior" in county_baseline.notes
    # the shipped national baseline row stays untouched
    assert baselines["all_cause_mortality_annual"].value == 0.004944


def test_place_mortality_refuses_broken_prior_chain():
    import dataclasses

    places = load_places(PARAMS_DIR / "places.csv")
    table = _county_mortality_table()
    row = dataclasses.replace(table["01001"], prior_rate=0.005)
    out = place_baselines(places, _baseline_dict(), "01001",
                          county_mortality={**table, "01001": row})
    override = out["provenance"]["overrides"]["all_cause_mortality_annual"]
    assert override["applied"] is False
    assert "does not match the national baseline value" in override["reason"]
    assert out["baselines"]["all_cause_mortality_annual"].value == 0.004944


def test_place_mortality_refuses_missing_row_or_table():
    from downstream.params import load_baselines

    places = load_places(PARAMS_DIR / "places.csv")
    baselines = load_baselines(PARAMS_DIR / "baselines.csv")
    # no table at all
    out = place_baselines(places, baselines, "01001")
    override = out["provenance"]["overrides"]["all_cause_mortality_annual"]
    assert override["applied"] is False
    assert "build params/county_mortality.csv" in override["reason"]
    # table present, county absent (suppressed)
    table = {k: v for k, v in _county_mortality_table().items() if k != "01001"}
    out = place_baselines(places, baselines, "01001", county_mortality=table)
    override = out["provenance"]["overrides"]["all_cause_mortality_annual"]
    assert override["applied"] is False
    assert "suppressed or absent" in override["reason"]
    assert out["baselines"]["all_cause_mortality_annual"].value == 0.004944


def test_scenario_place_resolved_mortality_changes_counts():
    from downstream.scenario import ScenarioInput, compute_counts
    from downstream.params import load_all, load_baselines

    parts = load_all(PARAMS_DIR)
    places = load_places(PARAMS_DIR / "places.csv")
    table = _county_mortality_table()
    baselines = load_baselines(PARAMS_DIR / "baselines.csv")
    national = compute_counts(parts["params"], baselines,
                              ScenarioInput(1000))
    resolved = compute_counts(parts["params"], baselines,
                              ScenarioInput(1000), places=places,
                              place_key="01001", county_mortality=table)
    n_point = national["modeled"]["excess_deaths"]["point"]
    r_point = resolved["modeled"]["excess_deaths"]["point"]
    assert r_point > n_point  # Autauga's rate is above the national mean
    # monotone consistency with the rate ratio at 20y follow-up
    ratio = resolved["modeled"]["excess_deaths"]["components"]
    assert ratio["follow_up_years"] == 20.0
