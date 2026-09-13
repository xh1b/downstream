"""Admission-contract guard rails across the small modules.

Each test pins one loud-failure branch: the loaders and constructors must
refuse malformed input with the reason named, and the back-compat /
fallback surfaces must keep working.
"""

import dataclasses
import json
from pathlib import Path

import pytest

from downstream.params import Baseline, Parameter, ParameterSet, load_all
from downstream.scenario import ScenarioInput

PARAMS_DIR = Path(__file__).resolve().parent.parent / "params"
PARTS = load_all(PARAMS_DIR)
PARAMS = PARTS["params"]
NODES = PARTS["nodes"]


# --- citations: bib field value forms --------------------------------------

def test_bib_field_parser_reads_quoted_braced_and_bare_values(tmp_path):
    from downstream.citations import parse_bib

    bib = tmp_path / "refs.bib"
    bib.write_text(
        "@article{a2020,\n"
        "  title = \"Quoted Title\",\n"
        "  year = {2021},\n"
        "  evidence = canonical,\n"
        "}\n",
        encoding="utf-8",
    )
    entries = parse_bib(bib)
    assert entries["a2020"].title == "Quoted Title"
    assert str(entries["a2020"].year) == "2021"
    assert entries["a2020"].evidence == "canonical"


# --- policy: PolicyCase admission checks ------------------------------------

def test_policy_case_requires_scenario_and_finite_bracket():
    from downstream.policy import PolicyCase

    with pytest.raises(ValueError, match="scenario must be ScenarioInput"):
        PolicyCase(name="n", source="s", method="m", scenario={"displaced_workers": 1})
    with pytest.raises(ValueError, match="exposure bounds"):
        PolicyCase(name="n", source="s", method="m",
                   scenario=ScenarioInput(displaced_workers=10),
                   exposure_low=float("nan"))
    with pytest.raises(ValueError, match="bracket"):
        PolicyCase(name="n", source="s", method="m",
                   scenario=ScenarioInput(displaced_workers=10), exposure_high=5)


# --- bundle: manifest verification refusals ---------------------------------

def _bundle_dir(tmp_path, name):
    from downstream.bundle import export_bundle

    out = tmp_path / name
    export_bundle(out, PARAMS_DIR)
    return out


def _rewrite_manifest(bundle, mutate):
    manifest = json.loads((bundle / "manifest.json").read_text())
    mutate(manifest)
    (bundle / "manifest.json").write_text(json.dumps(manifest))
    return manifest


def test_bundle_verification_refuses_tampering(tmp_path):
    from downstream.bundle import verify_bundle

    good = _bundle_dir(tmp_path, "good")
    assert verify_bundle(good)["schema"] == "downstream-engine-bundle/1"

    bad_schema = _bundle_dir(tmp_path, "schema")
    _rewrite_manifest(bad_schema, lambda m: m.update(schema="other/1"))
    with pytest.raises(ValueError, match="unsupported bundle schema"):
        verify_bundle(bad_schema)

    escape = _bundle_dir(tmp_path, "escape")
    _rewrite_manifest(escape, lambda m: m["files"].update({"../evil.txt": "0" * 64}))
    with pytest.raises(ValueError, match="invalid bundle path"):
        verify_bundle(escape)

    tampered = _bundle_dir(tmp_path, "tampered")
    target = next(iter(json.loads((tampered / "manifest.json").read_text())["files"]))
    (tampered / target).write_text("tampered")
    with pytest.raises(ValueError, match="checksum mismatch"):
        verify_bundle(tampered)

    bad_manifest = _bundle_dir(tmp_path, "manifest")
    _rewrite_manifest(bad_manifest, lambda m: m.update(sha256="0" * 64))
    with pytest.raises(ValueError, match="manifest checksum mismatch"):
        verify_bundle(bad_manifest)

    bad_version = _bundle_dir(tmp_path, "version")
    _rewrite_manifest(bad_version, lambda m: m.update(algo_version="wrong"))
    with pytest.raises(ValueError, match="bundle version mismatch"):
        verify_bundle(bad_version)


# --- employer: warehouse mapping + entity scenario guards --------------------

