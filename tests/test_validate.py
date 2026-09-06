"""V0 internal-consistency checks — the model's cheapest falsifier."""

from pathlib import Path

from downstream.params import load
from downstream.validate import internal_consistency, run, v1_backtest_spec

PARAMS = Path(__file__).resolve().parent.parent / "params" / "parameters.csv"


def test_v0_direct_and_ige_paths_agree_on_shipped_set():
    out = internal_consistency(load(PARAMS))
    assert out["pass"] is True
    # direct: Oreopoulos 0.91; IGE-composed: 1 - 0.55*0.20 = 0.89
    assert out["direct"]["point"] == 0.91
    assert abs(out["ige_composed"]["point"] - 0.89) < 1e-6


def test_v0_fails_loudly_when_paths_diverge():
    """Sabotage the IGE band to 0.10-0.15 (implausibly weak transmission):
    composed child gap becomes ~0.98 — outside the direct band. The
    check must catch the misreading, not paper over it."""
    import tempfile

    import csv as _csv

    with open(PARAMS, newline="") as f:
        rows = list(_csv.DictReader(f))
        fields = list(rows[0].keys())
    for r in rows:
        if r["link"] == "child_earnings->grandchild_earnings":
            r["point"], r["low"], r["high"] = "0.125", "0.10", "0.15"
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "parameters.csv"
        with open(p, "w", newline="") as fh:
            w = _csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        out = internal_consistency(load(p, version="t"))
        assert out["pass"] is False
        assert out["bands_overlap"] is False


def test_v1_target_is_specified_with_design_and_pass_rule():
    spec = v1_backtest_spec()
    assert "Autor" in spec["target"]
    assert "no parameter may be tuned" in spec["design"].lower() or "No parameter" in spec["design"]
    assert spec["status"].startswith("scaffolded")


def test_run_assembles_stages():
    out = run(load(PARAMS))
    assert "v0_internal_consistency" in out and "v1_backtest" in out
