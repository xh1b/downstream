#!/usr/bin/env python3
# @ref:script-serve-calculator
# Method: @link:doc-calculator.
# Implementation: @link:calculator-template; @link:calculator-math; @link:calculator-app.
# Verification: @link:test-calculator; @link:test-calculator-server.
# @tag:calculator
"""Build and serve the calculator on a local HTTP address."""
from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

if __package__:
    from .build_calculator import build
else:
    from build_calculator import build


class CalculatorHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._respond(body=True)

    def do_HEAD(self):
        self._respond(body=False)

    def _respond(self, *, body):
        if urlsplit(self.path).path not in {"/", "/index.html"}:
            self.send_error(404)
            return
        page = self.server.page
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if body:
            self.wfile.write(page)


class CalculatorServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, port=8000):
        self.page = build().encode("utf-8")
        # Serve only the calculator, never the repository or a file directory.
        super().__init__(("127.0.0.1", port), CalculatorHandler)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000, help="Local port (default: 8000)")
    args = parser.parse_args(argv)
    if not 0 <= args.port <= 65535:
        parser.error("port must be between 0 and 65535")
    try:
        server = CalculatorServer(args.port)
    except OSError as exc:
        parser.exit(1, f"Cannot start calculator: {exc}. Try --port 8001.\n")
    with server:
        print(f"Downstream: http://127.0.0.1:{server.server_address[1]}/", flush=True)
        print("Press Ctrl+C to stop.", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