def test_warehouse_mapping_refuses_bad_subject_type_or_breakdown():
    from downstream.employer import DocumentedExposure

    with pytest.raises(ValueError, match="employer and person"):
        DocumentedExposure.from_warehouse(
            subject_id="x", subject_type="plant", source="s",
            americans_displaced=2.0, displacement_breakdown={})
    with pytest.raises(ValueError, match="displacement_breakdown must be an object"):
        DocumentedExposure.from_warehouse(
            subject_id="x", subject_type="employer", source="s",
            americans_displaced=2.0, displacement_breakdown="nope")


def test_entity_counts_refuse_bool_child_counts():
    from downstream.employer import DocumentedExposure, compute_entity_counts

    exposure = DocumentedExposure(subject_id="x", subject_type="employer",
                                  displaced_workers=2, source="s", method="m")
    for kwargs in ({"n_children": True}, {"n_children": -1}):
        with pytest.raises(ValueError, match="nonnegative integer"):
            compute_entity_counts(PARAMS, PARTS["baselines"], exposure,
                                  ScenarioInput(0, **kwargs))


# --- community: SchoolExposure validation ------------------------------------

def test_school_exposure_validates_numbers():
    from downstream.community import SchoolExposure

    with pytest.raises(ValueError, match="must be finite"):
        SchoolExposure(spend_pct=float("nan"), exposure_years=1.0)
    with pytest.raises(ValueError, match="nonnegative"):
        SchoolExposure(spend_pct=1.0, exposure_years=-1.0)


# --- mortality: unit conversions and profile guards --------------------------

def test_rate_to_risk_refuses_invalid_rates():
    from downstream.mortality import rate_to_risk

    for bad in (-0.1, float("inf"), float("nan"), True, "0.1"):
        with pytest.raises(ValueError, match="finite and nonnegative"):
            rate_to_risk(bad)


def test_source_profile_phase_years_validates_years():
    from downstream.mortality import source_profile_phase_years

    with pytest.raises(ValueError, match="years must be finite"):
        source_profile_phase_years(-1)
    out = source_profile_phase_years(0.5)
    assert sum(out.values()) == pytest.approx(0.5)


def test_excess_deaths_profile_validates_inputs_and_phases():
    from downstream.mortality import excess_deaths_profile, source_profile_phase_years

    phases = {name: 1.2 for name, _ in
              [("peak", 0), ("sustained", 0)]}  # wrong keys on purpose
    with pytest.raises(ValueError, match="exactly phases"):
        excess_deaths_profile(100, 0.005, phases, 20)
    from downstream.mortality import SOURCE_PROFILE_PHASES
    good = {name: 1.2 for name, _ in SOURCE_PROFILE_PHASES}
    for bad in (-5, float("nan")):
        with pytest.raises(ValueError, match="finite and nonnegative"):
            excess_deaths_profile(bad, 0.005, good, 20)
    with pytest.raises(ValueError, match="finite and nonnegative"):
        excess_deaths_profile(100, 0.005, good, -1)
    out = excess_deaths_profile(0, 0.005, good, 20)
    assert out == 0  # no workers, no excess deaths


def test_excess_deaths_refuses_unknown_timing():
    from downstream.mortality import excess_deaths

    with pytest.raises(ValueError, match="unknown mortality timing"):
        excess_deaths(100, 0.005, 2.672, 1.135, 20, timing="whenever")


# --- vignette: back-compat wrapper -------------------------------------------

def test_standard_family_daughter_wrapper_matches_children_stream():
    from downstream.vignette import standard_family, standard_family_daughter

    out = standard_family_daughter(PARAMS)
    full = standard_family(PARAMS)
    assert out["daughter_line_earnings_multiplier"] is not None
    assert full["children_stream"]["grandchild"] is not None


# --- evidence: duplicate id refusals -----------------------------------------

def _corpus_row(corpus_id):
    return f"{corpus_id},https://example.org,x,1,true,retrieved,screened,imported,f.pdf\n"


