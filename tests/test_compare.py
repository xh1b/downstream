"""Version comparisons must expose numerical and schema changes without positional noise."""
import csv
import io
import json

import pytest

from downstream.cli import main
from downstream.compare import compare_documents, load_documents, render_comparison


def compare(before, after):
    return compare_documents(before, after, "v1", "v2")


def test_named_parameters_reorder_add_remove_and_change():
    before = {"parameters": [{"link": "a", "point": -2, "low": -3},
                              {"link": "removed", "point": 1}]}
    after = {"parameters": [{"link": "new", "point": 5},
                             {"link": "a", "point": -1, "low": -3}]}
    report = compare(before, after)
    rows = {row["path"]: row for row in report["rows"]}
    assert rows["/parameters/link=a/point"] == {
        "path": "/parameters/link=a/point", "status": "changed", "before": -2,
        "after": -1, "delta": 1, "percent_change": 50.0}
    assert rows["/parameters/link=a/low"]["status"] == "unchanged"
    assert rows["/parameters/link=new/point"]["status"] == "added"
    assert rows["/parameters/link=removed/point"]["status"] == "removed"
    assert compare(after, {"parameters": list(reversed(after["parameters"]))})["summary"]["changed"] == 0


def test_zero_null_types_empty_containers_and_escaped_paths():
    report = compare({"zero": 0, "unknown": None, "bool": True, "empty": [], "map": {},
                      "a/b~c": [1, 2], "metadata": "old"},
                     {"zero": 2, "unknown": 4, "bool": 1, "empty": [], "map": {},
                      "a/b~c": [1.0, 2], "metadata": "new"})
    rows = {row["path"]: row for row in report["rows"]}
    assert rows["/zero"]["delta"] == 2
    assert rows["/zero"]["percent_change"] is None
    assert rows["/unknown"]["status"] == "changed"
    assert rows["/unknown"]["delta"] is None
    assert rows["/bool"]["status"] == "changed"
    assert rows["/bool"]["delta"] is None
    assert rows["/a~1b~0c/0"]["status"] == "unchanged"
    assert rows["/metadata"]["status"] == "changed"


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_results_refused(value):
    with pytest.raises(ValueError, match="non-finite"):
        compare({}, {"value": value})


def test_overflow_and_duplicate_identifiers_refused():
    with pytest.raises(ValueError, match="overflow"):
        compare({"x": -1e308}, {"x": 1e308})
    with pytest.raises(ValueError, match="duplicate link"):
        compare({}, {"parameters": [{"link": "a"}, {"link": "a"}]})


def test_plain_arrays_and_records_without_names():
    report = compare({"x": [{"value": 1}, {"name": "a"}]},
                     {"x": [{"value": 2}, {"name": "a"}]})
    assert report["rows"][1]["path"] == "/x/1/name"
    assert report["summary"]["changed"] == 1


def test_repeated_outcomes_use_exposure_identity_and_unnamed_duplicates_use_positions():
    rows = [{"outcome": "mortality", "exposure": "pooled", "point": 1},
            {"outcome": "mortality", "exposure": "male", "point": 2}]
    report = compare({"rows": rows}, {"rows": list(reversed(rows))})
    assert report["summary"]["changed"] == 0
    assert any('"exposure":"male"' in row["path"] for row in report["rows"])
    report = compare({"rows": rows[:1]}, {"rows": rows})
    assert report["summary"]["removed"] == 0
    assert report["summary"]["changed"] == 0
    assert report["summary"]["unchanged"] == 3
    report = compare({}, {"rows": [{"name": "a", "point": 1}, {"name": "a", "point": 2}]})
    assert "/rows/0/point" in {row["path"] for row in report["rows"]}


def test_files_directories_missing_documents_and_empty_directory(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir()
    b.mkdir()
    with pytest.raises(ValueError, match="no JSON"):
        load_documents(a)
    (a / "family.json").write_text('{"deaths": 1}')
    (b / "family.json").write_text('{"deaths": 2}')
    (b / "new.json").write_text('{"child": null}')
    report = compare(load_documents(a), load_documents(b))
    assert report["summary"] == {"changed": 1, "added": 1, "removed": 0, "unchanged": 0}
    assert load_documents(a / "family.json") == {"result": {"deaths": 1}}


def test_render_formats_and_changes_only():
    report = compare({"same": 2, "value": 1}, {"same": 2, "value": 2})
    doc = json.loads(render_comparison(report, "json", True))
    assert len(doc["rows"]) == 1
    assert doc["summary"]["unchanged"] == 1
    rows = list(csv.DictReader(io.StringIO(render_comparison(report, "csv"))))
    assert len(rows) == 2
    assert rows[1]["delta"] == "1"
    markdown = render_comparison(report, changes_only=True)
    assert "| /same |" not in markdown
    assert "| /value | changed | 1 | 2 | 1 | 100.0 |" in render_comparison(report)
    assert "—" in render_comparison(compare({}, {"new": 2}))
    with pytest.raises(ValueError, match="unknown comparison format"):
        render_comparison(report, "invalid")


def test_markdown_shows_all_changes_beyond_one_hundred_fields():
    before = {f"field_{index:03d}": index for index in range(201)}
    after = {name: value + 1 for name, value in before.items()}
    before["removed"] = 7
    after["added"] = 8
    report = compare(before, after)
    markdown = render_comparison(report, changes_only=True)
    assert len([line for line in markdown.splitlines() if line.startswith("| /")]) == 203
    for row in report["rows"]:
        assert f"| {row['path']} | {row['status']} |" in markdown


def test_markdown_escapes_untrusted_result_content():
    report = compare({}, {"<script>|`\n\r&": "<img>"})
    markdown = render_comparison(report)
    assert "<script>" not in markdown
    assert "&lt;script&gt;&#124;&#96;" in markdown


def test_cli_compares_without_loading_local_parameters(tmp_path, monkeypatch, capsys):
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    a.write_text('{"calculated": 1}')
    b.write_text('{"calculated": 3}')
    monkeypatch.setattr("downstream.cli.load_all", lambda _: pytest.fail("loaded params"))
    args = ["compare", "--before", str(a), "--after", str(b)]
    assert main(args + ["--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["rows"][0]["delta"] == 2
    out = tmp_path / "report.csv"
    assert main(args + ["--format", "csv", "--out", str(out)]) == 0
    assert "calculated" in out.read_text()
    a.write_text("broken JSON")
    with pytest.raises(SystemExit) as exc:
        main(args)
    assert exc.value.code == 2
