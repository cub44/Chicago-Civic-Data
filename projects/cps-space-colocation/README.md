# CPS space and co-location

[Explore the project](https://connorblandford.com/projects/cps-space-colocation/) or open its [dataset page](https://connorblandford.com/data/cps-space-colocation/). This is the dataset behind an exploratory map and the article it accompanies, “Chicago’s underutilized schools are an unrealized opportunity” (part one of three). It examines Chicago Public Schools (CPS) space and potential co-location. Release: **2026-09-26**, tagged [`cps-space-colocation-2026-09-26`](https://github.com/cub44/Chicago-Civic-Data/tree/cps-space-colocation-2026-09-26); utilization year: **SY2026**. Sources were pulled 2026-09-09 to 2026-09-21; the [data dictionary](data/README.md#source-pulls) lists each pull date. All dates here are YYYY-MM-DD.

DOI: [https://doi.org/10.5281/zenodo.22972209](https://doi.org/10.5281/zenodo.22972209). Zenodo archives each release from 2026-09-26 on; this DOI stands for all of them and resolves to the latest.

## Download

| CSV | Rows | One row represents |
|---|---:|---|
| [schools.csv](data/processed/schools.csv) | 642 | One school |
| [school_buildings.csv](data/processed/school_buildings.csv) | 642 | One school: the City footprint matched to it, a point inside that footprint where one was matched, and how confidently (`match_quality`) |
| [utilization.csv](data/processed/utilization.csv) | 510 | One school in SY2026 |
| [colocation_campuses.csv](data/processed/colocation_campuses.csv) | 16 | One shared campus |
| [sbhc_publish.csv](data/processed/sbhc_publish.csv) | 38 | One school-based health center (SBHC) |
| [sbhc_resolved.csv](data/processed/sbhc_resolved.csv) | 38 | One center with source and resolved values side by side |
| [sbhc_discrepancies.csv](data/processed/sbhc_discrepancies.csv) | 153 | One center-field evidence finding |
| [libraries.csv](data/processed/libraries.csv) | 82 | One Chicago Public Library (CPL) branch |
| [library_buildings.csv](data/processed/library_buildings.csv) | 82 | One branch: the City footprint matched to it, a point inside that footprint where one was matched, and how confidently (`match_quality`) |
| [park_facilities.csv](data/processed/park_facilities.csv) | 743 | One Chicago Park District (CPD) building |
| [park_facility_buildings.csv](data/processed/park_facility_buildings.csv) | 743 | One park building: the City footprint matched to it, a point inside that footprint where one was matched, and how confidently (`match_quality`) |
| [health_clinics.csv](data/processed/health_clinics.csv) | 24 | One Chicago Department of Public Health (CDPH) clinic |
| [health_clinic_buildings.csv](data/processed/health_clinic_buildings.csv) | 24 | One clinic: the City footprint matched to it, a point inside that footprint where one was matched, and how confidently (`match_quality`) |
| [senior_centers.csv](data/processed/senior_centers.csv) | 21 | One senior center of the City's Department of Family and Support Services (DFSS) |
| [senior_center_buildings.csv](data/processed/senior_center_buildings.csv) | 21 | One senior center: the City footprint matched to it, a point inside that footprint where one was matched, and how confidently (`match_quality`) |
| [workforce_centers.csv](data/processed/workforce_centers.csv) | 5 | One DFSS workforce center |
| [workforce_center_buildings.csv](data/processed/workforce_center_buildings.csv) | 5 | One workforce center: the City footprint matched to it, a point inside that footprint where one was matched, and how confidently (`match_quality`) |
| [community_area_summary.csv](data/processed/community_area_summary.csv) | 77 | One community area: schools mapped, buildings with a space-use status, underutilized buildings, empty seats in them, and operating school-based health centers |
| [cdph_mental_health_centers.csv](data/processed/cdph_mental_health_centers.csv) | 7 | One CDPH mental health center as listed on 2026-09-21, with the coordinate the article measures to |
| [facts.json](data/processed/facts.json) | — | Every figure the project page states, with the display string it prints, a definition, its source file and rounding |

See the [data dictionary](data/README.md) for all fields and caveats. Join schools and utilization using `sid`, schools and school buildings using `sid`, libraries and library buildings using `name`, the two park files using `objectid` — not `bldg_id`, which is duplicated on two Lincoln Park buildings — and each of the three City service rosters to its building file using `site_id`. `site_id` is the data portal's own row handle, used because none of those three datasets publishes an id column and site names are not unique; it identifies a row within this snapshot and is not a durable public identifier. Campus totals overlap individual school records: do not add both together. The building files never replace a roster coordinate. They add a second point, inside a City footprint where one is in range, and `match_quality` says how confidently that footprint was matched: of the 1,517 building-file rows, 1,238 are matched by address, by containment or by a library label; 249 carry a point inside the largest nearby footprint, recorded as a candidate only; and 30 found no footprint within 160 m and carry no second point. [SHA-256 checksums](checksums.sha256) identify the download versions.

## Sources and method

Inputs are the CPS SY2026 Space Utilization workbook (`spaceuse_2026_final_forweb.xlsx`, last updated 2025-12-19), the CPS School Profile Information API (`api.cps.edu/schoolprofile/CPS/AllSchoolProfiles`), and City of Chicago datasets `pb6d-zzuh` (school locations), `igwz-8jzy` (community areas), `x8fc-8rcq` (library branch locations), `vcti-mbcd` (the Chicago Park District building inventory behind the portal's `u7uu-j2ma` map view), `kcki-hnch`, `qhfc-4cw2` and `cs4s-nsna` (the CDPH clinic, senior center and workforce center rosters behind the portal's `4msa-kt5t`, `8ayb-6mjs` and `i4rz-w47p` map views) and `syp8-uezg` (building footprints, a 2015 snapshot). Pull dates are in the [source pull table](data/README.md#source-pulls). Six schools converted from charters in 2026 are placed from `pb6d-zzuh` under the charter ids they held before; see "Before reporting" and `data/README.md`. Source snapshots are preserved privately. The SBHC reconciliation consulted 38 pages, PDFs and datasets and cites 36 of them. All 38 are third-party material and are not republished; [`data/source/evidence_manifest.csv`](data/source/evidence_manifest.csv) records each one's URL, access date, size and SHA-256. The reconciliation's standard-library Python build is included so the publication sheet remains auditable. Reproduce the three SBHC sheets with `make sbhc` from this directory (Python 3 standard library, no dependencies; equivalently `python3 build_resolved.py && python3 test_sbhc_publish.py`). The test runs either as a script or under `pytest`.

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
- CDPH records its clinic service flags (`wic`, `public_health_nursing`, `family_case_management`, `healthy_start_program`, `healthy_families_program`) on WIC (Special Supplemental Nutrition Program for Women, Infants, and Children) rows only. A blank means "not recorded on this row", never "this service is not offered".
- Three CDPH addresses carry more than one clinic and publish one coordinate between them; those rows are kept separate and stack on the map. Group them by coordinate, not by `address` — the same building is written three different ways across the rows that share it.
- Building coordinates come from a 2015 footprint snapshot, the most recent the City publishes. Anything built since is matched to whatever stood on the site, or to nothing; unmatched records keep their address point and are flagged rather than guessed.
- SBHC rows marked `closed` or `closed_or_consolidated` remain in the record but
  should not be treated as currently operating. The map hides them by default.
- `sbhc_publish.csv` carries no space-use status. Join its `sid` to
  `utilization.csv`; an earlier release's `cps_status_2025` columns came from an
  older CPS file and contradicted it for five host schools. Two hosts have no
  utilization row — Noble Mansueto (`400179`), a charter in its own building,
  and Simpson Academy (`609750`), a specialty school the workbook excludes by
  design — so 32 of the 34 host `sid`s join.
- The two mobile health units in `sbhc_publish.csv` are not drawn on the map.
  Neither has a fixed site, and the federal Health Resources and Services
  Administration (HRSA) registers both at their operator's own
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

## Cite and reuse

Cite this release as:

> Blandford, Connor Ulrich. “CPS space and co-location.” Data set, release 2026-09-26. connorblandford.com. https://connorblandford.com/data/cps-space-colocation/. https://doi.org/10.5281/zenodo.22972209.

The [dataset page](https://connorblandford.com/data/cps-space-colocation/) gives the same citation, with this release's own DOI in place of the page's URL, followed by the DOI for all releases. The data and this documentation are under [CC BY 4.0](../../LICENSE), and the code (`*.py`, `Makefile`) is under [MIT](../../LICENSE-CODE). The repository's [Reuse and corrections](../../README.md#reuse-and-corrections) section says what each license covers and how to report a correction.

## What changed on 2026-09-26

The school-based health center notes say who did the research, and `facts.json` says where its figures come from. **No figure changed**: every figure in `facts.json`, every status and every coordinate is as it was, and the 16 other files are byte for byte the files of release 2026-09-24: the 14 tables built from the source pulls, `community_area_summary.csv` and `cdph_mental_health_centers.csv`. Four files changed:

- **`sbhc_publish.csv`, `sbhc_resolved.csv` and `sbhc_discrepancies.csv`** carry the resolution notes verbatim, so all three change with them:
  - The Johnson center’s note says the author confirmed from local knowledge that 1504 S Albany is a separate building from the school at 1420 S Albany, and that the City’s building footprints put the two in separate buildings, about 270 feet apart.
  - Notes that cited “the uploaded CPS sheet” name CPS’s health-center sheet and the day it was pulled, 2026-09-11.
  - Asides that asked for a phone call now say the value is not yet confirmed with the sponsor.
  - Three notes no longer say “flagged”: the two on the Davis annex give the reason for their medium confidence, and the Gary Comer note says only that it fills an empty coordinate.
  - The Mansueto note places Esperanza’s Brighton Park clinic about one block (roughly 620 feet) east of the school, where it had said roughly a kilometer.
  - The summer window in the Davis and Drake centers’ hours is written Jun 16–Aug 8.
  - Esperanza at Cultivate Collective, the one operating center with a blank `sponsor`, now reads `Esperanza Health Centers`, taken from the row’s own HRSA grantee, and its `resolution_fields` lists `sponsor(high)`. That is a new finding, so `sbhc_discrepancies.csv` has 153 rows, up from 152. The count of sponsors of operating centers stays 13.
- **`facts.json`** takes the new release date and:
  - names the health-center roster as researched by AI agents and links it at this release’s tag;
  - dates the roster by its research, 2026-09-12, where it had given the day the sheet was copied into the working repository;
  - says AI agents compiled the CDPH mental health center list;
  - links the CPS School Profile Information API’s help page rather than its 15.5 MB data endpoint;
  - gives the footprint extracts their last pull date, 2026-09-14, as `pulled_last`, beside the first, 2026-09-13;
  - adds `coverage`, school year 2025–26 in months (2025-08 to 2026-06);
  - adds “school-based” to the labels of the roster’s figures, as in “School-based health centers operating”;
  - says the script that writes it is in the private working repository.

`build_resolved.py` and `test_sbhc_publish.py` now read and write the three sheets as UTF-8 whatever the system’s default encoding, so `make sbhc` reproduces their checksums under any locale; the en dash is the sheets’ first character outside ASCII.

## What changed on 2026-09-24

`community_area_summary.csv` gains `display_name`, each community area's name as the Chicago Potholes release spells it (title case, with O'Hare and McKinley Park), beside the boundary layer's capitals in `community_area`, which stays the key. **No figure changed**: `facts.json` differs only in its release date, and the other 18 files are byte for byte the files of release 2026-09-23.

## What changed on 2026-09-23

**Later the same day, three files joined the release** (tag [`cps-space-colocation-2026-09-23.1`](https://github.com/cub44/Chicago-Civic-Data/tree/cps-space-colocation-2026-09-23.1)): `facts.json`, every figure the project page states with the display string it prints, a definition, its source file and rounding; `community_area_summary.csv`, one row per community area; and `cdph_mental_health_centers.csv`, the seven centers the article measures distances to, three of which were on no published roster. **No figure changed**, and the 17 CSVs are byte for byte the morning's files. The counting basis the page states is now data: the utilization file's rows are school records, a building is a distinct school address, and 266 underutilized records stand in 265 buildings. The morning's changes follow.

Provenance and documentation, after a pre-showcase audit of this repository, the working
repository and the project page. **No figure changed**, and no coordinate, count, status,
address or hours value moved. Thirteen of the 17 CSVs are byte for byte the files published
on 2026-09-21; the four that differ are described below.

- **`schools.csv` names each source once.** YCCS-Austin Career Education Center HS
  (`400127`) is the one school the City file `pb6d-zzuh` does not carry, so the profile API
  supplies both its record and its coordinate, and `source` had named that pull twice. The
  row now reads `cps_school_profiles@2026-09-09+socrata_igwz-8jzy@2026-09-09` — two keys
  where every other row carries three — and a test rejects any repeated key. No value on
  the row changed.
- **The three SBHC sheets no longer cite a file that does not exist.** A resolution note on
  the Johnson row referred to `test_sbhc.py`; the rule it describes lives in
  `test_sbhc_publish.py`, which is what the note now names. The note text is published
  verbatim in `sbhc_publish.csv`, `sbhc_resolved.csv` and `sbhc_discrepancies.csv`, so all
  three change by that wording.
- **Two project-authored notes use ISO dates.** "Oct 2022" and "Feb 2026" are written
  2022-10 and 2026-02, as every other date in the release is.
- **The data dictionary describes the `source` separator correctly.** `schools.csv` and the
  two SBHC sheets join keys with `+`; the five City and Park District rosters join them with
  a comma and a space. The dictionary had claimed `+` throughout, which was wrong for 875
  rows.
- **`LICENSE` names paths that exist.** It had applied its code terms to `scripts/`,
  `tests/` and `site/index.html` and its data terms to a top-level `data/`, none of which
  are in this repository, and it now carries an SPDX identifier.
- **The resolution notes count their own findings correctly**, and state which rows publish
  no hours and why.
