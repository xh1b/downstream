# comments

## c-a015b3be61ef

- At: 2026-10-15 02:25 HKT
- By: John Larue

Created in inbox.

## c-d1b77e689e3b

- At: 2026-10-15 02:25 HKT
- By: codex

triage: inbox -> ready.

## c-9ef569133814

- At: 2026-10-15 02:25 HKT
- By: codex

claim: ready -> active.

## c-f7ab10279ef8

- At: 2026-10-15 02:35 HKT
- By: codex

The calculator is a top-level app with a running local server

`make serve` runs at http://127.0.0.1:8000/. The server builds current source data in memory at startup and serves only the app. `make calculator` builds the standalone page. There were no other examples; the empty examples directory was removed.

Implementation: a64a638, 53f5b33 and 376b0c9. Current evidence links were repaired in 47c3e90; historical comments remain unchanged. Calculator and HTTP regression tests: 16 passed. Ruff, Vulture, generated-page freshness and diff checks pass. Source-package inspection confirms all 11 required app/server/documentation files and no retired paths.

Actual browser checks at 320, 390, 600 and 1440 px found no page-wide overflow and aligned input rows. Fractional exposure, tail-null and reset work; console errors were absent. [Review and screenshot](../../../docs/CALCULATOR.md#browser-review--2026-10-15). Physical-device, zoom, assistive-technology and participant checks remain open on task:2026-10-14-calculator-design.

## c-edb54627d618

- At: 2026-10-15 02:35 HKT
- By: codex

done: active -> review.

The top-level app, local server and verification receipts are ready for review.

## c-935cef1ffbe1

- At: 2026-10-27 06:42 HKT
- By: codex-review

accept: review -> done.

Verified permanent calculator paths, narrow loopback HTTP server, GET/HEAD/path/CWD regressions, build/serve commands, retained browser receipt and mobile capture.

Verification receipt: @task:2026-10-27-review-acceptance#c-845b5298b984. Accepted under the owner's request to verify and complete review tasks.
