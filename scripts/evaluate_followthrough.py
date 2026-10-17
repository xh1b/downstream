# @ref:script-evaluate-followthrough
# Method: @link:doc-scenario-evidence-protocol.
# Implementation: @link:code-params; @link:code-synthesis; @link:code-validate.
# @tag:validation
"""Publish all available checks and explicit independent-event refusals."""
from collections import defaultdict
import argparse
import hashlib
import json
from pathlib import Path

from downstream.params import load_all, default_dir
from downstream.synthesis import load_study_estimates, synthesize
from downstream.validate import run

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=ROOT/'validation/followthrough_evaluation.json')
    args=parser.parse_args()
    protocol=ROOT/'docs/research/scenario_evidence_protocol.md'
    cohort=json.loads((ROOT/'validation/cps2024_displaced_cohort.json').read_text())
    sipp=json.loads((ROOT/'validation/sipp/r2_transitions/coverage_and_calibration.json').read_text())
    by_origin=defaultdict(list)
    for row in sipp['calibration']:
        by_origin[row['cell'].split('|')[-1]].append(row['abs_diff'])
    parts=load_all()
    report={'protocol_sha256':hashlib.sha256(protocol.read_bytes()).hexdigest(),
            'parameter_version':parts['params'].version,
            'cohort_reproduction':cohort['published_total_check'],
            'sipp_heldout_baseline':{'coverage':sipp['coverage'],
                'mean_absolute_probability_difference_by_origin':{k:sum(v)/len(v) for k,v in by_origin.items()},
                'interpretation':'Baseline transition calibration, not displacement causal validation.'},
            'evidence_synthesis':synthesize(load_study_estimates(default_dir()/'study_estimates.csv')),
            'existing_validation':run(parts['params']),
            'independent_new_event':{'status':'blocked_no_matched_independent_source',
                'missing':['event-aligned displacement counts and demographic composition',
                           'independent matched outcome estimates and uncertainty',
                           'counterfactual and horizon compatibility for each comparator'],
                'interpretation':'No new causal validation score is invented; prospective execution follows the frozen protocol.'}}
    destination=args.out
    with destination.open('x') as handle:
        json.dump(report,handle,indent=2,allow_nan=False)
        handle.write('\n')
    print(json.dumps({'cohort_check':report['cohort_reproduction']['pass'],
        'pooled_reports':len(report['evidence_synthesis']['reports']),
        'pooling_refusals':len(report['evidence_synthesis']['blocked']),
        'independent_event':report['independent_new_event']['status']}))


if __name__=='__main__':
    main()
