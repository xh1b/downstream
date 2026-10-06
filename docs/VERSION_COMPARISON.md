# Comparing versions

`downstream compare` reads saved JSON results. It does not recompute either
version with the current engine: run each version's own engine with identical
inputs, then compare its outputs. This captures changes to both code and data.
The comparator needs no installed parameter data for the versions being compared.

## One result or source parameter snapshot

Save a calculation with the older version, then the same command with the
newer version. For example, use `downstream family > family-before.json` and
`downstream family > family-after.json` in the respective environments.
For source estimates use `downstream export` instead.

```sh
downstream compare --before family-before.json --after family-after.json \
  --before-label v1 --after-label v2
downstream compare --before family-before.json --after family-after.json \
  --format csv --out comparison.csv
downstream compare --before family-before.json --after family-after.json \
  --format json --out comparison.json
```

All fields appear by default. `--changes-only` omits unchanged fields.
Changed, added, and removed fields are shown in full without a row limit.
`--out` writes a file instead of printing to standard output.

## A complete saved calculation inventory

Compare directories containing JSON files with matching names. Each filename
identifies a calculation, and every field in each calculation is compared.
Added and removed files become added and removed fields. Keep non-result JSON
files outside these directories.

The PR workflow saves the parameter snapshot, family vignette, scenarios for
zero, one, and 1,000 displaced workers, validation results, transmission
inventory, analytic grandchild inference, and audit findings. Scenarios use
200 draws and seed 1901. The cohort additionally declares a net loss of 1,000
manufacturing tradable jobs. Both versions run the same commands with default
national geography and documented default assumptions. This is a reproducible
review fixture; it does not enumerate every possible input, geography, policy,
or Monte Carlo configuration. Add saved JSON outputs to compare other cases.

```sh
downstream compare --before results-before/ --after results-after/ \
  --before-label old-commit --after-label new-commit \
  --format json --out comparison.json
```

For two tags or commits on GitHub, run the **model comparison** workflow
manually and supply `before_ref` and `after_ref`. The artifacts include exact
commit SHAs and raw snapshots. Workflow files must first be available on the
default branch. Historical versions must support the fixture commands;
unsupported commands fail visibly rather than producing an empty comparison.

## Reading the report

Fields use escaped JSON-pointer paths, for example
`/family/worker_stream/earnings/point`. Lists of records are keyed by stable identifiers
(`link`, `key`, `outcome`, `name`, `id`, `label`, or `profile_id`), so reordering
parameters does not look like a numerical change. Repeated outcomes use a
qualifier such as exposure to distinguish separate calculations when possible.
Duplicate parameter links, keys, or IDs fail instead of silently overwriting
rows. Lists without unique names or supported qualifiers use positional indexes;
reordered unnamed lists can therefore produce positional changes.

- **Changed:** the value or type differs.
- **Added / removed:** the field exists in only one version.
- **Unchanged:** the values match exactly, with equivalent numeric int/float values.
- **Delta:** after minus before for numeric values; booleans are not numbers.
- **Percent change:** `100 × delta / abs(before)`; undefined for a zero baseline.

No rounding or tolerance hides small numerical differences. Null remains an
explicit unknown value; field status distinguishes null from a missing field.
Non-finite values and numerical difference overflows fail comparison. Units,
citations, inputs, uncertainty, schema fields, and provenance remain visible
alongside calculated values. Interpret deltas together with any changed units
or assumptions; a numerical delta alone does not establish scientific agreement.

Versions and content hashes can change while outputs remain equal. Differences
in seeded intervals can also reflect changes in a sampler's draw sequence.
The report is an inspection tool: meaningful changes require review, not an
automatic assumption that all values should stay identical.
