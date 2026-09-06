"""references.bib parsing + citation coverage.

The bib file is the single citation database. Parameter rows cite by
semicolon-separated bib keys; this module resolves keys and reports
coverage. No output may cite a key that does not resolve here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class BibEntry:
    key: str
    kind: str                      # article / book / inproceedings ...
    fields: dict[str, str] = field(default_factory=dict)

    @property
    def evidence(self) -> str:
        return self.fields.get("xh1b-evidence", "canonical")

    @property
    def year(self) -> str:
        return self.fields.get("year", "")

    @property
    def title(self) -> str:
        return re.sub(r"[{}]", "", self.fields.get("title", ""))

    def cite(self) -> str:
        """Short inline citation string."""
        authors = self.fields.get("author", "")
        first = authors.split(" and ")[0]
        surname = first.split(",")[0].strip()
        return f"{surname} {self.year}"


def parse_bib(path: str | Path) -> dict[str, BibEntry]:
    text = Path(path).read_text(encoding="utf-8")
    entries: dict[str, BibEntry] = {}
    for m in re.finditer(r"@(\w+)\{([^,]+),\s*(.*?)\n\}", text, re.DOTALL):
        kind, key, body = m.group(1), m.group(2).strip(), m.group(3)
        entries[key] = BibEntry(key=key, kind=kind, fields=_parse_fields(body))
    return entries


_FIELD_RE = re.compile(r"(\w[\w-]*)\s*=\s*", re.DOTALL)


def _parse_fields(body: str) -> dict[str, str]:
    """Parse `name = "..."` / `name = {...}` fields with brace-depth
    matching (bib values nest braces for accented authors)."""
    fields: dict[str, str] = {}
    pos = 0
    while m := _FIELD_RE.search(body, pos):
        start = m.end()
        ch = body[start] if start < len(body) else ""
        if ch == '"':
            end = body.find('"', start + 1)
            value = body[start + 1 : end]
            pos = end + 1
        elif ch == "{":
            depth, i = 1, start + 1
            while i < len(body) and depth:
                if body[i] == "{":
                    depth += 1
                elif body[i] == "}":
                    depth -= 1
                i += 1
            value = body[start + 1 : i - 1]
            pos = i
        else:  # bare number
            m2 = re.match(r"[^,\n]+", body[start:])
            value = m2.group(0).strip()
            pos = start + m2.end()
        fields[m.group(1)] = " ".join(value.split())
    return fields