def test_evidence_loaders_refuse_duplicate_ids(tmp_path):
    from downstream.evidence import load_corpus, load_findings

    corpus_header = ("corpus_id,source_url,sha256,pages,text_extractable,"
                     "retrieval_status,screening_status,import_status,local_filename\n")
    dup = tmp_path / "corpus.csv"
    dup.write_text(corpus_header + _corpus_row("c1") + _corpus_row("c1"))
    with pytest.raises(ValueError, match="duplicate corpus_id"):
        load_corpus(dup)

    findings_header = ("finding_id,corpus_id,exposure,outcome,estimand,point,"
                       "standard_error,unit,time_horizon,population_scope,design,"
                       "composition_status,extraction_status,notes\n")
    row = ("f1,c1,ex,out,est,1.0,0.1,units,year 6+,US,IV,recorded,extracted,note\n")
    dupf = tmp_path / "findings.csv"
    dupf.write_text(findings_header + row + row)
    with pytest.raises(ValueError, match="duplicate finding_id"):
        load_findings(dupf)


# --- scoring: CRPS guards -----------------------------------------------------

def test_crps_guards_and_point_anchor():
    from downstream.scoring import crps_of_point, crps_sample

    with pytest.raises(ValueError, match="empty forecast sample"):
        crps_sample([], 1.0)
    assert crps_of_point(2.0, 5.0) == 3.0
    assert crps_sample([2.0, 2.0], 5.0) == pytest.approx(3.0)


# --- children: place_application guard ----------------------------------------

def test_child_line_refuses_unknown_place_application():
    from downstream.children import child_line

    with pytest.raises(ValueError, match="unknown place_application"):
        child_line(PARAMS, place_application="sometimes")


# --- knobs: band swap + voi guard + flatten fallback --------------------------

def test_with_band_swaps_inverted_edges():
    from downstream.knobs import with_band

    swapped = with_band(PARAMS, "displacement->worker_earnings", 1.2, 0.8)
    p = swapped.by_link("displacement->worker_earnings")
    assert p.low == 0.8 and p.high == 1.2


def test_voi_refuses_parameter_point_outside_its_band():
    from downstream.knobs import value_of_information

    broken = ParameterSet(version="v", parameters=tuple(
        dataclasses.replace(p, point=99.0) if p.link == "grandchild_earnings->greatgrandchild_earnings"
        else p for p in PARAMS.parameters
    ))
    with pytest.raises(ValueError, match="outside its own"):
        value_of_information(broken, lambda ps: 1.0, NODES, draws=4)


def test_flatten_keeps_non_point_values():
    from downstream.knobs import _flatten

    out = _flatten({"modeled": {"a": {"point": 1.0, "low": 0}, "b": "raw"},
                    "multipliers": {"m": {"point": 2.0}}})
    assert out["a"] == 1.0 and out["b"] == "raw"
    assert out["mult:m"] == 2.0 and out["blocked_count"] == 0


# --- county_mortality: metadata and cell guards -------------------------------

WONDER_OK_METADATA = dict(years=[2015, 2016, 2017, 2018, 2019], sex="Male",
                          age="45-54 years", cause="All causes", group_by=["County"],
                          population_unit="person-years", source_url="fixture",
                          retrieved_at="fixture")
WONDER_ROWS = '"County Code"\t"Deaths"\t"Population"\n"01001"\t"20"\t"10000"\n'


def _wonder(tmp_path, metadata, rows=WONDER_ROWS):
    from downstream.county_mortality import parse_export

    export = tmp_path / "county.txt"
    export.write_text(rows, encoding="utf-8")
    return parse_export(export, metadata=metadata)


def test_wonder_metadata_years_must_be_distinct_integers(tmp_path):
    with pytest.raises(ValueError, match="nonempty list of integer years"):
        _wonder(tmp_path, {**WONDER_OK_METADATA, "years": "nope"})
    with pytest.raises(ValueError, match="nonempty and unique"):
        _wonder(tmp_path, {**WONDER_OK_METADATA, "years": [2015, 2015]})


def test_wonder_unavailable_cells_are_counted_not_fatal(tmp_path):
    rows = ('"County Code"\t"Deaths"\t"Population"\n'
            '"01001"\t"20"\t"10000"\n'
            '"01003"\t"NA"\t"1000"\n'
            '"01005"\t"5"\t"0"\n')
    out = _wonder(tmp_path, WONDER_OK_METADATA, rows=rows)
    assert out["rows"] == {"01001": {"mortality_rate": 0.002, "mortality_n": 20}}
    assert out["unavailable_count"] == 2  # NA and zero-population cells


