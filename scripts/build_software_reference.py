#!/usr/bin/env python3
# @ref:script-software-reference
# Method: @link:doc-integration; @link:development-tooling.
# Implementation: @link:code-cli; @link:code-scenario.
# Verification: @link:test-documentation-checks.
# @tag:tooling
"""Render the software reference from the actual parser, signatures and input fields."""
from __future__ import annotations

import argparse
from dataclasses import MISSING, fields
import inspect
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
START = "<!-- BEGIN GENERATED SOFTWARE REFERENCE -->"
END = "<!-- END GENERATED SOFTWARE REFERENCE -->"


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def render():
    from downstream.child_gap_view import child_gap_view
    from downstream.child_support import child_support_report
    from downstream.consumer import scale_outcome, mix_expected
    from downstream.household import household_comparison
    from downstream.mortality_strata import project_mortality_cohort
    from downstream.receiving_community import receiving_comparison
    from downstream.cli import build_parser
    from downstream.employer import DocumentedExposure, compute_entity_counts
    from downstream.params import load_all
    from downstream.scenario import ScenarioInput, compute_counts, sample_counts

    parser = build_parser()
    commands = next(a for a in parser._actions if isinstance(a, argparse._SubParsersAction))
    descriptions = {a.dest: a.help for a in commands._choices_actions}
    lines = ["## Command reference", "",
             f"<!-- {'@'}ref:integration-command-reference -->", "",
             "Generated from the running CLI parser. Use `downstream <command> --help`",
             "for required arguments, option choices and defaults. This table is an",
             "inventory of commands, not a statement that every command returns the",
             "scenario result shape below.", "",
             "| Command | Parser description |", "| --- | --- |"]
    lines.extend(f"| `{cell(name)}` | {cell(descriptions[name])} |" for name in commands.choices)
    lines += ["", "### Python calling signatures", "",
              "These signatures are inspected from the implementation. The APIs do not",
              "silently accept every JSON field; use the appropriate input record.", "",
              "```python"]
    for function in (load_all, compute_counts, sample_counts, compute_entity_counts,
                     child_gap_view, child_support_report, household_comparison,
                     project_mortality_cohort, receiving_comparison, scale_outcome, mix_expected):
        lines.append(f"def {function.__name__}{inspect.signature(function)}: ...")
    lines += ["```", "", "### Scenario input fields", "",
              "`ScenarioInput` accepts the fields below. Defaults describe a reference",
              "scenario; they are not observed target data. Types and validation are",
              "defined by [scenario.py](../src/downstream/scenario.py).", "",
              "| Field | Declared type | Default |", "| --- | --- | --- |"]
    for field in fields(ScenarioInput):
        default = "required" if field.default is MISSING else repr(field.default)
        lines.append(f"| `{field.name}` | `{cell(field.type)}` | `{cell(default)}` |")
    required = [f.name for f in fields(DocumentedExposure) if f.default is MISSING and f.default_factory is MISSING]
    lines += ["", "`DocumentedExposure` requires " + ", ".join(f"`{name}`" for name in required) + ".",
              "See [exposure metadata](#exposure-and-event-metadata) for normalized",
              "semantics and [warehouse inputs](#warehouse-inputs) for that separate adapter."]
    return "\n".join(lines) + "\n"


def replace_reference(text, reference):
    if text.count(START) != 1 or text.count(END) != 1 or text.index(START) >= text.index(END):
        raise ValueError("software reference needs one ordered marker pair")
    before, tail = text.split(START)
    _, after = tail.split(END)
    return before + START + "\n\n" + reference.rstrip() + "\n\n" + END + after


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/integration.md")
    args = parser.parse_args(argv)
    old = args.output.read_text()
    new = replace_reference(old, render())
    if args.check and old != new:
        print(f"stale software reference: {args.output}", file=sys.stderr)
        return 1
    if not args.check and old != new:
        args.output.write_text(new)
    print(f"current software reference: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
