#!/usr/bin/env python3
# @ref:script-doccheck
# Method: @link:development-tooling; @link:docs-index; @link:integration-examples.
# Verification: @link:test-documentation-checks.
# @tag:tooling
"""Check maintained Markdown navigation, naming, executable examples and freshness."""
from __future__ import annotations

import argparse
import doctest
from html import unescape
import io
import os
import posixpath
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN = {".md", ".markdown", ".mdx"}
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def blocks(text):
    """Yield fenced (info, source, first source line) without executing anything."""
    marker = None
    body = []
    for number, line in enumerate(text.splitlines(keepends=True), 1):
        match = FENCE.match(line)
        if marker is None and match:
            marker, info, first = match[1], match[2].strip(), number + 1
            body = []
        elif marker and re.fullmatch(r" {0,3}" + re.escape(marker[0]) + "{" + str(len(marker)) + r",}\s*", line):
            yield info, "".join(body), first
            marker = None
        elif marker:
            body.append(line)


def prose(text):
    """Mask code/comments, retaining newline positions for error reporting."""
    lines = text.splitlines(keepends=True)
    marker = None
    for index, line in enumerate(lines):
        match = FENCE.match(line)
        if marker is None and match:
            marker = match[1]
            lines[index] = "\n"
        elif marker:
            lines[index] = "\n"
            if re.fullmatch(r" {0,3}" + re.escape(marker[0]) + "{" + str(len(marker)) + r",}\s*", line):
                marker = None
    text = "".join(lines)
    text = re.sub(r"<!--.*?-->", lambda m: "\n" * m[0].count("\n"), text, flags=re.S)
    return text


def heading_ids(text):
    clean = prose(text)
    ids = set(re.findall(r'<[^>]+\b(?:id|name)=[\"\']([^\"\']+)[\"\']', clean))
    counts = {}
    headings = [(m.start(), m[1]) for m in re.finditer(r"^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$", clean, re.M)]
    headings += [(m.start(), m[1]) for m in re.finditer(r"^([^\n]+)\n {0,3}(?:={3,}|-{3,})\s*$", clean, re.M)]
    for _, heading in sorted(headings):
        heading = re.sub(r"!?\[([^]]*)\]\([^)]*\)", r"\1", heading)
        heading = re.sub(r"<[^>]*>", "", heading).replace("`", "")
        slug = re.sub(r"[^\w\- ]", "", unescape(heading).lower()).replace(" ", "-")
        suffix = counts.get(slug, 0)
        candidate = slug if suffix == 0 else f"{slug}-{suffix}"
        while candidate in ids:
            suffix += 1
            candidate = f"{slug}-{suffix}"
        counts[slug] = suffix + 1
        ids.add(candidate)
    return ids


def destinations(text):
    """Read inline/image, reference-definition and HTML destinations.

    This deliberately checks destinations rather than rendering Markdown. Code
    examples and external URLs are outside the local-path contract.
    """
    clean = re.sub(r"(`+)([^`]*?)\1", "", prose(text))
    for match in re.finditer(r"!?\[[^]\n]*\]\(\s*", clean):
        start = match.end()
        if clean[start:start + 1] == "<":
            end = clean.find(">", start + 1)
            if end >= 0:
                yield clean[start + 1:end], clean.count("\n", 0, start) + 1
            continue
        end, depth = start, 0
        while end < len(clean):
            char = clean[end]
            if char == "\\" and end + 1 < len(clean):
                end += 2
                continue
            if char == "(":
                depth += 1
            elif char == ")":
                if depth == 0:
                    break
                depth -= 1
            elif char.isspace() and depth == 0:
                break
            end += 1
        if end > start:
            yield clean[start:end], clean.count("\n", 0, start) + 1
    for match in re.finditer(r"^ {0,3}\[(?!\^)[^]\n]+\]:\s*(<[^>]+>|\S+)", clean, re.M):
        yield match[1].strip("<>"), clean.count("\n", 0, match.start()) + 1
    for match in re.finditer(r'\b(?:href|src)=[\"\']([^\"\']+)[\"\']', clean):
        yield match[1], clean.count("\n", 0, match.start()) + 1


