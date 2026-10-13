"""Annual household-resource scenarios using observed SIPP baseline transitions.

This is an exact state-probability calculation. Forcing unemployment for a
supplied duration is a scenario assumption; observational U-origin recovery
is not an identified causal job-finding response to displacement.
"""
from __future__ import annotations

import csv
import hashlib
import math

from .params import default_dir

STATES = ('E','U','N')


def household_comparison(payload, params_dir=None):
    if payload.get('transition_assumption') != 'reuse_2021_2022_conditional_transitions':
        raise ValueError('explicit baseline transition reuse assumption required')
    years = payload.get('follow_up_years')
    if isinstance(years,bool) or not isinstance(years,int) or not 1 <= years <= 5:
        raise ValueError('household follow_up_years must be an integer 1-5')
    event = payload.get('event',{})
    duration = event.get('unemployed_years')
    if event.get('kind') != 'involuntary_displacement' or isinstance(duration,bool) or not isinstance(duration,int) or not 0 <= duration <= years:
        raise ValueError('displacement requires a supplied integer unemployment duration within follow-up')
    members = payload.get('members')
    if not isinstance(members,list) or not members:
        raise ValueError('household members required')
    ids = [p.get('id') for p in members]
    if any(not isinstance(i,str) or not i for i in ids) or len(set(ids)) != len(ids) or event.get('member_id') not in ids:
        raise ValueError('unique household member IDs and an existing event member required')
    for p in members:
        if (p.get('sex') not in ('male','female') or isinstance(p.get('age'),bool) or
                not isinstance(p.get('age'),int) or not 25 <= p['age'] <= 55-years or
                p.get('employment_state') not in STATES):
            raise ValueError('each member needs sex, supported ages throughout follow-up, and E/U/N state')
        earnings=p.get('annual_earnings_if_employed_usd_2024')
        if isinstance(earnings,bool) or not isinstance(earnings,(int,float)) or not math.isfinite(earnings) or earnings < 0:
            raise ValueError('finite nonnegative supplied annual earnings required')
    if next(p for p in members if p['id']==event['member_id'])['employment_state'] != 'E':
        raise ValueError('displacement must start from an employed reference member')
    scars = event.get('reemployment_earnings_multipliers',[1.0]*years)
    if (not isinstance(scars,list) or len(scars)!=years or any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or x<0 for x in scars)):
        raise ValueError('reemployment multipliers must supply one finite nonnegative value per year')
    if 'reemployment_earnings_multipliers' in event and not event.get('earnings_path_assumption'):
        raise ValueError('supplied earnings scars require earnings_path_assumption')
    children = payload.get('children',[])
    if not isinstance(children,list) or any(isinstance(a,bool) or not isinstance(a,int) or not 0 <= a <= 24 for a in children):
        raise ValueError('children must be a list of initial ages 0-24')
    source = (params_dir or default_dir()) / 'baseline_employment_transitions.csv'
    cells = {}
    with source.open(newline='') as handle:
        for row in csv.DictReader(handle):
            if row['sex']=='all' or row['age_band']=='all':
                continue
            probabilities=[float(row[f'to_{s}']) for s in STATES]
            if any(not math.isfinite(p) or p<0 or p>1 for p in probabilities) or not math.isclose(sum(probabilities),1,abs_tol=2e-6):
                raise ValueError('invalid baseline transition probability row')
            key=(row['sex'],row['age_band'],row['origin'])
            if key in cells:
                raise ValueError('duplicate baseline transition cell')
            cells[key]=(dict(zip(STATES,(p/sum(probabilities) for p in probabilities))),int(row['n_persons']))
    vectors={arm:{p['id']:{s:float(s==p['employment_state']) for s in STATES} for p in members}
             for arm in ('reference','displacement')}
    if duration:
        vectors['displacement'][event['member_id']]={'E':0.0,'U':1.0,'N':0.0}
    used={}
    rows=[]
    for year in range(years):
        row={'year_after_event':year,'children_ages':[a+year for a in children]}
        for arm in vectors:
            adults=[]
            for p in members:
                vector=vectors[arm][p['id']]
                multiplier=scars[year] if arm=='displacement' and p['id']==event['member_id'] else 1
                earnings=vector['E']*p['annual_earnings_if_employed_usd_2024']*multiplier
                adults.append({'id':p['id'],'age':p['age']+year,'state_probabilities':dict(vector),
                               'expected_earnings_usd_2024':earnings})
                if year+1<years:
                    age=p['age']+year
                    band='25-34' if age<35 else '35-44' if age<45 else '45-54'
                    next_vector=dict.fromkeys(STATES,0.0)
                    for origin,share in vector.items():
                        if share==0:
                            continue
                        key=(p['sex'],band,origin)
                        if key not in cells:
                            raise ValueError('missing baseline transition cell')
                        probabilities,n=cells[key]
                        used['|'.join(key)]=n
                        if n<30 and payload.get('allow_sparse_cells') is not True:
                            raise ValueError('sparse transition cell requires explicit allow_sparse_cells=true')
                        for destination,probability in probabilities.items():
                            next_vector[destination]+=share*probability
                    if arm=='displacement' and p['id']==event['member_id'] and year+1<duration:
                        next_vector={'E':0.0,'U':1.0,'N':0.0}
                    vectors[arm][p['id']]=next_vector
            row[arm]={'adults':adults,'expected_earnings_usd_2024':sum(a['expected_earnings_usd_2024'] for a in adults)}
        row['displacement_minus_reference']=row['displacement']['expected_earnings_usd_2024']-row['reference']['expected_earnings_usd_2024']
        rows.append(row)
    cumulative=sum(r['displacement_minus_reference'] for r in rows)
    if not math.isfinite(cumulative):
        raise ValueError('household earnings overflow')
    return {'schema':'downstream-household-comparison/1','eligible_for_public_headline':False,
            'input':payload,'annual':rows,'cumulative_earnings_difference_usd_2024':cumulative,
            'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'used_transition_cells_n':used,'sparse_cells':[k for k,n in used.items() if n<30],
            'uncertainty':{'intervals':None,'reason':'Sparse conditional cells and survey design variance need replicate-weight estimation; no full household prediction interval is claimed.'},
            'limitations':['Forced unemployment duration and any earnings scars are supplied scenario assumptions, not causal estimates from SIPP.',
                'Baseline transitions are observed December-to-December 2021-2022 conditional shares, normalized only for stored rounding; reuse over five years assumes stationarity and a Markov process.',
                'Recovery among observationally unemployed people may not transport to displaced workers.',
                'Household resources here are gross earnings only; taxes, transfers, savings, marriage, fertility and protective interventions remain unmodeled.',
                'Partner marginal expectations can be summed without identifying a joint distribution; cross-member dependence and responses are not estimated.',
                'Children age but no educational or earnings effect is inferred from this household baseline.']}