def test_wonder_cause_slug_refuses_unmappable_cause():
    from downstream.county_mortality import _outcome_id

    assert _outcome_id("All causes") == "all_cause_mortality_annual"
    with pytest.raises(ValueError, match="cannot be mapped"):
        _outcome_id("###")


# --- mortality_profiles: loader and mix guards --------------------------------

PROFILE_HEADER = ("profile_id,sex,age,years,cause,geography,annual_rate,"
                  "population_scope,citation,status\n")
PROFILE_ROW = ("p1,Male,45-54,2015-2019,All causes,US,0.005,scope,src,verified\n")


def test_profile_loader_requires_columns_and_metadata(tmp_path):
    from downstream.mortality_profiles import load_profiles

    bad_cols = tmp_path / "p.csv"
    bad_cols.write_text(PROFILE_HEADER.replace(",status", ""))
    with pytest.raises(ValueError, match="requires"):
        load_profiles(bad_cols)

    blank = tmp_path / "b.csv"
    blank.write_text(PROFILE_HEADER + PROFILE_ROW.replace(",Male,", ",,"))
    with pytest.raises(ValueError, match="blank metadata"):
        load_profiles(blank)

    bad_rate = tmp_path / "r.csv"
    bad_rate.write_text(PROFILE_HEADER + PROFILE_ROW.replace("0.005", "-1"))
    with pytest.raises(ValueError, match="invalid annual_rate"):
        load_profiles(bad_rate)

    unverified_rate = tmp_path / "v.csv"
    unverified_rate.write_text(PROFILE_HEADER
                               + PROFILE_ROW.replace("0.005", ""))
    with pytest.raises(ValueError, match="needs annual_rate"):
        load_profiles(unverified_rate)


def test_resolve_mix_refuses_empty_spec():
    from downstream.mortality_profiles import resolve_mix

    assert resolve_mix({}, profile_id=None, mixture=None) == []
    assert resolve_mix({}, profile_id=None, mixture={}) == []


# --- ledger: kind and ordering guards -----------------------------------------

def test_ledger_refuses_unknown_kind_and_orders_bands():
    from downstream.ledger import chain

    with pytest.raises(ValueError, match="unknown composition kind"):
        chain(PARAMS, ["displacement->worker_earnings"], kinds=["sideways"],
              label="x", unit="gap_multiplier")
    out = chain(PARAMS, ["displacement->worker_earnings"], kinds=["direct"],
                label="x", unit="gap_multiplier")
    assert out.point >= out.low - 1e-12


def test_validate_chain_length_mismatch():
    from downstream.ledger import validate_chain

    with pytest.raises(ValueError, match="same length"):
        validate_chain(PARAMS, ["displacement->worker_earnings"], [], NODES)


# --- mc: declared-correlation fallbacks and sample guards ----------------------

def test_declared_spearman_returns_none_without_file(tmp_path):
    from downstream.mc import _declared_spearman

    assert _declared_spearman(PARAMS, tmp_path) == (None, 0)


def test_simulate_many_refuses_non_numeric_samples(monkeypatch):
    import downstream.mc as mc
    import downstream.params as params_mod

    monkeypatch.setattr(params_mod, "default_dir",
                        lambda: PARAMS_DIR)
    with pytest.raises(TypeError, match="must be numeric"):
        mc.simulate_many(PARAMS, lambda ps: {"x": "not-a-number"}, draws=3, nodes={})


def test_simulate_chain_requires_kinds():
    from downstream.mc import simulate_chain

    with pytest.raises(ValueError, match="explicit composition kinds"):
        simulate_chain(PARAMS, ["displacement->worker_earnings"])


# --- render: formatting and empty-section text ---------------------------------

def test_fmt_swaps_inverted_band():
    from downstream.render import _fmt

    assert _fmt((1.0, 2.0, 0.5)) == "1.00 [0.50 to 2.00]"


def _explanation(**overrides):
    from downstream.explanation import Explanation

    fields = dict(claim="c", outcome="o", unit="u", value=(1.0, 0.9, 1.1),
                  horizon="h", population="p", parameter_set_version="v1")
    fields.update(overrides)
    return Explanation(**fields)


