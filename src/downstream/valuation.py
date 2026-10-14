"""Explicit real-dollar discounting of the existing synthetic earnings profile."""
from __future__ import annotations

import math


# The same SSA 4.B6 age-band medians used in baselines.csv, in 2023 dollars.
SSA_PROFILE = ((20,24,24218),(25,29,42561),(30,34,52485),(35,39,60423),
               (40,44,64962),(45,49,67506),(50,54,68160),(55,59,64854),
               (60,61,60666),(62,64,56666))


def child_valuation(ledger, baseline, workers, profiles, real_rate, valuation_year):
    if not isinstance(profiles,list) or any(p['age_at_displacement'] is None for p in profiles):
        raise ValueError('child valuation requires known ages at the event')
    annual = [(age,value) for low,high,value in SSA_PROFILE for age in range(low,high+1)]
    # Normalize the published profile to the rounded 2024-dollar baseline;
    # the zero-discount career total then equals the existing count exactly.
    scale = baseline.value / sum(value for _,value in annual)
    results = {}
    for name,age_range in (('constant_career_gap',(20,64)),('observed_adult_age_window',(25,33))):
        undiscounted = discounted = 0.0
        schedules = []
        for child in profiles:
            current_age = child['age_at_displacement']
            schedule = []
            for age,value in annual:
                if not age_range[0] <= age <= age_range[1] or age < current_age:
                    continue
                offset = age-current_age
                amount = value*scale
                try:
                    factor = math.exp(-offset*math.log1p(real_rate))
                except OverflowError as exc:
                    raise ValueError('discounting overflows for this rate and horizon') from exc
                undiscounted += amount
                discounted += amount*factor
                schedule.append({'age':age,'calendar_year':valuation_year+offset,
                                 'baseline_earnings_usd_2024':amount,'discount_factor':factor})
            schedules.append(schedule)
        values = [workers*(1-getattr(ledger,bound))*discounted for bound in ('point','low','high')]
        if not all(math.isfinite(v) for v in values):
            raise ValueError('nonfinite child present value')
        results[name] = {'point':values[0],'low':min(values),'high':max(values),
            'undiscounted_point':workers*(1-ledger.point)*undiscounted,
            'annual_schedules_per_worker_family':schedules,
            'assumption': 'A constant relative earnings gap over the listed ages; the source estimates an adult age-window average, not a full annual causal path.'}
    return {'available':True,'unit':'usd_2024','valuation_year':valuation_year,
            'event_year':valuation_year,'real_discount_rate':real_rate,
            'source':baseline.citation,'baseline_notes':baseline.notes,
            'annual_profile_source':'SSA Annual Statistical Supplement 2025, Table 4.B6; male median earnings by age, 2023 (preliminary); https://www.ssa.gov/policy/docs/statcomps/supplement/2025/4b.html',
            'normalization':'The fixed SSA age-band earnings shape is scaled to the supplied usd_2024 lifetime baseline; a custom lifetime total does not supply a new annual earnings path.',
            'eligible_for_public_headline':False,'projections':results,
            'uncertainty_scope':{'intervals':'Parameter-only, conditional on the selected annual earnings path and real discount rate.',
                'fixed':['discount rate','synthetic career profile','child ages','future survival and employment treatment'],
                'excluded':['annual effect-path identification','earnings-profile uncertainty','transport error']},
            'interpretation':'Real purchasing-power dollars discounted to the event date; the career projection extrapolates beyond observed adult ages. Negative losses represent modeled gains.'}
