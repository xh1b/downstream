- 2026-10-14 codex: Proposed from the owner-requested XH1B usage review; implementation is not claimed.

## c-3f4d7c6f6eea

- At: 2026-10-15 00:45 HKT
- By: codex

triage: inbox -> ready.

Owner authorized low-hanging work. Prepare engine-backed consumer fixtures and normalization acceptance checks; no companion repin or deployment.

## c-a17fa13f9444

- At: 2026-10-15 00:46 HKT
- By: codex

claim: ready -> active.

## c-5ca846c921e0

- At: 2026-10-15 00:59 HKT
- By: codex

Implemented acd04ec: raw totals with public provenance, complete scaling expectations, weighted persistence/removal/endpoints, explicit unavailable mixture quantiles and blocked positive-weight outcomes. Sixteen focused tests, deterministic fixture freshness and scoped Ruff pass. Companion parser/worker/cache/HTML/Markdown acceptance remains documented for XH1B; no repin or deployment. Eli is independently reviewing this unit.

## c-4d912af2e501

- At: 2026-10-15 00:59 HKT
- By: codex

done: active -> review.

## c-4cf5abd8bf11

- At: 2026-10-15 01:00 HKT
- By: eli

Independent read-only review of acd04ec: approved. Ran tests/test_consumer_fixtures.py (16 passed in 4.67s) and fixture builder --check (current). Inspected native/raw fractional precision, signed child effects, result-only scaling, variance squared scaling and zero-index handling; all active components contribute to persistence/removal/endpoint experiments, eligibility requires every active component, blocked components cannot become zero contributions, and quantile/variance mixture claims remain withheld. Docs clearly distinguish offline acceptance from companion integration or deployment; synthetic reviewed fields and 128-draw design are appropriately qualified. No blocking defect found.

## c-b7932e0ca419

- At: 2026-10-15 01:00 HKT
- By: eli

accept: review -> done.

## c-9fb9e7f1b273

- At: 2026-10-15 01:14 HKT
- By: codex

Final integrated quick-win receipt: full coverage run passed 1,152 tests in 935.26s; gate passed 96.9% lines / 93.4% branches. The five new focused suites passed 50 tests after the precision correction. Ruff src/scripts plus new tests, Vulture, audit (0 errors/0 warnings), all three generated-file freshness checks, source-archive asset inspection and ten installed-wheel CLI commands passed. Board validates with 0 errors and five existing unresolved-blocker notices. Implementation and board commits are local on master; engine remains 0.4.0. Calculator browser/visual/participant review remains pending as documented.