def test_render_text_names_empty_drivers_and_blocked_sections():
    from downstream.render import render_text

    exp = _explanation(blocked=[{"outcome": "excess_deaths", "reason": "no baseline"}])
    text = render_text(exp)
    assert "sensitivity analysis not yet run" in text
    assert "Refused to compute" in text
    assert "excess_deaths: no baseline" in text

    exp = _explanation(assumptions=["independence"], drivers=[{"sentence": "the IGE step"}])
    text = render_text(exp)
    assert "Declared assumptions" in text and "independence" in text
    assert "the IGE step" in text


# --- forecast_registry: date, required-field, envelope, and scoring guards ------

VALID_PROPOSAL = {
    "event_id": "e1", "event_source": "src", "population": "pop",
    "outcome": "out", "unit": "units", "measurement_source": "ms",
    "measurement_rule": "mr", "exposure_bridge_source": "bs",
    "algo_version": "av", "outcome_window_start": "2100-01-01T00:00:00+00:00",
    "outcome_window_end": "2100-02-01T00:00:00+00:00",
    "prediction": {"low": 1, "point": 2, "high": 3},
}


def test_forecast_date_requires_timezone():
    from downstream.forecast_registry import _date

    with pytest.raises(ValueError, match="timezone"):
        _date("2026-01-01T00:00:00")


@pytest.mark.parametrize("mutate, message", [
    (lambda p: p.update(event_id="  "), "event_id is required"),
    (lambda p: p.update(prediction={"low": True, "point": 2, "high": 3}),
     "finite numbers"),
    (lambda p: p.update(prediction={"low": 3, "point": 2, "high": 1}),
     "envelope must contain the point"),
])
def test_register_validations(tmp_path, mutate, message):
    from downstream.forecast_registry import register

    proposal = json.loads(json.dumps(VALID_PROPOSAL))
    mutate(proposal)
    with pytest.raises(ValueError, match=message):
        register(tmp_path / "reg.json", proposal)


def test_score_refuses_incomplete_window_or_mismatched_units(tmp_path):
    from datetime import datetime, timezone

    from downstream.forecast_registry import register, score

    reg = tmp_path / "reg.json"
    register(reg, dict(VALID_PROPOSAL))
    record = json.loads(reg.read_text())
    late = datetime(2101, 1, 1, tzinfo=timezone.utc)

    # window still open: refusal comes before any unit check
    with pytest.raises(ValueError, match="not complete"):
        score(record, 2.0, unit="units", source="s")

    # completed window (via `now`), but mismatched units
    with pytest.raises(ValueError, match="matching units and a source"):
        score(record, 2.0, unit="wrong", source="s", now=late)

    # non-finite measurement
    with pytest.raises(ValueError, match="measurement must be finite"):
        score(record, float("nan"), unit="units", source="s", now=late)


# --- scenario: ScenarioInput admission + baseline + mix paths -------------------

def test_scenario_input_validations():
    bad = [
        ({"net_tradable_jobs_lost": True}, "net_tradable_jobs_lost"),
        ({"net_tradable_jobs_lost": -1}, "net_tradable_jobs_lost"),
        ({"net_tradable_jobs_lost": float("nan")}, "net_tradable_jobs_lost"),
        ({"wage_multiplier": 0}, "wage_multiplier"),
        ({"wage_multiplier": float("nan")}, "wage_multiplier"),
        ({"mortality_method": "vibes"}, "unknown mortality_method"),
        ({"mortality_timing": "instant"}, "unknown mortality_timing"),
        ({"mortality_profile": ""}, "nonempty string"),
        ({"mortality_mix": ["a"]}, "must be an object"),
        ({"mortality_profile": "p", "mortality_mix": {"p": 1.0}}, "mutually exclusive"),
        ({"place_application": "sometimes"}, "unknown place_application"),
    ]
    for kwargs, message in bad:
        with pytest.raises(ValueError, match=message):
            ScenarioInput(10, **kwargs)


