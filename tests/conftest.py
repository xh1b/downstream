# @ref:test-conftest
# Method: @link:doc-testing-quality.
# Implementation: @link:engine-package.
# @tag:testing
"""Put src/ on the path for the test run (the package is not installed)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
