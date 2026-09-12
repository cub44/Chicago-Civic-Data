# Snapshot redactions

Three UIC HTML responses embedded the same client-side Azure Function key for
an emergency-alert banner. The credential was unrelated to the SBHC evidence
and was replaced with `[REDACTED_AZURE_FUNCTION_KEY]` before publication:

- `uic_ag.html`
- `uic_ocean.html`
- `uic_drake_open.html`

No SBHC evidence text was changed. The post-redaction byte counts are recorded
in `manifest.csv`.
