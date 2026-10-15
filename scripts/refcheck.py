#!/usr/bin/env python3
# @ref:script-refcheck
# Method: @link:docs-index.
# Verification: @link:test-refcheck.
# Related: @link:reference-token-contract.
# @tag:tooling
"""Repo-wide @ref:<id> anchors and @link:<id> references.

`@ref:<id>` defines a named anchor. It must appear exactly once across all
tracked text files. `@link:<id>` references that anchor; a link count is not
limited. This linter fails on duplicate definitions and on links without a
definition. The convention is documented in @link:reference-token-contract.
"""

import argparse
import bisect
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ALLOWLIST_PATH = Path(__file__).resolve().parent / "refcheck-allowlist.txt"
ID_PATTERN = r"[a-z0-9](?:[a-z0-9_-]*[a-z0-9])?"
ID_TAIL_RE = re.compile(r"[A-Za-z0-9_-]+")
NEEDLES = (("ref", "@ref:"), ("link", "@link:"), ("tag", "@tag:"))
FENCE_RE = re.compile(r"(`{3,}|~{3,}).*?\1", re.DOTALL)
MAX_BYTES = 1_000_000
MARKDOWN_SUFFIXES = {".md", ".mdx", ".markdown"}


def iter_tracked_files():
    """Yield repo-relative paths of every tracked file."""
    out = subprocess.run(["git", "-C", str(REPO_ROOT), "ls-files", "-z"],
                         capture_output=True, check=True)
    for raw in out.stdout.split(b"\0"):
        if raw:
            yield raw.decode("utf-8", "surrogateescape")


def iter_token_files():
    """Yield tracked files that contain at least one token needle.

    Every @ref:/@link:/@tag: occurrence must start with its needle, so a
    file with no needle can hold no token and need not be read. ripgrep
    (falling back to git grep) finds those files in one pass and skips
    binary files, the same files read_text would reject; the per-file
    token scan below still decides what counts, because fence-stripping
    and adjacent-character rules need the whole file. Falls back to the
    full tracked list when neither tool can run, so non-repo callers keep
    the old behavior.
    """
    out = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "-z"], capture_output=True)
    if out.returncode != 0:
        yield from iter_tracked_files()
        return
    names = out.stdout
    if names:
        try:
            found = subprocess.run(
                ["xargs", "-0", "rg", "-l", "-e", "@ref:", "-e", "@link:",
                 "-e", "@tag:", "--"],
                input=names, capture_output=True, cwd=str(REPO_ROOT))
        except OSError:  # rg not installed
            found = None
        # BSD xargs reports the utility's no-match exit 1 as 123; both mean
        # rg ran and produced a (possibly empty) path list.
        if found is not None and found.returncode in (0, 1, 123):
            for line in found.stdout.split(b"\n"):
                if line:
                    yield line.decode("utf-8", "surrogateescape")
            return
    out = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "grep", "-I", "--name-only", "-z",
         "-e", "@ref:", "-e", "@link:", "-e", "@tag:", "--"],
        capture_output=True)
    if out.returncode not in (0, 1):
        yield from iter_tracked_files()
        return
    for raw in out.stdout.split(b"\0"):
        if raw:
            yield raw.decode("utf-8", "surrogateescape")


def read_text(rel_path: str) -> str | None:
    """Read one tracked file for scanning; None when binary or oversized."""
    path = REPO_ROOT / rel_path
    try:
        if path.stat().st_size > MAX_BYTES:
            return None
        data = path.read_bytes()
    except OSError:
        return None
    if b"\0" in data:
        return None
    return data.decode("utf-8", "replace")


def strip_fences(text: str) -> str:
    """Blank out fenced blocks (``` or ~~~), preserving every newline so
    reported line numbers stay valid against the original file."""
    return FENCE_RE.sub(lambda m: re.sub(r"[^\n]", "", m.group(0)), text)


def _line_starts(text: str) -> list:
    starts = [0]
    for match in re.finditer("\n", text):
        starts.append(match.end())
    return starts


def _token_candidates(text: str):
    """Every @ref:/@link: occurrence as (position, kind), in text order."""
    found = []
    for kind, needle in NEEDLES:
        at = text.find(needle)
        while at != -1:
            found.append((at, kind))
            at = text.find(needle, at + 1)
    found.sort()
    return found


