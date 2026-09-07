"""CLI smoke traps: every public verb must at least run.

Born 2026-09-07 from a real bug the smoke test caught: a function-local
`from .scenario import ScenarioInput` inside the knobs branch made the
name local to main(), so `downstream scenario` died with
UnboundLocalError even though the module-level import existed.
"""
import json
import os
import subprocess
import sys

PY = sys.executable
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _cli(*argv):
    """Run the CLI as a user would: PYTHONPATH=src, repo cwd."""
    env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "src"))
    return subprocess.run(
        [PY, "-m", "downstream.cli", *argv],
        capture_output=True, text=True, cwd=ROOT, env=env,
    )


def test_scenario_verb_runs():
    r = _cli("scenario", "--workers", "10000")
    assert r.returncode == 0, r.stderr[-500:]
    out = json.loads(r.stdout)
    assert out["parameter_set_version"].startswith("v1.")
    assert out["exposure"]["displaced_workers"] == 10000.0


def test_family_verb_runs():
    r = _cli("family")
    assert r.returncode == 0, r.stderr[-500:]
    out = json.loads(r.stdout)
    assert "vignette" in out


def test_knobs_verb_still_runs_after_import_fix():
    r = _cli("knobs", "--action", "voi", "--draws", "200")
    assert r.returncode == 0, r.stderr[-500:]
