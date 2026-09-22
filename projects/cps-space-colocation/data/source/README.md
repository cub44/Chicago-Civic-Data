# SBHC reconciliation input

`sbhc.csv` is the 38-row consolidated SBHC table immediately before the
2026-09-12 field-level reconciliation. It is an input artifact, not a published
processed file. `build_resolved.py` preserves every original column in the audit
output, applies the evidence registry in `resolutions.py`, and writes all three
publication artifacts under `data/processed/`.

The input was recovered mechanically from the original-column prefix of the
supplied `sbhc_resolved.csv` audit artifact. Re-running the supplied generator
against it reproduced all three supplied CSVs byte-for-byte before repository
path and schema changes were applied.

It still carries three columns that no processed sheet publishes:
`cps_status_2025`, `cps_adjusted_su` and `cps_colo`. They came from the
`cps_schools_geojson_2025` file named in each row's `source`, an older CPS
vintage than the SY2026 workbook behind `utilization.csv`, and they disagree
with it for five host schools. Use `utilization.csv` for space-use status. The
retired `manually_verified` column is likewise kept here and published nowhere.

# SBHC evidence manifest

`evidence_manifest.csv` lists the 38 sources the reconciliation cites, one row
each: `source_key` (the key `resolutions.py` uses), `requested_url`,
`final_url`, `accessed`, `content_type`, `bytes` and the `sha256` of the
capture. The captures are third-party pages and documents; they are preserved
privately and not republished. `snapshot_sources.py --verify DIR` checks a
capture directory against this file.
