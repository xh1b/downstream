# @ref:code-source-contrasts
# Contract: @link:source-repair-contract. Verification: @link:test-source-repairs.
# @tag:evidence
"""Explicit source-scale contrasts for corrected, separately typed inputs."""
from __future__ import annotations

from copy import deepcopy
import math

from .source_support import policy, require_supported


def source_contrast(params, nodes, payload):
    """Evaluate a source contrast without admitting target transport or totals.

    Inputs identify the node AND unit, so a dollar shock cannot silently become
    penetration points, euros or an absolute female/male wage-ratio change.
    Fixed study contrasts accept dose=1 only: it is not a count of people.
    """
    fields = {'link', 'input_node', 'input_unit', 'dose'}
    if not isinstance(payload, dict) or set(payload) != fields:
        raise ValueError('source contrast requires exactly link, input_node, input_unit, dose')
    if any(not isinstance(payload[k], str) for k in fields - {'dose'}):
        raise ValueError('source contrast link, input_node and input_unit must be strings')
    link = payload['link']
    require_supported(link)
    review = next((r for r in policy()['individual_review'].values()
                   if r.get('disposition') == 'corrected_replacement'
                   and r['available_link'] == link), None)
    if review is None:
        raise ValueError('source-contrast accepts only the corrected, typed source links')
    param = params.by_link(link)
    if (param.from_node != review['input_node'] or param.to_node != review['output_node']
            or nodes[param.from_node].unit != review['input_unit']
            or nodes[param.to_node].unit != review['output_unit']
            or any(getattr(param, k) != v for k,v in review['verified_parameter'].items())
            or param.citation != review['source_key']):
        raise ValueError('source contrast requires reviewed source coefficients and node/unit definitions')
    if payload['input_node'] != param.from_node or payload['input_unit'] != nodes[param.from_node].unit:
        raise ValueError('source contrast input node/unit must match the source-specific exposure')
    dose = payload['dose']
    if isinstance(dose, bool) or not isinstance(dose, (int, float)):
        raise ValueError('source contrast dose must be finite')
    try:
        finite = math.isfinite(dose)
    except OverflowError:
        finite = False
    if not finite:
        raise ValueError('source contrast dose must be finite')
    if review['application'] == 'fixed_contrast' and dose != 1:
        raise ValueError('this source is a fixed exposed-versus-comparison contrast: dose must be 1, not a population count')
    values = [dose*x for x in (param.point, param.low, param.high)]
    if not all(math.isfinite(x) for x in values):
        raise ValueError('source contrast must be finite')
    point, low, high = values[0], min(values[1:]), max(values[1:])
    unit = nodes[param.to_node].unit
    if unit == 'percentage_point_delta' and max(abs(low), abs(high), abs(point)) > 100:
        raise ValueError('source contrast exceeds the possible percentage-point change')
    result = {
        'schema': 'downstream-source-contrast/1', 'parameter_set_version': params.version,
        'input': deepcopy(payload), 'output_node': param.to_node,
        'effect': {'point': point, 'low': low, 'high': high, 'unit': unit},
        'population_scope': param.population_scope, 'method': param.notes,
        'source': deepcopy(policy()['reviewed_sources'][review['source_key']]),
        'eligible_for_public_headline': False,
        'limitations': [
            'Source-population contrast; target transport and policy-to-exposure mapping are not identified.',
            'Coefficient support only; no exposure, baseline or transport error distribution is included.',
            'No aggregate attributable count, cross-stream sum or intergenerational composition.',
        ],
    }
    if unit == 'log_delta':
        try:
            ratios = [math.exp(x) for x in (point, low, high)]
            percentages = [100*math.expm1(x) for x in (point, low, high)]
        except OverflowError as exc:
            raise ValueError('source log contrast cannot be represented as a finite ratio') from exc
        if not all(math.isfinite(x) and x > 0 for x in ratios) or not all(math.isfinite(x) for x in percentages):
            raise ValueError('source log contrast cannot be represented as a finite ratio')
        result['rate_ratio'] = dict(zip(('point', 'low', 'high'), ratios))
        result['percent_change'] = dict(zip(('point', 'low', 'high'), percentages))
    return result
