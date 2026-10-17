# @ref:code-employer
# Rationale: @link:paper-exposure.
# Software contract: @link:doc-exposure-semantics-0-4.
# Verification: @link:test-employer; @link:test-audit04-custom-inputs; @link:test-employer-warehouse.
# @tag:exposure
"""Adapt documented entity exposure to the scenario engine.

The caller supplies an already computed displacement exposure. Wage-gap
money, filing counts, and WARN notices are not worker counts. This adapter
never converts or adds them to that exposure. Sources remain caller-owned.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal
import hashlib
import json
import math

from .params import Baseline, ParameterSet
from .scenario import ScenarioInput, compute_counts


EXPOSURE_KINDS = {"unspecified_reference_exposure", "reference_worker_equivalents",
                  "unique_displaced_people"}
OVERLAP_STATUSES = {"unknown", "not_deduplicated", "deduplicated", "disjoint_by_design"}
EVENT_TIME_BASES = {"unknown", "single_event", "historical_aggregate", "distributed_events"}


def _text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty string")
    return value


def _date(value, name):
    _text(value, name)
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an ISO calendar date YYYY-MM-DD") from exc
    if parsed.isoformat() != value:
        raise ValueError(f"{name} must be an ISO calendar date YYYY-MM-DD")
    return value


def _semantics(value, workers):
    """Validate caller claims; absent information stays unknown."""
    if value is None:
        value = {}
    if not isinstance(value, dict):
        raise ValueError("exposure_semantics must be an object")
    allowed = {"schema", "kind", "components", "method_version", "record_window",
               "overlap", "conversion_assumptions", "event_time"}
    if value.keys() - allowed:
        raise ValueError(f"unknown exposure_semantics fields: {sorted(value.keys() - allowed)}")
    out = {"schema": "downstream-exposure-semantics/1",
           "kind": "unspecified_reference_exposure", "components": None,
           "method_version": None, "record_window": None,
           "overlap": {"status": "unknown", "note": None},
           "conversion_assumptions": [], "event_time": {"basis": "unknown", "date": None}}
    out.update(deepcopy(value))
    if out["schema"] != "downstream-exposure-semantics/1":
        raise ValueError("unsupported exposure semantics schema")
    if not isinstance(out["kind"], str) or out["kind"] not in EXPOSURE_KINDS:
        raise ValueError("exposure kind must name reference equivalents or unique displaced people; convert other units explicitly upstream")
    if out["kind"] == "unique_displaced_people" and not float(workers).is_integer():
        raise ValueError("unique displaced people require an integer count")
    if out["method_version"] is not None:
        _text(out["method_version"], "method_version")
    if out["components"] is not None:
        if not isinstance(out["components"], dict) or not out["components"]:
            raise ValueError("components must be a nonempty named object when supplied")
        for name, component in out["components"].items():
            _text(name, "component name")
            if not isinstance(component, dict) or set(component) != {"value", "unit"}:
                raise ValueError("each exposure component requires exactly value and unit")
            amount = component["value"]
            if (isinstance(amount, bool) or not isinstance(amount, (int, float))
                    or amount < 0 or amount > float("1.7976931348623157e308")
                    or not math.isfinite(amount)):
                raise ValueError("component value must be finite and nonnegative")
            _text(component["unit"], "component unit")
    window = out["record_window"]
    if window is not None:
        if not isinstance(window, dict) or set(window) != {"start", "end"}:
            raise ValueError("record_window requires start and end")
        start, end = (_date(window[k], f"record_window.{k}") for k in ("start", "end"))
        if start > end:
            raise ValueError("record_window start must not follow end")
    overlap = out["overlap"]
    if (not isinstance(overlap, dict) or not {"status"} <= overlap.keys()
            or overlap.keys() - {"status", "note"}
            or not isinstance(overlap["status"], str) or overlap["status"] not in OVERLAP_STATUSES):
        raise ValueError("overlap requires a recognized status and optional note")
    overlap.setdefault("note", None)
    if overlap["status"] != "unknown" or overlap["note"] is not None:
        _text(overlap["note"], "overlap.note")
    if out["kind"] == "unique_displaced_people" and overlap["status"] == "not_deduplicated":
        raise ValueError("unique displaced people cannot be declared not_deduplicated")
    assumptions = out["conversion_assumptions"]
    if not isinstance(assumptions, list):
        raise ValueError("conversion_assumptions must be a list of strings")
    for assumption in assumptions:
        _text(assumption, "conversion assumption")
    event = out["event_time"]
    if (not isinstance(event, dict) or not {"basis"} <= event.keys()
            or event.keys() - {"basis", "date"}
            or not isinstance(event["basis"], str) or event["basis"] not in EVENT_TIME_BASES):
        raise ValueError("event_time requires a recognized basis and optional date")
    event.setdefault("date", None)
    if event["basis"] == "single_event":
        _date(event["date"], "event_time.date")
    elif event["date"] is not None:
        raise ValueError("a single event date requires event_time basis single_event")
    return out


@dataclass(frozen=True)
class DocumentedExposure:
    subject_id: str
    subject_type: str
    displaced_workers: float
    source: str
    method: str
    target_population: dict[str, str] | None = None
    applicability_decisions: dict[str, dict] | None = None
    exposure_semantics: dict | None = None

    def __post_init__(self):
        for name in ('subject_id', 'subject_type', 'source', 'method'):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f'{name} must be a nonempty string')
        ScenarioInput(self.displaced_workers, target_population=self.target_population,
                      applicability_decisions=self.applicability_decisions)
        object.__setattr__(self, "exposure_semantics",
                           _semantics(self.exposure_semantics, self.displaced_workers))

    @classmethod
    def from_warehouse(
        cls, *, subject_id: str, subject_type: str, source: str,
        americans_displaced: float, displacement_breakdown: dict,
        target_population=None, applicability_decisions=None, exposure_semantics=None,
    ) -> DocumentedExposure:
        """Validate the upstream employer/person aggregate without recalculating it.

        ``base`` and ``wage_depression`` are already worker-equivalent
        exposure components, not filing counts or dollars. Employer rows
        also require ``warn_layoffs``. Person rows may omit that component.
        The authoritative total is retained, including upstream rounding.
        Three independently rounded components and their rounded total can
        differ by at most 0.002 at the warehouse's three-decimal precision.
        """
        if subject_type not in {'employer', 'person'}:
            raise ValueError('warehouse mapping supports employer and person rows')
        if not isinstance(displacement_breakdown, dict):
            raise ValueError('displacement_breakdown must be an object')

        def number(value, name):
            if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
                raise ValueError(f'{name} must be a finite nonnegative number')
            value = Decimal(str(value))
            if not value.is_finite() or value < 0:
                raise ValueError(f'{name} must be a finite nonnegative number')
            return value

        total = number(americans_displaced, 'americans_displaced')
        required = ['base', 'wage_depression', 'total', 'formula']
        if subject_type == 'employer':
            required.append('warn_layoffs')
        missing = [key for key in required if key not in displacement_breakdown]
        if missing:
            raise ValueError(f'displacement_breakdown missing: {", ".join(missing)}')
        reported = number(displacement_breakdown['total'], 'total')
        if reported != total:
            raise ValueError('americans_displaced disagrees with displacement_breakdown.total')
        components = sum(number(displacement_breakdown[key], key)
                         for key in ('base', 'wage_depression', 'warn_layoffs')
                         if key in displacement_breakdown)
        if abs(components - total) > Decimal('0.002'):
            raise ValueError('displacement components disagree with the reported total')
        semantics = deepcopy(exposure_semantics) if exposure_semantics is not None else {}
        if not isinstance(semantics, dict):
            raise ValueError("exposure_semantics must be an object")
        semantics.setdefault("kind", "reference_worker_equivalents")
        canonical_components = {
            key: {"value": float(number(displacement_breakdown[key], key)),
                  "unit": "worker_equivalents"}
            for key in ("base", "wage_depression", "warn_layoffs") if key in displacement_breakdown}
        semantics.setdefault("components", canonical_components)
        if semantics["components"] != canonical_components:
            raise ValueError("warehouse semantics components must preserve the reported breakdown")
        if semantics["kind"] != "reference_worker_equivalents":
            raise ValueError("warehouse exposure is reference_worker_equivalents, not a unique cohort")
        return cls(subject_id, subject_type, float(total), source,
                   displacement_breakdown['formula'], target_population, applicability_decisions,
                   semantics)


def compute_entity_counts(
    params: ParameterSet,
    baselines: dict[str, Baseline],
    exposure: DocumentedExposure,
    scenario: ScenarioInput | None = None,
    *,
    places: dict | None = None,
    place_key: str | None = None,
    mortality_profiles: dict | None = None,
    county_mortality: dict | None = None,
    strict: bool = False,
    params_dir=None,
) -> dict:
    """Compute population-average impacts for employers or other entities.

    Scenario supplies family structure and modeling choices. Its worker
    count is replaced by the documented exposure. Persons use the same
    impact computation; the result never predicts an individual's life.
    """
    scenario = replace(scenario or ScenarioInput(0),
                       displaced_workers=exposure.displaced_workers,
                       target_population=(scenario.target_population if scenario and scenario.target_population is not None else exposure.target_population),
                       applicability_decisions=(scenario.applicability_decisions if scenario and scenario.applicability_decisions is not None else exposure.applicability_decisions))
    if (isinstance(scenario.n_children, bool) or not isinstance(scenario.n_children, int)
            or scenario.n_children < 0):
        raise ValueError('n_children must be a nonnegative integer')
    for name in ('tradable_share', 'exposure_years'):
        value = getattr(scenario, name)
        if isinstance(value, bool) or not math.isfinite(value) or value < 0:
            raise ValueError(f'{name} must be finite and nonnegative')
    if scenario.tradable_share > 1:
        raise ValueError('tradable_share must not exceed 1')
    out = compute_counts(params, baselines, scenario, strict=strict,
                         places=places, place_key=place_key,
                         mortality_profiles=mortality_profiles,
                         county_mortality=county_mortality, params_dir=params_dir)
    out['subject'] = {'id': exposure.subject_id, 'type': exposure.subject_type}
    semantics = _semantics(exposure.exposure_semantics, exposure.displaced_workers)
    provenance = {"source": exposure.source, "method": exposure.method, **semantics}
    out['exposure_provenance'] = provenance
    unique_basis = (semantics["kind"] == "unique_displaced_people"
                    and semantics["overlap"]["status"] in {"deduplicated", "disjoint_by_design"}
                    and semantics["event_time"]["basis"] == "single_event")
    out['exposure_contract'] = {
        "schema": "downstream-entity-exposure-contract/1",
        "quantity": exposure.displaced_workers,
        "application": "conditional reference consequence scaling",
        "integer_cohort_count_basis_eligible": unique_basis,
        "cohort_admission": "not established by exposure metadata; outcome transport review remains separate",
        "calendar_forecast_available": False,
        "time_interpretation": "follow-up relative to a hypothetical event; no historical-to-calendar allocation is inferred",
        "target_demographics": deepcopy(scenario.target_population),
        "family_composition": ("caller-supplied child profiles" if scenario.child_profiles is not None
                               else "unknown; n_children is a reference scenario assumption"),
        "process_uncertainty": "not computed by this adapter; integer count basis alone does not establish model applicability",
    }
    identity = {"subject": out["subject"], "quantity": exposure.displaced_workers,
                "provenance": provenance}
    out['exposure_input_sha256'] = hashlib.sha256(
        json.dumps(identity, sort_keys=True, allow_nan=False).encode()).hexdigest()
    out['interpretation'] = (
        'Population-average modeled impacts applied to the supplied exposure; '
        'not a prediction about any individual. The exposure conversion is '
        'supplied by the caller, not calibrated by this model.'
    )
    return out
