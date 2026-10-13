"""Build a hypothetical event cohort from pinned CPS reference composition.

Interview age is used as the onset age of a *hypothetical new event*, never
as an assertion about age at the historical displacement. No policy exposure
or H-1B target composition is inferred.
"""
from collections import defaultdict
import json
from pathlib import Path
from zipfile import ZipFile

from build_displaced_cohort import decode, ROOT
from downstream.mortality_strata import project_mortality_cohort


def main():
    counts=defaultdict(float)
    with ZipFile(ROOT/'data/followthrough/jan24pub.zip') as archive, archive.open('jan24pub.dat') as handle:
        for line in handle:
            row=decode(line.decode('ascii'))
            if row['PRDISPWK']==1 and row['PESD3'] in (1,2,3) and row['PTSD18TN']>=600 and row['PWSUPWGT']>0:
                counts[(row['PESEX'],row['PRTAGE'])]+=row['PWSUPWGT']/10000
    total=sum(counts.values())
    payload={'source':'CPS January 2024; validation/followthrough_sources.json',
             'method':'Normalize weighted known-year displaced workers with lost-job tenure >=6 to 1000 hypothetical exposures; preserve single interview ages and sex.',
             'transport_rationale':'Illustrative hypothetical onset-age composition only; interview age is not historical displacement age. Six-year tenure is a proxy for, not proof of, the source stable-employment history. Not an H-1B cohort.',
             'projection_assumption':'constant_source_window_log_odds','follow_up_years':20,
             'strata':[{'sex':{1:'Male',2:'Female'}[sex],'age_at_event':age,'workers':1000*w/total,
                        'tenure_years':6,'exposure_type':'mass layoff'}
                       for (sex,age),w in sorted(counts.items())]}
    result=project_mortality_cohort(payload)
    for filename,value in [('cps2024_hypothetical_mortality_input.json',payload),
                           ('cps2024_hypothetical_mortality_result.json',result)]:
        with (ROOT/'validation'/filename).open('x') as handle:
            json.dump(value,handle,indent=2,allow_nan=False)
            handle.write('\n')
    print(json.dumps({k:result[k] for k in ('total_workers','covered_workers','unmodeled_workers','covered_expected_excess_deaths','whole_cohort_excess_deaths')}))


if __name__=='__main__':
    main()