def test_require_baseline_names_missing_and_unpinned():
    from downstream.scenario import BaselineMissing, require_baseline

    with pytest.raises(BaselineMissing, match="not in params/baselines.csv"):
        require_baseline({}, "nope")
    pending = Baseline(outcome="x", unit="u", population="p", value=None,
                       citation="", source="", status="pending")
    with pytest.raises(BaselineMissing, match="status="):
        require_baseline({"x": pending}, "x")


def test_compute_counts_blocks_deaths_without_mortality_baseline():
    from downstream.scenario import ScenarioInput, compute_counts

    baselines = {k: v for k, v in PARTS["baselines"].items()
                 if k != "all_cause_mortality_annual"}
    out = compute_counts(PARAMS, baselines, ScenarioInput(displaced_workers=100))
    blocked = {b["outcome"] for b in out["blocked"]}
    assert "excess_deaths" in blocked


def test_sample_counts_refuses_bad_draws():
    from downstream.scenario import sample_counts

    scenario = ScenarioInput(displaced_workers=10)
    for bad in (1, True, 2.5, "many"):
        with pytest.raises(ValueError, match="draws"):
            sample_counts(PARAMS, PARTS["baselines"], scenario, draws=bad)


def test_predictive_mortality_unavailability_reasons():
    from downstream.scenario import ScenarioInput, sample_counts

    # legacy additive method defines no bounded cohort probabilities
    legacy = sample_counts(PARAMS, PARTS["baselines"],
                           ScenarioInput(100, mortality_method="legacy_additive"), draws=4)
    assert legacy["predictive_uncertainty"]["available"] is False
    assert "odds_survival" in legacy["predictive_uncertainty"]["reason"]

    # fractional worker aggregates keep expected effects, refuse predictive counts
    fractional = sample_counts(PARAMS, PARTS["baselines"], ScenarioInput(2.5), draws=4)
    assert fractional["predictive_uncertainty"]["available"] is False
    assert "integer worker cohort" in fractional["predictive_uncertainty"]["reason"]

    # no verified mortality baseline
    no_baseline = {k: v for k, v in PARTS["baselines"].items()
                   if k != "all_cause_mortality_annual"}
    out = sample_counts(PARAMS, no_baseline, ScenarioInput(10), draws=4)
    assert out["predictive_uncertainty"]["available"] is False
    assert "no verified mortality baseline" in out["predictive_uncertainty"]["reason"]


# --- admission: scale-compatibility branches ------------------------------------

def test_admission_scale_branches():
    from downstream.admission import compare_synthesis_to_parameter
    from downstream.synthesis import StudyEstimate, random_effects

    def pair(link, scale="log_odds_ratio"):
        return [
            StudyEstimate(link, "s1", .10, .02, scale, "US", "IV", "year 6+"),
            StudyEstimate(link, "s2", .14, .03, scale, "US", "IV", "year 6+"),
        ]

    report = random_effects(pair("earnings_shock->mortality_sustained"))
    out = compare_synthesis_to_parameter(PARAMS, report, NODES)
    assert out["compatible_scale"] is True

    # the same estimand aimed at a level-ratio target has no lossless transform
    out = compare_synthesis_to_parameter(
        PARAMS, random_effects(pair("displacement->local_service_jobs")), NODES)
    assert out["compatible_scale"] is False or out["review_status"] == "manual"

    # a compatible target offered the wrong scale is refused with the reason
    out = compare_synthesis_to_parameter(
        PARAMS, random_effects(pair("earnings_shock->mortality_sustained",
                                    scale="risk_difference")), NODES)
    assert out["compatible_scale"] is False
    assert "expected" in out.get("reason", "")


# --- place: loader edges, pooling validation, strict-contract refusals ---------

PLACE_HEADER = ("key,name,level,mobility_percentile,mobility_n,mortality_rate,"
                "mortality_n,divorce_rate,divorce_n,citation\n")


