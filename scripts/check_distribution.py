"""Install a wheel in isolation and exercise it without checkout data or imports."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
import venv


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel", type=Path)
    args = parser.parse_args()
    wheel = args.wheel.resolve(strict=True)
    env = {key: value for key, value in os.environ.items()
           if key not in {"PYTHONPATH", "PYTHONHOME"}}
    with tempfile.TemporaryDirectory(prefix="downstream-wheel-") as directory:
        root = Path(directory)
        venv.EnvBuilder(with_pip=True).create(root / "env")
        binaries = root / "env" / ("Scripts" if os.name == "nt" else "bin")
        python = binaries / ("python.exe" if os.name == "nt" else "python")
        cli = binaries / ("downstream.exe" if os.name == "nt" else "downstream")
        subprocess.run([str(python), "-m", "pip", "install", "--no-deps", str(wheel)],
                       cwd=root, env=env, check=True)
        for command in (["audit"], ["export"], ["family"], ["validate"],
                        ["scenario", "--workers", "1000", "--draws", "20", "--seed", "1901"],
                        ["bundle", "--out", str(root / "bundle")]):
            result = subprocess.run([str(cli), *command], cwd=root, env=env,
                                    capture_output=True, text=True)
            if result.returncode:
                raise RuntimeError(f"Installed-wheel {command[0]} failed:\n"
                                   f"{result.stdout}\n{result.stderr}")
            json.loads(result.stdout)
            print(f"Installed-wheel check passed: {command[0]}")


if __name__ == "__main__":
    main()
