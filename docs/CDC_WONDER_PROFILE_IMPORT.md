# CDC WONDER profile download and import

Use a separate CDC WONDER export for every demographic profile that will
appear in a scenario. A county file is valid only when the exported table is
grouped by **County** alone; sex, age, cause, and years are filters, not
additional group-by columns.

For a profile suitable for this model:

0. Reproducible downloads: `scripts/fetch_wonder.py` performs both pulls —
   `national` (machine XML API, year x age x gender table) and `county`
   (scripted web-UI session; the machine API is national-only by server
   policy, probed 2026-09-13). Each writes the raw artifact plus a
   `.provenance.json` sidecar; `county` also writes the `.metadata.json`
   this importer consumes. The manual steps below document what the
   script automates.
1. In CDC WONDER's *Underlying Cause of Death* query, choose the desired
   years, sex, age range, and cause of death. Use all counties required by
   the XH1B/entity exposure geography.
2. In *Group Results By*, select **County** only. Request **Deaths** and
   **Population**. The population total across selected years is treated as
   person-years; do not substitute a crude-rate column.
3. Download the CSV (the importer also accepts tab-delimited exports) and
   save a sidecar JSON file with `years`, `sex`, `age`, `cause`,
   `group_by: ["County"]`, `population_unit: "person-years"`, `source_url`,
   and `retrieved_at`. Preserve the original file unchanged. Every one of
   these fields is required: the importer refuses undeclared `cause` or
   `population_unit` rather than assuming a silent default, and `years`
   must be a contiguous window so the reported time window is exact.
4. Add a row to `params/mortality_profiles.csv` only after independently
   checking the matching national annual rate and citation. Set `status` to
   `verified`. A `context_only` row cannot produce scenario counts.
5. For county pooling, use `county-wonder-posterior`; its national prior
   must have exactly the same profile and time window as the export. The
   observation outcome id follows the declared cause: `All causes` maps to
   `all_cause_mortality_annual`, and any other cause becomes its own
   `<cause>_mortality_annual` id so an all-cause national prior can never be
   silently fit to cause-specific events. For scenario or entity results,
   select the profile explicitly:

```sh
uv run python -m downstream.cli scenario --workers 1000 \
  --mortality-profile PROFILE_ID

uv run python -m downstream.cli entity --input exposure.json \
  --mortality-profile PROFILE_ID
```

For a known composition, supply an explicit mixture instead of using a
single demographic proxy:

```sh
--mortality-mix female_45_54_2015_2019:0.4,male_45_54_2015_2019:0.6
```

Weights must sum to one, each profile may appear at most once, and every
selected profile must be `verified`. Verified rate rows now exist for both
sexes in the 25-34, 35-44, 45-54, and 55-64 bands (pooled 2015-2019,
`validation/cdc_wonder_d76_national_year_age_sex_1999_2020.xml`), but the
shipped displacement response is an *all-cause* mortality response for male
workers aged 45--54 only: a mixture computation refuses any profile with
another sex, age band, or cause until a separately admitted effect profile
exists. The program reports expected mortality for an admitted mixture and
intentionally withholds the predictive-count interval until
stratum-specific cohort counts are supplied.

The existing `cdc_wonder_county_all_ages_1999_2020.csv` remains context only:
its exported parameter block does not reproduce the filters, so it is not a
verified baseline or an eligible profile row.
