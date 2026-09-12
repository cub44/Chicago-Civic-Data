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
