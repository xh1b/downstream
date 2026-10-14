#!/usr/bin/env python3
"""tasks — the agent board CLI (validate / list / next / claim / comment / done / drop).

Board layout and process: tasks/AGENTS.md. Columns are subdirectories of tasks/;
one directory per card, named YYYY-MM-DD-<short-slug>; card.md + comments.md inside.

The mutating verbs (claim / comment / done / drop) edit the card AND commit it in
the same command. Directory moves are committed before metadata edits, as required
by this repository. Commits use
strict pathspecs (the card directory only), so they are safe next to other agents'
staged work. Preflight refuses to run mid-merge, mid-rebase, off master, or outside
a work tree.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import shlex
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

BOARD = Path(__file__).resolve().parent.parent / "tasks"
REPO_ROOT = BOARD.parent
COLUMNS = ("inbox", "ready", "active", "review", "done")
PRIORITIES = ("P1", "P2", "P3", "P4")
ID_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-[a-z0-9]+(-[a-z0-9]+)*$")
SKIP_NAMES = {".gitkeep"}


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
    commit = shlex.join(["git", "-C", str(REPO_ROOT), "commit", "-m", message, "--", *paths])
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
    code, out = _commit_card([old_rel, new_rel], f"chore: move task {Path(old_rel).name} to {Path(new_rel).parent.name}")
    return out if code else None


def _git_user() -> str:
    name = _git("config", "user.name").stdout.strip()
    return name or "agent"


def _stamp() -> str:
    return dt.datetime.now(ZoneInfo("Asia/Hong_Kong")).strftime("%Y-%m-%d %H:%M")


def _append_comment(card_dir: Path, who: str, text: str) -> str | None:
    """Append one timestamped entry. Returns an error message, or None on success."""
    entry = f"- {_stamp()} {who}: {text}"
    if len(entry) > 160:
        return f"comment is {len(entry)} chars (max 160) — shorten it"
    path = card_dir / "comments.md"
    content = path.read_text() if path.is_file() else "# comments\n"
    if not content.endswith("\n"):
        content += "\n"
    if content.strip() == "# comments":
        content += "\n"
    path.write_text(content + entry + "\n")
    return None


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


def _find_card(card_id: str) -> tuple[str, Path] | None:
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


def lint_card_text(card_dir: Path, column: str, problems: list[Problem]) -> None:
    for filename in ("card.md", "comments.md"):
        path = card_dir / filename
        if not path.is_file():
            continue
        for lineno, line in enumerate(path.read_text().splitlines(), start=1):
            if len(line) > 160:
                problems.append(
                    Problem("ERROR", f"{column}/{card_dir.name}/{filename}", f"line {lineno}: {len(line)} chars (max 160)")
                )


def check_checklist(card_dir: Path, column: str, problems: list[Problem]) -> None:
    if column not in ("review", "done"):
        return
    text = (card_dir / "card.md").read_text()
    unchecked = [line.strip() for line in text.splitlines() if line.strip().startswith("- [ ]")]
    if not unchecked:
        return
    level = "ERROR" if column == "done" else "WARN"
    problems.append(Problem(level, f"{column}/{card_dir.name}", f"{len(unchecked)} unchecked checklist item(s)"))


def validate_board() -> list[Problem]:
    problems: list[Problem] = []
    seen: dict[str, str] = {}
    all_ids = seen_ids()
    if not BOARD.is_dir():
        problems.append(Problem("ERROR", "tasks/", "board directory not found"))
        return problems
    columns_found = [p.name for p in BOARD.iterdir() if p.is_dir()]
    for column in COLUMNS:
        if column not in columns_found:
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
            lint_card_text(child, column, problems)
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
            blocked_by = meta.get("blocked-by", [])
            if not isinstance(blocked_by, list):
                problems.append(Problem("ERROR", f"{column}/{card_id}", "`blocked-by:` must be a list"))
                blocked_by = []
            for ref in blocked_by:
                if ref not in all_ids:
                    problems.append(Problem("ERROR", f"{column}/{card_id}", f"blocked-by id `{ref}` not found on the board"))
                elif all_ids[ref] != "done":
                    problems.append(Problem("WARN", f"{column}/{card_id}", f"blocked by `{ref}`, still in {all_ids[ref]}/"))
            expected = meta.get("expected-paths", [])
            if not isinstance(expected, list):
                problems.append(Problem("ERROR", f"{column}/{card_id}", "`expected-paths:` must be a list"))
                expected = []
            for path in expected:
                if not (REPO_ROOT / str(path).rstrip("/")).exists():
                    problems.append(Problem("WARN", f"{column}/{card_id}", f"expected-path `{path}` does not exist"))
            check_checklist(child, column, problems)
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
    if show_age and column == "active":
        age = _card_age_minutes(card_id, column)
        extra.append("just moved (uncommitted)" if age is None else f"claimed {age}m ago")
    return "  ".join(bits) + ("  [" + " ".join(extra) + "]" if extra else "")


def _print_board_notice() -> None:
    dirty = _dirty_board_changes()
    if dirty:
        print(f"NOTE: {dirty} uncommitted board change(s) in the worktree — run `tasks.py validate` and commit them", file=sys.stderr)


# -------------------------------------------------------------------- commands

def cmd_validate(_args: argparse.Namespace) -> int:
    problems = validate_board()
    errors = [p for p in problems if p.level == "ERROR"]
    for level in ("ERROR", "WARN"):
        for problem in [p for p in problems if p.level == level]:
            print(problem)
    counts = {column: 0 for column in COLUMNS}
    for card_id, column in seen_ids().items():
        counts[column] += 1
    print("board: " + "  ".join(f"{column}={counts[column]}" for column in COLUMNS))
    print(f"validate: {len(errors)} error(s), {len(problems) - len(errors)} warning(s)")
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


def cmd_claim(args: argparse.Namespace) -> int:
    error = _repo_preflight()
    if error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    src = BOARD / "ready" / args.id
    if not src.is_dir():
        print(f"error: no card `{args.id}` in ready/", file=sys.stderr)
        return 1
    tracked = _git("ls-files", "--", f"tasks/ready/{args.id}").stdout.strip()
    if not tracked:
        print(f"error: card `{args.id}` is untracked — commit it first (cards enter the board via a commit)", file=sys.stderr)
        return 1
    old_rel, new_rel = f"tasks/ready/{args.id}", f"tasks/active/{args.id}"
    problem = _move_card(old_rel, new_rel)
    if problem:
        print(f"error: {problem}", file=sys.stderr)
        return 1
    problem = _set_assignee(BOARD / "active" / args.id / "card.md", args.who)
    if not problem:
        problem = _append_comment(BOARD / "active" / args.id, args.who, "claimed (ready -> active)")
    if not problem:
        problems = [p for p in validate_board() if p.level == "ERROR"]
        if problems:
            for p in problems:
                print(p)
            problem = "board invalid — changes left UNCOMMITTED; fix, then commit with a pathspec of the card directory"
    if problem:
        print(f"error: {problem}", file=sys.stderr)
        return 1
    code, out = _commit_card([new_rel], f"chore: task claim {args.id} ({args.who})")
    if code:
        print(f"error: {out}", file=sys.stderr)
        return 1
    print(f"claimed {args.id} -> active/ as {args.who} (commit {out})")
    return 0


def cmd_comment(args: argparse.Namespace) -> int:
    error = _repo_preflight()
    if error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    found = _find_card(args.id)
    if not found:
        print(f"error: no card `{args.id}` on the board", file=sys.stderr)
        return 1
    column, card_dir = found
    if _git("status", "--porcelain", "--", f"tasks/{column}/{args.id}").stdout.strip():
        print("error: card has uncommitted changes; preserve them and commit your own work first", file=sys.stderr)
        return 1
    who = args.who or _git_user()
    problem = _append_comment(card_dir, who, args.message)
    if not problem:
        problems = [p for p in validate_board() if p.level == "ERROR"]
        if problems:
            for p in problems:
                print(p)
            problem = "board invalid — changes left UNCOMMITTED; fix, then commit with a pathspec of the card directory"
    if problem:
        print(f"error: {problem}", file=sys.stderr)
        return 1
    code, out = _commit_card([f"tasks/{column}/{args.id}"], f"chore: task comment on {args.id}")
    if code:
        print(f"error: {out}", file=sys.stderr)
        return 1
    print(f"commented on {args.id} ({column}/) (commit {out})")
    return 0


def cmd_done(args: argparse.Namespace) -> int:
    error = _repo_preflight()
    if error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    card_dir = BOARD / "active" / args.id
    if not card_dir.is_dir():
        print(f"error: no active card `{args.id}`", file=sys.stderr)
        return 1
    unchecked = [line.strip() for line in (card_dir / "card.md").read_text().splitlines() if line.strip().startswith("- [ ]")]
    if unchecked:
        print(f"error: {len(unchecked)} unchecked checklist item(s) — tick them (with receipts) before `done`:", file=sys.stderr)
        for line in unchecked:
            print(f"  {line}", file=sys.stderr)
        return 1
    who = args.who or _git_user()
    old_rel, new_rel = f"tasks/active/{args.id}", f"tasks/review/{args.id}"
    problem = _move_card(old_rel, new_rel)
    if problem:
        print(f"error: {problem}", file=sys.stderr)
        return 1
    problem = _append_comment(BOARD / "review" / args.id, who, "checklist complete (active -> review); awaiting owner review")
    if not problem:
        problems = [p for p in validate_board() if p.level == "ERROR"]
        if problems:
            for p in problems:
                print(p)
            problem = "board invalid — changes left UNCOMMITTED; fix, then commit with a pathspec of the card directory"
    if problem:
        print(f"error: {problem}", file=sys.stderr)
        return 1
    code, out = _commit_card([new_rel], f"chore: task {args.id} -> review")
    if code:
        print(f"error: {out}", file=sys.stderr)
        return 1
    print(f"{args.id} -> review/ (commit {out})")
    return 0


def cmd_drop(args: argparse.Namespace) -> int:
    error = _repo_preflight()
    if error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    card_dir = BOARD / "active" / args.id
    if not card_dir.is_dir():
        print(f"error: no active card `{args.id}`", file=sys.stderr)
        return 1
    who = args.who or _git_user()
    old_rel, new_rel = f"tasks/active/{args.id}", f"tasks/ready/{args.id}"
    problem = _move_card(old_rel, new_rel)
    if problem:
        print(f"error: {problem}", file=sys.stderr)
        return 1
    problem = _set_assignee(BOARD / "ready" / args.id / "card.md", "")
    if not problem:
        problem = _append_comment(BOARD / "ready" / args.id, who, f"claim released by {who} (active -> ready)")
    if not problem:
        problems = [p for p in validate_board() if p.level == "ERROR"]
        if problems:
            for p in problems:
                print(p)
            problem = "board invalid — changes left UNCOMMITTED; fix, then commit with a pathspec of the card directory"
    if problem:
        print(f"error: {problem}", file=sys.stderr)
        return 1
    code, out = _commit_card([new_rel], f"chore: task drop {args.id}")
    if code:
        print(f"error: {out}", file=sys.stderr)
        return 1
    print(f"dropped {args.id} -> ready/ (commit {out})")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tasks", description="The agent board (see tasks/AGENTS.md)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate", help="check board format and references")
    sub.add_parser("list", help="print the board view (with claim ages)")
    next_parser = sub.add_parser("next", help="claimable cards, priority then due date")
    next_parser.add_argument("--limit", type=int, default=5)
    claim = sub.add_parser("claim", help="claim a ready card (moves, assigns, comments, commits)")
    claim.add_argument("id")
    claim.add_argument("--as", dest="who", required=True, metavar="NAME")
    comment = sub.add_parser("comment", help="append a timestamped comment and commit it")
    comment.add_argument("id")
    comment.add_argument("-m", "--message", required=True)
    comment.add_argument("--as", dest="who", default=None, metavar="NAME")
    done_p = sub.add_parser("done", help="move a finished active card to review (requires checked checklist)")
    done_p.add_argument("id")
    done_p.add_argument("--as", dest="who", default=None, metavar="NAME")
    drop = sub.add_parser("drop", help="release a claim: active -> ready, assignee cleared")
    drop.add_argument("id")
    drop.add_argument("--as", dest="who", default=None, metavar="NAME")
    args = parser.parse_args(argv)
    commands = {
        "validate": cmd_validate,
        "list": cmd_list,
        "next": cmd_next,
        "claim": cmd_claim,
        "comment": cmd_comment,
        "done": cmd_done,
        "drop": cmd_drop,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
