import csv
from pathlib import Path

import pytest

from downstream.brac import build, parse

DATA = Path(__file__).resolve().parents[1] / "validation"


def test_gao_inventory_reconciles_to_published_totals():
    raw = (DATA / "brac_gao05138_table3.txt").read_bytes()
    rows = parse(raw)
    assert rows[0]['civilian_jobs_lost'] == 3228
    assert rows[-1]['redevelopment_jobs_created'] == 603
    with (DATA / "brac_gao05138_civilian_jobs.csv").open() as f:
        stored = list(csv.DictReader(f))
    assert [r['base'] for r in stored] == [r['base'] for r in rows]
    with pytest.raises(ValueError, match="reconcile"):
        parse(raw.replace(b"3,228", b"3,229", 1))


def test_build_writes_a_reproducible_inventory_and_provenance(tmp_path):
    source = DATA / "brac_gao05138_table3.txt"
    provenance = build(tmp_path, source)
    assert provenance["capture"] == "saved accessible-text excerpt"
    assert provenance["rows"] == 73
    assert (tmp_path / "brac_gao05138_civilian_jobs.csv").is_file()
    stored = (tmp_path / "brac_gao05138_civilian_jobs.provenance.json").read_text()
    assert provenance["source_sha256"] in stored
