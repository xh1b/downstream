"""Adapt documented entity exposure to the scenario engine.

The caller supplies an already computed displacement exposure. Wage-gap
money, filing counts, and WARN notices are not worker counts. This adapter
never converts or adds them to that exposure. Sources remain caller-owned.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
import math

from .params import Baseline, ParameterSet
from .scenario import ScenarioInput, compute_counts


@dataclass(frozen=True)
class DocumentedExposure:
    subject_id: str
    subject_type: str
    displaced_workers: float
    source: str
    method: str
    target_population: dict[str, str] | None = None
    applicability_decisions: dict[str, dict] | None = None

    def __post_init__(self):
        for name in ('subject_id', 'subject_type', 'source', 'method'):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f'{name} must be a nonempty string')
        ScenarioInput(self.displaced_workers, target_population=self.target_population,
                      applicability_decisions=self.applicability_decisions)

    @classmethod
    def from_warehouse(
        cls, *, subject_id: str, subject_type: str, source: str,
        americans_displaced: float, displacement_breakdown: dict,
        target_population=None, applicability_decisions=None,
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
        return cls(subject_id, subject_type, float(total), source,
                   displacement_breakdown['formula'], target_population, applicability_decisions)


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
                         county_mortality=county_mortality)
    out['subject'] = {'id': exposure.subject_id, 'type': exposure.subject_type}
    out['exposure_provenance'] = {'source': exposure.source, 'method': exposure.method}
    out['interpretation'] = (
        'Population-average modeled impacts applied to the supplied exposure; '
        'not a prediction about any individual. The exposure conversion is '
        'supplied by the caller, not calibrated by this model.'
    )
    return out
