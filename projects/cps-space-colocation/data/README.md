# Data dictionary

Release **2026-09-26**, tagged [`cps-space-colocation-2026-09-26`](https://github.com/cub44/Chicago-Civic-Data/tree/cps-space-colocation-2026-09-26). Cite that date and the file you used, in the form the [project README](../README.md#cite-and-reuse) gives. Each source was pulled on its own date, listed below. CSVs are UTF-8; blank cells mean missing, not zero. Join school tables on `sid`, read as text. `su_pct` is a ratio: 0.70 means 70%. All dates are YYYY-MM-DD. In the column tables, Type is one of `text`, `integer`, `decimal`, `boolean` (`true` or `false`), `date` (YYYY-MM-DD) or `enum` (one of the values listed); units are given in a Units column or in the notes, never as the type.

### Source pulls

| Source | Publisher's id | Pulled | The source's own date |
|---|---|---|---|
| Chicago Public Schools (CPS) Space Utilization workbook, SY2026 (`spaceuse_2026_final_forweb.xlsx`) | CPS | 2026-09-09 | last updated 2025-12-19 |
| CPS School Profile Information API | `AllSchoolProfiles` | 2026-09-09 | labels conflict; see below |
| Chicago Public Schools – School Locations SY2526 | `pb6d-zzuh` | 2026-09-09 | rows updated 2025-09-09 |
| Boundaries – Community Areas | `igwz-8jzy` | 2026-09-09 | rows updated 2025-04-22 |
| School-based health center (SBHC) input lists from the Illinois Department of Public Health (IDPH), CPS and the U.S. Health Resources and Services Administration (HRSA), plus a CPS school file | see `sbhc_publish.csv` | 2026-09-11 | varies; see `sbhc_publish.csv` |
| SBHC evidence pages (38 consulted, 36 cited) | `data/source/evidence_manifest.csv` | 2026-09-12 | per page |
| Libraries – Locations, Contact Information, and Usual Hours of Operation | `x8fc-8rcq` | 2026-09-13 | rows updated 2026-08-24 |
| Building Footprints | `syp8-uezg` | 2026-09-13 (around schools and libraries), 2026-09-14 (around park buildings and City service sites) | rows updated 2015-08-15 |
| CPD_Park_Buildings | `vcti-mbcd` | 2026-09-14 | rows updated 2022-05-18; inventory dated 2016-11-04 |
| Chicago Department of Public Health (CDPH) Clinic Locations | `kcki-hnch` | 2026-09-14 | rows updated 2017-08-03 |
| Senior Centers | `qhfc-4cw2` | 2026-09-14 | rows updated 2019-03-07 |
| Workforce Centers | `cs4s-nsna` | 2026-09-14 | rows updated 2011-08-21 |
| CDPH Mental Health Centers (web page, the seven centers it lists) | chicago.gov | 2026-09-21 | as listed that day; three centers are on no published roster |
| U.S. Census Bureau Geocoder (three center addresses) | geocoding.geo.census.gov | 2026-09-21 | — |

Every `source` column names the pulls its row came from, as `key@YYYY-MM-DD`
(`key@YYYY-MM-DD:<predecessor id>` on the six converted schools in
`schools.csv`), with one exception: `cdph_mental_health_centers.csv` describes
its source in words and gives the access date in a separate `accessed` column.
Where a row has more than one key, the separator depends on the table: `schools.csv`
and the two SBHC sheets join the keys with `+`, and the five City and Park
District rosters — `health_clinics.csv`, `libraries.csv`, `park_facilities.csv`,
`senior_centers.csv` and `workforce_centers.csv` — join them with a comma and a
space. A key never repeats in either form, so splitting a row on its own
separator gives each source once.

### Source-level limitations

- **The profile API contradicts itself on vintage.** It reports
  `SchoolProfileYear: 2026` and `SchoolYearReadable: "School Year 2024-2025"` on
  all 641 records. Its `StudentCount` (`enrollment_profile` here) differs from
  the workbook's 20th-day enrollment on 502 of the 509 schools both publish. Treat `enrollment_profile` as an
  approximate headcount of uncertain year; use `enrollment_20th_day` for
  anything load-bearing.
- **The space utilization workbook excludes whole categories by design.** Its
  own notes state the `Data` sheet covers traditional CPS schools and excludes
  specialty, early childhood and options schools. The `Data - Co-Locations`
  sheet covers co-located campuses, including charters in CPS buildings. This
  build reads both.
- **The school locations file has no community area field.** Community is
  assigned by point-in-polygon against `igwz-8jzy`, not by trusting a text
  field.
- **The library roster is locations, not provision.** `x8fc-8rcq` publishes
  where each branch is and how to reach it. It carries no floor area, collection
  size, staffing level or program-space figure, and its hours field is the
  usual published schedule, not a record of any given day.
- **The three City service rosters are stale, and none carries an operating
  status.** `kcki-hnch` (CDPH clinics), `qhfc-4cw2` (senior centers) and
  `cs4s-nsna` (workforce centers) publish where a service was delivered, with
  hours and a phone number. On each, the portal's own *Time Period* is earlier
  than the date the rows were last edited:

  | Roster | Portal *Time Period* | Rows last updated |
  |---|---|---|
  | CDPH clinics | "Current as of June 2016" | 2017-08-03 |
  | Senior centers | "Current as of 2011" | 2019-03-07 |
  | Workforce centers | "Current list" | 2011-08-21 |

  A row establishes that the City published that address as a service location
  as of that date, and nothing more. Both dates ride on every row as `vintage`
  and `rows_updated`. **Do not report any of these as currently operating
  without checking a current source.**
- **CDPH records its clinic service flags on WIC rows only.** WIC is the Special
  Supplemental Nutrition Program for Women, Infants, and Children. `wic`,
  `public_health_nursing`, `family_case_management`, `healthy_start_program` and
  `healthy_families_program` are blank on every mental health and STI (sexually
  transmitted infection) row, so a blank means "not recorded on this row", never
  "this service is not offered".
- **Portal datasets get revised retroactively.** Raw pulls are dated and
  preserved privately, with the processing pipeline behind every file except the
  SBHC sheets, and the build reads those snapshots, so published numbers stay
  reproducible after an upstream revision.

---

## `schools.csv` — one row per school

Grain: one school. 642 rows.

| Column | Type | Units | Source | Notes and limitations |
|---|---|---|---|---|
| `sid` | text | — | `cps_school_profiles` (`SchoolID`) | 6-digit CPS id, read as text. District ids begin 6, charter ids begin 4. Unique in this file. |
| `name` | text | — | `cps_school_profiles` (`SchoolLongName`) | |
| `layer` | text | — | derived | Reconstructed from governance × grade category: `cps_elem`, `cps_high`, `charter_elem`, `charter_high`, and `other_alt` for the 16 contract, Alternative Learning Opportunities Program (ALOP) and SAFE (Safe Achieve Academy) schools. Private schools have no source at all, so they are absent here rather than manufactured. |
| `governance` | text | — | `cps_school_profiles` (`Governance`) | District, Charter, ALOP, Contract, SAFE. Empty for the one school present only in the space-use file. |
| `school_type` | text | — | `cps_school_profiles` (`SchoolType`) | Empty string in the API for many schools; stored as empty, not as `"nan"`. |
| `grades` | text | — | `cps_school_profiles` (`GradesOffered`) | |
| `community` | text | — | `socrata_igwz-8jzy` | Point-in-polygon assignment. Falls back to the API's own `Community` field only when the point lands outside every polygon. Empty where coordinates are absent. |
| `address` | text | — | `cps_school_profiles` | `AddressStreet` + zip. For the one school present only in the space-use file (`400105`), `pb6d-zzuh`'s street line, with no zip because that file publishes none. |
| `lat` / `lon` | decimal | WGS84 (World Geodetic System 1984) degrees | `socrata_pb6d-zzuh`, falling back to `cps_school_profiles` | Six converted schools are read from `pb6d-zzuh` under their predecessor ids. See "missing coordinates" below. |
| `student_count` | integer | students | `cps_school_profiles` (`StudentCount`) | The API's own headcount, of uncertain vintage. Published for every school, unlike `enrollment_20th_day`, which exists only where CPS scores the building. **Do not use it where `enrollment_20th_day` exists.** See "headcount" below. |
| `provenance` | text | — | derived | `sourced` on every row: each comes from the CPS sources `source` names. `unverified` is reserved for a record with no identified source; this release has none. An earlier release labeled the 16 `other_alt` schools `unverified` although they come from the same CPS sources as every other school. |
| `source` | text | — | derived | Source keys and pull dates that produced the row. |

**Missing coordinates: none.** Every school's coordinate comes from the City's
school-locations file (`pb6d-zzuh`) or the profile API. Eight rows need a note.

- Six district schools converted from former charters — five Acero schools
  (Fuentes `610602`, Santiago `610603`, de las Casas `610604`, Cisneros
  `610605`, Tamayo `610606`) and ChiArts (`610607`) — are returned by the
  profile API at `0.0 / 0.0`, null island. Zero is recognized as a missing
  sentinel and never published as a coordinate. `pb6d-zzuh` publishes all six
  under the charter ids they held before conversion, and that is where their
  coordinates come from:

  | `sid` | School | Predecessor id in `pb6d-zzuh` | Name there |
  |---|---|---|---|
  | `610602` | Carlos Fuentes Elementary School | `400082` | ACERO - FUENTES |
  | `610603` | Esmeralda Santiago Elementary School | `400114` | ACERO - SANTIAGO |
  | `610604` | Bartolome de las Casas Elementary School | `400081` | ACERO - DE LAS CASAS |
  | `610605` | Sandra Cisneros Elementary School | `400101` | ACERO - CISNEROS |
  | `610606` | Rufino Tamayo Elementary School | `400084` | ACERO - TAMAYO |
  | `610607` | Chicago Arts High School | `400022` | CHIARTS HS |

  Each pair shares a street address in the two files; the old id is absent from
  the profile API and the new id from `pb6d-zzuh`; and the profile API gives
  each new school an `OpenDate` of 2026-06-14. The build checks all of that on
  every run and fails if a pair goes stale. `source` on these rows reads
  `socrata_pb6d-zzuh@2026-09-09:<predecessor id>`.
- Urban Prep – Bronzeville (`400105`) is absent from the profile API, and its
  row comes from the space-use workbook. `pb6d-zzuh` publishes it under its own
  id at 521 E 35th St, which is where its coordinate and address come from.
- YCCS-Austin Career Education Center HS (`400127`) is the one school placed
  from the profile API rather than the City file: `pb6d-zzuh` carries no row
  under that id, so the coordinate falls back to the API's own
  `AddressLatitude` / `AddressLongitude`. Its `source` therefore names the
  profile API once, as both the record and the geometry source, and reads
  `cps_school_profiles@2026-09-09+socrata_igwz-8jzy@2026-09-09` — two keys
  where every other row carries three. An earlier release wrote that key twice.

An earlier release said no primary source placed the seven schools in the two
bullets above — the six converted schools and Urban Prep – Bronzeville — and
filled them from coordinates read off Google Earth imagery. That was wrong: the
City file places all seven. The Google Earth coordinates have been removed, and no
coordinate in this file comes from imagery.

**Headcount (2 rows absent).** `student_count` is present for 640 of 642
schools. Urban Prep – Bronzeville (`400105`) is absent from the profile API
entirely and its row comes from the space-use workbook, which publishes no
enrollment figure. YCCS-Austin (`400127`) is returned by the API as `0`, which
is read as its missing sentinel: the school is open and no other row in the file
is below three figures. Both are left empty rather than filled.

`student_count` disagrees with the workbook's `enrollment_20th_day` on 502 of
the 509 schools both sources publish, and the API labels a single record
`SchoolProfileYear: 2026` and `SchoolYearReadable: "School Year 2024-2025"` at
the same time. It is carried because for a charter in its own building it is the
only enrollment figure published anywhere, and it is what the map sizes those
markers by — but anything load-bearing should use `enrollment_20th_day`.

**`sid` uniqueness.** Unique in `schools.csv`.

---

## `utilization.csv` — one row per school per year

Grain: one school-year. 510 rows, all SY2026.

| Column | Type | Units | Source column | Notes |
|---|---|---|---|---|
| `sid` | text | — | `School ID` | Read as text. |
| `school_year` | text | — | derived | `SY2026` throughout. |
| `grade_category` | enum | — | `Grade Category` | ES (elementary school) or HS (high school) **as the space-use file assigns it**, which is not always the school's overall band. Noble – Gary Comer is a high school whose co-located rows cover grades 6–8 and are scored ES. This column, not the school's layer, governs the capacity rule. |
| `enrollment_profile` | integer | students | `cps_school_profiles` `StudentCount` | Uncertain vintage — see source limitations. |
| `enrollment_20th_day` | integer | students | `20th Day Enrollment` | Total enrollment at the 20th day. |
| `enrollment_utilization` | integer | students | `Adjusted SY2026 20th Day School Enrollment` | The numerator of the published rate. **Excludes students assigned to cluster *or* pre-K program classrooms** — see the note below. |
| `homerooms` | decimal | homerooms | **derived** | Not published by CPS. Computed from `classrooms_demand` by the rule below and asserted against published capacity. Empty for the 14 co-located rows that carry no classroom counts. |
| `ideal_capacity` | integer | seats | `Ideal Capacity (IC) for Permanent Bldg Only` | Permanent building only.  |
| `adj_ideal_capacity` | integer | seats | `Adjusted IC 2 After CR Deductions` | The denominator of the published rate, after classroom deductions. |
| `su_pct` | decimal | ratio (1.0 = 100%) | `SY2026 Adjusted SU 2` | Published rate. Equals `enrollment_utilization / adj_ideal_capacity` to within 0.01. |
| `cps_status` | enum | — | `Space Use Status` | Underutilized / Efficient / Overcrowded, CPS's own label under its published standard; see "What “underutilized” means" below. Empty for the 14 rows without capacity. |
| `classrooms_supply` | decimal | classrooms | `Total Classrooms (CRs)` | Fitting the published file shows this is total *permanent* classrooms; rooms under 650 sq ft count as 0.5, which is why the column is fractional. Excludes modular and leased space. Retains this label until CPS confirms. |
| `classrooms_modular` | decimal | classrooms | `Modular CR's` | |
| `classrooms_leased` | decimal | classrooms | `Leased CR's` | |
| `classrooms_demand` | decimal | classrooms | `Total CR's Less Cluster, Pre-K, Other & Small` | Fitting shows this is *not* a demand measure at all: it is `(permanent + modular + leased) − (cluster + pre-K + other + small)`, i.e. an adjusted supply figure. The legacy name is retained for compatibility; interpret it as adjusted classroom supply. |
| `source` | text | — | derived | `cps_space_utilization_sy2026@2026-09-09` on every row. It names the workbook only, although `enrollment_profile` is read from the profile API (`cps_school_profiles@2026-09-09`). |

### The capacity rule

CPS publishes adjusted classrooms and adjusted ideal capacity, but no homeroom
count. Its [Space Utilization Methodology SY26](https://www.cps.edu/globalassets/cps-pages/services-and-supports/school-facilities/facilities-standards/space-utilization-methodology-sy26.pdf) states the rule — 77% of
an elementary building's classrooms are homerooms at 28 students; a high
school's ideal capacity is 80% of its classrooms at 30 — and the SY2026 file
follows it exactly:

```
ES:  homerooms      = floor(classrooms_demand × 0.77)
     adj_ideal_capacity = homerooms × 28          417/417 exact

HS:  homerooms      = classrooms_demand × 0.80
     adj_ideal_capacity = homerooms × 30           79/79 exact
```

**The elementary seat figure is 28, not 30.** The build asserts the rule
against every row, so if CPS changes it the build fails rather than drifting.

### What “underutilized” means

`cps_status` is CPS's label, not this project's. CPS's [Space Utilization
Methodology SY26](https://www.cps.edu/globalassets/cps-pages/services-and-supports/school-facilities/facilities-standards/space-utilization-methodology-sy26.pdf) ("Capacity Utilization Standards Described", effective
for school year 2025–26) sets three bands on the space utilization rate,
enrollment divided by ideal capacity:

| `cps_status` | CPS's standard | `su_pct` range in this file | Schools |
|---|---|---|---:|
| Underutilized | Less than 70% of ideal capacity | 0.03–0.69 | 266 |
| Efficient | 70% to 110% of ideal capacity | 0.70–1.09 | 196 |
| Overcrowded | Greater than 110% of ideal capacity | 1.11–1.72 | 34 |

The workbook applies the bands to the adjusted rate, `su_pct` (CPS's *Adjusted
SU 2*), and every scored row falls in the band its status names. Underutilized
therefore means an adjusted enrollment below 70% of the seats the building's
adjusted classroom count allows: its homerooms at 28 or 30 students each. It is a
statement about homerooms, not floor area, and says nothing about whether any
room could hold another service.

### What the utilization enrollment actually excludes

CPS's own data dictionary defines the student deduction as **"Students Assigned
to Cluster or PK programs"** — cluster programs being separate-classroom
placements for students needing significantly modified curriculum with moderate
to intensive support for over 61% of the day.

Pre-K alone does not account for it. 60 schools whose `grades` in
`schools.csv` list no pre-K still show `enrollment_utilization <
enrollment_20th_day`, including Lane Tech (−63),
Whitney Young (−82) and the Chicago High School for Agricultural Sciences (−75).
Walter S Christopher, a special-education elementary with no pre-K, drops from
306 to 153. The corresponding classroom deductions (cluster, pre-K, other,
small) come off the denominator, which is why the rate is not simply deflated.

`enrollment_utilization ≤ enrollment_20th_day` is enforced as a build-failing
assertion. The *explanation* is cluster-or-pre-K, not pre-K.

### Zero permanent classrooms

Four schools report `classrooms_supply = 0`: Ashburn Community (`610287`),
Fairfield (`610057`), Talman (`610249`) and Chicago Academy ES (`610248`). The
zero is correct, not a missing-value placeholder — each operates entirely in
leased space (16 to 30 leased classrooms), and each reports permanent ideal
capacity of 0 and no permanent SU rate. Any surplus space in these buildings is
a landlord's, not the district's, which bears directly on whether it can host a
co-located service. The build asserts that a zero is always corroborated by
non-permanent space, so a zero meaning "unknown" would fail it.

---

## `colocation_campuses.csv` — one row per co-located campus

Grain: one campus. 16 rows.

The space utilization workbook's `Data - Co-Locations` sheet carries
campus-level subtotals for buildings shared by two or more schools — for example
`ES/HS COLO: KIPP - ONE & ORR HS`, labeled `ES/HS COLO 1`. The columns mirror
`utilization.csv`. Campus totals overlap the school records in
`utilization.csv`: do not add the two together.

| Column | Type | Units | Source column | Notes |
|---|---|---|---|---|
| `campus_label` | text | — | `School ID` | CPS's own campus label (`ES COLO 1`, `ES/HS COLO 2`, `HS COLO 4`), which the workbook carries in its school-id column. A label, not a school id; unique in this file. The numbering has gaps: there is no `ES COLO 5` or `ES COLO 8`. |
| `campus_name` | text | — | `School Name` | CPS's name for the campus, naming the schools that share it, verbatim and in its own capitals, including one misspelling (`CHICACO ACADEMY ES`). |
| `grade_category` | enum | — | `Grade Category` | `ES` (8 campuses), `HS` (4) or `ES/HS` (4, a campus shared by an elementary and a high school). |
| `enrollment_20th_day` | integer | students | `20th Day Enrollment` | The campus total. |
| `enrollment_utilization` | integer | students | `Adjusted SY2026 20th Day School Enrollment` | The numerator of the campus rate. Excludes students assigned to cluster or pre-K program classrooms, as in `utilization.csv`. |
| `adj_ideal_capacity` | integer | seats | `Adjusted IC 2 After CR Deductions` | The denominator of the campus rate. |
| `su_pct` | decimal | ratio (1.0 = 100%) | `SY2026 Adjusted SU 2` | The campus's published rate. Equals `enrollment_utilization / adj_ideal_capacity` to two decimals on every row. |
| `cps_status` | enum | — | `Space Use Status` | Underutilized (7), Efficient (8) or Overcrowded (1): CPS's label for the campus as a whole. |
| `source` | text | — | derived | `cps_space_utilization_sy2026@2026-09-09` on every row. |

---

## `school_buildings.csv` — one row per school, footprint match

Grain: one school, joined to `schools.csv` on `sid`. 642 rows — every school in
`schools.csv` has exactly one row here, so a left join loses nothing.

**This file does not replace the coordinates in `schools.csv`.** Those stay
exactly as published: `lat`/`lon` there are the answer to "where is this
address", which is what any distance, catchment or nearest-service work has to
be computed against. This file records the City footprint matched to each
school, a point inside that footprint where one was matched, and how
confidently (`match_quality`), so a consumer decides for itself which
coordinate to use. The map uses the footprint point where the match is well
established and falls back to the source point everywhere else.

Source: Socrata `syp8-uezg` (*Building Footprints*), reached from the
`Building Footprints - Map` view `hz9b-7nh8`. The extract pulls the footprints
within 160 m of each school point rather than all 820,606 citywide.

| Column | Type | Notes |
|---|---|---|
| `sid` | text | CPS school id, read as text. Joins to `schools.csv`. |
| `name` | text | The school's name as `schools.csv` publishes it, carried so the file reads on its own. |
| `match_quality` | enum | How the footprint was matched. See below. Only `address_exact` and `containing` assert "this is the building". |
| `bldg_lat` / `bldg_lon` | decimal | WGS84 degrees. Pole of inaccessibility of the matched footprint — the interior point furthest from any wall. Empty for `no_match` and `no_point`. |
| `offset_m` | decimal | Meters from the `schools.csv` point to `bldg_lat`/`bldg_lon`: how far the marker moved. Empty where there is no footprint point. |
| `edge_m` | decimal | Meters from the `schools.csv` point to the footprint's nearest wall; `0` means the source point falls inside the footprint. Empty where there is no footprint. |
| `bldg_id` | integer | `syp8-uezg` building id, so any match can be re-checked against the source. |
| `bldg_address` | text | Address the footprint itself carries, for comparison against the school's. |
| `bldg_name` | text | Building name in the footprint file, where it has one. Not used for matching, so it is an independent check: 80 snapped rows carry a name, 70 of them containing the word `SCHOOL`. Six more are school names without it (`JONES COLLEGE PREP`, `PLAMONDON`), and four are not schools (a health center, `RUBENSTEIN LUMBER CO.`, `ELSDON`, `HEMINGWAY HOUSE`). A school's name is not always this school's: some footprints still carry a former occupant's. |
| `bldg_stories` | integer | Story count from the footprint file. **Blank where the file has no figure**, which it writes as 0: blank on 337 of 642 rows here, and in the other building files on 32 of 82 branches, 550 of 743 park buildings and 19 of 50 City service sites. A building of zero stories does not exist, so 0 is never published. |
| `footprint_area_sqft` | decimal | Square feet: the source's own `shape_area`, republished unconverted. |
| `candidates_in_range` | integer | Footprints within the extract radius. A high count is a dense block, not a problem. |
| `provenance` | text | `sourced` on every row. |
| `source` | text | The footprint pull the match was made against, as `key@YYYY-MM-DD`: `socrata_syp8-uezg@2026-09-13` here and in `library_buildings.csv`, `socrata_syp8-uezg@2026-09-14` in the other four building files. |

### `match_quality`

| Value | Rows | Meaning |
|---|---|---|
| `address_exact` | 502 | Geometry and address agree: the footprint's address range, side of the street and street match the school's, and the school point is inside it or within 60 m of its wall. |
| `containing` | 16 | The school point falls inside the footprint, but the footprint carries no address or a non-matching one. Direct geometric evidence. |
| `largest_nearby` | 122 | Nothing contains the point and no address matched within 60 m. The largest footprint in range is recorded as a *candidate only*. |
| `no_match` | 2 | A school point exists but the source has no footprint within 160 m. Verified against the portal, not a gap in this extract. |
| `no_point` | 0 | `schools.csv` has no coordinate, so there was nothing to match. Every school now has one; see "Missing coordinates" above. |

The 60 m cap on non-containing address matches is load-bearing. Chicago
footprint address ranges span a whole block face, so "house number inside
`f_add1`–`t_add1` on the same street" collides freely with a school's
neighbors. Without the cap the match confidently placed a high school on a
326 m² outbuilding 137 m away. That row is now `largest_nearby` and the map
leaves it alone.

The cap does not catch the building across the street, which is usually closer
than 60 m, so an address now matches only a range of its own parity: Chicago
numbers one side of every street odd and the other even, and every addressed
footprint in the extract has a same-parity range. An earlier version of this
file said the cap had kept Legacy Charter (`400049`, 3318 W Ogden) off the
police station down the block. It had not: the school was published as
`address_exact` to the Chicago Police 10th District station at 3301–3325 W
Ogden, across the street and 43.5 m away. Ten schools were matched across the
street this way (as were one senior center and one workforce center). With the
parity check, five of the ten now snap to the right building on their own side
(YCCS-West, Little Village, Laughlin Falconer, Stone and Tilton), and five —
Legacy Charter, L.E.A.R.N. Middle School Campus, Hancock, Northside Prep and
Jensen — stay unsnapped on their address point.

Among snapped rows the source point is a median 10 m outside its building's
wall and only 38 fall inside one, which is what an address-level geocode looks
like: close to the right building, rarely in it. Snapping moves a marker a
median 40 m.

### Known limitation: the footprint snapshot is from 2015

`syp8-uezg` reports `rowsUpdatedAt` of 2015-08-15 and has not been revised
since. Any school built or rebuilt after that date is therefore matched against
whatever stood on the site in 2015, or not at all. Noble – ITW David Speer
Academy, which opened in 2016, snaps to a footprint named `RUBENSTEIN LUMBER
CO.`; the school point does fall inside that footprint, so the coordinate is
defensible for 2015 geometry, but the building name is a reminder of what the
match is really asserting. `bldg_name` and `offset_m` are published so this
class of error stays visible rather than being absorbed into a coordinate. The
City publishes no newer citywide footprint dataset on this portal.

---

## `libraries.csv` — one row per public library branch

Grain: one Chicago Public Library (CPL) branch. 82 rows. Pulled 2026-09-13; the
source's rows were last updated 2026-08-24.

Source: Socrata `x8fc-8rcq`, *Libraries - Locations, Contact Information, and
Usual Hours of Operation* — CPL's own branch roster.

This layer is here because the project asks what underused school space could
additionally hold, and library programming is one of the candidate uses. Where
the public library service already reaches bears directly on that: a school with
surplus space three blocks from a branch is a different proposition from one two
miles from the nearest.

| Column | Type | Notes |
|---|---|---|
| `name` | text | CPL's branch name. **The join key** to `library_buildings.csv`; unique across all 82 rows. |
| `cpl_location_id` | integer | CPL's internal location id, parsed from the branch's own `website` URL. The dataset publishes no id column, so this is derived rather than sourced — join to chipublib.org with it, but join within this project on `name`. |
| `address` | text | As published, with CPL's abbreviating periods. |
| `zip` | text | `city` and `state` are omitted: both are constant across all 82 rows. |
| `phone`, `email`, `website` | text | Published branch contact details. |
| `service_hours` | text | **The usual published schedule, not an observed opening record.** Verbatim free text, not parsed into structured hours — doing so would impose a precision the field does not have. |
| `community` | text | Community area, assigned by point-in-polygon against `igwz-8jzy`, the same way `schools.csv` assigns it, so the two are comparable. All 82 fall inside a polygon. |
| `lat` / `lon` | decimal | WGS84 degrees. Every branch has a coordinate. |
| `provenance` / `source` | text | `sourced` for all rows, citing the dataset and pull date. |

### Before reporting from this file

A blank area on a map of these points is an area with **no CPL branch**. It is
not an area with no library service, and it is not a measure of how much library
service the surrounding area gets:

- Chicago Public Library also operates locations inside other institutions, and
  school, university and suburban library systems that Chicagoans use are not in
  this dataset at all.
- Branch *presence* is not provision. Two branches an equal distance away may
  differ by an order of magnitude in floor area, collection, staffing and open
  hours, and none of those figures is published here.
- The hours field describes an ordinary week, not any particular week.

---

## `library_buildings.csv` — one row per branch, footprint match

Grain: one branch, joined to `libraries.csv` on `name`. 82 rows — every branch
has exactly one row, so a left join loses nothing.

The same design as `school_buildings.csv`, built by the same code, and with the
same guarantee: **it does not replace the coordinates in `libraries.csv`.**
Those stay exactly as published and remain what distance work is computed
against. This file records the City footprint matched to each branch, a point
inside that footprint where one was matched, and how confidently
(`match_quality`). Columns are identical to `school_buildings.csv` except that
there is no `sid`: `name`, CPL's branch name, is the key.

Source: Socrata `syp8-uezg` (*Building Footprints*), pulled within 160 m of each
branch point — the same extract method as the school sidecar, so offsets from
the two files are comparable.

### `match_quality`

| Value | Rows | Meaning |
|---|---|---|
| `address_exact` | 66 | Geometry and address agree, as in the school file. |
| `library_named` | 8 | The City's own footprint record labels that building a library, and it lies within 60 m of the branch point. |
| `containing` | 1 | The branch point falls inside a footprint carrying no matching address. |
| `largest_nearby` | 7 | Nothing contains the point and neither rule matched. Recorded as a *candidate only*. |
| `no_match` | 0 | — |
| `no_point` | 0 | Every branch has a coordinate. |

75 of 82 branches (91.5%) are placed inside their building on evidence strong
enough to assert it. Snapping moves a marker a median 22 m.

### Why `library_named` exists

`syp8-uezg` carries a building-use label: 66 of the 8,981 footprints in this
extract name a library in `bldg_name1` or `bldg_name2`, most as the City's own
`CHICAGO PUBLIC LIBRARY`. That is the same class of evidence as the address
range the matcher already trusts — a field the publisher of the geometry
attached to the footprint — and a better one, because an address range describes
a whole block face while a use label describes that building.

Checked against the branches the address rule already matched, the label agrees
with the footprint chosen in 56 of 58 cases, and no branch has two labeled
footprints within 60 m. Both disagreements are cases the label gets right and
the address rule gets wrong: Gage Park sits 0.5 m outside the footprint the City
labels `GAGE PARK` and just inside its unlabeled neighbor; Whitney M. Young,
Jr. matched an address range 54.8 m away — inside the cap, but exactly the
block-face collision that cap exists to bound — while its labeled footprint is
18.1 m away. Six further branches are corner sites addressed on the cross
street (Albany Park, Back of the Yards, Bezazian, Douglass, King, North
Pulaski), which the address rule could never reach.

Where label and address agree the row stays `address_exact`: the stronger claim
is kept rather than overwritten. The school footprints carry no comparable
labeling, so `school_buildings.csv` can never contain this value.

### Known limitation: the 2015 footprint snapshot applies here too

The seven unsnapped branches are Altgeld, Blackstone, Daley (Richard M.),
Galewood-Mont Clare, Little Italy, the Obama Presidential Center Library and
Vodak-East Side. Several were built or rebuilt after the footprint file's 2015
vintage, so nothing in the source stands where they now do. They keep their
address point, and the map says so rather than implying a position it has not
established. For the same reason, two branches that *are* snapped — King and
Back of the Yards — sit on footprints of buildings that have since been
replaced. `bldg_name` and `offset_m` are published so this class of error stays
visible rather than being absorbed into a coordinate.

---

## `park_facilities.csv` — one row per Chicago Park District building

Grain: one building on Chicago Park District (CPD) premises. 743 rows. Pulled 2026-09-14;
the source's rows were last updated 2022-05-18, and the portal dates the
inventory itself 2016-11-04.

Source: Socrata `vcti-mbcd`, *CPD_Park_Buildings*, the tabular dataset behind the
portal's `u7uu-j2ma` map view, *Parks - Chicago Park District Buildings
(current)*.

This layer is here for the same reason the library roster is. The project asks
what underused school space could additionally hold, and the answer depends on
what public space a neighborhood already has. A field house three blocks from a
half-empty school building is already doing some of what that school's surplus
space might be asked to do.

**This is an asset inventory, not a program roster.** It establishes that a
building of a recorded type stands at a point. It establishes nothing about what
runs inside, when the building opens, or whether the pool is filled and the
field house staffed.

| Column | Type | Notes |
|---|---|---|
| `objectid` | integer | The row id. **The join key** to `park_facility_buildings.csv`. Use it rather than `bldg_id`, which is not unique: two Lincoln Park buildings, a comfort station and a concession, both carry `0100-81`. |
| `park` | text | CPD's park name, verbatim and in its own capitals (`LINCOLN (ABRAHAM)`). |
| `park_no` | integer | CPD's park number. |
| `bldg_id` | text | CPD's building id. Published, but **not unique** — see `objectid`. |
| `bldg_name` | text | CPD's building name. Blank on 62 rows. |
| `category` | text | **Derived**, and the only derived classification here: `field_house`, `museum`, `pool`, `stadium`, `other`, from `bldg_type` alone. See below. |
| `bldg_type` | text | CPD's own type, **verbatim**, 38 distinct values. Published beside `category` so the grouping loses nothing. Three rows carry an `INACTIVE: ` prefix in the type string itself. |
| `field_house_class` | text | The class CPD grades a field house at, parsed from `bldg_type` — `A1 A2 A3 A4 AA B BH1 BH2 C D D2 JOINT`. Blank for everything that is not a field house. |
| `status` | text | `ACTIVE` / `INACTIVE` as published; blank on one row. A standing building, not a programmed one. |
| `year_built` | integer | **Blank where CPD publishes 0**, which is its null. Present on 333 of 743 rows, range 1836–2020. |
| `stories` | integer | Blank where CPD publishes 0. Present on 542 of 743 rows. |
| `building_sqft` | integer | **Gross floor area in square feet as CPD records it.** Blank where CPD publishes 0 — present on 232 of 743 rows. Different from `footprint_area_sqft` in the sidecar, which is the City's footprint polygon area; neither is derived from the other. |
| `owner` | text | Owner code as published (`CPD`, `CITY`, `BOE`, `CHA`, `CTA`, `STATE`, `MWRD`, `OTHER`, …), not expanded — the codes are undocumented in the dataset. Not an operator. Blank on 19 rows; one value contains an embedded newline and two read `CPS` and `COD`, all published as found. |
| `address` | text | As published. Blank on 323 rows, and many of the rest are not civic addresses (`SW corner Central Park & Peterson`, `Belmont Harbor`). Not repaired. |
| `ward` | integer | As published. |
| `community` | text | Community area by point-in-polygon against `igwz-8jzy`, the same way `schools.csv` and `libraries.csv` assign it. Blank on three rows that genuinely fall outside every polygon: a breakwater light and a floating yacht club in the lake, and a stadium just north of the city boundary at Devon. |
| `lat` / `lon` | decimal | WGS84 degrees. **Already a building point, not an address geocode** — which is why containment, not address matching, carries the sidecar. Every building has one. |
| `provenance` / `source` | text | `sourced` for all rows, citing the datasets and pull dates. |

### `category` — the five groups

| Value | Rows | From `bldg_type` |
|---|---:|---|
| `field_house` | 251 | every `FIELDHOUSE` class CPD records, not a single type |
| `pool` | 63 | `POOL BUILDING` |
| `museum` | 14 | `MUSEUM` |
| `stadium` | 7 | `STADIUM` |
| `other` | 408 | the remaining 22 types |

`other` is **not** CPD's own `OTHER` type, which covers 15 buildings. The rest of
the residue is comfort stations, shelters, maintenance buildings, utility
structures, concessions, zoo buildings, harbor buildings, golf buildings and
two dozen more. The grouping is a presentation decision, so `bldg_type` is
published verbatim beside it and nothing about the source value is lost.

The `INACTIVE: ` prefix is stripped **only** to choose a category, so an inactive
field house is categorized as a field house. `bldg_type` keeps the prefix and
`status` keeps the status; nothing is rewritten.

### Before reporting from this file

- A blank area is an area with **no Park District building**, not an area with
  no park. Park land carrying no building — a playlot, a ball field, a beach —
  is absent from this dataset entirely.
- Building *presence* is not provision, and this file carries no program,
  hours, staffing or condition figure of any kind.
- **Absence is not zero.** CPD writes 0 for "no figure" in `year_built`,
  `stories` and `bldg_sq_fo`; those are published blank. A build year is missing
  for 410 of 743 buildings and a floor area for 511. Nothing is interpolated.
- The source contradicts itself in places, and is published as found rather than
  reconciled. `objectid` 303, a Jackson Park comfort station, is typed
  `INACTIVE: COMFORT STATION` and statused `ACTIVE`. Four buildings carry a
  build year after the 2016-11-04 inventory date.

---

## `park_facility_buildings.csv` — one row per park building, footprint match

Grain: one CPD building, joined to `park_facilities.csv` on `objectid`. 743 rows
— every building has exactly one row, so a left join loses nothing.

The same design as `school_buildings.csv` and `library_buildings.csv`, built by
the same code, with the same guarantee: **it does not replace the coordinates in
`park_facilities.csv`.** Those stay exactly as published and remain what
distance work is computed against. This file records the City footprint matched
to each park building, a point inside that footprint where one was matched, and
how confidently (`match_quality`).

Columns are identical to `school_buildings.csv` except that the key is
`objectid` in place of `sid`, and that `park` and `cpd_bldg_name` take the place
of `name`, so the file reads on its own. `cpd_bldg_name` is prefixed
deliberately: `bldg_name` in this file is the City's name for the
**footprint**, a different name from a different publisher, and the two
disagree often.

Source: Socrata `syp8-uezg` (*Building Footprints*), pulled within 160 m of each
CPD building point — the same extract method and radius as the school and
library sidecars, so offsets from all three files are comparable.

### `match_quality`

| Value | Rows | Meaning |
|---|---:|---|
| `address_exact` | 312 | Geometry and address agree. |
| `containing` | 298 | The CPD point falls inside a footprint carrying no matching address. |
| `largest_nearby` | 105 | Nothing contains the point and no address matched. Recorded as a *candidate only*. |
| `no_match` | 28 | No footprint within 160 m of the point. |
| `no_point` | 0 | Every building has a coordinate. |

610 of 743 buildings (82.1%) are placed inside a footprint on evidence strong
enough to assert it. Snapping moves a marker a median of **1.9 m**.

`library_named` cannot appear in this file. `syp8-uezg` labels library
buildings; it carries no comparable park-building label, so the park matcher
passes no such rule.

### Why the numbers look different from the school file

CPD publishes a **building point**, not an address geocode, so 608 of the 610
snapped rows are placed by containment: the point was already inside its
footprint and the marker moves to that footprint's interior point. The
`address_exact` / `containing` split here is therefore not a split between
address evidence and geometric evidence — it is whether the address *also*
corroborated a containment that had already happened. By category, 233 of 251
field houses (92.8%), 53 of 63 pool buildings, 11 of 14 museum buildings, 5 of 7
stadiums and 308 of 408 in `other` are placed inside a footprint.

### Known limitations: the 2015 snapshot, and its granularity

The 133 buildings that do not snap are overwhelmingly small structures the 2015
footprint file does not carry — comfort stations, shelters and utility
structures in open parkland. They keep CPD's own point, flagged rather than
guessed.

The footprint file is also **coarser than CPD's inventory**. Nine footprints
carry more than one CPD building between them, 25 snapped rows in total; the
worst is the Sherman Park complex, where eight CPD buildings — lifeguard office,
two pergolas, two locker buildings, two gymnasiums and a boiler house — are a
single footprint in the 2015 file. Those rows snap to the same `bldg_id` and
therefore to nearly the same point. That is the footprint file being less
granular, not a matching error: dropping the duplicates would delete buildings
that exist and moving them would invent positions. `bldg_id` and `offset_m` are
published so the condition stays visible.

---

## `health_clinics.csv` — one row per CDPH clinic

Grain: one clinic. 24 rows. Source: Socrata `kcki-hnch`, the tabular dataset
behind the portal's `4msa-kt5t` map view, pulled 2026-09-14.

**A location roster of uncertain currency**, described by the portal as "Current
as of June 2016" with rows last updated 2017-08-03, and carrying **no
operating-status column at all**. See the source-level limitations above.

| Column | Type | Notes |
|---|---|---|
| `site_id` | text | The data portal's own row handle. **The join key** for `health_clinic_buildings.csv`. Used because the dataset publishes no id column and `site_name` is not unique — two rows are both "Erie Health Center", at different addresses. It identifies a row within this snapshot and is **not** a durable public identifier. |
| `site_name` | text | CDPH's own site name, verbatim. Not unique. |
| `category` | enum | `mental_health` (5), `wic` (15), `sti` (4). A one-to-one relabeling of `clinic_type`, and the three map layers. CDPH publishes exactly three types, so there is no `other` bucket. |
| `clinic_type` | text | CDPH's own type, verbatim, published beside `category`. |
| `site_number` | integer | CDPH's site number, on 11 of 24 rows. Not a key — it cannot join the other 13. |
| `hours_of_operation` | text | The published schedule, not an observed opening record, and of the same 2016 vintage as the rest of the row. |
| `public_health_nursing`, `family_case_management`, `healthy_start_program`, `healthy_families_program`, `wic` | text | `Y` or blank. **Blank means "not recorded on this row", not "service not offered"** — CDPH fills these in on WIC rows only. |
| `address` | text | As published, **including the suite and floor**. Not normalized, so `address` does **not** identify a site: see below. |
| `zip`, `phone`, `fax` | text | As published. `phone` is CDPH's `phone_1`. |
| `phone_additional` | text | CDPH's `phone_2`–`phone_5`, joined with `; `. Values untouched, including one that is a typo in the source. |
| `community` | text | Point-in-polygon against `igwz-8jzy`, the same way the school, library and park files assign it. All 24 land inside a polygon. |
| `lat` / `lon` | decimal | WGS84 degrees, from the Socrata `location` geometry. Every clinic has a coordinate. |
| `vintage` | text | The portal's own statement of what the rows describe: `Current as of June 2016`. |
| `rows_updated` | date | When the portal last changed the rows: `2017-08-03`. A different fact from `vintage`. |
| `provenance` / `source` | text | `sourced`, citing the dated pulls. |

### Three addresses carry more than one clinic

The portal's own description of the map view says so: *"some locations have
multiple clinic types but will show as a single dot on this map."*

| Coordinate | Address | Categories |
|---|---|---|
| 41.779692, −87.641428 | 641 W. 63rd St | `mental_health`, `sti`, `wic` |
| 41.793275, −87.727664 | 4150 W. 55th | `mental_health`, `wic` |
| 41.902212, −87.748845 | 4909 W. Division | `sti`, `wic` |

**Group them by coordinate, not by `address`.** Each of those sites writes the
shared address differently on each row — `641 W. 63rd St`, `641 W. 63rd St.,
Lower Level` and `641 W. 63rd St.` are one building — so matching on `address`
finds 24 distinct addresses and no sharing at all. The rows are kept separate:
collapsing three services into one would delete two of them.

---

## `senior_centers.csv` — one row per DFSS senior center

Grain: one senior center of the City's Department of Family and Support
Services (DFSS). 21 rows. Source: Socrata `qhfc-4cw2`, the tabular dataset
behind the portal's `8ayb-6mjs` map view, pulled 2026-09-14.

**A location roster the portal itself dates to 2011**, last edited 2019-03-07,
with no operating-status column.

| Column | Type | Notes |
|---|---|---|
| `site_id` | text | The portal's row handle. **The join key** for `senior_center_buildings.csv`; see `health_clinics.csv`. |
| `site_name` | text | DFSS names these for the neighborhood — `Pilsen`, `Abbott Park` — not "X Senior Center". |
| `program` | enum | `Regional Senior Center` (6) or `Satellite Senior Center` (15), verbatim. |
| `hours_of_operation` | text | The published schedule, of 2011 vintage. |
| `address`, `zip`, `phone` | text | As published. Two addresses carry a hyphenated house number (`653-657 W. 63rd Street`, `5674-B S. Archer Avenue`). |
| `community` | text | Point-in-polygon. All 21 land inside a polygon. |
| `lat` / `lon` | decimal | WGS84 degrees. Every center has a coordinate. |
| `vintage` | text | The portal's own statement of what the rows describe: `Current as of 2011`. |
| `rows_updated` | date | When the portal last changed the rows: `2019-03-07`. |
| `provenance` / `source` | text | `sourced`, citing the dated pulls. |

---

## `workforce_centers.csv` — one row per DFSS workforce center

Grain: one center. 5 rows. Source: Socrata `cs4s-nsna`, the tabular dataset
behind the portal's `i4rz-w47p` map view, pulled 2026-09-14.

**The stalest of the three, and the one whose stated vintage says least.** The
portal labels it a "Current list", which dates nothing, while its rows have not
been edited since **2011-08-21**. Five rows is a short enough list that a gap
means this file does not cover an area, not that employment services are absent
from it.

| Column | Type | Notes |
|---|---|---|
| `site_id` | text | The portal's row handle. **The join key** for `workforce_center_buildings.csv`. |
| `site_name` | text | As published — `Garfield Workforce Center`, and four more. |
| `hours_of_operation` | text | The published schedule, of 2011 vintage. |
| `address`, `zip`, `phone` | text | As published, including `7500 S. Pulaski, Bldg 100`. |
| `community` | text | Point-in-polygon. All five land inside a polygon. |
| `lat` / `lon` | decimal | WGS84 degrees. Every center has a coordinate. |
| `vintage` | text | `Current list`, which is not a date. |
| `rows_updated` | date | When the portal last changed the rows: `2011-08-21`. |
| `provenance` / `source` | text | `sourced`, citing the dated pulls. |

---

## `health_clinic_buildings.csv`, `senior_center_buildings.csv`, `workforce_center_buildings.csv`

Grain: one clinic (24), one senior center (21), one workforce center (5), joined
to their rosters on `site_id`. Every row has exactly one sidecar row, so a left
join loses nothing.

The same design as `school_buildings.csv`, `library_buildings.csv` and
`park_facility_buildings.csv`, built by **the same code, unchanged**, with the
same guarantee: **they do not replace the coordinates in the rosters.** Those
stay exactly as published and remain what distance work is computed against.
These files record the City footprint matched to each site, a point inside that
footprint where one was matched, and how confidently (`match_quality`).

Columns are identical to `school_buildings.csv` except that the key is
`site_id` in place of `sid`, and that `clinic_name` / `center_name` — plus
`category` on the clinic file and `program` on the senior center file — take
the place of `name`, so each file reads on its own. The name is prefixed for
the reason `cpd_bldg_name` is: `bldg_name` in these files is the City's name for
the **footprint**, a different name from a different publisher.

Source: Socrata `syp8-uezg` (*Building Footprints*), pulled within 160 m of each
site — the same extract method and radius as the school, library and park
sidecars, so offsets from all six files are comparable.

### `match_quality`

| Value | Clinics | Senior centers | Workforce centers | Meaning |
|---|---:|---:|---:|---|
| `address_exact` | 18 | 12 | 2 | Geometry and address agree. |
| `containing` | 1 | 1 | 1 | The point falls inside a footprint carrying no matching address. |
| `largest_nearby` | 5 | 8 | 2 | Nothing contains the point and no address matched. Recorded as a *candidate only*. |
| `no_match` / `no_point` | 0 | 0 | 0 | Every site has a coordinate and a footprint in range. |

35 of these 50 sites (70%) are placed inside a footprint on evidence strong
enough to assert it; the other 15 keep their address point and are flagged.
Snapping moves a marker a median of 27.1 m, 30.8 m and 22.8 m respectively.
The Kelvyn Park senior center (2715 N. Cicero) is unsnapped because its only
address match was across the street; the Garfield workforce center (10 S.
Kedzie) now snaps to the building on its own side.

`library_named` cannot appear in these files. `syp8-uezg` labels library
buildings, which is what earns that quality on the branch file; it carries no
comparable clinic, senior-center or workforce-center label, and inventing one
would assert a rule the source does not support.

### Known limitations

**The 2015 footprint snapshot applies here too.** Anything built or replaced
since is matched to whatever stood on the site, or to nothing.

**One clinic is placed in the wrong building on the right campus.** North River
MHC's (mental health center's) address, 5801 N. Pulaski, is North Park Village — one address across
several buildings, four of which the footprint file gives that same address
range. The shared rules take the address-matched footprint nearest the published
point, which is the 760 sq ft `NORTH PARK VILLAGE - GUARD HOUSE`, while the
27,646 sq ft footprint labeled `NORTH PARK VILLAGE - HEALTH CENTER` sits
further in. The marker lands about 25 m from CDPH's point, on the right campus
and in the wrong building on it. It is recorded rather than special-cased: a
one-row exception would stop these layers being positioned by the same method as
every other layer, and `bldg_name` names the building chosen so the error is
visible in the data rather than hidden by it.

