# School-based health center (SBHC) reconciliation input

`sbhc.csv` is the 38-row consolidated SBHC table immediately before the
2026-09-12 field-level reconciliation. It is an input artifact, not a published
processed file. `build_resolved.py` preserves every original column in the audit
output, applies the evidence registry in `resolutions.py`, and writes all three
publication artifacts under `data/processed/`.

`sbhc.csv`, `resolutions.py` and `build_resolved.py` came into this repository
on 2026-09-12 (commit `5f8f3c0`), with the three sheets they build. AI agents
had produced them outside the repository: `sbhc.csv` joins the four lists pulled
on 2026-09-11, and `resolutions.py` records the agents' findings of 2026-09-12
(see `data/README.md`). `sbhc.csv` was recovered mechanically from the leading
columns of the agents' `sbhc_resolved.csv`, which carried every input column
unchanged ahead of the new ones, and running the agents' generator against it
reproduced all three sheets byte for byte before this repository's paths and
schema were applied. Every change since is in this repository's history.

It still carries three columns that no processed sheet publishes:
`cps_status_2025`, `cps_adjusted_su` and `cps_colo`. They came from the
`cps_schools_geojson_2025` file named in each row's `source`, an older Chicago
Public Schools (CPS) vintage than the SY2026 workbook behind `utilization.csv`,
and they disagree with it for five host schools. Use `utilization.csv` for space-use status. The
retired `manually_verified` column is likewise kept here and published nowhere.

# SBHC evidence manifest

`evidence_manifest.csv` lists the 38 sources the reconciliation consulted, one
row each; it cites 36 of them, all but `cps_resources` and `cps_staff`. The
columns are `source_key` (the key `resolutions.py` uses), `requested_url`,
`final_url`, `accessed`, `content_type`, `bytes`, the `sha256` of the capture,
and a `note` where the capture needs one. The captures are third-party pages and documents; they are preserved
privately and not republished. `snapshot_sources.py --verify DIR` checks a
capture directory against this file.
