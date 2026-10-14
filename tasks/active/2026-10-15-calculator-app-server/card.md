---
title: Promote calculator app and add local web server
area: calculator
priority: P1
assignee: codex
blocked-by: []
---

Promote the calculator from examples/ to a top-level application and provide a small local HTTP server. Keep the compact interface and native-equation checks.

## Acceptance

- [ ] Move the app, builder, tests and documentation to clear permanent paths; update current links while preserving historical comments.
- [ ] Provide one local serve command that builds current inputs and serves only the calculator.
- [ ] Verify HTTP GET/HEAD, unavailable paths, current calculation data and startup from another working directory.
- [ ] Update setup and mobile-review instructions; record a working local URL and any actual browser checks or access limits.
