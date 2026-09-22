# CPS space and co-location

[Explore the project](https://connorblandford.com/projects/cps-space-colocation/). This is the dataset behind an exploratory map and the article it accompanies, “Chicago’s underutilized schools are an unrealized opportunity” (part one of three). It examines school space and potential co-location. Health-center operating status is tracked separately. Release: **2026-09-21**, tagged [`cps-space-colocation-2026-09-21`](https://github.com/cub44/Chicago-Civic-Data/tree/cps-space-colocation-2026-09-21); utilization year: **SY2026**. Sources were pulled between 2026-09-09 and 2026-09-14; the [data dictionary](data/README.md#source-pulls) lists each pull date. All dates here are YYYY-MM-DD.

## Download

| CSV | Rows | One row represents |
|---|---:|---|
| [schools.csv](data/processed/schools.csv) | 642 | One school |
| [school_buildings.csv](data/processed/school_buildings.csv) | 642 | One school, with a coordinate inside its building |
| [utilization.csv](data/processed/utilization.csv) | 510 | One school in SY2026 |
| [colocation_campuses.csv](data/processed/colocation_campuses.csv) | 16 | One shared campus |
| [sbhc_publish.csv](data/processed/sbhc_publish.csv) | 38 | One school-based health center |
| [sbhc_resolved.csv](data/processed/sbhc_resolved.csv) | 38 | One center with source and resolved values side by side |
| [sbhc_discrepancies.csv](data/processed/sbhc_discrepancies.csv) | 152 | One center-field evidence finding |
| [libraries.csv](data/processed/libraries.csv) | 82 | One Chicago Public Library branch |
| [library_buildings.csv](data/processed/library_buildings.csv) | 82 | One branch, with a coordinate inside its building |
| [park_facilities.csv](data/processed/park_facilities.csv) | 743 | One Chicago Park District building |
| [park_facility_buildings.csv](data/processed/park_facility_buildings.csv) | 743 | One park building, with a coordinate inside its footprint |
| [health_clinics.csv](data/processed/health_clinics.csv) | 24 | One Chicago Department of Public Health clinic |
| [health_clinic_buildings.csv](data/processed/health_clinic_buildings.csv) | 24 | One clinic, with a coordinate inside its building |
| [senior_centers.csv](data/processed/senior_centers.csv) | 21 | One DFSS senior center |
| [senior_center_buildings.csv](data/processed/senior_center_buildings.csv) | 21 | One senior center, with a coordinate inside its building |
| [workforce_centers.csv](data/processed/workforce_centers.csv) | 5 | One DFSS workforce center |
| [workforce_center_buildings.csv](data/processed/workforce_center_buildings.csv) | 5 | One workforce center, with a coordinate inside its building |

See the [data dictionary](data/README.md) for all fields and caveats. Join schools and utilization using `sid`, schools and school buildings using `sid`, libraries and library buildings using `name`, the two park files using `objectid` — not `bldg_id`, which is duplicated on two Lincoln Park buildings — and each of the three City service rosters to its building file using `site_id`. `site_id` is the data portal's own row handle, used because none of those three datasets publishes an id column and site names are not unique; it identifies a row within this snapshot and is not a durable public identifier. Campus totals overlap individual school records: do not add both together. The building files never replace a roster coordinate; they add a second one, inside the building, and say how confidently it was derived. [SHA-256 checksums](checksums.sha256) identify the download versions.

## Sources and method

Inputs are the CPS SY2026 Space Utilization workbook (`spaceuse_2026_final_forweb.xlsx`, last updated 2025-12-19), the CPS School Profile Information API (`api.cps.edu/schoolprofile/CPS/AllSchoolProfiles`), and City of Chicago datasets `pb6d-zzuh` (school locations), `igwz-8jzy` (community areas), `x8fc-8rcq` (library branch locations), `vcti-mbcd` (the Chicago Park District building inventory behind the portal's `u7uu-j2ma` map view), `kcki-hnch`, `qhfc-4cw2` and `cs4s-nsna` (the CDPH clinic, senior center and workforce center rosters behind the portal's `4msa-kt5t`, `8ayb-6mjs` and `i4rz-w47p` map views) and `syp8-uezg` (building footprints, a 2015 snapshot). Pull dates are in the [source pull table](data/README.md#source-pulls). Six schools converted from charters in 2026 are placed from `pb6d-zzuh` under the charter ids they held before; see "Before reporting" and `data/README.md`. Source snapshots are preserved privately. The 38 pages, PDFs and datasets cited by the SBHC reconciliation are third-party material and are not republished; [`data/source/evidence_manifest.csv`](data/source/evidence_manifest.csv) records each one's URL, access date, size and SHA-256. The reconciliation's standard-library Python build is included so the publication sheet remains auditable.

The pipeline reads the workbook’s traditional-school and co-location sheets, joins school records by CPS ID, and assigns community areas from coordinates and boundary polygons, falling back to the profile API’s community when a point falls outside all polygons. Missing values remain blank. Homerooms are derived from adjusted classrooms: elementary `floor(adjusted classrooms × 0.77)` with 28 seats each; high-school `adjusted classrooms × 0.80` with 30 seats each. CPS states these rules in its [Space Utilization Methodology SY26](https://www.cps.edu/globalassets/cps-pages/services-and-supports/school-facilities/facilities-standards/space-utilization-methodology-sy26.pdf) but publishes no homeroom count; the build derives one and checks it against every row of the workbook.

“Underutilized” is CPS's label, applied under that methodology's standard: a building is underutilized below 70% of its ideal capacity, efficient from 70% to 110%, and overcrowded above 110%. The workbook applies it to the adjusted rate, `su_pct`. It counts homerooms, not floor area; see the [data dictionary](data/README.md#what-underutilized-means).

## Before reporting

- The profile API has conflicting year labels. `enrollment_profile` is of uncertain vintage; use the documented SY2026 enrollment fields for utilization analysis.
- `enrollment_utilization` excludes students assigned to cluster or pre-K program classrooms.
- `classrooms_demand` is a legacy field name for adjusted classroom supply, not measured demand. `classrooms_supply` represents permanent classrooms.
- Every school has a coordinate from a published source. Five Acero schools and ChiArts, converted to district schools, are returned by the profile API at `0.0/0.0` under their new ids; `pb6d-zzuh` places them under their former charter ids, which `source` names. An earlier release filled these six, and Urban Prep – Bronzeville, from Google Earth reads; those are gone. 14 co-located school rows lack classroom and capacity counts. Absence is not zero.
- Building coordinates match an address only on the same side of the street. An earlier release published Legacy Charter (`400049`) inside the police station across Ogden Avenue; see `data/README.md`.
- School utilization does not establish that space is usable or available for additional services. Some schools operate wholly in leased space.
- The library file is a roster of branch **locations**. It carries no floor area, collection, staffing or program-space figure, and its hours are the usual published schedule rather than a record of any given day. A blank area is an area with no CPL branch — not an area with no library service, since school, university and suburban systems are outside the dataset.
- The park file is a building **inventory**, not a record of park provision. It says a building of a recorded type stands on Park District premises, with the year, stories and floor area CPD holds for it — nothing about what runs inside, opening hours, staffing or condition. Park land with no building on it (a playlot, a ball field, a beach) is not in the dataset at all, so a blank area is an area with no park *building*, not an area with no park. CPD writes 0 where it has no figure; those are published as blank, which leaves build year missing on 410 of 743 rows and floor area on 511. Absence is not zero, and nothing is interpolated. The same rule now holds in every building file: the City's footprint data writes 0 for a missing story count, and `bldg_stories` publishes it blank.
- The three City service files — CDPH clinics, senior centers, workforce centers — are location rosters, and every one of them is stale. None carries an operating-status column, and on each the portal's own *Time Period* is earlier than the date the rows were last edited: clinics "current as of June 2016" (rows updated 2017-08-03), senior centers "current as of 2011" (updated 2019-03-07), workforce centers labeled a "current list" whose rows have not been touched since 2011-08-21. A row establishes that the City published that address as a service location as of that date and nothing more; both dates ride on every row as `vintage` and `rows_updated`. Do not report any of these as currently operating without checking a current source. Five workforce centers is also a short enough list that a gap means the file does not cover it, not that employment services are absent.
- CDPH records its clinic service flags (`wic`, `public_health_nursing`, `family_case_management`, `healthy_start_program`, `healthy_families_program`) on WIC rows only. A blank means "not recorded on this row", never "this service is not offered".
- Three CDPH addresses carry more than one clinic and publish one coordinate between them; those rows are kept separate and stack on the map. Group them by coordinate, not by `address` — the same building is written three different ways across the rows that share it.
- Building coordinates come from a 2015 footprint snapshot, the most recent the City publishes. Anything built since is matched to whatever stood on the site, or to nothing; unmatched records keep their address point and are flagged rather than guessed.
- SBHC rows marked `closed` or `closed_or_consolidated` remain in the record but
  should not be treated as currently operating. The map hides them by default.
- `sbhc_publish.csv` carries no space-use status. Join its `sid` to
  `utilization.csv`; an earlier release's `cps_status_2025` columns came from an
  older CPS file and contradicted it for five host schools.
- The two mobile health units in `sbhc_publish.csv` are not drawn on the map.
  Neither has a fixed site, and HRSA registers both at their operator's own
  address, so their only coordinate points at a building that is neither a
  school nor anywhere the unit goes. The rows stay in the file, where an address
  is a field rather than a position.
- `student_count` in `schools.csv` is the profile API's headcount and is the only
  enrollment figure published for a charter in its own building. It disagrees
  with `enrollment_20th_day` on 502 of the 509 schools both sources cover; use
  `enrollment_20th_day` for utilization analysis.

See [SBHC resolution notes](docs/RESOLUTION_NOTES.md) for source hierarchy,
current-status evidence, deliberately unresolved values, and the 2014-only use
of the CDPH health-center dataset.

Data are covered by the repository [license](../../LICENSE). Include the release date, 2026-09-21, when citing or reusing them.
