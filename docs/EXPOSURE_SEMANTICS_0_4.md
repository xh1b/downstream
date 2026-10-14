# Entity exposure semantics in 0.4

`DocumentedExposure` accepts optional `exposure_semantics` metadata. Existing
positional arguments, warehouse input and numeric calculations are preserved.
The adapter uses the supplied authoritative exposure; it does not turn wages,
filings, WARN notices, worker-years or historical sums into displaced people.

## Input contract

```json
{
  "subject_id": "synthetic-employer",
  "subject_type": "employer",
  "displaced_workers": 100.125,
  "source": "synthetic upstream aggregate",
  "method": "caller-owned exposure formula",
  "exposure_semantics": {
    "schema": "downstream-exposure-semantics/1",
    "kind": "reference_worker_equivalents",
    "method_version": "upstream/2",
    "components": {
      "requested_positions": {"value": 75, "unit": "worker_equivalents"},
      "wage_gap": {"value": 25.125, "unit": "worker_equivalents"}
    },
    "record_window": {"start": "2010-01-01", "end": "2025-12-31"},
    "overlap": {
      "status": "not_deduplicated",
      "note": "Repeated filings and matched layoffs can overlap."
    },
    "conversion_assumptions": [
      "Components are reference equivalents under the supplied upstream method."
    ],
    "event_time": {"basis": "historical_aggregate"}
  }
}
```

This is synthetic metadata, not an accepted empirical conversion.

| Field | Meaning and validation |
| --- | --- |
| `kind` | `unspecified_reference_exposure`, `reference_worker_equivalents`, or `unique_displaced_people`. The last requires an integer; worker-years and other units need explicit upstream conversion. |
| `components` | Optional named `{value, unit}` records. Values must be finite/nonnegative; units must be explicit. General components can retain raw audit quantities and are never summed or converted by this contract. |
| `method_version` | Optional nonempty upstream method version; the method description remains separately required. |
| `record_window` | Optional inclusive start/end ISO dates in order. These date the records, not the displacement event. |
| `overlap` | `unknown`, `not_deduplicated`, `deduplicated`, or `disjoint_by_design`; nonunknown claims require an explanatory note. Unique people cannot simultaneously be labeled not deduplicated. |
| `conversion_assumptions` | Explicit list of nonempty caller assumptions, preserved without endorsement. |
| `event_time` | `unknown`, `single_event`, `historical_aggregate`, or `distributed_events`. A single event requires its ISO date. Other bases cannot silently borrow a single date. |

Omitted fields are explicitly unknown, not inferred from a method name, source,
entity type or numeric value. Unknown schema versions/fields are refused.

The existing warehouse mapping already defines `base`, `wage_depression` and
optional/required `warn_layoffs` as worker-equivalent components. It preserves
these components, labels their units and retains the authoritative rounded
total. Supplied metadata cannot relabel that aggregate as unique people or
replace its reported components. No upstream formula is recalculated.

## Returned interpretation and identity

`exposure_provenance` retains `source` and `method` and adds the normalized
semantics. `exposure_contract` distinguishes the numeric scaling convention
from cohort admission. Missing target demographics stay `null`; absent child
profiles mean family composition is unknown. `n_children=2` is a reference
scenario assumption, not an observed family distribution. Supplied profiles
remain caller supplied. Generic CPS composition is not an H-1B exposure bridge.

`integer_cohort_count_basis_eligible` requires all three caller claims:

1. Unique displaced people with an integer count.
2. Deduplication or disjoint records, with an explanatory note.
3. One dated event.

This flag qualifies the **count basis only**. It does not validate these claims,
admit mortality/child transport, identify family composition or compute process
uncertainty. An integer worker-equivalent aggregate does not qualify. Fractional
reference equivalents can scale expected consequences, but cannot become a
binomial cohort simply by rounding. The entity adapter does not compute
integer-cohort process uncertainty; that remains a separately qualified model.

`calendar_forecast_available` is false for this adapter. Follow-up remains
relative to a modeled event. A filing history does not place all displacement
in the present year; distributed events would require a separately supplied
schedule and corresponding refits, which this adapter does not implement.
An event date alone does not repair fixed-age baseline or transport limits.

`exposure_input_sha256` fingerprints subject, quantity and full provenance.
The scenario's existing `input_content_sha256` remains its own identity; consumers
need both identities plus model/bundle and adapter identities. Changing a
record window, overlap claim, component or method version changes exposure
identity even when the numerical reference estimate stays the same.

Outcome-level applicability and existing modeled numbers remain unchanged.
Exposure metadata never manufactures reviewed scientific applicability.

## Verification

[Contract tests](../tests/test_exposure_semantics.py) exercise backward-compatible
numbers, unknown demographics, fractional versus integer count bases, absent
event timing, caller-input preservation, warehouse rounding/components,
malformed metadata refusal, CLI round-trip and provenance invalidation.
[Existing employer tests](../tests/test_employer.py) and
[warehouse tests](../tests/test_employer_warehouse.py) retain prior behavior.
