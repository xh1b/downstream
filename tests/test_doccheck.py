# @ref:test-documentation-checks
# Method: @link:development-tooling; @link:integration-examples.
# Implementation: @link:script-doccheck; @link:script-software-reference; @link:code-cli.
# @tag:tooling @tag:testing
"""Documentation checks reject broken navigation and executable-contract drift."""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]


def script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"scripts/{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECK = script("doccheck")
REFERENCE = script("build_software_reference")


def project(root, files):
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    known = set(files) | {parent.as_posix() for name in files for parent in Path(name).parents}
    return known


def test_exact_case_is_checked_against_inventory_not_host_filesystem(tmp_path):
    known = project(tmp_path, {"docs/readme.md": "[bad](Guide.md#scope)\n", "docs/guide.md": "# Scope\n"})
    errors, links = CHECK.check_documents(tmp_path, ["docs/readme.md"], known)
    assert links == 1
    assert len(errors) == 1
    assert "incorrectly cased" in errors[0] and "Guide.md" in errors[0]


def test_missing_target_and_missing_heading_have_distinct_diagnostics(tmp_path):
    known = project(tmp_path, {"README.md": "[absent](none.md) [section](docs/guide.md#absent)",
                               "docs/guide.md": "# Present\n"})
    errors, _ = CHECK.check_documents(tmp_path, ["README.md"], known)
    assert len(errors) == 2
    assert "path" in errors[0]
    assert "missing heading" in errors[1]


def test_relative_root_encoded_and_reference_links_resolve(tmp_path):
    known = project(tmp_path, {"docs/readme.md": '[a](../README.md#start) [b](/README.md#start)\n'
                               '[c](<a (b).md#named>)\n[d][destination]\n'
                               '[destination]: a%20(b).md#named "title"\n'
                               '<img src="image.svg">\n',
                               "README.md": "# Start\n", "docs/a (b).md": '<a id="named"></a>\n',
                               "docs/image.svg": "<svg/>"})
    errors, links = CHECK.check_documents(tmp_path, ["docs/readme.md"], known)
    assert not errors
    assert links == 5


def test_nested_parentheses_and_optional_titles(tmp_path):
    known = project(tmp_path, {"docs/readme.md": '[one](a(b).md#one "title") [same](#home)\n# Home\n',
                               "docs/a(b).md": "# One\n"})
    assert CHECK.check_documents(tmp_path, ["docs/readme.md"], known)[0] == []


def test_external_urls_and_repository_tokens_are_not_files(tmp_path):
    known = project(tmp_path, {"README.md": '[a](https://example.com/a#b) [b](mailto:a@example.com) '
                               '[c](@task:2026-10-17-source) [d](' + '@' + 'link:source) [e](task:2026-10-17-source)'})
    assert CHECK.check_documents(tmp_path, ["README.md"], known) == ([], 0)


def test_fenced_inline_and_commented_examples_are_ignored(tmp_path):
    text = '# Actual\n```md\n[bad](missing)\n# Fake\n```\n`[bad](missing)`\n<!-- [bad](missing) -->\n'
    known = project(tmp_path, {"README.md": text})
    assert CHECK.check_documents(tmp_path, ["README.md"], known) == ([], 0)
    assert CHECK.heading_ids(text) == {"actual"}


def test_slugs_follow_document_order_and_keep_duplicate_headings():
    text = "Same\n====\n## Same\n### `Code` & [Link](other.md)\n~~~\n# Hidden\n~~~\n"
    assert CHECK.heading_ids(text) == {"same", "same-1", "code--link"}


def test_fence_length_and_language_preserve_source_lines():
    text = "# Intro\n\n````pycon\n>>> 2 + 2\n4\n```\n````\n"
    assert list(CHECK.blocks(text)) == [("pycon", ">>> 2 + 2\n4\n```\n", 4)]


def test_lowercase_policy_is_limited_to_docs(tmp_path):
    known = project(tmp_path, {"docs/Guide.md": "# Scope\n", "README.md": "# Scope\n"})
    errors, _ = CHECK.check_documents(tmp_path, sorted(known - {"docs", "."}), known)
    assert errors == ["docs/Guide.md: documentation filename must be lowercase"]


def test_historical_task_threads_and_migration_are_not_live_docs():
    files = {"README.md", "docs/audits/review.md", "tasks/README.md", "tasks/AGENTS.md",
             "tasks/MIGRATION.md", "tasks/review/2026-10-17-scope/comments.md",
             "tasks/review/2026-10-17-scope/card.md", "validation/sipp/MANIFEST.md"}
    assert CHECK.documents(files) == ["README.md", "docs/audits/review.md", "tasks/AGENTS.md",
                                     "tasks/README.md", "validation/sipp/MANIFEST.md"]


