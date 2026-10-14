"""Task links and state changes use Markdown and disposable Git repositories."""

import contextlib
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SOURCE = Path(__file__).resolve().parents[1] / "scripts/tasks.py"
A = "2026-10-14-a"
B = "2026-10-14-b"
C = "2026-10-14-c"
COMMENT = "c-0123456789ab"
EVIDENCE = f"- [x] Preserves source values. [receipt](task:{B}#{COMMENT})\n"


class TaskTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="task-board-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        spec = importlib.util.spec_from_file_location("task_board", SOURCE)
        self.board = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.board)
        self.board.REPO_ROOT = self.root
        self.board.BOARD = self.root / "tasks"
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith("GIT_")}
        self.git("init", "-q", "-b", "master")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.invalid")
        # This fixture has no repository hooks or external signers.
        self.git("config", "core.hooksPath", str(self.root / "no-hooks"))
        self.git("config", "commit.gpgSign", "false")
        for column in self.board.COLUMNS:
            directory = self.board.BOARD / column
            directory.mkdir(parents=True)
            (directory / ".gitkeep").touch()
        self.commit("tasks")

    def git(self, *args):
        result = subprocess.run(["git", "-C", str(self.root), *args],
                                env=self.env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def commit(self, *paths):
        self.git("add", "--", *paths)
        self.git("commit", "-qm", "fixture", "--", *paths)

    def seed(self, card_id, column="ready", fields="", body="- [ ] Check the input.\n", comments="# comments\n"):
        directory = self.board.BOARD / column / card_id
        directory.mkdir()
        assignee = "worker" if column in ("active", "review", "done") else ""
        (directory / "card.md").write_text(
            f"---\ntitle: {card_id}\narea: scripts\npriority: P2\nassignee: {assignee}\n"
            f"{fields}---\n\n{body}")
        (directory / "comments.md").write_text(comments)
        self.commit(str(directory.relative_to(self.root)))
        return directory

    def receipt(self):
        return self.seed(B, comments=f"# comments\n\n## {COMMENT}\n\nTests pass.\n")

    def run_cli(self, *args, code=0, stdin=""):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out), patch("sys.stdin", io.StringIO(stdin)):
            result = self.board.main(list(args))
        self.assertEqual(result, code, out.getvalue())
        return out.getvalue()

    def errors(self):
        return [str(p) for p in self.board.validate_board() if p.level == "ERROR"]

    def test_forward_dependency_to_done_task_validates_and_is_claimable(self):
        self.seed(A, fields=f"blocked-by: [{B}]\n")
        self.seed(B, "done", body="- [x] Complete. [report](https://example.invalid/report)\n")
        self.assertEqual(self.errors(), [])
        self.assertIn(A, self.run_cli("next"))
        self.run_cli("claim", A, "--as", "worker")
        self.assertTrue((self.board.BOARD / "active" / A).is_dir())

    def test_dependencies_to_later_ready_tasks_and_missing_ids_are_distinct(self):
        directory = self.seed(A, fields=f"blocked-by: [{B}]\n")
        self.seed(B)
        self.assertEqual(self.errors(), [])
        self.assertNotIn(A, self.run_cli("next"))
        path = directory / "card.md"
        path.write_text(path.read_text().replace(B, C))
        self.assertIn(f"task `{C}` not found", "\n".join(self.errors()))

    def test_cycles_and_self_relationships_are_errors(self):
        for index, relation in enumerate(("blocked-by", "parent", "duplicate-of")):
            with self.subTest(relation=relation):
                first, second = f"{A}-{index}", f"{B}-{index}"
                value_a = f"[{second}]" if relation == "blocked-by" else second
                value_b = f"[{first}]" if relation == "blocked-by" else first
                self.seed(first, fields=f"{relation}: {value_a}\n")
                self.seed(second, fields=f"{relation}: {value_b}\n")
                self.assertIn(f"{relation} cycle:", "\n".join(self.errors()))
        self.seed(C, fields=f"related-to: [{C}]\n")
        self.assertIn("relationship to itself", "\n".join(self.errors()))

    def test_relationship_types_and_duplicate_fields_do_not_pass_silently(self):
        self.seed(A, fields=f"parent: [{B}]\nrelated-to: {B}\npriority: P1\n")
        errors = "\n".join(self.errors())
        self.assertIn("parent", errors)
        self.assertIn("related-to", errors)
        self.assertIn("duplicate field `priority`", errors)

    def test_markdown_comment_preserves_old_bytes_and_has_no_length_limit(self):
        directory = self.seed(A, comments="# comments\n\n- 2026-10-14 10:00 old: Keep this.\n")
        path = directory / "comments.md"
        old = path.read_bytes()
        body = "### Finding\n\n" + "Full source value " * 200 + "\n\n- First\n- Second\n\n```sql\nSELECT 1;\n```\n"
        output = self.run_cli("comment", A, "--file", "-", "--as", "worker", stdin=body)
        self.assertTrue(path.read_bytes().startswith(old))
        self.assertIn(body, path.read_text())
        self.assertRegex(output, rf"task:{A}#c-[0-9a-f]{{12}}")
        self.assertIn(" HKT", path.read_text())
        self.assertEqual(self.errors(), [])

    def test_replies_resolutions_and_backlinks_survive_column_moves(self):
        self.seed(A)
        self.receipt()
        target = f"task:{B}#{COMMENT}"
        output = self.run_cli("comment", A, "--reply-to", target, "-m", "This also fixes the input.")
        reply = next(line for line in output.splitlines() if line.startswith("task:"))
        self.run_cli("resolve", A, target, "-m", "The rerun confirms it.")
        self.run_cli("claim", B, "--as", "worker")
        output = self.run_cli("refs", target)
        self.assertIn(f"tasks/active/{B}/comments.md", output)
        self.assertIn(reply, output)
        self.assertIn("reply:", output)
        self.assertIn("resolves:", output)
        self.assertIn(f"Resolved: {target}", output)
        self.assertIn(target, self.run_cli("refs", reply))
        self.assertEqual(self.errors(), [])

    def test_relationship_backlinks_include_context_and_no_stored_index(self):
        self.seed(A, fields=f"related-to: [{B}]\nparent: {B}\n")
        self.seed(B)
        output = self.run_cli("refs", B)
        self.assertIn(f"parent: task:{A} -> task:{B}", output)
        self.assertIn(f"related-to: [{B}]", output)
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_bad_comment_references_are_rejected_before_append(self):
        directory = self.seed(A)
        self.receipt()
        previous = (directory / "comments.md").read_bytes()
        for arguments in (("--reply-to", f"task:{B}#c-ffffffffffff", "-m", "Reply"),
                          ("-m", f"Missing task:{C}."),
                          ("-m", f"## {COMMENT}\n\nSpoofed boundary.")):
            self.run_cli("comment", A, *arguments, code=1)
            self.assertEqual((directory / "comments.md").read_bytes(), previous)
        self.run_cli("resolve", A, f"task:{B}", "-m", "Resolved", code=1)
        self.assertEqual((directory / "comments.md").read_bytes(), previous)

    def test_fenced_examples_are_not_edges_checklists_or_comment_ids(self):
        body = f"- [ ] Real criterion.\n\n~~~markdown\ntask:{C}#c-ffffffffffff\n- [x] Example only.\n~~~\n"
        comments = f"# comments\n\n```markdown\n## {COMMENT}\ntask:{C}\n```\n"
        self.seed(A, body=body, comments=comments)
        self.assertEqual(self.errors(), [])
        self.assertEqual(self.board.comment_ids(self.board.collect_cards()[0]), [])
        self.assertEqual(len(self.board.checklist_errors(body)), 1)
        self.assertIn("(none)", self.run_cli("refs", A))

    def test_validation_finds_broken_links_and_duplicate_comment_ids_in_files(self):
        directory = self.seed(A, body=f"- [ ] Check.\n\nSee task:{B}#c-ffffffffffff.\n")
        self.receipt()
        path = directory / "comments.md"
        path.write_text(f"# comments\n\n## {COMMENT}\n\nOne\n\n## {COMMENT}\n\nTwo\n")
        errors = "\n".join(self.errors())
        self.assertIn("duplicate comment ids", errors)
        self.assertIn("comment `c-ffffffffffff` not found", errors)

    def test_create_triage_claim_review_request_changes_accept_and_reopen(self):
        self.receipt()
        self.run_cli("create", A, "--title", "Source: repair", "--area", "scripts",
                     "--file", "-", stdin="Context.\n\n- [ ] Check the input.\n")
        self.run_cli("claim", A, "--as", "worker", code=1)
        self.run_cli("triage", A)
        self.run_cli("claim", A, "--as", "worker")
        self.run_cli("done", A, code=1)
        path = self.board.BOARD / "active" / A / "card.md"
        path.write_text(path.read_text().replace("- [ ] Check the input.\n", EVIDENCE))
        self.commit(str(path.parent.relative_to(self.root)))
        self.run_cli("done", A)
        self.run_cli("request-changes", A, code=1)
        self.run_cli("request-changes", A, "--as", "reviewer", "-m", "Explain the sample.")
        self.assertIn("assignee: worker", (self.board.BOARD / "active" / A / "card.md").read_text())
        self.run_cli("done", A)
        self.run_cli("accept", A, "--as", "reviewer")
        self.run_cli("reopen", A, code=1)
        self.run_cli("reopen", A, "-m", "A new input fails.")
        self.assertIn("assignee:\n", (self.board.BOARD / "ready" / A / "card.md").read_text())
        self.assertEqual(self.errors(), [])
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_done_and_accept_require_nonempty_checklist_and_evidence(self):
        directory = self.seed(A, "active")
        path = directory / "card.md"
        original = path.read_text()
        for body in ("No checklist.\n", "- [x] No evidence.\n", "- [ ] Incomplete.\n"):
            path.write_text(original.replace("- [ ] Check the input.\n", body))
            self.run_cli("done", A, code=1)
            self.assertTrue(directory.exists())
        path.write_text(original.replace("- [ ] Check the input.\n", "- [x] Complete. [report](https://example.invalid/report)\n"))
        self.commit(str(path.parent.relative_to(self.root)))
        self.run_cli("done", A)
        path = self.board.BOARD / "review" / A / "card.md"
        path.write_text(path.read_text().replace("[report](https://example.invalid/report)", "Report pending."))
        self.run_cli("accept", A, code=1)
        self.assertTrue(path.exists())

    def test_blocker_override_drop_cancel_and_cancelled_blockers(self):
        self.seed(A, fields=f"blocked-by: [{B}]\n")
        self.seed(B)
        self.run_cli("claim", A, "--as", "worker", code=1)
        self.run_cli("claim", A, "--as", "worker", "-m", "The independent portion can start.")
        self.run_cli("drop", A)
        self.run_cli("cancel", B, code=1)
        self.run_cli("cancel", B, "-m", "The source is no longer available.")
        self.assertNotIn(A, self.run_cli("next"))
        self.assertEqual(self.errors(), [])
        self.run_cli("reopen", B, "-m", "The source returns.")

    def test_mutating_commands_preserve_unrelated_staged_work(self):
        self.seed(A)
        (self.root / "unrelated.py").write_text("other work\n")
        self.git("add", "--", "unrelated.py")
        self.run_cli("claim", A, "--as", "worker")
        self.assertEqual(self.git("diff", "--cached", "--name-only"), "unrelated.py")
        changed = self.git("show", "--format=", "--name-only", "HEAD")
        self.assertNotIn("unrelated.py", changed)
        self.run_cli("comment", A, "-m", "Keep the index isolated.")
        self.assertEqual(self.git("diff", "--cached", "--name-only"), "unrelated.py")

    def test_bad_ids_foreign_branch_and_missing_files_do_not_mutate(self):
        directory = self.seed(A)
        before = self.git("rev-parse", "HEAD")
        self.run_cli("create", "../escape", "--title", "Test", "--area", "scripts", "-m", "Text", code=1)
        self.run_cli("comment", A, "--file", str(self.root / "missing.md"), code=1)
        self.run_cli("comment", A, "--as", "name\nforged", "-m", "Text", code=1)
        self.git("checkout", "-qb", "foreign")
        self.run_cli("comment", A, "-m", "Text", code=1)
        self.assertEqual(self.git("rev-parse", "HEAD"), before)
        self.assertEqual((directory / "comments.md").read_text(), "# comments\n")

    def test_create_rejects_duplicate_ids_and_multiline_metadata(self):
        self.seed(A)
        self.run_cli("create", A, "--title", "Duplicate", "--area", "scripts", "-m", "Text", code=1)
        self.run_cli("create", B, "--title", "Injected\nassignee: other", "--area", "scripts", "-m", "Text", code=1)
        self.assertIsNone(self.board._find_card(B))


if __name__ == "__main__":
    unittest.main()
