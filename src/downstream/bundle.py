"""Content-addressed, standalone engine and parameter export for consumers."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from . import __version__
from .params import default_dir
from .snapshot import build


def export_bundle(destination: str | Path, params_dir=None) -> dict:
    """Atomically write a new directory; refuse overwrites and partial bundles."""
    destination = Path(destination)
    if destination.exists():
        raise FileExistsError(destination)
    data = Path(params_dir) if params_dir else default_dir()
    snapshot = build(data)  # audit before any writes
    files = {f"src/downstream/{p.name}": p.read_bytes()
             for p in sorted(Path(__file__).parent.glob("*.py"))}
    files.update({f"params/{p.name}": p.read_bytes()
                  for p in sorted(data.iterdir()) if p.is_file()})
    files["parameter_set.json"] = (json.dumps(snapshot, indent=2) + "\n").encode()
    hashes = {name: hashlib.sha256(content).hexdigest() for name, content in files.items()}
    digest = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
    manifest = {"schema": "downstream-engine-bundle/1", "engine_version": __version__,
                "parameter_set_version": snapshot["version"], "sha256": digest,
                "algo_version": f"{snapshot['version']}+engine{__version__}+{digest}",
                "files": hashes}
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{destination.name}.staging-", dir=destination.parent))
    published = False
    try:
        for name, content in files.items():
            path = staging / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        (staging / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        # Rename is atomic on one filesystem.  All consumers therefore see
        # either no bundle or a complete checksum-verifiable bundle.
        staging.rename(destination)
        published = True
    finally:
        if not published and staging.exists():
            shutil.rmtree(staging)
    return manifest


def verify_bundle(directory: str | Path) -> dict:
    directory = Path(directory).resolve()
    manifest = json.loads((directory / "manifest.json").read_text())
    if manifest["schema"] != "downstream-engine-bundle/1":
        raise ValueError("unsupported bundle schema")
    for name, digest in manifest["files"].items():
        path = (directory / name).resolve()
        if not path.is_relative_to(directory) or not path.is_file():
            raise ValueError(f"invalid bundle path: {name}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f"bundle checksum mismatch: {name}")
    digest = hashlib.sha256(json.dumps(manifest["files"], sort_keys=True).encode()).hexdigest()
    if digest != manifest["sha256"]:
        raise ValueError("bundle manifest checksum mismatch")
    expected = f"{manifest['parameter_set_version']}+engine{manifest['engine_version']}+{digest}"
    if manifest["algo_version"] != expected:
        raise ValueError("bundle version mismatch")
    return manifest
