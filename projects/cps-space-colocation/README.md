# CPS space and co-location

[Explore the project](https://connorblandford.com/projects/cps-space-colocation/). This is the dataset behind an exploratory map; the accompanying article is forthcoming. It examines school space and potential co-location, not school closures. Snapshot: **9 September 2026**; utilization year: **SY2026**.

## Download

| CSV | Rows | One row represents |
|---|---:|---|
| [schools.csv](data/processed/schools.csv) | 642 | One school |
| [utilization.csv](data/processed/utilization.csv) | 510 | One school in SY2026 |
| [colocation_campuses.csv](data/processed/colocation_campuses.csv) | 16 | One shared campus |

See the [data dictionary](data/README.md) for all fields and caveats. Join schools and utilization using `sid`. Campus totals overlap individual school records: do not add both together. [SHA-256 checksums](checksums.sha256) identify the download versions.

## Sources and method

Inputs are the CPS SY2026 Space Utilization workbook (`spaceuse_2026_final_forweb.xlsx`, published 19 December 2025), the CPS School Profile Information API (`api.cps.edu/schoolprofile/CPS/AllSchoolProfiles`), and City of Chicago datasets `pb6d-zzuh` (school locations) and `igwz-8jzy` (community areas). Source snapshots are preserved privately; this public package does not include the raw inputs or analysis pipeline.

The pipeline reads the workbook’s traditional-school and co-location sheets, joins school records by CPS ID, and assigns community areas from coordinates and boundary polygons, falling back to the profile API’s community when a point falls outside all polygons. Missing values remain blank. Homerooms are derived from adjusted classrooms: elementary `floor(adjusted classrooms × 0.77)` with 28 seats each; high-school `adjusted classrooms × 0.80` with 30 seats each. These are inferred rules checked against the workbook, not an independently published homeroom count.

## Before reporting

- The profile API has conflicting year labels. `enrollment_profile` is of uncertain vintage; use the documented SY2026 enrollment fields for utilization analysis.
- `enrollment_utilization` excludes students assigned to cluster or pre-K program classrooms.
- `classrooms_demand` is a legacy field name for adjusted classroom supply, not measured demand. `classrooms_supply` represents permanent classrooms.
- Seven schools lack coordinates; 14 co-located school rows lack classroom and capacity counts. Absence is not zero.
- School utilization does not establish that space is usable or available for additional services. Some schools operate wholly in leased space.
- The unverified historical health-center roster and frozen atlas tables are excluded from these reporter-facing downloads.

Data are covered by the repository [license](../../LICENSE). Include the snapshot date when citing or reusing them.