**Suites, floors and hyphenated house numbers are not parsed.** `4909 W.
Division St., Suite 411` and `653-657 W. 63rd Street` are published as the City
writes them; the address parser declines both rather than guessing which part of
a building or which half of a range a site occupies. Those rows fall through to
containment or stay unsnapped.

**Three clinics share one footprint.** The rows at 641 W. 63rd St snap to the
same building and therefore to nearly the same point, as do the pairs at 4150 W.
55th and 4909 W. Division. That is the source recording several services in one
building, not a matching error; nothing is deduplicated.

---

## `facts.json` — the figures the project page states

Written by the build beside the tables; never hand-edited. One entry per figure
the project page states about buildings, seats, classrooms, enrollment,
distances and health centers, each with:

| Field | Meaning |
|---|---|
| `value` | The exact figure: a count, a percentage on a 0–100 scale, or a distance in miles. |
| `display` | The string the page prints, thousands separators and unit included (`"265"`, `"101,800"`, `"68%"`, `"2.1 miles"`). Hedge words such as "about" stay in the prose. |
| `label` | A short noun phrase for a stat tile. |
| `definition` | One sentence naming the file, the field and, for every count of buildings, the counting basis. |
| `source_file` | The file in this release the figure is computed from. |
| `sources` | Ids from the top-level `sources` list: the pulls behind it. |
| `rounding` | Set wherever `display` differs from the plain rendering of `value` (`"nearest 100"`, `"nearest percent"`, `"nearest tenth"`). |
| `unit` | `buildings`, `records`, `students`, `percent`, `miles`, … Never a metric unit. |

