"""Exact age-stratum scenarios with sourced responses and explicit projection.

The Table 7 annual-logit contrasts are averaged over a source follow-up
window. Applying one constant response to every projected year is declared
here, never confused with the default Table 5 source-offset profile.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

from .mortality import odds_risk, rate_to_risk
from .params import default_dir
from .study_library import load_library


def project_mortality_cohort(payload: dict, params_dir: Path | None = None) -> dict:
    required = ('source', 'method', 'transport_rationale')
    if any(not isinstance(payload.get(k), str) or not payload[k].strip() for k in required):
        raise ValueError('cohort needs source, method and transport_rationale')
    if payload.get('projection_assumption') != 'constant_source_window_log_odds':
        raise ValueError('explicit constant_source_window_log_odds projection assumption required')
    years = payload.get('follow_up_years')
    if isinstance(years, bool) or not isinstance(years, int) or not 0 <= years <= 22:
        raise ValueError('follow_up_years must be an integer from 0 to 22')
    strata = payload.get('strata')
    if not isinstance(strata, list) or not strata:
        raise ValueError('nonempty cohort strata required')
    directory = params_dir or default_dir()
    with (directory / 'age_mortality.csv').open(newline='') as handle:
        baselines = list(csv.DictReader(handle))
    for b in baselines:
        events, person_years, rate = (float(b[k]) for k in ('events','person_years','annual_rate'))
        if (not all(math.isfinite(x) for x in (events,person_years,rate)) or
                not 0 <= events <= person_years or person_years <= 0 or
                not math.isclose(rate, events/person_years, rel_tol=1e-12) or
                (b['years'],b['cause'],b['geography']) != ('2015-2019','All causes','US')):
            raise ValueError('incompatible or arithmetically invalid mortality baseline')
    library = load_library(directory / 'study_estimates.csv')
    supported, unsupported = [], []
    total = covered = 0.0
    for index, row in enumerate(strata):
        if not isinstance(row, dict):
            raise ValueError('cohort stratum must be an object')
        age, workers, tenure = (row.get(k) for k in ('age_at_event', 'workers', 'tenure_years'))
        if isinstance(age, bool) or not isinstance(age, int) or not 20 <= age <= 100:
            raise ValueError('age_at_event must be an integer 20-100')
        for value in (workers, tenure):
            if isinstance(value, bool) or not isinstance(value, (int,float)) or not math.isfinite(value) or value < 0:
                raise ValueError('worker exposure and tenure must be finite nonnegative numbers')
        if row.get('sex') not in ('Male','Female','Unknown'):
            raise ValueError('sex must be Male, Female or Unknown')
        total += workers
        if not math.isfinite(total):
            raise ValueError('cohort exposure overflows')
        if row['sex'] != 'Male' or not 30 <= age <= 69 or tenure < 6 or row.get('exposure_type') not in ('mass layoff','firm closure'):
            unsupported.append({'stratum':index,'workers':workers,'reason':'no compatible source mortality response'})
            continue
        low = age // 10 * 10
        source = library[f'sullivan2007_age_{low}_{low+9}']

        def baseline_for(attained_age):
            matches = [b for b in baselines if b['sex']==row['sex'] and int(b['age_min'])<=attained_age<=int(b['age_max'])]
            if len(matches)!=1:
                raise ValueError('attained age lacks one verified baseline')
            return matches[0]

        def evaluate(aging):
            rows = [baseline_for(age + t if aging else age) for t in range(years)]
            risks = [rate_to_risk(float(b['annual_rate'])) for b in rows]
            contrast = []
            for z in (0,-1.96,1.96):
                odds = math.exp(source['point']+z*source['standard_error'])
                reference = math.prod(1-b for b in risks)
                exposed = math.prod(1-odds_risk(b,odds) for b in risks)
                contrast.append(workers*(reference-exposed))
            return {'point':contrast[0],'low':min(contrast),'high':max(contrast),
                    'annual_baseline_rates':[float(b['annual_rate']) for b in rows]}

        supported.append({'stratum':index,'workers':workers,'age_at_event':age,
                          'source_contrast':source,'aging_bands':evaluate(True),
                          'fixed_baseline':evaluate(False)})
        covered += workers
    totals = {mode:{bound:sum(r[mode][bound] for r in supported) for bound in ('point','low','high')}
              for mode in ('aging_bands','fixed_baseline')}
    return {'schema':'downstream-stratified-mortality/1','eligible_for_public_headline':False,
            'input':payload,'total_workers':total,'covered_workers':covered,
            'unmodeled_workers':sum(r['workers'] for r in unsupported),
            'covered_expected_excess_deaths':totals,
            'whole_cohort_excess_deaths':None if any(r['workers']>0 for r in unsupported) else totals,
            'supported_strata':supported,'unsupported_strata':unsupported,
            'uncertainty':{'band':'simultaneous coefficient-support envelope, not a cohort confidence interval',
                'fixed':['exposure','age composition','baseline rates','transport','constant response shape'],
                'excluded':['baseline sampling variance','exposure error','cross-coefficient covariance','transport error']},
            'limitations':['Exact weighted stratum aggregation; individual sampling is unnecessary for this expected total.',
                'Aging uses piecewise age-band 2015-2019 period rates, not single-age hazards or a forecast of future mortality trends.',
                'Source age is age at displacement; the response is held fixed as survivors age.',
                'Source-window annual logit contrasts are projected constantly by explicit assumption, not a recovered phase-specific effect.',
                'Unmodeled strata are unknown, never zero or silently omitted from a whole-cohort total.']}
