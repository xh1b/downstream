# @ref:test-audit04-sources
# Method: @link:doc-citing.
# Implementation: @link:code-audit; @link:code-params.
# @tag:evidence @tag:testing
"""Primary-table fixtures independently checked in the 2026-10-14 release audit.

NBER w13626 Tables 5/7, Oreopoulos JOLE Tables 2/8, Browning-Heinesen
2011 AKF Tables 6.1/6.2, and SSA Supplement 2025 Table 4.B6.
"""
import hashlib
import json
import math

import pytest

from downstream.params import default_dir, load_all
from downstream.study_library import load_library
from downstream.valuation import SSA_PROFILE


TABLE_FIXTURES = {
    'oreopoulos2008_overall':(-.097,.037),
    'oreopoulos2008_q1':(-.143,.088), 'oreopoulos2008_q2':(-.117,.070),
    'oreopoulos2008_q3':(.007,.065), 'oreopoulos2008_q4':(-.095,.068),
    'sullivan2007_displacement':(.982,.119), 'sullivan2007_offset_1':(.685,.189),
    'sullivan2007_offsets_2_3':(.549,.137), 'sullivan2007_offsets_4_5':(.240,.138),
    'sullivan2007_offset_6_plus':(.127,.048),
    'sullivan2007_age_30_39':(.313,.090), 'sullivan2007_age_40_49':(.266,.058),
    'sullivan2007_age_50_59':(.219,.034), 'sullivan2007_age_60_69':(-.005,.036),
}
BROWNING_CI_FIXTURES = {
    'allcause_1y':(1.84,1.44,2.34), 'allcause_2y':(1.46,1.24,1.72),
    'allcause_3y':(1.38,1.21,1.57), 'allcause_4y':(1.36,1.22,1.51),
    'allcause_10y':(1.17,1.10,1.25), 'allcause_15y':(1.13,1.07,1.19),
    'allcause_20y':(1.10,1.05,1.16), 'cancer_4y':(1.15,.97,1.38),
    'cancer_20y':(1.03,.96,1.11),
}


@pytest.mark.parametrize('key,values', TABLE_FIXTURES.items())
def test_source_log_coefficients_and_reported_standard_errors(key,values):
    row=load_library()[key]
    assert (row['point'],row['standard_error'])==values
    assert row['standard_error_method']=='reported standard error'


@pytest.mark.parametrize('suffix,values',BROWNING_CI_FIXTURES.items())
def test_cumulative_hazards_keep_the_reported_scale_and_approximation(suffix,values):
    point,low,high=values
    row=load_library()['browning2011_'+suffix]
    assert row['point']==pytest.approx(math.log(point),abs=1e-15)
    assert row['standard_error']==pytest.approx((math.log(high)-math.log(low))/3.92,abs=1e-15)
    assert row['scale']=='log_cumulative_hazard_ratio'
    assert 'approximate' in row['standard_error_method']
    assert '2011 AKF' in row['source_locator']


def test_every_source_contrast_hash_matches_the_acquisition_manifest():
    rows=load_library()
    manifest=json.loads((default_dir().parent/'validation/followthrough_sources.json').read_text())
    by_hash={row['sha256']:row for row in manifest['sources'].values()}
    assert set(rows)==set(TABLE_FIXTURES)|{'browning2011_'+key for key in BROWNING_CI_FIXTURES}
    for row in rows.values():
        record=by_hash[row['source_sha256']]
        assert row['source_url']==record['url']
    assert len({r['overlap_group'] for r in rows.values()})==3
    # Raw PDFs are cached acquisition data, not distributed package inputs.
    for record in manifest['sources'].values():
        path=default_dir().parent/record['path']
        if path.is_file():assert hashlib.sha256(path.read_bytes()).hexdigest()==record['sha256']


def test_default_mortality_transforms_match_primary_table_with_declared_rounding():
    params=load_all()['params']
    mapping={'displacement':'peak','offset_1':'offset_1','offsets_2_3':'offsets_2_3',
             'offsets_4_5':'offsets_4_5','offset_6_plus':'sustained'}
    for phase,target in mapping.items():
        beta,se=TABLE_FIXTURES['sullivan2007_'+phase]
        row=params.by_link('earnings_shock->mortality_'+target)
        for actual,value in zip((row.point,row.low,row.high),(beta,beta-1.96*se,beta+1.96*se)):
            assert actual==pytest.approx(math.exp(value),abs=.00005)


def test_synthetic_earnings_shape_and_cpi_conversion_reproduce_the_pinned_total():
    assert [r[2] for r in SSA_PROFILE]==[24218,42561,52485,60423,64962,67506,68160,64854,60666,56666]
    total=sum((hi-lo+1)*value for lo,hi,value in SSA_PROFILE)
    assert total==2517175
    assert round(total*313.689/304.702)==load_all()['baselines']['median_male_lifetime_earnings'].value


def test_source_notes_keep_different_estimands_and_null_compatible_findings():
    parts=load_all();params=parts['params']
    sustained=params.by_link('earnings_shock->mortality_sustained').notes
    assert 'not a like-for-like replication' in sustained and 'near-exact long-run replication' not in sustained
    assert 'compatible with the null' in sustained
    assert 'MI-or-stroke 1-20y 1.09 [0.97, 1.23]' in params.by_link('displacement->circulatory_mortality_hazard').notes
    assert 'Canadian -9.2%' in params.by_link('displacement->child_earnings').notes
    for row in params.parameters:
        if row.citation=='browningheinesen2012':
            assert '2011 AKF working paper' in row.notes
            assert 'Read from the published JHE version of record' not in row.notes