**The counting basis.** The utilization file's rows are school records, not
buildings: five addresses carry two scored schools each, and at one of them,
2400 S Marshall Blvd, both are labeled underutilized, so 266 underutilized
records stand in 265 buildings. Every fact that says buildings counts distinct
school addresses; the Spry pair's enrollments and spare classrooms are added
together, and distances measure each building to the nearest other building.
Facts that say records say so. `district_utilization` is the aggregate ratio
(utilization enrollment summed over the scored records over their summed
adjusted ideal capacity), not the mean of building rates.

The top level carries `release`, `school_year`, `coverage`, `generated_by`,
the `sources` list, and `invariants`: sums that are re-checked on every build.
`coverage` is the school year in ISO months, `start` 2025-08 and `end` 2026-06:
CPS’s 2025–26 calendar has students in grades K–12 in class from 2025-08-18 to
2026-06-04. `generated_by` names the script that writes the file, which is in
the private working repository and not published. Each source gives the date it
was pulled; the building footprints, pulled over two days, give the first as
`pulled` and the last as `pulled_last`. The health-center roster is dated by its
research: `pulled` and `verified_through` are the day AI agents checked it,
2026-09-12, its link names this release’s tag, and `sha256` is the hash of the
`sbhc_publish.csv` the figures were computed from.

