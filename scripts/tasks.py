#!/usr/bin/env python3
# @ref:script-tasks
# Method: @link:docs-index.
# Verification: @link:test-tasks-workflow; @link:test-tasks-board.
# Related: @link:task-workflow.
# @tag:tooling
"""Markdown task board. See tasks/AGENTS.md for format, references, and commands."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import shlex
import subprocess
import sys
import uuid
from pathlib import Path
from zoneinfo import ZoneInfo

BOARD = Path(__file__).resolve().parent.parent / "tasks"
REPO_ROOT = BOARD.parent
COLUMNS = ("inbox", "ready", "active", "review", "done", "cancelled")
PRIORITIES = ("P1", "P2", "P3", "P4")
ID_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-[a-z0-9]+(-[a-z0-9]+)*$")
SKIP_NAMES = {".gitkeep"}
RELATIONS = {"blocked-by": True, "related-to": True, "parent": False, "duplicate-of": False}
REF_RE = re.compile(r"(?<![@\w:/])@?task:(\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*)(?:#([\w-]+))?")
TAG_NAME_RE = re.compile(r"[a-z0-9][a-z0-9_-]*")
TAG_RE = re.compile(r"@tag:[a-z0-9][a-z0-9_-]*")
COMMENT_RE = re.compile(r"^## (c-[0-9a-f]{12})$")
CHECK_RE = re.compile(r"^\s*- \[([ xX])\]\s+(.+)$")
LINK_RE = re.compile(r"\[[^\]\n]+\]\([^\s)]+(?:\s+[^)]*)?\)")


class Problem:
    def __init__(self, level: str, where: str, message: str):
        self.level, self.where, self.message = level, where, message

    def __str__(self) -> str:
        return f"{self.level}: {self.where}: {self.message}"


# ---------------------------------------------------------------- git helpers

def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(REPO_ROOT), *args], capture_output=True, text=True)


def _repo_preflight() -> str | None:
    """Return an error message when the repo is not ready for a board commit."""
    inside = _git("rev-parse", "--is-inside-work-tree")
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        return "not inside a git work tree"
    branch = _git("branch", "--show-current").stdout.strip()
    if branch != "master":
        return f"on branch `{branch}` — board verbs commit only on master"
    gitdir = Path(_git("rev-parse", "--git-dir").stdout.strip())
    if not gitdir.is_absolute():
        gitdir = REPO_ROOT / gitdir
    for marker in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "rebase-merge", "rebase-apply"):
        if (gitdir / marker).exists():
            return f"repository is mid-operation ({marker}) — resolve it before board verbs"
    return None


def _commit_card(paths: list[str], message: str) -> tuple[int, str]:
    """Commit only named paths, with add/commit chained under the repo rules."""
    error = _repo_preflight()
    if error:
        return 1, error
    status = _git("status", "--short", "--", *paths)
    if status.returncode:
        return 1, status.stderr
    existing = [p for p in paths if (REPO_ROOT / p).exists()]
    commit = shlex.join(["git", "-C", str(REPO_ROOT), "commit", "--only", "-m", message, "--", *paths])
    command = commit
    if existing:
        add = shlex.join(["git", "-C", str(REPO_ROOT), "add", "--", *existing])
        command = add + " && " + commit
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode:
        return 1, result.stdout + result.stderr
    return 0, _git("rev-parse", "--short", "HEAD").stdout.strip()


def _move_card(old_rel: str, new_rel: str) -> str | None:
    """Commit a clean directory move before touching its metadata or comments."""
    dirty = _git("status", "--porcelain", "--", old_rel)
    if dirty.returncode or dirty.stdout.strip():
        return "card has uncommitted changes; commit your checklist/receipts first; preserve other agents' work"
    moved = _git("mv", old_rel, new_rel)
    if moved.returncode:
        return f"git mv failed:\n{moved.stderr}"
    code, out = _commit_card([old_rel, new_rel], task_commit_message(REPO_ROOT / new_rel, f"move {Path(old_rel).name} to {Path(new_rel).parent.name}"))
    return out if code else None


def _git_user() -> str:
    name = _git("config", "user.name").stdout.strip()
    return name or "agent"


def _stamp() -> str:
    return dt.datetime.now(ZoneInfo("Asia/Hong_Kong")).strftime("%Y-%m-%d %H:%M %Z")


def _append_comment(card_dir: Path, who: str, text: str, *,
                    reply_to: str = "", resolves: str = "") -> str:
    """Append a Markdown block. Return its permanent comment id."""
    comment_id = "c-" + uuid.uuid4().hex[:12]
    entry = f"## {comment_id}\n\n- At: {_stamp()}\n- By: {who}\n"
    if reply_to:
        entry += f"- Reply-to: {reply_to}\n"
    if resolves:
        entry += f"- Resolves: {resolves}\n"
    entry += "\n" + text.rstrip() + "\n"
    path = card_dir / "comments.md"
    previous = path.read_text() if path.is_file() else ""
    content = previous or "# comments\n"
    if not content.endswith("\n"):
        content += "\n"
    if not content.endswith("\n\n"):
        content += "\n"
    with path.open("a") as out:
        # Add only the separator and new block. Preserve all previous bytes.
        out.write(content[len(previous):] + entry)
    return comment_id


def _set_assignee(card_md: Path, who: str) -> str | None:
    """Set the front-matter assignee line. Returns an error message, or None."""
    lines = card_md.read_text().splitlines()
    try:
        end = lines.index("---", 1)
    except ValueError:
        return "card.md has no front matter block"
    for i in range(1, end):
        if lines[i].startswith("assignee:"):
            lines[i] = f"assignee: {who}".rstrip()
            card_md.write_text("\n".join(lines) + "\n")
            return None
    return "front matter has no `assignee:` line"


def normalize_tag(token: str) -> str:
    """Normalize one input token to the canonical `@tag:<name>` form."""
    name = token.strip()
    if name[:1] == "@":
        name = name[1:]
    name = name.lstrip("#")
    if name[:4].lower() == "tag:":
        name = name[4:]
    name = name.lower()
    if not TAG_NAME_RE.fullmatch(name):
        raise ValueError(f"invalid tag `{token}` — use `@tag:` followed by lowercase letters, digits, hyphens, or underscores")
    return f"@tag:{name}"


def parse_tag_list(text: str) -> list[str]:
    """Normalize a comma-separated tag option into a sorted unique list."""
    tags = set()
    for token in text.split(","):
        if token.strip():
            tags.add(normalize_tag(token))
    return sorted(tags)


def card_tags(meta: dict[str, object]) -> list[str]:
    """The tags field as a plain list, empty when the field is absent or scalar."""
    tags = meta.get("tags", [])
    return [str(tag) for tag in tags] if isinstance(tags, list) else []


def _set_tags(card_md: Path, tags: list[str]) -> str | None:
    """Set or insert the front-matter tags line. Returns an error message, or None."""
    lines = card_md.read_text().splitlines()
    try:
        end = lines.index("---", 1)
    except ValueError:
        return "card.md has no front matter block"
    line = f"tags: [{', '.join(tags)}]" if tags else "tags: []"
    for i in range(1, end):
        if lines[i].startswith("tags:"):
            lines[i] = line
            break
    else:
        for i in range(1, end):
            if lines[i].startswith("assignee:"):
                lines.insert(i + 1, line)
                break
        else:
            return "front matter has no `assignee:` line"
    card_md.write_text("\n".join(lines) + "\n")
    return None


def _find_card(card_id: str) -> tuple[str, Path] | None:
    if not ID_RE.fullmatch(card_id):
        return None
    for column in COLUMNS:
        card_dir = BOARD / column / card_id
        if card_dir.is_dir():
            return column, card_dir
    return None


def _dirty_board_changes() -> int:
    status = _git("status", "--porcelain", "--", "tasks")
    return len([line for line in status.stdout.splitlines() if line.strip()])


def _card_age_minutes(card_id: str, column: str) -> int | None:
    log = _git("log", "-1", "--format=%ct", "--", f"tasks/{column}/{card_id}")
    text = log.stdout.strip()
    if not text:
        return None
    try:
        return max(0, int((dt.datetime.now() - dt.datetime.fromtimestamp(int(text))).total_seconds() // 60))
    except (ValueError, OverflowError):
        return None


# ------------------------------------------------------------------ validation

def parse_front_matter(text: str, where: str, problems: list[Problem]) -> dict[str, object]:
    """Minimal YAML subset: `key: value`, empty values, inline `[a, b]` lists."""
    if not text.startswith("---"):
        problems.append(Problem("ERROR", where, "missing front matter block"))
        return {}
    lines = text.splitlines()
    if len(lines) < 2 or lines[1:].count("---") == 0:
        problems.append(Problem("ERROR", where, "unterminated front matter block"))
        return {}
    end = lines.index("---", 1)
    meta: dict[str, object] = {}
    for lineno, raw in enumerate(lines[1:end], start=2):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            problems.append(Problem("ERROR", where, f"line {lineno}: not `key: value`"))
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if key in meta:
            problems.append(Problem("ERROR", where, f"line {lineno}: duplicate field `{key}`"))
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            items = [item.strip().strip("'\"") for item in inner.split(",")] if inner else []
            meta[key] = [item for item in items if item]
        else:
            meta[key] = value.strip("'\"")
    return meta


def read_card(card_dir: Path, column: str, problems: list[Problem]) -> dict[str, object]:
    card_md = card_dir / "card.md"
    where = f"{column}/{card_dir.name}"
    if not card_md.is_file():
        problems.append(Problem("ERROR", where, "missing card.md"))
        return {}
    meta = parse_front_matter(card_md.read_text(), where + "/card.md", problems)
    if not (card_dir / "comments.md").is_file():
        problems.append(Problem("WARN", where, "missing comments.md"))
    return meta


def markdown_lines(text: str):
    """Yield source lines outside fenced code blocks, with their line numbers."""
    fence = ""
    for lineno, line in enumerate(text.splitlines(), 1):
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker[1]
            if not fence:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = ""
            continue
        if not fence:
            yield lineno, line


def checklist_errors(text: str) -> list[str]:
    items = [match for _, line in markdown_lines(text) if (match := CHECK_RE.match(line))]
    if not items:
        return ["acceptance checklist is required"]
    errors = []
    for item in items:
        if item[1] == " ":
            errors.append(f"unchecked criterion: {item[2]}")
        elif not LINK_RE.search(item[2]):
            errors.append(f"criterion needs a Markdown evidence link: {item[2]}")
    return errors


def check_checklist(card_dir: Path, column: str, problems: list[Problem]) -> None:
    if column not in ("review", "done"):
        return
    for error in checklist_errors((card_dir / "card.md").read_text()):
        problems.append(Problem("ERROR", f"{column}/{card_dir.name}", error))


def references(cards: list[dict[str, object]]) -> list[dict[str, str | int]]:
    """Read references and their source locations. Store no backlink files."""
    result = []
    for card in cards:
        card_id, column, meta = card["id"], card["column"], card["meta"]
        for filename in ("card.md", "comments.md"):
            path = BOARD / str(column) / str(card_id) / filename
            if not path.is_file():
                continue
            source = f"@task:{card_id}"
            for lineno, line in markdown_lines(path.read_text()):
                if filename == "comments.md" and (heading := COMMENT_RE.fullmatch(line)):
                    source = f"@task:{card_id}#{heading[1]}"
                kind = "mention"
                if filename == "comments.md":
                    if line.startswith("- Reply-to: "):
                        kind = "reply"
                    elif line.startswith("- Resolves: "):
                        kind = "resolves"
                for match in REF_RE.finditer(line):
                    result.append({"source": source, "target": "@" + match[0].lstrip("@"), "kind": kind,
                                   "path": str(path.relative_to(REPO_ROOT)), "line": lineno,
                                   "text": line})
        card_path = BOARD / str(column) / str(card_id) / "card.md"
        text_lines = card_path.read_text().splitlines() if card_path.is_file() else []
        for relation, many in RELATIONS.items():
            value = meta.get(relation, [] if many else "")
            targets = value if isinstance(value, list) else [value] if isinstance(value, str) and value else []
            lineno = next((i for i, line in enumerate(text_lines, 1) if line.startswith(relation + ":")), 1)
            for target in targets:
                result.append({"source": f"@task:{card_id}", "target": f"@task:{target}",
                               "kind": relation, "path": str(card_path.relative_to(REPO_ROOT)),
                               "line": lineno, "text": text_lines[lineno - 1]})
    return result


def comment_ids(card: dict[str, object]) -> list[str]:
    path = BOARD / str(card["column"]) / str(card["id"]) / "comments.md"
    if not path.is_file():
        return []
    return [match[1] for _, line in markdown_lines(path.read_text())
            if (match := COMMENT_RE.fullmatch(line))]


def reference_error(ref: str, cards: list[dict[str, object]], *, comment: bool = False) -> str | None:
    match = REF_RE.fullmatch(ref)
    if not match or not ID_RE.fullmatch(match[1]):
        return f"invalid task reference `{ref}`"
    target = next((card for card in cards if card["id"] == match[1]), None)
    if target is None:
        return f"task `{match[1]}` not found on the board"
    if comment and not match[2]:
        return "a comment reference is required (@task:<id>#c-<id>)"
    if match[2] and match[2] not in comment_ids(target):
        return f"comment `{match[2]}` not found in task `{match[1]}`"
    return None


def check_cycles(cards: list[dict[str, object]], relation: str, problems: list[Problem]) -> None:
    graph = {}
    for card in cards:
        value = card["meta"].get(relation, [])
        graph[card["id"]] = value if isinstance(value, list) else [value] if value else []
    visited, active = set(), []

    def visit(node):
        if node in active:
            cycle = active[active.index(node):] + [node]
            problems.append(Problem("ERROR", "tasks/", f"{relation} cycle: " + " -> ".join(cycle)))
            return
        if node in visited or node not in graph:
            return
        visited.add(node)
        active.append(node)
        for target in graph[node]:
            visit(target)
        active.pop()

    for node in graph:
        visit(node)


def validate_board() -> list[Problem]:
    problems: list[Problem] = []
    seen: dict[str, str] = {}
    if not BOARD.is_dir():
        problems.append(Problem("ERROR", "tasks/", "board directory not found"))
        return problems
    columns_found = [p.name for p in BOARD.iterdir() if p.is_dir()]
    for column in COLUMNS:
        if column not in columns_found and column != "cancelled":
            problems.append(Problem("ERROR", "tasks/", f"missing column directory `{column}/`"))
    for column in COLUMNS:
        col_dir = BOARD / column
        if not col_dir.is_dir():
            continue
        for child in sorted(col_dir.iterdir()):
            if child.name in SKIP_NAMES:
                continue
            if not child.is_dir():
                problems.append(Problem("ERROR", f"{column}/", f"stray file `{child.name}` (cards are directories)"))
                continue
            card_id = child.name
            if not ID_RE.match(card_id) or not _valid_date(card_id[:10]):
                problems.append(Problem("ERROR", f"{column}/{card_id}", "id must be YYYY-MM-DD-<short-slug>"))
            if card_id in seen:
                problems.append(Problem("ERROR", f"{column}/{card_id}", f"duplicate id (also in {seen[card_id]}/)"))
            seen[card_id] = column
            meta = read_card(child, column, problems)
            for field in ("title", "area", "priority", "assignee"):
                if field not in meta or not isinstance(meta[field], str):
                    problems.append(Problem("ERROR", f"{column}/{card_id}", f"`{field}:` must be a scalar field"))
            title = str(meta.get("title", "")).strip()
            if not title:
                problems.append(Problem("ERROR", f"{column}/{card_id}", "front matter `title:` required"))
            if meta.get("priority") not in PRIORITIES:
                problems.append(Problem("ERROR", f"{column}/{card_id}", "`priority:` must be one of " + ", ".join(PRIORITIES)))
            if not str(meta.get("area", "")).strip():
                problems.append(Problem("ERROR", f"{column}/{card_id}", "front matter `area:` required"))
            due = str(meta.get("due", "")).strip()
            if due and not _valid_date(due):
                problems.append(Problem("ERROR", f"{column}/{card_id}", f"`due:` not a date: {due}"))
            assignee = str(meta.get("assignee", "")).strip()
            if column == "active" and not assignee:
                problems.append(Problem("ERROR", f"{column}/{card_id}", "active card needs `assignee:`"))
            if column in ("ready", "inbox") and assignee:
                problems.append(Problem("WARN", f"{column}/{card_id}", f"unclaimed card has assignee `{assignee}`"))
            for relation, many in RELATIONS.items():
                value = meta.get(relation, [] if many else "")
                if not isinstance(value, list if many else str):
                    expected_type = "a list" if many else "one card id"
                    problems.append(Problem("ERROR", f"{column}/{card_id}", f"`{relation}:` must be {expected_type}"))
            tags = meta.get("tags", [])
            if not isinstance(tags, list):
                problems.append(Problem("ERROR", f"{column}/{card_id}", "`tags:` must be a list"))
                tags = []
            for tag in tags:
                if not TAG_RE.fullmatch(str(tag)):
                    problems.append(Problem("ERROR", f"{column}/{card_id}",
                                            f"`tags:` holds an invalid tag `{tag}` — use `@tag:` followed by lowercase letters, digits, hyphens, or underscores"))
            if len(tags) != len(set(tags)):
                problems.append(Problem("ERROR", f"{column}/{card_id}", "`tags:` holds a duplicate tag"))
            expected = meta.get("expected-paths", [])
            if not isinstance(expected, list):
                problems.append(Problem("ERROR", f"{column}/{card_id}", "`expected-paths:` must be a list"))
                expected = []
            for path in expected:
                if not (REPO_ROOT / str(path).rstrip("/")).exists():
                    problems.append(Problem("WARN", f"{column}/{card_id}", f"expected-path `{path}` does not exist"))
            if (child / "card.md").is_file():
                check_checklist(child, column, problems)
    cards = collect_cards()
    for card in cards:
        ids = comment_ids(card)
        if len(ids) != len(set(ids)):
            problems.append(Problem("ERROR", str(card["id"]), "duplicate comment ids"))
    for ref in references(cards):
        error = reference_error(str(ref["target"]), cards, comment=ref["kind"] in ("reply", "resolves"))
        where = f"{ref['path']}:{ref['line']}"
        if error:
            problems.append(Problem("ERROR", where, error))
        elif ref["kind"] in RELATIONS and ref["source"] == ref["target"]:
            problems.append(Problem("ERROR", where, "a task cannot have a relationship to itself"))
        elif ref["kind"] == "blocked-by":
            target_id = str(ref["target"])[6:]
            if seen[target_id] != "done":
                problems.append(Problem("BLOCKED", where, f"blocked by `{target_id}`, still in {seen[target_id]}/"))
    for relation in ("blocked-by", "parent", "duplicate-of"):
        check_cycles(cards, relation, problems)
    return problems


def _valid_date(text: str) -> bool:
    try:
        dt.date.fromisoformat(text)
        return True
    except ValueError:
        return False


def collect_cards() -> list[dict[str, object]]:
    cards: list[dict[str, object]] = []
    for column in COLUMNS:
        col_dir = BOARD / column
        if not col_dir.is_dir():
            continue
        for child in sorted(col_dir.iterdir()):
            if child.name in SKIP_NAMES or not child.is_dir():
                continue
            card_md = child / "card.md"
            problems: list[Problem] = []
            meta = parse_front_matter(card_md.read_text(), child.name, problems) if card_md.is_file() else {}
            cards.append({"id": child.name, "column": column, "meta": meta})
    return cards


def fmt_card(card: dict[str, object], show_age: bool = False) -> str:
    meta = card["meta"]
    column, card_id = str(card["column"]), str(card["id"])
    bits = [card_id, str(meta.get("priority", "?")), str(meta.get("title", "(untitled)"))]
    extra: list[str] = []
    assignee = str(meta.get("assignee", "")).strip()
    if assignee:
        extra.append(f"@{assignee}")
    due = str(meta.get("due", "")).strip()
    if due:
        extra.append(f"due {due}")
    blocked = meta.get("blocked-by", [])
    if isinstance(blocked, list) and blocked:
        extra.append("blocked-by " + ", ".join(str(ref) for ref in blocked))
    tags = card_tags(meta)
    if tags:
        extra.append(" ".join(tags))
    if show_age and column == "active":
        age = _card_age_minutes(card_id, column)
        extra.append("uncommitted" if age is None else f"updated {age}m ago")
    return "  ".join(bits) + ("  [" + " ".join(extra) + "]" if extra else "")


def _print_board_notice() -> None:
    dirty = _dirty_board_changes()
    if dirty:
        print(f"NOTE: {dirty} uncommitted board change(s) in the worktree — run `tasks.py validate` and commit them", file=sys.stderr)


# -------------------------------------------------------------------- commands

def cmd_validate(args: argparse.Namespace) -> int:
    problems = validate_board()
    errors = [p for p in problems if p.level == "ERROR"]
    warnings = [p for p in problems if p.level == "WARN"]
    blocked = [p for p in problems if p.level == "BLOCKED"]
    for level in ("ERROR", "WARN"):
        for problem in [p for p in problems if p.level == level]:
            print(problem)
    print(f"blocked: {len({p.where.split(':')[0] for p in blocked})} task(s), "
          f"{len(blocked)} unsatisfied dependency reference(s)")
    counts = {column: 0 for column in COLUMNS}
    for card_id, column in seen_ids().items():
        counts[column] += 1
    print("board: " + "  ".join(f"{column}={counts[column]}" for column in COLUMNS))
    print(f"validate: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


def seen_ids() -> dict[str, str]:
    out: dict[str, str] = {}
    for column in COLUMNS:
        col_dir = BOARD / column
        if not col_dir.is_dir():
            continue
        for child in sorted(col_dir.iterdir()):
            if child.name not in SKIP_NAMES and child.is_dir():
                out[child.name] = column
    return out


def cmd_list(_args: argparse.Namespace) -> int:
    _print_board_notice()
    for column in COLUMNS:
        cards = [c for c in collect_cards() if c["column"] == column]
        print(f"## {column} ({len(cards)})")
        for card in sorted(cards, key=lambda c: (str(c["meta"].get("priority", "P4")), str(c["id"]))):
            print("  " + fmt_card(card, show_age=True))
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    found = _find_card(args.id)
    if not found:
        return fail(f"no task `{args.id}` on the board")
    _, card_dir = found
    print(f"Card: {(card_dir / 'card.md').relative_to(REPO_ROOT)}")
    print(f"Comments: {(card_dir / 'comments.md').relative_to(REPO_ROOT)}\n")
    text = (card_dir / "card.md").read_text()
    print(text, end="" if text.endswith("\n") else "\n")
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    _print_board_notice()
    ids = seen_ids()
    done_ids = {card_id for card_id, column in ids.items() if column == "done"}
    ready = []
    for card in collect_cards():
        if card["column"] != "ready":
            continue
        blocked = card["meta"].get("blocked-by", [])
        if isinstance(blocked, list) and [ref for ref in blocked if ref not in done_ids]:
            continue
        ready.append(card)
    priority_rank = {p: i for i, p in enumerate(PRIORITIES)}

    def sort_key(card: dict[str, object]):
        due = str(card["meta"].get("due", "")).strip()
        return (priority_rank.get(str(card["meta"].get("priority")), 9), due or "9999-12-31", str(card["id"]))

    ready.sort(key=sort_key)
    for card in ready[: args.limit]:
        print(fmt_card(card))
    print(f"{len(ready)} claimable card(s), showing {min(args.limit, len(ready))}", file=sys.stderr)
    return 0


TRANSITIONS = {
    "triage": (("inbox",), "ready"),
    "claim": (("ready",), "active"),
    "done": (("active",), "review"),
    "accept": (("review",), "done"),
    "request-changes": (("review",), "active"),
    "drop": (("active",), "ready"),
    "reopen": (("done", "cancelled"), "ready"),
    "cancel": (("inbox", "ready", "active", "review"), "cancelled"),
}


def cmd_tags(args: argparse.Namespace) -> int:
    _print_board_notice()
    cards = collect_cards()
    if not args.name:
        counts: dict[str, int] = {}
        for card in cards:
            for tag in card_tags(card["meta"]):
                counts[tag] = counts.get(tag, 0) + 1
        for tag, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
            print(f"{tag}  {count}")
        if not counts:
            print("(no tags on the board)")
        return 0
    try:
        tag = normalize_tag(args.name)
    except ValueError as exc:
        return fail(str(exc))
    found = False
    for column in COLUMNS:
        matches = [card for card in cards if card["column"] == column and tag in card_tags(card["meta"])]
        if not matches:
            continue
        found = True
        print(f"## {column} ({len(matches)})")
        for card in sorted(matches, key=lambda c: (str(c["meta"].get("priority", "P4")), str(c["id"]))):
            print("  " + fmt_card(card))
    if not found:
        print(f"no task carries {tag}")
    return 0


def cmd_tag(args: argparse.Namespace) -> int:
    if error := _repo_preflight():
        return fail(error)
    found = _find_card(args.id)
    if not found:
        return fail(f"no task `{args.id}` on the board")
    column, card_dir = found
    if _git("status", "--porcelain", "--", str(card_dir.relative_to(REPO_ROOT))).stdout.strip():
        return fail("card has uncommitted changes; preserve them and commit your own work first")
    if not _git("ls-files", "--", str(card_dir.relative_to(REPO_ROOT))).stdout.strip():
        return fail("commit the task before changing its tags")
    try:
        names = sorted({normalize_tag(name) for name in args.names})
    except ValueError as exc:
        return fail(str(exc))
    card_md = card_dir / "card.md"
    current = card_tags(parse_front_matter(card_md.read_text(), args.id, []))
    if args.action == "add":
        if held := [name for name in names if name in current]:
            return fail("task already carries " + ", ".join(held))
        updated = sorted(set(current) | set(names))
        summary = "tags: add " + ", ".join(names)
    else:
        if absent := [name for name in names if name not in current]:
            return fail("task does not carry " + ", ".join(absent))
        updated = [name for name in current if name not in set(names)]
        summary = "tags: remove " + ", ".join(names)
    if error := _set_tags(card_md, updated):
        return fail(error)
    _append_comment(card_dir, args.who or _git_user(), summary + ".")
    return finish_change([f"tasks/{column}/{args.id}/card.md", f"tasks/{column}/{args.id}/comments.md"],
                         task_commit_message(card_dir, f"{args.command} {args.action} {args.id}", summary))


def fail(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 1


def read_message(args: argparse.Namespace) -> str:
    if args.file:
        return sys.stdin.read() if args.file == "-" else Path(args.file).read_text()
    return args.message or ""


def task_commit_message(card_dir: Path, action: str, text: str = "") -> str:
    """Prefix the task title with its action and retain supplied Markdown details."""
    title = read_card(card_dir, card_dir.parent.name, [])["title"]
    verb = (action.split() or ["update"])[0].lower()
    message = f"board({verb}): {title}"
    if text:
        message += "\n\n" + text.rstrip()
    return message


def finish_change(paths: list[str], message: str) -> int:
    errors = [p for p in validate_board() if p.level == "ERROR"]
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return fail("board invalid; changes left uncommitted. Fix them, then commit only these paths: " + ", ".join(paths))
    # Recheck the branch immediately before the commit.
    if error := _repo_preflight():
        return fail(error)
    code, output = _commit_card(paths, message)
    if code:
        return fail(output)
    print(f"{message.splitlines()[0]} (commit {output})")
    return 0


def cmd_create(args: argparse.Namespace) -> int:
    if error := _repo_preflight():
        return fail(error)
    if not ID_RE.fullmatch(args.id) or not _valid_date(args.id[:10]):
        return fail("id must be YYYY-MM-DD-<short-slug>")
    if _find_card(args.id):
        return fail(f"task `{args.id}` already exists")
    body = read_message(args)
    if not body.strip():
        return fail("provide the task description and acceptance checklist with --file or -m")
    if any(not value.strip() or "\n" in value or "\r" in value for value in (args.title, args.area)):
        return fail("title and area must each be one nonempty line")
    try:
        tags = parse_tag_list(args.tags or "")
    except ValueError as exc:
        return fail(str(exc))
    tag_field = f"tags: [{', '.join(tags)}]\n" if tags else ""
    card_dir = BOARD / "inbox" / args.id
    card_dir.mkdir(parents=True)
    (card_dir / "card.md").write_text(
        f"---\ntitle: {args.title}\narea: {args.area}\npriority: {args.priority}\n"
        f"assignee:\n{tag_field}blocked-by: []\n---\n\n{body.rstrip()}\n")
    comment_id = _append_comment(card_dir, args.who or _git_user(), "Created in inbox.")
    print(f"@task:{args.id}#{comment_id}")
    return finish_change([str(card_dir.relative_to(REPO_ROOT))], task_commit_message(card_dir, f"create {args.id}", body))


def cmd_comment(args: argparse.Namespace) -> int:
    if error := _repo_preflight():
        return fail(error)
    found = _find_card(args.id)
    if not found:
        return fail(f"no task `{args.id}` on the board")
    text = read_message(args)
    if not text.strip():
        return fail("comment must not be empty")
    reply_to = getattr(args, "reply_to", "") or ""
    resolves = getattr(args, "ref", "") or ""
    cards = collect_cards()
    for ref in (reply_to, resolves):
        if ref and (error := reference_error(ref, cards, comment=True)):
            return fail(error)
    reply_to = "@" + reply_to.lstrip("@") if reply_to else ""
    resolves = "@" + resolves.lstrip("@") if resolves else ""
    # Reject broken references before appending to the permanent thread.
    for _, line in markdown_lines(text):
        for match in REF_RE.finditer(line):
            if error := reference_error(match[0], cards):
                return fail(error)
        if COMMENT_RE.fullmatch(line):
            return fail("comment-id headings are reserved; use ### for headings inside comments")
    column, card_dir = found
    if _git("status", "--porcelain", "--", f"tasks/{column}/{args.id}").stdout.strip():
        return fail("card has uncommitted changes; preserve them and commit your own work first")
    comment_id = _append_comment(card_dir, args.who or _git_user(), text,
                                 reply_to=reply_to, resolves=resolves)
    print(f"@task:{args.id}#{comment_id}")
    return finish_change([f"tasks/{column}/{args.id}/comments.md"], task_commit_message(card_dir, f"{args.command} on {args.id}", text))


def cmd_move(args: argparse.Namespace) -> int:
    if error := _repo_preflight():
        return fail(error)
    found = _find_card(args.id)
    allowed, destination = TRANSITIONS[args.command]
    if not found or found[0] not in allowed:
        return fail(f"`{args.command}` requires a task in {' or '.join(allowed)}/")
    column, card_dir = found
    if not _git("ls-files", "--", str(card_dir.relative_to(REPO_ROOT))).stdout.strip():
        return fail("commit the task before changing its state")
    reason = read_message(args).strip()
    if args.command in ("cancel", "reopen", "request-changes") and not reason:
        return fail(f"`{args.command}` requires a reason (-m or --file)")
    if args.command in ("done", "accept"):
        errors = checklist_errors((card_dir / "card.md").read_text())
        if errors:
            return fail("\n".join(errors))
    if args.command == "claim":
        card = next(c for c in collect_cards() if c["id"] == args.id)
        ids = seen_ids()
        blockers = [ref for ref in card["meta"].get("blocked-by", []) if ids.get(ref) != "done"]
        if blockers and not reason:
            return fail("open blockers: " + ", ".join(blockers) + "; supply -m to explain the override")
    who = args.who or _git_user()
    if "\n" in who or "\r" in who:
        return fail("author must be one line")
    old_rel, new_rel = f"tasks/{column}/{args.id}", f"tasks/{destination}/{args.id}"
    (BOARD / destination).mkdir(exist_ok=True)
    if error := _move_card(old_rel, new_rel):
        return fail(error)
    card_dir = BOARD / destination / args.id
    if args.command == "claim" or destination == "ready":
        if error := _set_assignee(card_dir / "card.md", who if args.command == "claim" else ""):
            return fail(error)
    text = f"{args.command}: {column} -> {destination}."
    if reason:
        text += "\n\n" + reason
    _append_comment(card_dir, who, text)
    return finish_change([new_rel], task_commit_message(card_dir, f"{args.command} {args.id}", reason))


def cmd_refs(args: argparse.Namespace) -> int:
    ref = args.ref
    if ref.startswith("task:"):
        ref = "@" + ref
    elif not ref.startswith("@task:"):
        ref = "@task:" + ref
    cards = collect_cards()
    if error := reference_error(ref, cards):
        return fail(error)
    card = next(c for c in cards if c["id"] == ref[6:].split("#")[0])
    filename = "comments.md" if "#" in ref else "card.md"
    path = BOARD / str(card["column"]) / str(card["id"]) / filename
    lineno = 1
    if "#" in ref:
        lineno = next(i for i, line in markdown_lines(path.read_text()) if line == "## " + ref.split("#")[1])
    print(f"{ref} -> {path.relative_to(REPO_ROOT)}:{lineno}")
    refs = references(cards)
    def matches(candidate):
        return candidate == ref or ("#" not in ref and str(candidate).startswith(ref + "#"))
    for label, key in (("Outgoing", "source"), ("Incoming", "target")):
        print(f"{label}:")
        found = [edge for edge in refs if matches(edge[key])]
        for edge in found:
            print(f"  {edge['kind']}: {edge['source']} -> {edge['target']}")
            print(f"    {edge['path']}:{edge['line']}: {edge['text']}")
        if not found:
            print("  (none)")
    resolved = sorted({str(edge["target"]) for edge in refs if edge["kind"] == "resolves" and matches(edge["target"])})
    for target in resolved:
        print(f"Resolved: {target}")
    return 0


def add_message_args(parser, *, required=False, author_required=False):
    messages = parser.add_mutually_exclusive_group(required=required)
    messages.add_argument("-m", "--message", help="one-line summary, blank line, optional Markdown details; existing text also works")
    messages.add_argument("--file", help="read the full message from a file; - reads stdin")
    parser.add_argument("--as", dest="who", metavar="NAME", required=author_required)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tasks", description="Markdown task board (tasks/AGENTS.md)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate", help="check task format, evidence, references, and cycles")
    sub.add_parser("list", help="print the board")
    show = sub.add_parser("show", help="print a task card and its current comments path")
    show.add_argument("id", help="stable task id")
    next_parser = sub.add_parser("next", help="claimable tasks, priority then due date")
    next_parser.add_argument("--limit", type=int, default=5)
    tags = sub.add_parser("tags", help="list all tags, or the tasks carrying one")
    tags.add_argument("name", nargs="?")
    tag = sub.add_parser("tag", help="add or remove @tag:<name> labels on a task; record and commit")
    tag.add_argument("id")
    tag.add_argument("action", choices=("add", "remove"))
    tag.add_argument("names", nargs="+", metavar="NAME")
    tag.add_argument("--as", dest="who", metavar="NAME")
    refs = sub.add_parser("refs", help="resolve a reference and list outgoing links and backlinks")
    refs.add_argument("ref", help="task id or @task:<id>[#c-<comment-id>]")
    create = sub.add_parser("create", help="create a task in inbox and commit it")
    create.add_argument("id")
    create.add_argument("--title", required=True)
    create.add_argument("--area", required=True)
    create.add_argument("--priority", choices=PRIORITIES, default="P3")
    create.add_argument("--tags", help="comma-separated tags; the @tag: prefix is optional")
    add_message_args(create, required=True)
    comment = sub.add_parser("comment", help="append Markdown and commit it")
    comment.add_argument("id")
    comment.add_argument("--reply-to", help="@task:<id>#c-<comment-id>")
    add_message_args(comment, required=True)
    resolve = sub.add_parser("resolve", help="append a resolution linked to a comment")
    resolve.add_argument("id", help="task where the resolution is recorded")
    resolve.add_argument("ref", help="comment to resolve: @task:<id>#c-<comment-id>")
    add_message_args(resolve, required=True)
    for command, (allowed, destination) in TRANSITIONS.items():
        move = sub.add_parser(command, help=f"{'/'.join(allowed)} -> {destination}; record and commit")
        move.add_argument("id")
        add_message_args(move, author_required=command == "claim")
    args = parser.parse_args(argv)
    who = getattr(args, "who", None)
    if who is not None and (not who.strip() or "\n" in who or "\r" in who):
        return fail("author must be one nonempty line")
    commands = {"validate": cmd_validate, "list": cmd_list, "show": cmd_show, "next": cmd_next,
                "tags": cmd_tags, "tag": cmd_tag, "refs": cmd_refs, "create": cmd_create, "comment": cmd_comment, "resolve": cmd_comment}
    try:
        return commands.get(args.command, cmd_move)(args)
    except (OSError, UnicodeError) as exc:
        return fail(str(exc))


if __name__ == "__main__":
    sys.exit(main())
