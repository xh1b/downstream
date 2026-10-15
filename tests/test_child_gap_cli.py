# @ref:test-child-gap-cli
# Method: @link:doc-child-gap-view.
# Implementation: @link:code-child-gap-view; @link:code-cli.
# @tag:children @tag:testing
"""CLI delivery preserves signed subgroup results and explicit refusals."""
import json

import pytest

from downstream.cli import main


def test_child_gap_command_has_three_separate_generations(capsys):
    assert main(["child-gaps", "--workers", "1000"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["combined_total"] is None
    assert [row["generation"] for row in result["rows"]] == ["child", "grandchild", "greatgrandchild"]
    assert result["rows"][0]["value"]["point"] == pytest.approx(9.24)
    assert not result["housing_chain"]["available"]


def test_child_gap_cli_keeps_benefits_place_and_valuation_context(tmp_path, capsys):
    path = tmp_path / "profiles.json"
    path.write_text(json.dumps([{"age_at_displacement": 12, "sex": "Male"}]*2))
    assert main(["child-gaps", "--workers", "0.125", "--child-income-quartile", "3",
                 "--income-rank-definition", "source-matched fixture", "--place", "17043",
                 "--child-profiles", str(path), "--real-discount-rate", ".03", "--valuation-year", "2026"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["rows"][0]["value"]["point"] < 0
    assert result["place"]["key"] == "17043"
    assert result["child_applicability"]["status"] == "demographic_match"
    assert result["child_valuation"]["real_discount_rate"] == .03
    assert result["child_valuation"]["projections"]["constant_career_gap"]["point"] < 0
    assert all(not row["eligible_for_public_headline"] for row in result["rows"])


def test_child_gap_cli_withholds_incompatible_demographics(tmp_path, capsys):
    path = tmp_path / "profiles.json"
    path.write_text(json.dumps([{"age_at_displacement": 30, "sex": "Female"}]*2))
    assert main(["child-gaps", "--workers", "1000", "--child-profiles", str(path)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert all(not row["available"] and row["value"] is None for row in result["rows"])


@pytest.mark.parametrize("extra", [["--workers", "-1"], ["--workers", "1", "--place", "invalid"],
                                   ["--workers", "1", "--child-profiles", "/missing-fixture.json"]])
def test_child_gap_cli_errors_are_standard_parser_errors(extra):
    with pytest.raises(SystemExit) as exc:
        main(["child-gaps", *extra])
    assert exc.value.code == 2