## `community_area_summary.csv` — one row per community area

Grain: one community area. 77 rows, one per area in the City's boundary file,
sorted by number. Built from `schools.csv`, `utilization.csv` and
`sbhc_publish.csv` on the counting basis above.

| Column | Type | Notes |
|---|---|---|
| `community_area_num` | integer | The area's number in `igwz-8jzy` (`area_numbe`). |
| `community_area` | text | Its name as the boundary layer publishes it, matching `schools.csv` `community`. |
| `display_name` | text | `community_area` as the pothole release (Chicago-Potholes) spells it: title case, with O'Hare and McKinley Park. The name to print; `community_area` stays the key. |
| `schools_mapped` | integer | Schools in `schools.csv` located in the area. |
| `buildings_with_status` | integer | Distinct school addresses in the area with a CPS space-use status. |
| `underutilized_buildings` | integer | Distinct school addresses in the area whose records are labeled Underutilized. A count, not a recommendation: the label is CPS's. |
| `empty_seats_underutilized` | integer | Adjusted ideal capacity minus utilization enrollment, summed over the area's underutilized records. Empty where the area has no underutilized building. |
| `health_centers_operating` | integer | Operating school-based health centers located in the area by point-in-polygon on the sheet's coordinate, the same assignment the rosters use. |

