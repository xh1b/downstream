---
title: Scale aliased consumer intervals exactly once
area: engine
priority: P1
assignee:
blocked-by: []
---

Repair a release defect found by the 0.4 companion fixture parity checks.

The sampled national result shares its top-level parameter_interval_90 object with persistence_sensitivity.variants.source_profile.parameter_interval_90. deepcopy preserves that alias, so scale_outcome mutates it once at the top level and again during recursive variant scaling. Fractional and large display exposures then have incorrect nested intervals. Keep the source object unchanged and scale every reported result interval exactly once.

- [ ] Add a regression with a real shared interval and repair the transform without changing source metadata or default model arithmetic.
- [ ] Refresh affected consumer fixtures, paper provenance and candidate qualification with explicit superseding identities.
- [ ] Refresh the local companion bundle/fixtures and verify Python/TypeScript display parity.
