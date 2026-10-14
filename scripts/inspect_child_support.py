#!/usr/bin/env python3
"""Print an inspectable existing-source child support report as JSON."""

import argparse
import json
from pathlib import Path
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, help='ScenarioInput JSON; omitted means unknown target')
    parser.add_argument('--params-dir', type=Path, help='custom source-library directory')
    parser.add_argument('--parent-tenure-years', type=float, help='numeric tenure; omitted stays unknown')
    args = parser.parse_args(argv)
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
    from downstream.child_support import child_support_report
    from downstream.scenario import ScenarioInput

    try:
        scenario = ScenarioInput(**json.loads(args.input.read_text())) if args.input else None
        report = child_support_report(scenario, params_dir=args.params_dir,
                                      parent_tenure_years=args.parent_tenure_years)
    except (ValueError, TypeError, KeyError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