The columns sum to the citywide figures (642, 491, 265, 101,818 and 33). There
is no rank column.

## `cdph_mental_health_centers.csv` — the seven centers CDPH lists today

Grain: one CDPH mental health center. 7 rows. The centers CDPH's *Mental
Health Centers* page listed on 2026-09-21, published so that the two distance
figures the article rests on — the median distance from an underutilized
building to the nearest center, and the underutilized records within a mile of
one — are reproducible from this release alone. AI agents compiled the seven rows from the
Chicago Department of Public Health's Mental Health Centers page on 2026-09-21; no person has
re-checked them.

| Column | Type | Notes |
|---|---|---|
| `name`, `address` | text | As CDPH's page listed them on 2026-09-21. |
| `lat` / `lon` | decimal | WGS84 degrees. |
| `coord_basis` | enum | `cdph_2016_roster`: the coordinate the City's 2016 clinic roster (`kcki-hnch`, `health_clinics.csv`) publishes for that address. `census_geocoder`: the U.S. Census Bureau geocoder, for the three centers on no published roster. |
| `note` | text | Lawndale has moved since the 2016 roster; Pilsen opened 2024; Roseland reopened 2025. |
| `source` | text | What the row was read from, in words: CDPH's page, and the roster or geocoder the coordinate came from. The one `source` column in the release that is not `key@YYYY-MM-DD`. |
| `accessed` | date | When the row was read: 2026-09-21. |

