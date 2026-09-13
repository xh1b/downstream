#!/usr/bin/env python3
"""Reproducible CDC WONDER Underlying Cause of Death (D76) downloads.

Two flows, matching the two access paths CDC provides:

``national``
    Machine XML API (keyless, polite: the server enforces >=15 s between
    requests). National year x ten-year age group x gender, all causes,
    1999-2020: deaths + population + crude rate. This is the source of the
    verified national profile rates in params/mortality_profiles.csv.
    The web service is national-only by policy; the server answers any
    county/state/urbanization group-by or location filter with:
    "Only national data are available for this dataset when using the
    WONDER web service." (probed live 2026-09-13).

``county``
    Public web UI session. A Playwright-driven browser agrees to the data
    use restrictions, sets the query (group by County alone; years, sex,
    age band as filters), sends it, dumps the returned form state, and the
    export itself is downloaded by replaying that form state with a plain
    requests POST (+ ``action-Export=Download``, ``O_export-format=csv``)
    against the session-bound action URL. A fetch/XHR replay from inside
    the page is refused by the controller; plain requests is accepted.

Both modes write the raw artifact plus a ``.provenance.json`` sidecar
(retrieved_at, sha256, query criteria, caveats); ``county`` also writes a
``.metadata.json`` compatible with
``downstream.cli county-wonder-posterior --metadata``.

Usage:
    uv run --with requests scripts/fetch_wonder.py national \
        --out validation/cdc_wonder_d76_national_year_age_sex_1999_2020.xml
    uv run --with playwright,requests scripts/fetch_wonder.py county \
        --sex M --age 45-54 --years 2015,2016,2017,2018,2019 \
        --out validation/cdc_wonder_county_male_45_54_2015_2019.csv
    # one-time browser install for the county flow:
    uv run --with playwright playwright install chromium

Data use restrictions (must be preserved downstream): counts of 9 or
fewer are suppressed by NCHS; with the UI default (Show Suppressed:
False) affected counties are OMITTED from county exports entirely, while
the Total row still counts them. Never reconstruct suppressed cells.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

WONDER_URL = "https://wonder.cdc.gov/controller/datarequest/D76"
REQUEST_PAGE = "https://wonder.cdc.gov/ucd-icd10.html"
MIN_API_INTERVAL = 16.0  # server-enforced for the machine API
_last_request_at = 0.0


def _pace() -> None:
    global _last_request_at
    wait = MIN_API_INTERVAL - (time.monotonic() - _last_request_at)
    if wait > 0:
        time.sleep(wait)
    _last_request_at = time.monotonic()


def _write_artifacts(out: Path, body: bytes, provenance: dict) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(body)
    provenance["local_file"] = out.name
    provenance["sha256"] = hashlib.sha256(body).hexdigest()
    provenance["retrieved_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    out.with_suffix(".provenance.json").write_text(
        json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out} ({len(body)} bytes) sha256={provenance['sha256']}")


# ---------------------------------------------------------------- national

def _emit(parts: list[str], name: str, *values: str) -> None:
    parts.append(f"<parameter><name>{name}</name>"
                 + "".join(f"<value>{v}</value>" for v in values)
                 + "</parameter>")


def build_national_xml(dataset: str = "D76") -> str:
    """The live-validated query: year x ten-year age group x gender."""
    parts: list[str] = ["<request-parameters>"]
    _emit(parts, "action-Send", "Send")
    _emit(parts, "stage", "request")
    _emit(parts, "B_1", f"{dataset}.V1-level1")
    _emit(parts, "B_2", f"{dataset}.V5")
    _emit(parts, "B_3", f"{dataset}.V7")
    _emit(parts, "B_4", "*None*")
    _emit(parts, "B_5", "*None*")
    _emit(parts, "M_1", f"{dataset}.M1")
    _emit(parts, "M_2", f"{dataset}.M2")
    _emit(parts, "M_3", f"{dataset}.M3")
    for c in ("V1", "V2", "V9", "V10", "V27"):
        _emit(parts, f"F_{dataset}.{c}", "*All*")
    for c, label in {
        "V1": "*All* (All Dates)", "V2": "*All* (All Causes of Death)",
        "V9": "*All* (The United States)", "V10": "*All* (The United States)",
        "V27": "*All* (The United States)",
    }.items():
        _emit(parts, f"I_{dataset}.{c}", label)
    _emit(parts, "O_age", f"{dataset}.V5")
    _emit(parts, "O_ucd", f"{dataset}.V2")
    _emit(parts, "O_location", f"{dataset}.V9")
    _emit(parts, "O_urban", f"{dataset}.V19")
    _emit(parts, "O_aar", "aar_none")
    _emit(parts, "O_aar_pop", "0000")
    _emit(parts, "O_rate_per", "100000")
    _emit(parts, "O_precision", "1")
    _emit(parts, "O_show_totals", "false")
    _emit(parts, "O_timeout", "300")
    _emit(parts, "O_title", "downstream all-cause mortality, year x age x gender")
    _emit(parts, "O_javascript", "on")
    for c, v in {"V1": "", "V2": "", "V9": "", "V10": "", "V27": "",
                 "V4": "*All*", "V5": "*All*", "V6": "00", "V7": "*All*",
                 "V8": "*All*", "V11": "*All*", "V12": "*All*", "V17": "*All*",
                 "V19": "*All*", "V20": "*All*", "V21": "*All*", "V22": "*All*",
                 "V23": "*All*", "V24": "*All*", "V25": "*All*",
                 "V51": "*All*", "V52": "*All*"}.items():
        _emit(parts, f"V_{dataset}.{c}", v)
    for c in ("V1", "V2", "V9", "V27"):
        _emit(parts, f"finder-stage-{dataset}.{c}", "codeset")
    for c in ("V1", "V2", "V9", "V10", "V27"):
        _emit(parts, f"O_{c}_fmode", "freg")
    parts.append("</request-parameters>")
    return "".join(parts)


def fetch_national(out: Path) -> None:
    import requests

    _pace()
    resp = requests.post(
        WONDER_URL,
        data={"request_xml": build_national_xml(),
              "accept_datause_restrictions": "true"},
        timeout=330,
    )
    if resp.status_code == 429:
        raise SystemExit("rate limited (>=15 s between API requests); retry later")
    resp.raise_for_status()
    body = resp.content
    if b"<data-table" not in body[:200_000]:
        raise SystemExit("response is not a WONDER results document")
    _write_artifacts(out, body, {
        "source": "CDC WONDER Underlying Cause of Death, 1999-2020 (controller D76)",
        "source_url": REQUEST_PAGE,
        "endpoint": WONDER_URL,
        "method": "XML data API POST (request_xml + accept_datause_restrictions); "
                  "national-only by server policy",
        "query": {"group_by": ["Year (V1-level1)", "Ten-Year Age Groups (V5)",
                               "Gender (V7)"],
                  "filters": {"cause": "All causes", "geography": "The United States",
                              "years": "1999-2020"},
                  "measures": ["Deaths", "Population", "Crude Rate per 100,000"],
                  "age_adjusted": "aar_none", "show_totals": False},
        "contents": {"rows": body.count(b"<r>"),
                     "population_semantics": "July 1 census estimate per year; pooled "
                                             "person-years = sum of annual populations"},
    })


# ------------------------------------------------------------------ county

def fetch_county(out: Path, sex: str, age: str, years: list[int]) -> None:
    from playwright.sync_api import sync_playwright
    import requests

    if len(years) < 2 or sorted(years) != years or years[-1] - years[0] != len(years) - 1:
        raise SystemExit("years must be a contiguous window")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(REQUEST_PAGE, wait_until="domcontentloaded")
        page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('input[type="submit"], button'));
            const agree = btns.find(b => (b.value || b.textContent || '').trim() === 'I Agree');
            if (agree) agree.click();
        }""")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2500)
        page.evaluate(
            """([sex, age, years]) => {
                const set = (name, vals) => {
                    const sel = document.querySelector(`select[name="${name}"]`);
                    Array.from(sel.options).forEach(o => (o.selected = vals.includes(o.value)));
                    sel.dispatchEvent(new Event('change', {bubbles: true}));
                };
                set('V_D76.V7', [sex]);
                set('V_D76.V5', [age]);
                set('F_D76.V1', years.map(String));
                const b1 = document.querySelector('select[name="B_1"]');
                b1.value = 'D76.V9-level2';   // group by County (location hierarchy level 2)
                b1.dispatchEvent(new Event('change', {bubbles: true}));
                Array.from(document.querySelectorAll('input[type="submit"], button'))
                    .find(b => (b.value || b.textContent || '').trim() === 'Send')
                    .click();
            }""", [sex, age, years])
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(6000)
        if "Results Form" not in (page.title() or ""):
            raise SystemExit(f"unexpected page after Send: {page.title()!r}")
        form_dump = page.evaluate("""() => {
            const fmt = document.querySelector('select[name="O_export-format"]');
            const f = fmt.form;
            const entries = [];
            for (const el of f.elements) {
                if (!el.name) continue;
                if (el.tagName === 'SELECT') {
                    for (const o of el.selectedOptions) entries.push([el.name, o.value]);
                } else if (el.type === 'checkbox' || el.type === 'radio') {
                    if (el.checked) entries.push([el.name, el.value]);
                } else if (el.type !== 'submit' && el.type !== 'button') {
                    entries.push([el.name, el.value]);
                }
            }
            const notes = Array.from(document.querySelectorAll('table.response-notes'))
                .map(t => (t.innerText || '').replace(/\\s+/g, ' ').trim());
            const citation = notes.find(t => t.startsWith('Suggested Citation')) || null;
            const criteria = notes.find(t => t.startsWith('Query Criteria')) || null;
            const caveats = notes.find(t => t.startsWith('Notes:')) || null;
            return {action: f.action, method: f.method, entries, citation, criteria, caveats};
        }""")
        criteria_text = form_dump["criteria"] or ""
        browser.close()

    data = dict(form_dump["entries"])
    data["O_export-format"] = "csv"
    data["action-Export"] = "Download"
    resp = requests.post(form_dump["action"], data=data, timeout=180,
                         headers={"Referer": form_dump["action"],
                                  "Origin": "https://wonder.cdc.gov"})
    resp.raise_for_status()
    if resp.content[:1] == b"<":
        raise SystemExit("export request returned an HTML error page")
    _write_artifacts(out, resp.content, {
        "source": "CDC WONDER Underlying Cause of Death, 1999-2020 (controller D76)",
        "source_url": REQUEST_PAGE,
        "method": "public web UI session (Playwright); export downloaded by replaying "
                  "the results-form state with a plain requests POST "
                  "(action-Export=Download, O_export-format=csv). The machine XML API "
                  "is national-only by server policy; in-page fetch replays are "
                  "refused by the controller.",
        "query_criteria": criteria_text,
        "suggested_citation": form_dump["citation"],
        "caveats": form_dump["caveats"],
        "suppression": "counties with <=9 deaths are omitted entirely (Show "
                       "Suppressed: False) while the Total row still counts them; "
                       "never reconstruct suppressed cells from the difference",
    })
    sidecar = {
        "years": years,
        "sex": {"M": "Male", "F": "Female"}[sex],
        "age": f"{age} years",
        "cause": "All causes",
        "group_by": ["County"],
        "population_unit": "person-years",
        "source_url": REQUEST_PAGE,
        "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    out.with_suffix(".metadata.json").write_text(
        json.dumps(sidecar, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out.with_suffix('.metadata.json')} (county-wonder-posterior --metadata)")


# ------------------------------------------------------------------- parse

_INT_RE = re.compile(r"^-?\d[\d,]*$")


def summarize_national(body: bytes, pool_from: int, pool_to: int) -> None:
    """Print pooled event/person-year rates per age x gender for a window."""
    root = ET.fromstring(body)
    table = root.find(".//data-table")
    pools: dict[tuple[str, str], list[float]] = {}
    carry: dict[str, str | None] = dict.fromkeys(("year", "age", "gender"))
    remaining: dict[str, int] = dict.fromkeys(("year", "age", "gender"), 0)
    for r in table.findall("r"):
        cells = r.findall("c")
        label_cells = [c for c in cells if c.get("l") is not None]
        value_cells = [c for c in cells if c.get("l") is None]
        label: dict[str, str] = {}
        li = len(label_cells) - 1
        for dim in ("gender", "age", "year"):
            if remaining[dim] > 0:
                label[dim] = carry[dim]  # type: ignore[assignment]
                remaining[dim] -= 1
            else:
                cell = label_cells[li]
                label[dim] = cell.get("l")  # type: ignore[assignment]
                carry[dim] = cell.get("l")
                remaining[dim] = int(cell.get("r", "1")) - 1
                li -= 1

        def num(text: str | None):
            if text is None:
                return None
            compact = text.replace(",", "")
            if _INT_RE.match(text.strip()):
                return int(compact)
            return None

        year = int(label["year"])
        deaths, pop = num(value_cells[0].get("v")), num(value_cells[1].get("v"))
        if pool_from <= year <= pool_to and deaths is not None and pop:
            acc = pools.setdefault((label["age"], label["gender"]), [0.0, 0.0])
            acc[0] += deaths
            acc[1] += pop
    for (age, gender), (d, p) in sorted(pools.items()):
        print(f"{gender:8s} {age:14s} {pool_from}-{pool_to}  deaths={d:>8.0f}  "
              f"person_years={p:>12.0f}  annual_rate={d / p:.6f}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="mode", required=True)

    n = sub.add_parser("national", help="machine API: national year x age x gender table")
    n.add_argument("--out", default="validation/cdc_wonder_d76_national_year_age_sex_1999_2020.xml")
    n.add_argument("--pool-from", type=int, default=2015)
    n.add_argument("--pool-to", type=int, default=2019)

    c = sub.add_parser("county", help="web UI: county-level deaths + population export")
    c.add_argument("--sex", choices=["M", "F"], default="M")
    c.add_argument("--age", default="45-54", help="ten-year age group code, e.g. 45-54")
    c.add_argument("--years", default="2015,2016,2017,2018,2019",
                   help="contiguous comma-separated years")
    c.add_argument("--out", default=None,
                   help="default: validation/cdc_wonder_county_<sex>_<age>_<from>_<to>.csv")

    args = ap.parse_args()
    if args.mode == "national":
        fetch_national(Path(args.out))
        summarize_national(Path(args.out).read_bytes(), args.pool_from, args.pool_to)
        return 0
    years = [int(y) for y in args.years.split(",")]
    sex_word = {"M": "male", "F": "female"}[args.sex]
    out = Path(args.out or
               f"validation/cdc_wonder_county_{sex_word}_{args.age.replace('-', '_')}_"
               f"{years[0]}_{years[-1]}.csv")
    fetch_county(out, args.sex, args.age, years)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
