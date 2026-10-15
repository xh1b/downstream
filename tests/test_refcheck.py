"""@ref:/@link: anchors are unique, well-formed, and every link resolves."""

import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / "scripts/refcheck.py"
SPEC = importlib.util.spec_from_file_location("refcheck", SOURCE)
REFCHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REFCHECK)


def scan(files):
    return REFCHECK.scan_entries(list(files.items()))


class RefcheckTests(unittest.TestCase):
    def test_single_anchor_with_many_links_passes(self):
        defs, links, malformed = scan({
            "a.py": "# anchor\n# @ref:deploy-checklist\n",
            "docs/guide.md": "See `@link:deploy-checklist` first.\n"
                             "Also `@link:deploy-checklist` again.\n",
            "tasks/x/card.md": "Evidence: @link:deploy-checklist\n",
        })
        self.assertEqual(sorted(defs), ["deploy-checklist"])
        self.assertEqual(len(links), 3)
        self.assertEqual(malformed, [])
        self.assertEqual(REFCHECK.check_problems(defs, links, malformed), [])

    def test_duplicate_definition_fails_and_lists_both_sites(self):
        defs, links, malformed = scan({
            "a.py": "# @ref:one-place\n",
            "b/c.md": "text @ref:one-place tail\n",
        })
        problems = REFCHECK.check_problems(defs, links, malformed)
        self.assertEqual(len(problems), 1)
        self.assertIn("@ref:one-place", problems[0])
        self.assertIn("a.py:1", problems[0])
        self.assertIn("b/c.md:1", problems[0])
        self.assertIn("duplicate", problems[0])

    def test_dangling_link_fails_and_resolved_link_passes(self):
        defs, links, malformed = scan({
            "a.py": "# @link:missing\n# @link:known\n",
            "b.md": "@ref:known\n",
        })
        problems = REFCHECK.check_problems(defs, links, malformed)
        self.assertEqual(len(problems), 1)
        self.assertIn("dangling link @link:missing -> a.py:1", problems[0])

    def test_markdown_fenced_examples_are_ignored(self):
        defs, links, malformed = scan({
            "guide.md": "Real: @ref:real-one and @link:real-one.\n\n"
                        "```sh\n# fake @ref:fake-one and @link:fake-two\n"
                        "rg '@ref:fake-one'\n```\n\n~~~text\n@ref:fake-three\n~~~\n",
        })
        self.assertEqual(sorted(defs), ["real-one"])
        self.assertEqual([rid for rid, _, _ in links], ["real-one"])
        self.assertEqual(malformed, [])
        self.assertEqual(REFCHECK.check_problems(defs, links, malformed), [])

    def test_placeholders_css_and_embedded_tokens_do_not_match(self):
        defs, links, malformed = scan({
            "docs.md": "Write @ref:<id> in prose. Not `x@ref:bad`, not `1@link:bad2`.\n",
            "s.css": ".link:hover { color: red; } .ref:focus {}\n",
            "t.py": "value = 'word@link:nine'\n",
        })
        self.assertEqual(defs, {})
        self.assertEqual(links, [])
        self.assertEqual(malformed, [])

    def test_malformed_token_case_and_edges_fail_loudly(self):
        defs, links, malformed = scan({
            "a.py": "# @ref:Deploy-Checklist\n# @link:Bad_Id\n# @ref:trailing-\n# @ref:good-one\n",
        })
        self.assertEqual(sorted(defs), ["good-one"])
        problems = REFCHECK.check_problems(defs, links, malformed)
        self.assertEqual(len(problems), 3)
        joined = "\n".join(problems)
        for token in ("@ref:Deploy-Checklist", "@link:Bad_Id", "@ref:trailing-"):
            self.assertIn(f"malformed anchor `{token}`", joined)
        self.assertIn("ids are lowercase", joined)

    def test_tag_tokens_only_need_a_valid_shape(self):
        defs, links, malformed = scan({
            "a.py": "# @tag:deploy and @tag:deploy again — tags repeat freely\n",
            "card.md": "tags: [@tag:bug, @tag:deploy]\n",
        })
        self.assertEqual(defs, {})
        self.assertEqual(links, [])
        self.assertEqual(malformed, [])
        self.assertEqual(REFCHECK.check_problems(defs, links, malformed), [])
        defs2, links2, malformed2 = scan({
            "b.py": "# @tag:Deploy and @link:known\n",
            "c.md": "@ref:known\n",
        })
        self.assertEqual([t for t, _, _ in malformed2], ["@tag:Deploy"])
        problems = REFCHECK.check_problems(defs2, links2, malformed2)
        self.assertEqual(len(problems), 1)
        self.assertIn("malformed anchor `@tag:Deploy`", problems[0])

    def test_list_and_show_report_sites_and_links(self):
        entries = [("a.py", "# @ref:hub\n"),
                   ("b.md", "@link:hub\n"),
                   ("c.md", "@link:hub\n")]
        out = io.StringIO()
        with contextlib.redirect_stdout(out), patch.object(
                REFCHECK, "scan_repo", return_value=REFCHECK.scan_entries(entries)):
            code = REFCHECK.main(["list"])
        self.assertEqual(code, 0)
        self.assertIn("@ref:hub  links=2  a.py:1", out.getvalue())

        out = io.StringIO()
        with contextlib.redirect_stdout(out), patch.object(
                REFCHECK, "scan_repo", return_value=REFCHECK.scan_entries(entries)):
            code = REFCHECK.main(["show", "hub"])
        self.assertEqual(code, 0)
        self.assertIn("@ref:hub -> a.py:1", out.getvalue())
        self.assertIn("b.md:1", out.getvalue())
        self.assertIn("c.md:1", out.getvalue())

        out = io.StringIO()
        err = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), patch.object(
                REFCHECK, "scan_repo", return_value=REFCHECK.scan_entries(entries)):
            code = REFCHECK.main(["show", "absent"])
        self.assertEqual(code, 1)
        self.assertIn("no anchor", err.getvalue())

    def test_check_exit_codes_on_clean_and_broken_trees(self):
        clean = [("a.py", "# @ref:ok\n"), ("b.md", "@link:ok\n")]
        broken = [("a.py", "@link:nowhere\n")]
        for entries, expected in ((clean, 0), (broken, 1)):
            out = io.StringIO()
            with contextlib.redirect_stdout(out), patch.object(
                    REFCHECK, "scan_repo", return_value=REFCHECK.scan_entries(entries)):
                code = REFCHECK.main(["check"])
            self.assertEqual(code, expected, out.getvalue())
            self.assertIn("failure(s)", out.getvalue())

    def test_read_text_skips_binary_oversized_and_missing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "bin.dat").write_bytes(b"\0\1binary")
            (root / "big.txt").write_bytes(b"a" * (REFCHECK.MAX_BYTES + 1))
            (root / "ok.txt").write_text("hello @ref:x", encoding="utf-8")
            with patch.object(REFCHECK, "REPO_ROOT", root):
                self.assertIsNone(REFCHECK.read_text("bin.dat"))
                self.assertIsNone(REFCHECK.read_text("big.txt"))
                self.assertEqual(REFCHECK.read_text("ok.txt"), "hello @ref:x")
        self.assertIsNone(REFCHECK.read_text("definitely/missing/file.txt"))

    def test_allowlisted_files_are_not_scanned(self):
        texts = {"a.py": "# @ref:kept\n", "tests/fixtures.py": "# @ref:dup\n# @link:dup\n"}
        with patch.object(REFCHECK, "load_allowlist", return_value={"tests/fixtures.py"}), \
                patch.object(REFCHECK, "iter_token_files", return_value=list(texts)), \
                patch.object(REFCHECK, "read_text", side_effect=lambda p: texts[p]), \
                patch.object(REFCHECK, "_cache_file", return_value=None):
            defs, links, _ = REFCHECK.scan_repo()
        self.assertEqual(sorted(defs), ["kept"])
        self.assertEqual(links, [])

    def test_scan_cache_reuses_results_for_identical_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").mkdir()
            texts = {"a.md": "# @ref:one\n"}
            scanned = []
            real_scan = REFCHECK.scan_entries

            def counting(entries):
                scanned.append(entries[0][0])
                return real_scan(entries)

            with patch.object(REFCHECK, "_cache_file",
                              return_value=root / ".git" / "refcheck-cache-v1.json"), \
                    patch.object(REFCHECK, "iter_token_files", return_value=list(texts)), \
                    patch.object(REFCHECK, "read_text", side_effect=lambda p: texts[p]), \
                    patch.object(REFCHECK, "scan_entries", side_effect=counting):
                REFCHECK.scan_repo()
                REFCHECK.scan_repo()
            self.assertEqual(scanned, ["a.md"])  # second run served from cache

    def test_scan_cache_invalidates_on_changed_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").mkdir()
            texts = {"a.md": "# @ref:one\n"}
            with patch.object(REFCHECK, "_cache_file",
                              return_value=root / ".git" / "refcheck-cache-v1.json"), \
                    patch.object(REFCHECK, "iter_token_files", return_value=list(texts)), \
                    patch.object(REFCHECK, "read_text", side_effect=lambda p: texts[p]):
                defs1, links1, _ = REFCHECK.scan_repo()[:3]
                texts["a.md"] = "# @ref:two\n# @ref:two\n"
                defs2, links2, _ = REFCHECK.scan_repo()[:3]
            self.assertEqual(sorted(defs1), ["one"])
            self.assertEqual(defs2["two"], [("a.md", 1), ("a.md", 2)])
            self.assertNotIn("one", defs2)

    def test_load_allowlist_reads_comments_and_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "refcheck-allowlist.txt"
            path.write_text("# comment\n\na.py\nb.md\n", encoding="utf-8")
            with patch.object(REFCHECK, "ALLOWLIST_PATH", path):
                self.assertEqual(REFCHECK.load_allowlist(), {"a.py", "b.md"})


    def test_partial_lowercase_prefix_does_not_hide_malformed_names(self):
        defs, links, malformed = scan({
            "a.py": "# @ref:goodBad and @link:goodBAD and @tag:goodBad\n",
        })
        self.assertEqual(defs, {})
        self.assertEqual(links, [])
        self.assertEqual(len(malformed), 3)

    def test_tag_shape_matches_board_names_including_trailing_separators(self):
        defs, links, malformed = scan({"card.md": "tags: [@tag:bug-, @tag:bug_]\n"})
        self.assertEqual(REFCHECK.check_problems(defs, links, malformed), [])

if __name__ == "__main__":
    unittest.main()
