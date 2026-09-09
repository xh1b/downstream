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
    assert (PARAMS_DIR / "VERSION").read_text().strip() == "v1.30"


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

def test_place_baselines_swaps_mortality_and_records_pooling():
    out = place_baselines(_places(_philly()), _baseline_dict(), "42101")
    o = out["provenance"]["overrides"]["all_cause_mortality_annual"]
    assert o["applied"] is True
    assert o["county_value"] == 0.006200
    assert o["national_value"] == NAT_RATE
    b = out["baselines"]["all_cause_mortality_annual"]
    assert b.value == pytest.approx(o["shrunk_value"])
    # unit honesty: the swapped row carries the NATIONAL unit and
    # population, and the note declares no conversion
    assert b.unit == "deaths_per_person_year"
    assert "same unit and population as the national baseline" in b.notes
    assert "no conversion applied" in b.notes


def test_place_baselines_without_n_stays_national():
    out = place_baselines(_places(_philly(deaths_n=None)), _baseline_dict(), "42101")
    o = out["provenance"]["overrides"]["all_cause_mortality_annual"]
    assert o["applied"] is False
    assert "precision n missing" in o["reason"]
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