def scan_entries(entries) -> tuple[dict, list, list]:
    """Scan (path, text) pairs. Returns (definitions, links, malformed).

    definitions maps an id to its [(path, lineno), ...] sites; links holds
    (id, path, lineno) tuples; malformed holds (token, path, lineno) for
    token-shaped ids that violate the charset — this covers @ref:, @link:,
    and @tag: (tags only need the shape; they are defined by use).
    Markdown fences are ignored, so fenced examples never match anything.
    """
    defs: dict[str, list] = {}
    links: list = []
    malformed: list = []
    for path, text in entries:
        if Path(path).suffix.lower() in MARKDOWN_SUFFIXES:
            text = strip_fences(text)
        starts = None

        def lineno(pos: int) -> int:
            nonlocal starts
            if starts is None:
                starts = _line_starts(text)
            return bisect.bisect_right(starts, pos)

        for pos, kind in _token_candidates(text):
            if pos > 0 and (text[pos - 1].isalnum() or text[pos - 1] in "_@"):
                continue  # embedded in a larger token (x@ref:, word@link:)
            id_start = pos + len(kind) + 2  # "@" + kind + ":"
            tail = ID_TAIL_RE.match(text, id_start)
            if not tail:
                continue  # bare needles and angle-bracket prose placeholders
            name = tail[0]
            pattern = r"[a-z0-9][a-z0-9_-]*" if kind == "tag" else ID_PATTERN
            if not re.fullmatch(pattern, name):
                malformed.append((text[pos:tail.end()], path, lineno(pos)))
            elif kind == "ref":
                defs.setdefault(name, []).append((path, lineno(pos)))
            elif kind == "link":
                links.append((name, path, lineno(pos)))
    return defs, links, malformed


def check_problems(defs: dict, links: list, malformed: list) -> list[str]:
    """Uniqueness, resolvability, and charset findings, stable order."""
    problems = []
    for token, path, lineno in sorted(malformed):
        problems.append(f"FAIL malformed anchor `{token}` (ids are lowercase "
                        f"letters, digits, hyphens, underscores) -> {path}:{lineno}")
    for ref_id in sorted(defs):
        sites = defs[ref_id]
        if len(sites) > 1:
            where = ", ".join(f"{path}:{lineno}" for path, lineno in sites)
            problems.append(f"FAIL duplicate definition @ref:{ref_id} -> {where}")
    for ref_id, path, lineno in sorted(links):
        if ref_id not in defs:
            problems.append(f"FAIL dangling link @link:{ref_id} -> {path}:{lineno}")
    return problems


def load_allowlist() -> set:
    """Repo-relative paths exempt from scanning (one per line, # comments).

    The linter's own test fixtures deliberately hold duplicate, dangling,
    and malformed tokens; they live here.
    """
    if not ALLOWLIST_PATH.is_file():
        return set()
    entries = set()
    for line in ALLOWLIST_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            entries.add(line)
    return entries


# ── per-file scan cache ─────────────────────────────────────────────────────
# Fence-stripping and tokenizing the candidate files is most of the
# remaining runtime, and the hook reruns refcheck on every commit. Each
# file's scan result is memoized in .git/ keyed by a hash of the exact
# text, so a cache hit can never diverge from a fresh scan of the same
# bytes. A cache write failure is silent — the scan is complete either way.

CACHE_VERSION = 1


def _cache_file() -> Path | None:
    git_dir = REPO_ROOT / ".git"
    return git_dir / "refcheck-cache-v1.json" if git_dir.is_dir() else None


def _load_cache() -> dict:
    path = _cache_file()
    if path is None:
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if isinstance(data, dict) and data.get("version") == CACHE_VERSION \
            and isinstance(data.get("files"), dict):
        return data["files"]
    return {}


def _save_cache(files: dict) -> None:
    path = _cache_file()
    if path is None:
        return
    tmp = path.with_name(f"{path.name}.tmp-{os.getpid()}")
    try:
        tmp.write_text(json.dumps({"version": CACHE_VERSION, "files": files}),
                       encoding="utf-8")
        os.replace(tmp, path)
    except OSError:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass


