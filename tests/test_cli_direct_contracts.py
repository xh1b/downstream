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
