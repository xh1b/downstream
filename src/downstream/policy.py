"""Conditional policy contrasts with explicit exposure assumptions.

This layer compares supplied counterfactual exposures. It does not estimate
how a law, visa rule, tax, or spending decision changes displacement.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass, replace
import math

from . import __version__
from .scenario import ScenarioInput, compute_counts


@dataclass(frozen=True)
class PolicyCase:
    name: str
    source: str
    method: str
    scenario: ScenarioInput
    exposure_low: float | None = None
    exposure_high: float | None = None
    place_key: str | None = None

    def __post_init__(self):
        for key in ('name', 'source', 'method'):
            if not isinstance(getattr(self, key), str) or not getattr(self, key).strip():
                raise ValueError(f'{key} is required')
        if not isinstance(self.scenario, ScenarioInput):
            raise ValueError('scenario must be ScenarioInput')
        lo, hi = self.exposure_band
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in (lo, hi)):
            raise ValueError('exposure bounds must be finite numbers')
        if not 0 <= lo <= self.scenario.displaced_workers <= hi:
            raise ValueError('exposure bounds must bracket displaced_workers and be nonnegative')

    @property
    def exposure_band(self):
        point = self.scenario.displaced_workers
        return (point if self.exposure_low is None else self.exposure_low,
                point if self.exposure_high is None else self.exposure_high)

    @classmethod
    def from_dict(cls, value):
        value = dict(value)
        value['scenario'] = ScenarioInput(**value['scenario'])
        return cls(**value)


def compare_policies(params, baselines, baseline: PolicyCase, policy: PolicyCase, *, places=None, county_mortality=None, mortality_profiles=None):
    def evaluate(case):
        point = compute_counts(params, baselines, case.scenario, places=places, place_key=case.place_key, county_mortality=county_mortality, mortality_profiles=mortality_profiles)
        extremes = [compute_counts(params, baselines, replace(case.scenario, displaced_workers=n),
                                   places=places, place_key=case.place_key, county_mortality=county_mortality, mortality_profiles=mortality_profiles)
                    for n in case.exposure_band]
        combined = {}
        for key, row in point['modeled'].items():
            values = [r['modeled'][key][bound] for r in extremes for bound in ('low', 'high')]
            combined[key] = {'point': row['point'], 'low': min(values), 'high': max(values), 'unit': row['unit']}
        return {'name': case.name, 'exposure_assumption': {'source': case.source, 'method': case.method,
                'point': case.scenario.displaced_workers, 'low': case.exposure_band[0], 'high': case.exposure_band[1]},
                'parameter_envelope': point, 'parameter_and_exposure_envelope': combined}

    before, after = evaluate(baseline), evaluate(policy)
    left, right = asdict(baseline.scenario), asdict(policy.scenario)
    left.pop('label')
    right.pop('label')
    identical = (left == right and baseline.place_key == policy.place_key
                 and baseline.exposure_band == policy.exposure_band)
    delta = {}
    blocked = [{"outcome": row["outcome"], "arm": arm, "reason": row["reason"]}
               for arm, result in (("baseline", before), ("policy", after))
               for row in result["parameter_envelope"]["blocked"]]
    all_keys = set(before['parameter_and_exposure_envelope']) | set(after['parameter_and_exposure_envelope'])
    for key in sorted(all_keys):
        b = before['parameter_and_exposure_envelope'].get(key)
        p = after['parameter_and_exposure_envelope'].get(key)
        if b is None or p is None:
            blocked.append({'outcome': key, 'reason': 'one comparison arm lacks the required baseline'})
            continue
        if b['unit'] != p['unit']:
            raise ValueError(f'incompatible units for {key}')
        delta[key] = {'point': 0.0 if identical else round(p['point']-b['point'], 4),
                      'low': 0.0 if identical else round(p['low']-b['high'], 4),
                      'high': 0.0 if identical else round(p['high']-b['low'], 4),
                      'unit': p['unit']}
    return {'schema': 'downstream-policy-comparison/1', 'engine_version': __version__,
            'parameter_set_version': params.version, 'baseline': before, 'policy': after,
            'policy_minus_baseline': delta, 'blocked': blocked,
            'interpretation': 'Conditional modeled change; negative values mean fewer modeled losses. '
                'Policy-to-exposure effects are caller-supplied assumptions, not identified by this model.',
            'uncertainty': {'delta_band': 'conservative difference of support envelopes; not a confidence interval',
                'shared_parameters': 'same parameter set; general envelope does not assume a cross-arm correlation',
                'identical_cases': 'identical scenarios with identical exposure bounds are the same counterfactual and cancel exactly',
                'fixed': ['baseline estimates', 'place measurements', 'pooling weights'],
                'excluded': ['unmodeled mechanisms', 'policy-to-exposure estimation beyond supplied bounds']}}