def _scan_cached(rel_path: str, text: str, cache: dict) -> tuple[dict, list, list, bool]:
    """scan_entries for one file, memoized by the hash of its text.

    Returns (defs, links, malformed, cache_hit)."""
    digest = hashlib.sha1(text.encode("utf-8", "replace")).hexdigest()
    hit = cache.get(rel_path)
    if isinstance(hit, list) and len(hit) == 4 and hit[0] == digest:
        defs = {ref_id: [tuple(site) for site in sites] for ref_id, sites in hit[1].items()}
        links = [tuple(link) for link in hit[2]]
        malformed = [tuple(tok) for tok in hit[3]]
        return defs, links, malformed, True
    defs, links, malformed = scan_entries([(rel_path, text)])
    cache[rel_path] = [digest,
                       {ref_id: [list(site) for site in sites]
                        for ref_id, sites in defs.items()},
                       [list(link) for link in links],
                       [list(tok) for tok in malformed]]
    return defs, links, malformed, False


def scan_repo():
    allowlist = load_allowlist()
    cache = _load_cache()
    seen: set[str] = set()
    dirty = False
    defs: dict[str, list] = {}
    links: list = []
    malformed: list = []
    for rel_path in sorted(iter_token_files()):
        if rel_path in allowlist:
            continue
        text = read_text(rel_path)
        if text is not None:
            seen.add(rel_path)
            file_defs, file_links, file_malformed, was_hit = \
                _scan_cached(rel_path, text, cache)
            dirty = dirty or not was_hit
            for ref_id, sites in file_defs.items():
                defs.setdefault(ref_id, []).extend(sites)
            links.extend(file_links)
            malformed.extend(file_malformed)
    if dirty:
        _save_cache({k: cache[k] for k in seen if k in cache})
    return defs, links, malformed


def cmd_check() -> int:
    defs, links, malformed = scan_repo()
    problems = check_problems(defs, links, malformed)
    for problem in problems:
        print(problem)
    print(f"refcheck: {len(defs)} anchor(s), {len(links)} link(s), "
          f"{len(problems)} failure(s)")
    return 1 if problems else 0


def cmd_list() -> int:
    defs, links, _ = scan_repo()
    counts: dict[str, int] = {}
    for ref_id, _, _ in links:
        counts[ref_id] = counts.get(ref_id, 0) + 1
    for ref_id in sorted(defs):
        sites = defs[ref_id]
        where = ", ".join(f"{path}:{lineno}" for path, lineno in sites)
        mark = " (!)" if len(sites) > 1 else ""
        print(f"@ref:{ref_id}  links={counts.get(ref_id, 0)}  {where}{mark}")
    for ref_id in sorted({ref_id for ref_id, _, _ in links} - set(defs)):
        print(f"@link:{ref_id}  (dangling)")
    print(f"refcheck: {len(defs)} anchor(s), {len(links)} link(s)")
    return 0


def cmd_show(ref_id: str) -> int:
    if not re.fullmatch(ID_PATTERN, ref_id):
        print(f"error: invalid anchor id `{ref_id}`", file=sys.stderr)
        return 1
    defs, links, _ = scan_repo()
    sites = defs.get(ref_id)
    if not sites:
        print(f"error: no anchor `@ref:{ref_id}` on the repository", file=sys.stderr)
        return 1
    for path, lineno in sites:
        print(f"@ref:{ref_id} -> {path}:{lineno}")
    found = [(path, lineno) for rid, path, lineno in links if rid == ref_id]
    print("Links:")
    if found:
        for path, lineno in found:
            print(f"  {path}:{lineno}")
    else:
        print("  (none)")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="@ref:<id> anchors and @link:<id> references (@link:reference-token-contract)")
    parser.add_argument("verb", nargs="?", default="check",
                        help="check (default), list, or show")
    parser.add_argument("ref", nargs="?", help="anchor id, for `show`")
    args = parser.parse_args(argv)
    if args.verb == "show":
        if not args.ref:
            parser.error("show requires an anchor id")
        return cmd_show(args.ref)
    if args.ref:
        parser.error(f"`{args.verb}` takes no anchor id")
    return cmd_check() if args.verb == "check" else cmd_list()


if __name__ == "__main__":
    sys.exit(main())
