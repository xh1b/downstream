# @ref:test-calculator-server
# Method: @link:doc-calculator.
# Implementation: @link:calculator-math; @link:calculator-app; @link:script-build-calculator;
# @link:script-serve-calculator.
# @tag:calculator @tag:testing
"""The local server serves the current app without exposing repository files."""
from contextlib import contextmanager
import json
from pathlib import Path
import re
import subprocess
import sys
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from scripts.serve_calculator import CalculatorServer, main

ROOT = Path(__file__).resolve().parents[1]


@contextmanager
def running_server():
    server = CalculatorServer(0)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_http_page_is_current_and_head_has_no_body():
    with running_server() as address:
        with urlopen(address + "/", timeout=5) as response:
            page = response.read()
            assert response.status == 200
            assert response.headers["Content-Type"] == "text/html; charset=utf-8"
            assert response.headers["Cache-Control"] == "no-store"
        data = json.loads(re.search(rb'<script id="engine-data" type="application/json">(.*?)</script>', page, re.S)[1])
        assert data["result"]["engine_version"] == "0.4.0"
        assert data["result"]["parameter_set_version"] == (ROOT / "params/VERSION").read_text().strip()
        assert data["result"]["modeled"]["excess_deaths"]["point"] == 28.76
        assert data["defaults"]["workers"] == 1000
        with urlopen(Request(address + "/index.html", method="HEAD"), timeout=5) as response:
            assert response.status == 200
            assert int(response.headers["Content-Length"]) == len(page)
            assert response.read() == b""
        with urlopen(address + "/?view=mobile", timeout=5) as response:
            assert response.read() == page


@pytest.mark.parametrize("path", ["/params/parameters.csv", "/.env", "/../AGENTS.md", "/%2e%2e/AGENTS.md", "/scripts/", "/style.css"])
def test_other_paths_never_serve_files_or_directory_listings(path):
    with running_server() as address:
        with pytest.raises(HTTPError) as error:
            urlopen(address + path, timeout=5)
        assert error.value.code == 404


@pytest.mark.parametrize("port", ["-1", "65536", "invalid"])
def test_invalid_ports_fail_before_starting(port):
    with pytest.raises(SystemExit) as error:
        main(["--port", port])
    assert error.value.code == 2


def test_startup_works_outside_repository(tmp_path):
    process = subprocess.Popen([sys.executable, str(ROOT / "scripts/serve_calculator.py"), "--port", "0"],
                               cwd=tmp_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        line = process.stdout.readline().strip()
        assert line.startswith("Downstream: http://127.0.0.1:"), line
        address = line.removeprefix("Downstream: ")
        with urlopen(address, timeout=5) as response:
            assert b'<title>Downstream</title>' in response.read()
    finally:
        process.terminate()
        process.communicate(timeout=5)


def test_busy_port_reports_a_clear_error(capsys):
    with CalculatorServer(0) as server:
        with pytest.raises(SystemExit) as error:
            main(["--port", str(server.server_address[1])])
        assert error.value.code == 1
    assert "Try --port 8001" in capsys.readouterr().err