def test_place_loader_refuses_duplicates_nonfinite_and_negative_n(tmp_path):
    from downstream.place import load_places

    dup = tmp_path / "d.csv"
    row = "01001,Autauga County,county,,,,,,,src\n"
    dup.write_text(PLACE_HEADER + row + row)
    with pytest.raises(ValueError, match="duplicate place key"):
        load_places(dup)

    nonfinite = tmp_path / "n.csv"
    nonfinite.write_text(PLACE_HEADER + "01001,A,county,nan,,,,,,src\n")
    with pytest.raises(ValueError, match="non-finite"):
        load_places(nonfinite)

    negative = tmp_path / "neg.csv"
    negative.write_text(PLACE_HEADER + "01001,A,county,,-5,,,,,src\n")
    with pytest.raises(ValueError, match="negative precision"):
        load_places(negative)


def test_shrink_validates_pooling_inputs():
    from downstream.place import shrink

    with pytest.raises(ValueError, match="pooling inputs"):
        shrink(0.5, 10, float("nan"), 1)
    with pytest.raises(ValueError, match="pooling inputs"):
        shrink(0.5, 10, 0.5, -1)
    with pytest.raises(ValueError, match="county value must be finite"):
        shrink(float("inf"), 10, 0.5, 1)
    with pytest.raises(ValueError, match="county precision must be finite"):
        shrink(0.5, float("nan"), 0.5, 1)


def test_place_strict_contract_refusals_name_the_broken_link():
    from downstream.county_rates import load_county_mortality_posteriors
    from downstream.params import load_baselines
    from downstream.place import load_places, place_baselines

    places = load_places(PARAMS_DIR / "places.csv")
    baselines = load_baselines(PARAMS_DIR / "baselines.csv")
    table = load_county_mortality_posteriors(PARAMS_DIR / "county_mortality.csv")
    row = table["01001"]

    cases = [
        (dataclasses.replace(row, outcome="other_outcome"), "outcome"),
        (dataclasses.replace(row, prior_unit="probability"), "unit mismatch"),
        (dataclasses.replace(row, prior_population="other pop"), "population"),
        (dataclasses.replace(row, prior_citation="other"), "citation does not match"),
    ]
    for new_row, needle in cases:
        out = place_baselines(places, baselines, "01001",
                              county_mortality={**table, "01001": new_row})
        override = out["provenance"]["overrides"]["all_cause_mortality_annual"]
        assert override["applied"] is False
        assert needle in override["reason"]

    # no verified national baseline to verify the prior against
    out = place_baselines(places, {}, "01001", county_mortality=table)
    override = out["provenance"]["overrides"]["all_cause_mortality_annual"]
    assert override["applied"] is False
    assert "no verified national baseline" in override["reason"]


def test_compute_counts_mortality_mix_paths(tmp_path):
    from downstream.mortality_profiles import load_profiles
    from downstream.scenario import ScenarioInput, compute_counts

    profiles = load_profiles(PARAMS_DIR / "mortality_profiles.csv")

    # odds_survival + source_profile (the profile-driven survival kernel)
    out = compute_counts(PARAMS, PARTS["baselines"],
                         ScenarioInput(100, mortality_mix={"male_45_54_2015_2019": 1.0}),
                         mortality_profiles=profiles)
    deaths = out["modeled"]["excess_deaths"]
    assert deaths["baseline"]["profiles"][0]["weight"] == 1.0
    assert deaths["point"] > 0

    # source_aligned timing routes through the legacy excess_deaths kernel
    out = compute_counts(PARAMS, PARTS["baselines"],
                         ScenarioInput(100, mortality_mix={"male_45_54_2015_2019": 1.0},
                                       mortality_timing="source_aligned"),
                         mortality_profiles=profiles)
    assert out["modeled"]["excess_deaths"]["point"] > 0

    # legacy_additive with a profile supplied
    out = compute_counts(PARAMS, PARTS["baselines"],
                         ScenarioInput(100, mortality_mix={"male_45_54_2015_2019": 1.0},
                                       mortality_method="legacy_additive"),
                         mortality_profiles=profiles)
    assert out["modeled"]["excess_deaths"]["point"] > 0

    # a profile requested with no registry supplied is blocked honestly
    out = compute_counts(PARAMS, PARTS["baselines"],
                         ScenarioInput(100, mortality_profile="male_45_54_2015_2019"))
    blocked = {b["outcome"]: b["reason"] for b in out["blocked"]}
    assert "excess_deaths" in blocked
    assert "no mortality profile registry" in blocked["excess_deaths"]
