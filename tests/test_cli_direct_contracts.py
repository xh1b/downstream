"""In-process CLI contract coverage for fast public-command routing checks."""
from __future__ import annotations

import json

import pytest

from downstream.cli import main


def _write_json(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


@pytest.mark.parametrize(
    "argv, required",
    [
        (["family"], "vignette"),
        (["scenario", "--workers", "1", "--draws", "2"], "modeled"),
        (["explain", "--draws", "2"], "claim"),
        (["sensitivity", "--base", "2"], "indices"),
        (["knobs", "--action", "sweep", "--link", "displacement->worker_earnings", "--values", "0.75,0.8"], "rows"),
        (["simulate", "--outcome", "child", "--draws", "2"], "outcome"),
        (["infer", "--outcome", "child"], "mean"),
        (["ensemble"], "variants"),
        (["place", "--key", "national"], "mobility_modifier"),
        (["audit"], "summary"),
        (["citations"], "bib_entries"),
        (["credits"], "studies"),
    ],
)
def test_public_cli_verbs_return_json_contracts(argv, required, capsys):
    assert main(argv) == 0
    payload = json.loads(capsys.readouterr().out)
    assert required in payload


def test_parser_error_has_standard_exit_code_and_message(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["simulate", "--links", "displacement->child_earnings"])
    assert exc.value.code == 2
    assert "--kinds is required" in capsys.readouterr().err


@pytest.mark.parametrize(
    "argv, message",
    [
        (["infer", "--links", "displacement->child_earnings"], "infer --links requires --kinds"),
        (["knobs", "--action", "sweep"], "needs --link and --values"),
    ],
)
def test_manual_cli_validation_returns_two(argv, message, capsys):
    assert main(argv) == 2
    assert message in capsys.readouterr().err


def test_file_backed_cli_verbs_route_and_emit_contracts(tmp_path, monkeypatch, capsys):
    policy = _write_json(tmp_path / "policy.json", {
        "baseline": {"name": "before", "source": "fixture", "method": "fixture",
                     "scenario": {"displaced_workers": 1}},
        "policy": {"name": "after", "source": "fixture", "method": "fixture",
                   "scenario": {"displaced_workers": 2}},
    })
    assert main(["policy", "--input", str(policy)]) == 0
    assert json.loads(capsys.readouterr().out)["schema"] == "downstream-policy-comparison/1"

    entity = _write_json(tmp_path / "entity.json", {
        "subject_id": "fixture", "subject_type": "employer", "displaced_workers": 2,
        "source": "fixture", "method": "fixture",
    })
    assert main(["entity", "--input", str(entity)]) == 0
    assert json.loads(capsys.readouterr().out)["subject"]["id"] == "fixture"

    assert main(["entity", "--input", str(entity),
                 "--mortality-profile", "male_45_54_2015_2019"]) == 0
    mortality = json.loads(capsys.readouterr().out)["modeled"]["excess_deaths"]
    assert mortality["baseline"]["profiles"][0]["id"] == "male_45_54_2015_2019"

    proposal = _write_json(tmp_path / "proposal.json", {
        "event_id": "fixture", "event_source": "fixture", "population": "fixture",
        "outcome": "fixture", "unit": "units", "measurement_source": "fixture",
        "measurement_rule": "fixture", "exposure_bridge_source": "fixture", "algo_version": "fixture",
        "outcome_window_start": "2100-01-01T00:00:00+00:00",
        "outcome_window_end": "2100-02-01T00:00:00+00:00",
        "prediction": {"low": 1, "point": 2, "high": 3},
    })
    registration = tmp_path / "registration.json"
    assert main(["forecast-register", "--input", str(proposal), "--out", str(registration)]) == 0
    assert json.loads(capsys.readouterr().out)["schema"] == "downstream-forecast/1"

    import downstream.forecast_registry as registry
    monkeypatch.setattr(registry, "score", lambda *args, **kwargs: {"covered": True, "source": kwargs["source"]})
    assert main(["forecast-score", "--input", str(registration), "--measured", "2", "--unit", "units", "--source", "fixture"]) == 0
    assert json.loads(capsys.readouterr().out)["covered"] is True

    export = tmp_path / "snapshot.json"
    assert main(["export", "--out", str(export)]) == 0
    assert export.is_file()
    capsys.readouterr()

    bundle = tmp_path / "bundle"
    assert main(["bundle", "--out", str(bundle)]) == 0
    assert json.loads(capsys.readouterr().out)["schema"] == "downstream-engine-bundle/1"

    import downstream.cli as cli
    monkeypatch.setattr(cli, "validate_run", lambda params: {"v0_internal_consistency": {"pass": True}})
    assert main(["validate"]) == 0
    assert json.loads(capsys.readouterr().out)["v0_internal_consistency"]["pass"] is True


def test_cli_optional_output_modes_and_failure_statuses(tmp_path, monkeypatch, capsys):
    """Exercise public flags whose output contracts differ from the defaults."""
    from downstream.params import default_dir

    params = str(default_dir())
    assert main(["explain", "--text", "--draws", "2"]) == 0
    assert "parameter set" in capsys.readouterr().out

    snapshot = tmp_path / "snapshot.json"
    assert main(["export", "--params", params, "--out", str(snapshot)]) == 0
    assert snapshot.exists()
    assert f"wrote {snapshot}" in capsys.readouterr().err

    import downstream.cli as cli
    monkeypatch.setattr(cli, "validate_run", lambda params: {"v0_internal_consistency": {"pass": False}})
    assert main(["validate", "--params", params]) == 1
    assert json.loads(capsys.readouterr().out)["v0_internal_consistency"]["pass"] is False


def test_cli_infer_and_simulate_chain_contracts(capsys):
    """The less-common analysis modes retain their distinct JSON schemas."""
    mixed_links = "displacement->child_earnings,child_earnings->grandchild_earnings"
    assert main(["simulate", "--links", mixed_links, "--kinds", "direct,gap", "--draws", "2"]) == 0
    assert "links" in json.loads(capsys.readouterr().out)

    assert main(["infer", "--links", mixed_links, "--kinds", "direct,gap", "--action", "chain"]) == 0
    assert "mean" in json.loads(capsys.readouterr().out)


@pytest.mark.parametrize(
    "argv, message",
    [
        (["infer", "--outcome", "child", "--action", "stress"], "stress needs --stress-links"),
        (["simulate", "--outcome", "child", "--kinds", "gap"], "--kinds and --base apply only"),
        (["knobs", "--action", "sweep", "--link", "x", "--values", "not-a-number"], "could not convert string to float"),
    ],
)
def test_cli_rejects_invalid_optional_mode_combinations(argv, message, capsys):
    if argv[0] == "infer":
        assert main(argv) == 2
    else:
        with pytest.raises(SystemExit) as exc:
            main(argv)
        assert exc.value.code == 2
    assert message in capsys.readouterr().err


# ===========================================================================
# Coverage round: uncommon verbs, error branches, and alternate output modes
# ===========================================================================

import shutil

from downstream.params import default_dir

STUDIES_CSV = (
    "link,study_id,point,standard_error,scale,population_scope,design,time_horizon,citation\n"
    "earnings_shock->mortality_sustained,s1,0.10,0.02,log_odds_ratio,US,IV,year 6+,src1\n"
    "earnings_shock->mortality_sustained,s2,0.14,0.03,log_odds_ratio,US,DiD,year 6+,src2\n"
)

RATES_CSV = (
    "key,outcome,events,person_years,population_scope,time_window,citation\n"
    "01001,mortality,12,2.5,prime-age men,2015-19,src\n"
)

WONDER_EXPORT = '"County Code"\t"Deaths"\t"Population"\n"01001"\t"20"\t"10000"\n'
WONDER_METADATA = ('{"years":[2015,2016,2017,2018,2019],"sex":"Male","age":"45-54 years",'
                   '"cause":"All causes","group_by":["County"],"population_unit":"person-years",'
                   '"source_url":"fixture","retrieved_at":"fixture"}')


def _params_copy_without_places(tmp_path):
    d = tmp_path / "params"
    shutil.copytree(default_dir(), d, ignore=shutil.ignore_patterns("__pycache__"))
    (d / "places.csv").unlink()
    return d


def test_export_without_out_prints_snapshot_to_stdout(capsys):
    assert main(["export"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema"]
    assert payload["source_sha256"]


def test_credits_write_mode_renders_markdown(tmp_path, capsys):
    d = tmp_path / "params"
    shutil.copytree(default_dir(), d, ignore=shutil.ignore_patterns("__pycache__"))
    assert main(["credits", "--write", "--params", str(d)]) == 0
    assert "written: CREDITS.md" in capsys.readouterr().out
    assert (tmp_path / "CREDITS.md").is_file()


def test_sensitivity_dependent_blocks_runs(capsys):
    assert main(["sensitivity", "--base", "2", "--dependent-blocks"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["method"].startswith("correlation-aware")
    assert out["blocks"] and all("S_first" in b for b in out["blocks"])


def test_family_place_error_names_missing_registry(tmp_path):
    bare = _params_copy_without_places(tmp_path)
    with pytest.raises(SystemExit) as exc:
        main(["family", "--place", "national", "--params", str(bare)])
    assert "places.csv absent" in str(exc.value)


def test_simulate_place_errors_are_named(tmp_path, capsys):
    bare = _params_copy_without_places(tmp_path)
    with pytest.raises(SystemExit) as exc:
        main(["simulate", "--outcome", "child", "--draws", "2", "--place", "national",
              "--params", str(bare)])
    assert "places.csv absent" in capsys.readouterr().err

    with pytest.raises(SystemExit) as exc:
        main(["simulate", "--outcome", "child", "--draws", "2", "--place", "atlantis"])
    assert "unknown place" in capsys.readouterr().err


def test_infer_closure_action_reports_coverage(capsys):
    assert main(["infer", "--outcome", "child", "--action", "closure",
                 "--trials", "3", "--draws", "60", "--seed", "7"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["experiment"] == "closure_coverage"
    assert len(out["levels"]) == 4


def test_infer_stress_action_reports_width_move(capsys):
    assert main(["infer", "--outcome", "child", "--action", "stress",
                 "--stress-links", "displacement->child_earnings,child_earnings->grandchild_earnings",
                 "--draws", "60", "--trials", "3", "--seed", "7"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["experiment"] == "correlation_stress"
    assert "width_change" in out


def test_infer_agree_action_crosschecks_mc(capsys):
    assert main(["infer", "--outcome", "child", "--action", "agree", "--draws", "60"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert "mean_diff_in_se" in out


def test_sensitivity_rejects_ci_with_dependent_blocks(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["sensitivity", "--base", "2", "--ci", "2", "--dependent-blocks"])
    assert exc.value.code == 2
    assert "--ci" in capsys.readouterr().err


def test_scenario_place_resolves_national_row(capsys):
    assert main(["scenario", "--workers", "1", "--draws", "2", "--place", "national"]) == 0
    assert "modeled" in capsys.readouterr().out


def test_synthesize_verb_emits_reports_and_parameter_comparisons(tmp_path, capsys):
    csv = tmp_path / "studies.csv"
    csv.write_text(STUDIES_CSV, encoding="utf-8")
    assert main(["synthesize", "--input", str(csv)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert len(out["reports"]) == 1

    assert main(["synthesize", "--input", str(csv), "--link",
                 "earnings_shock->mortality_sustained", "--compare-params"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["reports"][0]["link"] == "earnings_shock->mortality_sustained"
    assert "parameter_comparisons" in out


def test_county_posterior_verb_computes_and_names_misses(tmp_path, capsys):
    csv = tmp_path / "rates.csv"
    csv.write_text(RATES_CSV, encoding="utf-8")
    base = ["county-posterior", "--input", str(csv), "--key", "01001", "--outcome", "mortality",
            "--time-window", "2015-19", "--national-rate", "0.005",
            "--national-population-scope", "prime-age men", "--national-citation", "nat",
            "--prior-person-years", "2000", "--draws", "10"]
    assert main(base) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["observation"]["events"] == 12

    miss = ["county-posterior", "--input", str(csv), "--key", "99999", "--outcome", "mortality",
            "--time-window", "2015-19", "--national-rate", "0.005",
            "--national-population-scope", "prime-age men", "--national-citation", "nat",
            "--prior-person-years", "2000", "--draws", "10"]
    with pytest.raises(SystemExit) as exc:
        main(miss)
    assert exc.value.code == 2
    assert "no county observation matches" in capsys.readouterr().err


def test_county_wonder_posterior_error_paths(tmp_path, capsys):
    export = tmp_path / "county.tsv"
    export.write_text(WONDER_EXPORT, encoding="utf-8")

    bad_json = tmp_path / "bad.json"
    bad_json.write_text("{nope", encoding="utf-8")
    with pytest.raises(SystemExit):
        main(["county-wonder-posterior", "--export", str(export), "--metadata", str(bad_json),
              "--key", "01001", "--national-rate", "0.005", "--prior-person-years", "2000"])
    assert "invalid WONDER metadata JSON" in capsys.readouterr().err

    bad_meta = tmp_path / "incomplete.json"
    bad_meta.write_text('{"years": [2015]}', encoding="utf-8")
    with pytest.raises(SystemExit):
        main(["county-wonder-posterior", "--export", str(export), "--metadata", str(bad_meta),
              "--key", "01001", "--national-rate", "0.005", "--prior-person-years", "2000"])
    assert "invalid WONDER export" in capsys.readouterr().err

    meta = tmp_path / "metadata.json"
    meta.write_text(WONDER_METADATA, encoding="utf-8")
    with pytest.raises(SystemExit):
        main(["county-wonder-posterior", "--export", str(export), "--metadata", str(meta),
              "--key", "99999", "--national-rate", "0.005", "--prior-person-years", "2000"])
    assert "absent or suppressed" in capsys.readouterr().err


def test_policy_invalid_input_is_reported_not_raised(tmp_path, capsys):
    bad_json = tmp_path / "p.json"
    bad_json.write_text("{oops", encoding="utf-8")
    with pytest.raises(SystemExit):
        main(["policy", "--input", str(bad_json)])
    capsys.readouterr()

    missing_keys = tmp_path / "p2.json"
    missing_keys.write_text(json.dumps({"baseline": {}}), encoding="utf-8")
    with pytest.raises(SystemExit):
        main(["policy", "--input", str(missing_keys)])
    assert capsys.readouterr().err


def test_entity_invalid_payload_and_place_errors(tmp_path, capsys):
    bad = tmp_path / "entity.json"
    bad.write_text(json.dumps({"subject_id": "fixture"}), encoding="utf-8")
    with pytest.raises(SystemExit):
        main(["entity", "--input", str(bad)])
    capsys.readouterr()

    good = tmp_path / "good.json"
    good.write_text(json.dumps({
        "subject_id": "fixture", "subject_type": "employer", "displaced_workers": 2,
        "source": "fixture", "method": "fixture",
    }), encoding="utf-8")
    with pytest.raises(SystemExit):
        main(["entity", "--input", str(good), "--place", "atlantis"])
    assert "cannot resolve place" in capsys.readouterr().err


def test_entity_mortality_profile_registry_failure_is_named(tmp_path, capsys):
    d = tmp_path / "params"
    shutil.copytree(default_dir(), d, ignore=shutil.ignore_patterns("__pycache__"))
    (d / "mortality_profiles.csv").write_text("garbage,columns\n1,2\n", encoding="utf-8")
    good = tmp_path / "good.json"
    good.write_text(json.dumps({
        "subject_id": "fixture", "subject_type": "employer", "displaced_workers": 2,
        "source": "fixture", "method": "fixture",
    }), encoding="utf-8")
    with pytest.raises(SystemExit):
        main(["entity", "--input", str(good), "--params", str(d),
              "--mortality-profile", "male_45_54_2015_2019"])
    assert "cannot load mortality profile registry" in capsys.readouterr().err


def test_scenario_invalid_mortality_mix_is_named(capsys):
    with pytest.raises(SystemExit):
        main(["scenario", "--workers", "1", "--draws", "2", "--mortality-mix", "bogus"])
    assert "invalid --mortality-mix" in capsys.readouterr().err


def test_simulate_links_with_place_is_refused(capsys):
    with pytest.raises(SystemExit):
        main(["simulate", "--links", "displacement->child_earnings", "--kinds", "direct",
              "--draws", "2", "--place", "national"])
    assert "--place requires --outcome" in capsys.readouterr().err
