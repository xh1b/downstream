import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from downstream.bundle import export_bundle, verify_bundle


def test_standalone_bundle_runs_without_source_checkout(tmp_path):
    target = tmp_path / "bundle"
    manifest = export_bundle(target)
    assert verify_bundle(target) == manifest
    env = dict(os.environ, PYTHONPATH=str(target / "src"))
    result = subprocess.run([sys.executable, "-m", "downstream.cli", "scenario", "--workers", "1000"],
                            cwd=tmp_path, env=env, text=True, capture_output=True, check=True)
    assert json.loads(result.stdout)["engine_version"] == manifest["engine_version"]
    assert export_bundle(tmp_path / "second") == manifest
    with pytest.raises(FileExistsError):
        export_bundle(target)
    (target / "params" / "VERSION").write_text("tampered")
    with pytest.raises(ValueError, match="checksum"):
        verify_bundle(target)


def test_failed_export_leaves_no_partial_bundle_or_staging_directory(tmp_path, monkeypatch):
    target = tmp_path / "bundle"
    original = Path.write_bytes

    def fail_on_parameter_set(path, content):
        if path.name == "parameter_set.json":
            raise OSError("simulated disk failure")
        return original(path, content)

    monkeypatch.setattr(Path, "write_bytes", fail_on_parameter_set)
    with pytest.raises(OSError, match="simulated disk failure"):
        export_bundle(target)
    assert not target.exists()
    assert not list(tmp_path.glob(".bundle.staging-*"))
