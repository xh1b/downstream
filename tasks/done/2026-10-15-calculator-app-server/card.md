---
title: Promote calculator app and add local web server
area: calculator
priority: P1
assignee: codex
blocked-by: []
---

Promote the calculator from examples/ to a top-level application and provide a small local HTTP server. Keep the compact interface and native-equation checks.

## Acceptance

- [x] Move the app, builder, tests and documentation to clear permanent paths; update current links while preserving historical comments. [move receipts](task:2026-10-15-calculator-app-server#c-f7ab10279ef8)
- [x] Provide one local serve command that builds current inputs and serves only the calculator. [server](../../../scripts/serve_calculator.py) [command](../../../Makefile)
- [x] Verify HTTP GET/HEAD, unavailable paths, current calculation data and startup from another working directory. [HTTP tests](../../../tests/test_calculator_server.py) [checks](task:2026-10-15-calculator-app-server#c-f7ab10279ef8)
- [x] Update setup and mobile-review instructions; record a working local URL and any actual browser checks or access limits. [setup and review](../../../docs/calculator.md) [screenshot](../../../docs/images/calculator-mobile-390.jpg)