The map still draws the 2016 roster, the most recent CDPH publishes as data;
the article measures to these seven.

## `sbhc_publish.csv` — one row per school-based health center

Grain: one health center. 38 rows: 33 operating, two closed, one
closed-or-consolidated, and two unverified (the mobile units of TCA Health, Inc.,
or TCA). CPS states there are 33 centers citywide, the number marked
`operating`. Closed centers are
retained as historical records and are not evidence that a host school ceased
operating. The map draws every row with a fixed site; it hides closed centers by
default and omits the two mobile units, which have none.

This roster has no machine-readable primary source. It starts from four lists
pulled 2026-09-11 and joined in `data/source/sbhc.csv`, each one a different
definition of a center:

| Source key | What it is | Rows asserted |
|---|---|---:|
| `idph_shc_certified` | IDPH's list of certified school health centers (SHCs) in Chicago | 34 |
| `cps_health_centers_sheet` | CPS's health-center sheet (its provider column is labeled SY2021) | 32 |
| `hrsa_il_school_setting` | HRSA health-center sites in Illinois whose setting is School | 28 |
| `cps_schools_geojson_2025` | A CPS school file used only to join a center to its school's id, address, community and ward | — |

The health-center roster was researched by AI agents, which checked each
site's setting, access line and hours against the sponsor's own published pages
on 2026-09-12. No person has re-checked those findings, except the Johnson
center's setting, which the author confirmed from local knowledge. The agents
also drew on HRSA's 340B records and CPS's 2025–26 forms booklet, accessed the
same day. `build_resolved.py` applies the findings from `resolutions.py`; the
processed CSVs are its output and are never edited by hand. See
`docs/RESOLUTION_NOTES.md` for the source hierarchy and the evidence behind each
resolution.

