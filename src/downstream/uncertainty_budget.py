"""Propagate documented exposure and mortality-baseline uncertainty separately.

This conditional budget adds an explicit count likelihood and declared
exposure distribution. It does not estimate transport error or turn a
structural comparison into a posterior model average.
"""
from __future__ import annotations

from dataclasses import replace
import math
import random

from .child_applicability import select_child_contrast
from .mc import simulate_many
from .mortality import rate_to_risk
from .scenario import ScenarioInput, compute_counts, sample_counts


def propagate_uncertainty(params, baselines, payload, *, nodes=None, params_dir=None):
    scenario=ScenarioInput(**payload['scenario'])
    if scenario.mortality_profile is not None or scenario.mortality_mix is not None or scenario.mortality_method!='odds_survival' or scenario.mortality_timing!='source_profile':
        raise ValueError('joint count budget currently requires the national source-profile mortality scenario')
    exposure,counts=payload['exposure_model'],payload['baseline_counts']
    if exposure.get('distribution')!='integer_uniform_declared':
        raise ValueError('exposure distribution must be integer_uniform_declared')
    low,high=exposure.get('low'),exposure.get('high')
    if any(isinstance(x,bool) or not isinstance(x,int) or x<0 for x in (low,high)) or not low<=scenario.displaced_workers<=high:
        raise ValueError('integer exposure bounds must bracket displaced_workers')
    if scenario.displaced_workers!=int(scenario.displaced_workers):
        raise ValueError('process budget requires an integer reference cohort')
    for record in (exposure,counts):
        if any(not isinstance(record.get(k),str) or not record[k].strip() for k in ('source','method')):
            raise ValueError('uncertainty inputs require source and method')
    events,person_years=counts.get('events'),counts.get('person_years')
    if isinstance(events,bool) or not isinstance(events,int) or events<0:
        raise ValueError('baseline events must be a nonnegative integer')
    if isinstance(person_years,bool) or not isinstance(person_years,(int,float)) or not math.isfinite(person_years) or person_years<=0 or events>person_years:
        raise ValueError('baseline person_years must be finite, positive and at least events')
    baseline=baselines['all_cause_mortality_annual']
    if baseline.status!='verified' or baseline.unit!='deaths_per_person_year':
        raise ValueError('verified annual mortality event/person-time baseline required')
    for key in ('sex','age','years','cause','geography'):
        if not counts.get(key) or counts[key]!=getattr(baseline,key):
            raise ValueError(f'baseline count metadata mismatch: {key}')
    if not math.isclose(events/person_years,baseline.value,abs_tol=5e-7,rel_tol=0):
        raise ValueError('baseline counts do not reproduce the pinned rate within its rounding')
    draws,seed=payload.get('draws',2000),payload.get('seed',1901)
    if isinstance(draws,bool) or not isinstance(draws,int) or not 2<=draws<=100000:
        raise ValueError('draws must be an integer 2-100000')
    if isinstance(seed,bool) or not isinstance(seed,int):
        raise ValueError('seed must be an integer')
    params=select_child_contrast(params,scenario.child_income_quartile,params_dir)
    rng=random.Random(seed+32452843)
    process_rng=random.Random(seed+49979687)

    def outcomes(sampled):
        n=rng.randint(low,high)
        rate=rng.gammavariate(events+.5,1/person_years)
        sampled_baselines={**baselines,'all_cause_mortality_annual':replace(baseline,value=rate)}
        result=compute_counts(sampled,sampled_baselines,replace(scenario,displaced_workers=n),_raw=True)
        values={name:row['point'] for name,row in result['modeled'].items()}
        values.update(sampled_workers=n,sampled_baseline_rate_per_100k=rate*100000)
        mortality=result['modeled'].get('excess_deaths')
        if mortality is not None:
            sensitivity=mortality['persistence_sensitivity']
            values['mortality_no_sustained_excess']=sensitivity['variants']['no_sustained_excess']['point']
            values['mortality_persistence_difference']=sensitivity['source_minus_no_sustained_point']
            p0=1-(1-rate_to_risk(rate))**scenario.exposure_years
            p1=min(1.0,max(0.0,p0+mortality['point']/n)) if n else p0
            exposed=process_rng.binomialvariate(n,p1)
            reference=process_rng.binomialvariate(n,p0)
            values.update(realized_exposed_deaths=exposed,realized_reference_deaths=reference,
                          realized_independent_cohort_difference=exposed-reference)
        return values

    sampled=simulate_many(params,outcomes,draws=draws,seed=seed,nodes=nodes,params_dir=params_dir)
    intervals=sampled.pop('outcomes')
    inputs={key:intervals.pop(key) for key in ('sampled_workers','sampled_baseline_rate_per_100k')}
    realized={key:intervals.pop(key) for key in tuple(intervals) if key.startswith('realized_')}
    return {'schema':'downstream-uncertainty-budget/1','eligible_for_public_headline':False,
            'input':payload,'sampling':sampled,'sampled_inputs':inputs,
            'sampled_input_units':{'sampled_workers':'workers','sampled_baseline_rate_per_100k':'events per 100000 person-years'},
            'expected_effect_intervals_90':intervals,'process_intervals_90':realized,
            'fixed_input_reference':sample_counts(params,baselines,scenario,draws=draws,seed=seed,nodes=nodes,params_dir=params_dir),
            'included':['published parameter distributions','documented baseline count likelihood',
                        'declared integer exposure distribution','binomial variation for independent reference and exposed cohorts'],
            'baseline_model':'Poisson counts conditional on person-time; Jeffreys rate prior gives Gamma(events+0.5, rate=person_years). Prior choice is declared.',
            'exposure_model':'User-declared discrete uniform over the supplied count bounds, not an inferred confidence distribution.',
            'dependence':'Parameter correlations retain their declared sampler; baseline, exposure and study parameters are assumed independent. Mortality structures share the same draw.',
            'excluded':['target-population transport error','structural model probabilities','unmodeled pathways',
                        'baseline age/time trends','uncertainty in child structure and lifetime earnings profile'],
            'interpretation':'Central 90% simulation intervals under the stated inputs and independence assumptions; process contrasts compare independent cohorts, not paired individual causal effects.'}
