# @ref:script-build-age-mortality
# Method: @link:integration-mortality.
# @tag:mortality
"""Derive age-band mortality counts/rates from the pinned national WONDER pull."""
import argparse
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    source = ROOT / 'validation/cdc_wonder_d76_national_year_age_sex_1999_2020.xml'
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    provenance = json.loads(source.with_suffix('.provenance.json').read_text())
    if provenance['sha256'] != digest:
        raise ValueError('national mortality source hash mismatch')
    groups = defaultdict(lambda: [0, 0, set()])
    for row in ET.parse(source).findall('.//data-table/r'):
        cells = list(row)
        year, age, sex = [c.get('l') for c in cells[:3]]
        if not year or not 2015 <= int(year) <= 2019:
            continue
        match = re.fullmatch(r'(\d+)-(\d+) years', age or '')
        if match:
            low, high = map(int, match.groups())
        elif age == '85+ years':
            low, high = 85, 120
        else:
            continue
        events, person_years = [int(c.get('v').replace(',', '')) for c in cells[3:5]]
        key = (sex, low, high)
        group = groups[key]
        if year in group[2] or events < 0 or person_years <= 0:
            raise ValueError('invalid or duplicate mortality observation')
        group[0] += events
        group[1] += person_years
        group[2].add(year)
    rows = []
    for (sex, low, high), (events, person_years, years) in sorted(groups.items()):
        if years != set(map(str, range(2015, 2020))):
            raise ValueError('incomplete mortality window')
        rows.append(dict(sex=sex, age_min=low, age_max=high, events=events,
            person_years=person_years, annual_rate=events/person_years, years='2015-2019',
            cause='All causes', geography='US', source_sha256=digest))
    with args.out.open('x', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f'{len(rows)} sex/age baselines')


if __name__ == '__main__':
    main()