### Columns

**Identity and join**

| Column | Type | Notes |
|---|---|---|
| `sponsor` | text | The public-facing operating unit (`Tapestry 360 Health`, `UI Health Mile Square Health Center`). One canonical name, resolved from the IDPH and CPS names, which often disagree (stale provider names, a rename, one real change of operator); the two source values stay in `sbhc_resolved.csv`. Esperanza at Cultivate Collective, which neither IDPH nor CPS lists, takes its sponsor from its own `hrsa_grantee`, written as the operator writes it (`Esperanza Health Centers`). The three closed or consolidated rows keep the sponsor names this release recorded for them and are not brought up to date: IDPH’s `Heartland Health Center` at Uplift, the name before the organization became Tapestry 360 Health in 2022-10; IDPH’s legal grantee, `Board of Trustees, U of I at Chicago`, at the Hope center; and `Near North Health` at Reavis. Blank only on the two unverified mobile units. |
| `sponsor_legal_name` | text | The legal grantee, where it differs from `sponsor` and has been established. Only the four UI Health rows: `Board of Trustees, U of I at Chicago`. |
| `site_name` | text | The input sheet's row label, unique, and the key `resolutions.py` joins on. **Not the host school**: on the Hope row it still reads `Wilma Rudolph Elementary Learning Center`, the school the input sheet wrongly matched. Use `school_name` and `sid` for the host. |
| `sid` | text | CPS id of the host school, read as text, joining to `schools.csv` and `utilization.csv`. Blank where there is no CPS host: the mobile units, Esperanza at Cultivate Collective, and the closed Hope Health & Wellness center (see below). Unique where present. |
| `school_name` | text | Host school as the evidence names it. Can be present without a `sid` when the host has no CPS id in this release (`Hope Institute Learning Academy`, `Academy for Global Citizenship`). |
| `idph_center_name` | text | The center's name on the IDPH certified list. Blank on the four rows IDPH does not list. |
| `campus_sids` | text | `;`-separated CPS ids of every school sharing the host building, on the two shared campuses (Greater Lawndale's four schools; Orr and KIPP One). A center there serves a campus, not one school. |
| `match_basis` | enum | How the row was joined to a school: `cps_school_id+cps_directory_address` (26), `cps_school_id+school_name` (5), `evidence_resolution` (3, rows whose original address join was wrong and which the evidence fixed), `hrsa_site_name_mobile` (2), `cps_offsite_override` (1, Mansueto) and `unmatched` (1, Cultivate Collective). |

**Where it is**

| Column | Type | Notes |
|---|---|---|
| `setting` | enum | `in_building` (33): inside CPS school space. `school_linked` (3): serves a school from a separate building (Johnson, Gary Comer, Mansueto). `mobile` (2): no fixed site. |
| `site_address` | text | The center's own address, which can differ from the school's: Farragut's clinic has its own entrance at 3256 W 24th St. |
| `school_address` | text | The host school's building address, from the CPS school file. |
| `zip` | text | The center's zip. |
| `community`, `ward` | text | Community area and ward of the host school's building, from the CPS school file. Blank where there is no host school. |
| `lat` / `lon` | decimal | WGS84 degrees. Where the **center** is, never a school it is merely linked to; `coord_basis` says where each came from. The two mobile units carry HRSA's coordinate for their operator's office, which is why the map does not draw them. |
| `coord_basis` | enum | `hrsa_site` (28): HRSA's geocode of the registered site. `cps_school_building` (8): the host school's building point, used only for `in_building` rows. `cdph_2014_geocode` (1): CDPH's 2014 geocode of the Gary Comer Youth Center, an address that has not changed. `cps_offsite_override` (1): CPS's own off-site point for Mansueto's clinic. |
| `room_or_entrance` | text | A published room number or named exterior door, on 15 `in_building` rows. The strongest evidence that a center occupies school space; never set on a `school_linked` or `mobile` row. |

**Which list asserts it**

| Column | Type | Notes |
|---|---|---|
| `idph_certified` | boolean | On IDPH's certified list. 34 rows. |
| `cps_listed` | boolean | In CPS's health-center sheet. 32 rows. |
| `hrsa_scope` | boolean | In HRSA's school-setting site list. 28 rows. The three flags are never collapsed into one, and every row has at least one `true`. |
| `hrsa_site_num` | text | HRSA's Bureau of Primary Health Care (BPHC) site number, e.g. `BPS-H80-013554`. Unique. |
| `hrsa_site_name`, `hrsa_grantee` | text | HRSA's site name and grantee, verbatim and in HRSA's capitals. |
| `hrsa_setting_desc`, `hrsa_site_type`, `hrsa_status`, `hrsa_sbhc_subprogram` | text | HRSA's setting (`School` on every row it lists), site type, status (`Active`) and school-based subprogram flag (`N` on all 28), verbatim. `hrsa_status` was not re-verified and asserts nothing about current operation. |

All nine HRSA columns are blank on the 10 rows HRSA does not list.

**Access and hours**

| Column | Type | Notes |
|---|---|---|
| `access_text` | text | Who may use the center, in the wording CPS or the operator publishes (`Open to the Community: No Restrictions`, `Open to Enrolled Students at the School`). Blank on the three closed rows, the two mobile units, and Cultivate Collective, which CPS does not list. |
| `open_to_public` | boolean | `true` only where `access_text` opens the center to the community (15 rows). Never `true` on a closed row. Blank where `access_text` is. |
| `phone` | text | The center's phone as published. Blank on four rows where no current number was established. |
| `hours_medical_school_year` | text | School-year medical schedule, as the operator or CPS writes it. Blank means not established. |
| `hours_medical_summer` | text | Separate summer schedule where published (Mile Square's two schools; its window is published without a year). Blank never means “same as school year.” |
| `hours_dental` | text | Separate dental schedule where published (Hibbard). |

No hours column is ever filled on a closed row.

**Status**

| Column | Type | Notes |
|---|---|---|
| `operational_status` | enum | `operating`, `closed`, `closed_or_consolidated`, or `unverified`; required on every row. |
| `closed_on` | date | Present only when a source supplies an actual date (both closed rows: 2024-04-01, from HRSA's 340B termination records). `closed_or_consolidated` Reavis correctly has none. |

**Provenance**

| Column | Type | Notes |
|---|---|---|
| `source` | text | The input lists that assert the row, with their pull dates, joined by `+`. |
| `review_note` | text | The input sheet's own note on a join it flagged for review (a shared campus, an off-site center, a transposed IDPH entry). Nine rows. |
| `resolution_fields` | text | Every field the build checked on this row, with its confidence, e.g. `phone(high) setting(medium)`. `hours_split(carried)` means the input sheet's single hours value was carried into `hours_medical_school_year` with no split researched. |
| `resolution_confidence` | enum | Worst confidence among the row's findings: `high`, `medium`, `low`, or `unresolved`. |
| `resolution_sources` | text | Every URL behind the row's resolutions, joined by ` \| `. Each appears in `data/source/evidence_manifest.csv`. |
| `resolution_note` | text | The finding behind each resolved field, prefixed by the field name in brackets. |
| `verified_on` | date | The evidence access date, 2026-09-12. Not a claim of manual field verification. |

### Space-use status is not in this file

Join `sid` to `utilization.csv` for a host school's space-use status. An earlier
release published `cps_status_2025`, `cps_adjusted_su` and `cps_colo` here,
copied from the `cps_schools_geojson_2025` file. They were an older vintage than
`utilization.csv`, were not labeled as one, and disagreed with it for five host
schools (Marquette, National Teachers, Gary Comer, Sullivan and Roosevelt). They
are retired from both processed sheets; `data/source/sbhc.csv` keeps them because
the build does not modify its inputs.

### The Hope Health & Wellness center has no `sid`

The row labeled `Wilma Rudolph Elementary Learning Center` is IDPH's Hope Health
& Wellness SHC at 1628 W Washington Blvd, which closed 2024-04-01. The input sheet
matched it to Wilma Rudolph (`610308`) because the two share an address. The only
source naming its host school, UIC's announcement of 2014-12-11, names Hope
Institute Learning Academy, which has no CPS id in this release, so `sid` is
blank and `school_name` names Hope. The CPS profile API now places Rudolph at the
same address; no source ties the center to Rudolph.

### The two companion files

`sbhc_resolved.csv` is the audit sheet: 33 of the 37 input columns unchanged
(`manually_verified` and the three space-use columns are retired), then a
`resolved_*` column beside each field the evidence changed — `resolved_sponsor`,
`resolved_setting`, `resolved_site_address`, `resolved_zip`, `resolved_phone`,
`resolved_hours`, `resolved_access_text`, `resolved_school_name`,
`resolved_operational_status`, `resolved_lat_lon` — then the schema and
provenance columns above. It also keeps the input's `sponsor_cps`,
`sponsor_idph` and single `hours` columns, which the publication sheet replaces.
An empty `resolved_*` cell means that field was not changed. The input `sid` is
kept here for audit; the correction lives in `sbhc_publish.csv` and the findings.

`sbhc_discrepancies.csv` is the evidence table, 153 rows, one per center-field
finding:

| Column | Notes |
|---|---|
| `site_name`, `sid` | The row, under its corrected `sid` (read as text). |
| `field` | The field examined. `hours_split`, `room_or_entrance` and `sid` are findings about the new columns. |
| `cps_value`, `idph_value`, `other_value` | Each source's value as found, blank where that source is silent. |
| `resolved` | The value the evidence supports, or blank where it settles nothing. |
| `confidence` | `high`: the operator's own current page, or two independent current official sources agree. `medium`: one credible current source. `low`: sources conflict and none resolves it. `unresolved`: recorded for review, no value asserted. |
| `sources`, `accessed`, `note` | Citations (`; `-separated URLs), access date, and the reasoning. |

Five source fields remain unresolved rather than inferred: Drake's school-year
medical hours and phone conflict across UI Health/CPS pages; Greater Lawndale's
hours conflict with a provider-claimed listing while the operator publishes
none; Hibbard's former combined `hours` value cannot itself be resolved even
though the medical/dental schedules are separated into the new columns; and
Reavis's historical hours are not published because the center is not
established as operating. See `docs/RESOLUTION_NOTES.md` for full evidence.

### The evidence behind it

The findings consulted 38 pages, PDFs and datasets and cite 36 of them. All 38
are third-party material and are not republished here.
`data/source/evidence_manifest.csv` records each one:
`source_key`, the `requested_url` and the `final_url` actually served, `accessed`,
`content_type`, `bytes`, and the `sha256` of the capture, which is preserved
privately. Two were captured from the Internet Archive because the live URL failed
on the day, and three had an unrelated embedded credential redacted before
hashing; `note` says which. `snapshot_sources.py` recaptures them and can check a
capture directory against the manifest.

The CPS 2025–26 student-health forms booklet p.11 is the only current
CPS-published directory used here, and it covers only the “Open to ALL CPS
Students” subset — not all 33 centers. The CDPH dataset `cjg8-dbka` is a 2014
snapshot last updated 2014-04-22; it is used only to corroborate unchanged
addresses and geocodes, never current status.