def inventory(root):
    output = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
                            cwd=root, check=True, capture_output=True, text=True)
    files = {name for name in output.stdout.split("\0") if name and (root / name).is_file()}
    directories = {parent.as_posix() for name in files for parent in Path(name).parents}
    return files, files | directories


def documents(files):
    """Maintained entry points and supporting docs; task history is immutable."""
    return sorted(name for name in files if Path(name).suffix.lower() in MARKDOWN and (
        len(Path(name).parts) == 1 or name.startswith("docs/")
        or name in {"tasks/README.md", "tasks/AGENTS.md"}
        or name.endswith("/MANIFEST.md")))


def check_documents(root, names, known):
    errors = []
    links = 0
    headings = {}
    for name in names:
        path = Path(name)
        if name.startswith("docs/") and path.name != path.name.lower():
            errors.append(f"{name}: documentation filename must be lowercase")
        text = (root / name).read_text()
        for target, line in destinations(text):
            if target.startswith(("@task:", "task:", "@link:")):
                continue
            if re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith("//"):
                continue
            parsed = urlsplit(unescape(target))
            if parsed.scheme or parsed.netloc:
                continue
            file = unquote(parsed.path)
            fragment = unquote(parsed.fragment)
            file = re.sub(r"\\([ ()])", r"\1", file)
            resolved = posixpath.normpath((path.parent / file).as_posix()) if file else name
            if file.startswith("/"):
                resolved = posixpath.normpath(file.lstrip("/"))
            links += 1
            if resolved not in known:
                errors.append(f"{name}:{line}: missing or incorrectly cased path: {target}")
                continue
            if fragment and Path(resolved).suffix.lower() in MARKDOWN | {".html", ".htm"}:
                if resolved not in headings:
                    headings[resolved] = heading_ids((root / resolved).read_text())
                if fragment not in headings[resolved]:
                    errors.append(f"{name}:{line}: missing heading #{fragment} in {resolved}")
    return errors, links


def check_examples(root, names):
    errors = []
    attempted = 0
    previous = Path.cwd()
    sys.path.insert(0, str(root / "src"))
    try:
        os.chdir(root)
        for name in names:
            if Path(name).parent != Path("docs") or Path(name).name == "readme.md":
                continue
            for info, source, first in blocks((root / name).read_text()):
                if info != "pycon":
                    continue
                test = doctest.DocTestParser().get_doctest(source, {}, name, name, first - 1)
                output = io.StringIO()
                result = doctest.DocTestRunner(optionflags=doctest.ELLIPSIS).run(test, out=output.write)
                attempted += result.attempted
                if result.failed:
                    errors.append(output.getvalue().rstrip())
    finally:
        os.chdir(previous)
        sys.path.pop(0)
    return errors, attempted


def check_freshness(root):
    errors = []
    builders = ("build_evidence_classification.py", "build_pool_readiness.py",
                "build_consumer_fixtures.py", "build_calculator.py",
                "build_methods_html.py", "build_software_reference.py")
    for builder in builders:
        result = subprocess.run([sys.executable, f"scripts/{builder}", "--check"],
                                cwd=root, capture_output=True, text=True)
        if result.returncode:
            errors.append(f"{builder}: freshness check failed\n{result.stdout}{result.stderr}".rstrip())
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--examples", action="store_true", help="execute pycon examples in maintained guides")
    parser.add_argument("--freshness", action="store_true", help="run read-only generated-doc checks")
    args = parser.parse_args(argv)
    files, known = inventory(ROOT)
    names = documents(files)
    errors, links = check_documents(ROOT, names, known)
    attempted = 0
    if args.examples:
        example_errors, attempted = check_examples(ROOT, names)
        errors.extend(example_errors)
    if args.freshness and not errors:
        errors.extend(check_freshness(ROOT))
    for error in errors:
        print(error, file=sys.stderr)
    print(f"doccheck: {len(names)} documents, {links} local links, {attempted} example statements, {len(errors)} failures")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