def test_examples_check_actual_output_and_restore_cwd(tmp_path):
    project(tmp_path, {"docs/integration.md": '```pycon\n>>> print("hello")\nhello\n```\n'})
    previous = Path.cwd()
    assert CHECK.check_examples(tmp_path, ["docs/integration.md"]) == ([], 1)
    assert Path.cwd() == previous


def test_changed_example_output_fails_with_source_context(tmp_path):
    project(tmp_path, {"docs/integration.md": "```pycon\n>>> 2 + 2\n5\n```\n"})
    errors, attempted = CHECK.check_examples(tmp_path, ["docs/integration.md"])
    assert attempted == 1
    assert "Expected:" in errors[0] and "Got:" in errors[0]
    assert "docs/integration.md" in errors[0]


def test_example_namespaces_are_isolated_and_audits_do_not_execute(tmp_path):
    project(tmp_path, {"docs/integration.md": '```pycon\n>>> private = 3\n```\n'
                      '```pycon\n>>> "private" in globals()\nFalse\n```\n',
                      "docs/audits/review.md": "```pycon\n>>> raise RuntimeError('historical')\n```\n"})
    assert CHECK.check_examples(tmp_path, ["docs/integration.md", "docs/audits/review.md"]) == ([], 2)


def test_freshness_runs_every_builder_read_only_and_reports_failures(monkeypatch):
    calls = []
    def run(command, **kwargs):
        calls.append(command)
        bad = "pool_readiness" in command[1]
        return SimpleNamespace(returncode=int(bad), stdout="", stderr="stale" if bad else "")
    monkeypatch.setattr(CHECK.subprocess, "run", run)
    errors = CHECK.check_freshness(ROOT)
    assert len(calls) == 6
    assert all(command[-1] == "--check" for command in calls)
    assert len(errors) == 1 and "pool_readiness" in errors[0]


def test_generated_reference_follows_added_parser_commands(monkeypatch):
    from downstream import cli
    parser = cli.build_parser()
    action = next(a for a in parser._actions if isinstance(a, argparse._SubParsersAction))
    action.add_parser("new-contract", help="new command | description")
    monkeypatch.setattr(cli, "build_parser", lambda: parser)
    text = REFERENCE.render()
    assert "| `new-contract` | new command \\| description |" in text
    assert "receiving-community" in text
    assert "| `displaced_workers` | `float` | `required` |" in text
    assert "compute_counts(" in text


def test_reference_replacement_preserves_authored_surroundings():
    text = f"intro\n{REFERENCE.START}\nold\n{REFERENCE.END}\noutro\n"
    updated = REFERENCE.replace_reference(text, "new\n")
    assert updated.startswith("intro\n") and updated.endswith("\noutro\n")
    assert "old" not in updated and "new" in updated
    with pytest.raises(ValueError, match="marker pair"):
        REFERENCE.replace_reference("no markers", "new")


def test_methods_html_check_does_not_repair_stale_output(tmp_path, monkeypatch):
    methods = script("build_methods_html")
    monkeypatch.setattr(methods, "ROOT", tmp_path)
    monkeypatch.setattr(methods, "build", lambda: "current\n")
    output = tmp_path / "docs/methods.html"
    assert methods.main(["--check"]) == 1
    assert not output.exists()
    output.parent.mkdir()
    output.write_text("stale\n")
    assert methods.main(["--check"]) == 1
    assert output.read_text() == "stale\n"
    assert methods.main([]) == 0
    assert methods.main(["--check"]) == 0


def test_html_fragment_links_are_checked_in_addition_to_markdown(tmp_path):
    known = project(tmp_path, {"README.md": "[ok](docs/methods.html#scope) [bad](docs/methods.html#absent)",
                               "docs/methods.html": '<section id="scope">Content</section>'})
    errors, links = CHECK.check_documents(tmp_path, ["README.md"], known)
    assert links == 2
    assert len(errors) == 1 and "missing heading #absent" in errors[0]


def test_generated_signature_block_is_valid_python_syntax():
    import ast
    text = REFERENCE.render()
    source = next(source for info, source, _ in CHECK.blocks(text) if info == "python")
    tree = ast.parse(source)
    assert any(isinstance(node, ast.FunctionDef) and node.name == "compute_counts" for node in tree.body)
    assert all(isinstance(node, ast.FunctionDef) for node in tree.body)
