# @ref:code-uncertainty-cases
# Rationale: @link:paper-uncertainty-budget.
# Software contract: @link:uncertainty-assumption-cases.
# Verification: @link:test-uncertainty-cases.
# @tag:uncertainty
"""Unweighted mortality transport and dependence experiments on shared draws."""
from __future__ import annotations

from copy import deepcopy
import math

from .mortality import excess_deaths_profile, rate_to_risk


def validate_cases(cases):
    """Require explicit assumptions and provenance; never supply case weights."""
    if not isinstance(cases, list) or not 1 <= len(cases) <= 16:
        raise ValueError('assumption_cases must contain 1-16 explicit cases')
    names = set()
    fields = {'name', 'mortality_log_odds_scale', 'exposure_rank', 'baseline_rank', 'source', 'method'}
    for case in cases:
        if not isinstance(case, dict) or set(case) != fields:
            raise ValueError('each assumption case requires exactly ' + ', '.join(sorted(fields)))
        for key in ('name', 'source', 'method'):
            if not isinstance(case[key], str) or not case[key].strip():
                raise ValueError(f'assumption case {key} must be a nonempty string')
        if case['name'] in names:
            raise ValueError('assumption case names must be unique')
        names.add(case['name'])
        scale = case['mortality_log_odds_scale']
        if isinstance(scale, bool) or not isinstance(scale, (int, float)) or not math.isfinite(scale):
            raise ValueError('mortality_log_odds_scale must be finite')
        for key in ('exposure_rank', 'baseline_rank'):
            if case[key] not in ('independent', 'aligned', 'opposed'):
                raise ValueError(f'{key} must be independent, aligned or opposed')


def _summary(values):
    if not all(math.isfinite(value) for value in values):
        raise ValueError('assumption case outcomes must be finite')
    ordered = sorted(values)
    return {key: round(ordered[int(p * (len(ordered)-1))], 4)
            for key, p in (('p05', .05), ('p50', .5), ('p95', .95))} | {
                'mean': round(math.fsum(values) / len(values), 4)}


def pair_by_rank(values, anchors, direction):
    """Reorder only an auxiliary marginal; keep every study vector intact."""
    if direction == 'independent':
        return list(values)
    if len(set(anchors)) == 1:
        raise ValueError('aligned/opposed cases require a nonconstant source-effect anchor')
    order = sorted(range(len(anchors)), key=lambda i: (anchors[i], i))
    ordered = sorted(values, reverse=direction == 'opposed')
    result = [0.0] * len(values)
    for index, value in zip(order, ordered):
        result[index] = value
    return result


def evaluate_cases(cases, records, scenario, baseline):
    """Keep separate conditional intervals and paired differences for each case.

    Each record retains the mortality profile from one study vector, the original
    independent exposure/rate draws, and the admitted raw mortality result.
    Sorting auxiliary values preserves both marginals and all within-study
    parameter relationships. These arrangements are stress tests, not sharp
    multivariate bounds or estimates of a real target's dependence structure.
    """
    validate_cases(cases)
    profiles = [row[0] for row in records]
    anchors = [excess_deaths_profile(1, rate_to_risk(baseline.value), odds, scenario.exposure_years)
               for odds in profiles]
    workers, rates = [row[1] for row in records], [row[2] for row in records]
    reports = []
    for case in cases:
        ns = pair_by_rank(workers, anchors, case['exposure_rank'])
        rs = pair_by_rank(rates, anchors, case['baseline_rank'])
        source, alternative, reference_difference, structural_difference = [], [], [], []
        for row, odds, n, rate in zip(records, profiles, ns, rs):
            try:
                transported = (dict(odds) if case['mortality_log_odds_scale'] == 1 else
                    {phase: math.exp(case['mortality_log_odds_scale'] * math.log(value))
                     for phase, value in odds.items()})
            except (OverflowError, ValueError) as exc:
                raise ValueError('transported mortality odds must be finite and positive') from exc
            if not all(math.isfinite(value) and value > 0 for value in transported.values()):
                raise ValueError('transported mortality odds must be finite and positive')
            point = excess_deaths_profile(n, rate_to_risk(rate), transported, scenario.exposure_years)
            alternate = excess_deaths_profile(n, rate_to_risk(rate),
                {**transported, 'offset_6_plus': 1.0}, scenario.exposure_years)
            source.append(point)
            alternative.append(alternate)
            structural_difference.append(point-alternate)
            reference_difference.append(point-row[3])
        reports.append({
            'assumption': deepcopy(case), 'eligible_for_public_headline': False,
            'status': 'declared_sensitivity_not_calibrated_target_uncertainty',
            'expected_effect_intervals_90': {
                'excess_deaths': _summary(source),
                'mortality_no_sustained_excess': _summary(alternative),
                'mortality_persistence_difference': _summary(structural_difference),
            },
            'case_minus_independent_source_reference_90': _summary(reference_difference),
            'sampled_inputs': {'sampled_workers': _summary(ns),
                              'sampled_baseline_rate_per_100k': _summary([r*100000 for r in rs])},
        })
    return {
        'scope': 'Mortality only; source profile and no-sustained-excess structure remain separate.',
        'rank_anchor': 'Signed source-profile excess-death probability per worker at the pinned baseline and horizon.',
        'pairing': 'Study parameter vectors stay intact; align/oppose auxiliary ranks with the anchor, breaking anchor ties by original draw index.',
        'transport_rule': 'For every source mortality phase, OR_target = exp(scale * log(OR_source)); scale is a fixed caller declaration, not an estimated distribution.',
        'cases': reports,
        'limitations': [
            'No probabilities, model averages or overall confidence envelope across cases.',
            'Aligned/opposed ranks are selected dependence stress tests, not bounds over all possible joint laws.',
            'Preserved marginal draws do not identify target-population transport or actual dependence.',
            'Paired differences reuse study draw identities; they are not individual causal-effect distributions.',
            'No case-specific process intervals, child transport model or new population admission.',
        ],
    }
