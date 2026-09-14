# Data dictionary

Snapshot: 9 September 2026. CSVs are UTF-8; blank cells mean missing, not zero. Join school tables on `sid`, read as text. `su_pct` is a ratio: 0.70 means 70%.

### Source-level limitations

- **The profile API contradicts itself on vintage.** It reports
  `SchoolProfileYear: 2026` and `SchoolYearReadable: "School Year 2024-2025"` on
  all 641 records. Its `StudentCount` differs from the snapshot's profile
  enrollment on 477 of 483 comparable rows. Treat `enrollment_profile` as an
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
  size, staffing level or programme-space figure, and its hours field is the
  usual published schedule, not a record of any given day.
- **Portal datasets get revised retroactively.** Raw pulls are dated and
  preserved privately, and the build reads those snapshots, so published numbers
  stay reproducible after an upstream revision.

---

## `schools.csv` — one row per school

Grain: one school. 642 rows.

| Column | Type | Units | Source | Notes and limitations |
|---|---|---|---|---|
| `sid` | integer | — | `cps_school_profiles` (`SchoolID`) | 6-digit CPS id. District ids begin 6, charter ids begin 4. Unique in this file. |
| `name` | text | — | `cps_school_profiles` (`SchoolLongName`) | |
| `layer` | text | — | derived | Reconstructed from governance × grade category. Only the district and charter layers are derivable from these sources; private schools have no source at all, so they are absent here rather than manufactured. |
| `governance` | text | — | `cps_school_profiles` (`Governance`) | District, Charter, ALOP, Contract, SAFE. Empty for the one school present only in the space-use file. |
| `school_type` | text | — | `cps_school_profiles` (`SchoolType`) | Empty string in the API for many schools; stored as empty, not as `"nan"`. |
| `grades` | text | — | `cps_school_profiles` (`GradesOffered`) | |
| `community` | text | — | `socrata_igwz-8jzy` | Point-in-polygon assignment. Falls back to the API's own `Community` field only when the point lands outside every polygon. Empty where coordinates are absent. |
| `address` | text | — | `cps_school_profiles` | `AddressStreet` + zip. Empty when unavailable. |
| `lat` / `lon` | float | WGS84 degrees | `socrata_pb6d-zzuh`, falling back to `cps_school_profiles` | See "missing coordinates" below. |
| `student_count` | integer | students | `cps_school_profiles` (`StudentCount`) | The API's own headcount, of uncertain vintage. Published for every school, unlike `enrollment_20th_day`, which exists only where CPS scores the building. **Do not use it where `enrollment_20th_day` exists.** See "headcount" below. |
| `provenance` | text | — | derived | `sourced` or `unverified`. Source status. |
| `source` | text | — | derived | Source keys and pull dates that produced the row. |

**Missing coordinates (7 rows).** The profile API returns `0.0 / 0.0` — null
island — for six district schools recently converted from Acero charter
campuses (`610602`–`610607`), and one school (`400105`, Urban Prep –
Bronzeville) appears only in the space-use file with no geometry anywhere.
Zero is recognised as a missing sentinel and stored as empty. It is **not**
interpolated. The set is pinned in `tests/test_validate.py`; a new absence
fails the build.

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
| `sid` | integer | — | `School ID` | |
| `school_year` | text | — | derived | `SY2026` throughout. |
| `grade_category` | text | — | `Grade Category` | ES or HS **as the space-use file assigns it**, which is not always the school's overall band. Noble – Gary Comer is a high school whose co-located rows cover grades 6–8 and are scored ES. This column, not the school's layer, governs the capacity rule. |
| `enrollment_profile` | integer | students | `cps_school_profiles` `StudentCount` | Uncertain vintage — see source limitations. |
| `enrollment_20th_day` | integer | students | `20th Day Enrollment` | Total enrollment at the 20th day. |
| `enrollment_utilization` | integer | students | `Adjusted SY2026 20th Day School Enrollment` | The numerator of the published rate. **Excludes students assigned to cluster *or* pre-K programme classrooms** — see the note below. |
| `homerooms` | float | homerooms | **derived** | Not published by CPS. Computed from `classrooms_demand` by the rule below and asserted against published capacity. Empty for the 14 co-located rows that carry no classroom counts. |
| `ideal_capacity` | integer | seats | `Ideal Capacity (IC) for Permanent Bldg Only` | Permanent building only.  |
| `adj_ideal_capacity` | integer | seats | `Adjusted IC 2 After CR Deductions` | The denominator of the published rate, after classroom deductions. |
| `su_pct` | float | ratio (1.0 = 100%) | `SY2026 Adjusted SU 2` | Published rate. Equals `enrollment_utilization / adj_ideal_capacity` to within 0.01. |
| `cps_status` | text | — | `Space Use Status` | Underutilized / Efficient / Overcrowded. Empty for the 14 rows without capacity. |
| `classrooms_supply` | float | classrooms | `Total Classrooms (CRs)` | Fitting the published file shows this is total *permanent* classrooms; rooms under 650 sq ft count as 0.5, which is why the column is fractional. Excludes modular and leased space. Retains this label until CPS confirms. |
| `classrooms_modular` | float | classrooms | `Modular CR's` | |
| `classrooms_leased` | float | classrooms | `Leased CR's` | |
| `classrooms_demand` | float | classrooms | `Total CR's Less Cluster, Pre-K, Other & Small` | Fitting shows this is *not* a demand measure at all: it is `(permanent + modular + leased) − (cluster + pre-K + other + small)`, i.e. an adjusted supply figure. The legacy name is retained for compatibility; interpret it as adjusted classroom supply. |
| `source` | text | — | derived | |

### The capacity rule

CPS publishes adjusted classrooms and adjusted ideal capacity, but no homeroom
count. Fitting the published SY2026 file recovers the rule exactly:

```
ES:  homerooms      = floor(classrooms_demand × 0.77)
     adj_ideal_capacity = homerooms × 28          417/417 exact

HS:  homerooms      = classrooms_demand × 0.80
     adj_ideal_capacity = homerooms × 30           79/79 exact
```

**The elementary seat figure is 28, not 30.** This is asserted by
`test_capacity_rule`; if CPS changes the rule the build fails rather than
drifting.

### What the utilization enrollment actually excludes

CPS's own data dictionary defines the student deduction as **"Students Assigned
to Cluster or PK programs"** — cluster programmes being separate-classroom
placements for students needing significantly modified curriculum with moderate
to intensive support for over 61% of the day.

Pre-K alone does not account for it. 56 schools that serve no pre-K still show
`enrollment_utilization < enrollment_20th_day`, including Lane Tech (−63),
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
co-located service. `test_zero_permanent_classrooms_is_explained_by_leased_space`
asserts that a zero is always corroborated by non-permanent space, so a zero
meaning "unknown" would still fail.

---

## `colocation_campuses.csv` — one row per co-located campus

Grain: one campus. 16 rows. Not in the brief; added because CPS publishes it and
it is the natural unit for this analysis.

The space utilization workbook's `Data - Co-Locations` sheet carries
campus-level subtotals for buildings shared by two or more schools — for example
`ES/HS COLO 1: KIPP - ONE & ORR HS`. Columns mirror `utilization.csv`;
`campus_label` is CPS's own label (`ES COLO 1`, `HS COLO 2`, …), which is a
label and not a school id.

---


Except for the public evidence bundle for the 2026-09-12 SBHC reconciliation,
raw snapshots, historical tables, and the broader processing pipeline are
maintained privately.

---

## `school_buildings.csv` — one row per school, building coordinate

Grain: one school, joined to `schools.csv` on `sid`. 642 rows — every school in
`schools.csv` has exactly one row here, so a left join loses nothing.

**This file does not replace the coordinates in `schools.csv`.** Those stay
exactly as published: `lat`/`lon` there are the answer to "where is this
address", which is what any distance, catchment or nearest-service work has to
be computed against. This file adds a second, differently derived coordinate —
a point *inside* the school's building — and states how confidently it was
derived, so a consumer decides for itself which one to use. The map uses the
building point where it is well established and falls back to the source point
everywhere else.

Source: Socrata `syp8-uezg` (*Building Footprints*), reached from the
`Building Footprints - Map` view `hz9b-7nh8`. The extract pulls the footprints
within 160 m of each school point rather than all 820,606 citywide.

| Column | Type | Notes |
|---|---|---|
| `sid` | integer | CPS school id. Joins to `schools.csv`. |
| `match_quality` | enum | How the building was established. See below. Only `address_exact` and `containing` assert "this is the building". |
| `bldg_lat` / `bldg_lon` | decimal | Pole of inaccessibility of the matched footprint — the interior point furthest from any wall. Empty for `no_match` and `no_point`. |
| `offset_m` | metres | Distance from the `schools.csv` point to `bldg_lat`/`bldg_lon`. How far the marker moved. |
| `edge_m` | metres | Distance from the `schools.csv` point to the footprint's nearest wall; `0` means the source point falls inside the footprint. |
| `bldg_id` | integer | `syp8-uezg` building id, so any match can be re-checked against the source. |
| `bldg_address` | text | Address the footprint itself carries, for comparison against the school's. |
| `bldg_name` | text | Building name in the footprint file, where it has one. Not used for matching, so it is an independent check: 74 of the 80 named snapped buildings carry a school name. |
| `bldg_stories` | integer | From the footprint file. Absent where the source is blank. |
| `footprint_area_sqft` | number | The source's own `shape_area`, in square feet, republished unconverted. |
| `candidates_in_range` | integer | Footprints within the extract radius. A high count is a dense block, not a problem. |

### `match_quality`

| Value | Rows | Meaning |
|---|---|---|
| `address_exact` | 501 | Geometry and address agree: the footprint's address range and street match the school's, and the school point is inside it or within 60 m of its wall. |
| `containing` | 16 | The school point falls inside the footprint, but the footprint carries no address or a non-matching one. Direct geometric evidence. |
| `largest_nearby` | 116 | Nothing contains the point and no address matched within 60 m. The largest footprint in range is recorded as a *candidate only*. |
| `no_match` | 2 | A school point exists but the source has no footprint within 160 m. Verified against the portal, not a gap in this extract. |
| `no_point` | 7 | `schools.csv` has no coordinate, so there was nothing to match — the seven schools already reported as unmappable above. |

The 60 m cap on non-containing address matches is load-bearing. Chicago
footprint address ranges span a whole block face, so "house number inside
`f_add1`–`t_add1` on the same street" collides freely with a school's
neighbours. Without the cap the match confidently placed one charter school on
the police station down the block and a high school on a 326 m² outbuilding
137 m away. Those rows are now `largest_nearby` and the map leaves them alone.

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

Grain: one Chicago Public Library branch. 82 rows. Snapshot pulled
13 September 2026; the source's rows were last updated 24 August 2026.

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
| `address` | text | As published, with CPL's abbreviating full stops. |
| `zip` | text | `city` and `state` are omitted: both are constant across all 82 rows. |
| `phone`, `email`, `website` | text | Published branch contact details. |
| `service_hours` | text | **The usual published schedule, not an observed opening record.** Verbatim free text, not parsed into structured hours — doing so would impose a precision the field does not have. |
| `community` | text | Community area, assigned by point-in-polygon against `igwz-8jzy`, the same way `schools.csv` assigns it, so the two are comparable. All 82 fall inside a polygon. |
| `lat` / `lon` | decimal | WGS84. Every branch has a coordinate; unlike the school roster there are no gaps. |
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

## `library_buildings.csv` — one row per branch, building coordinate

Grain: one branch, joined to `libraries.csv` on `name`. 82 rows — every branch
has exactly one row, so a left join loses nothing.

The same design as `school_buildings.csv`, built by the same code, and with the
same guarantee: **it does not replace the coordinates in `libraries.csv`.**
Those stay exactly as published and remain what distance work is computed
against. This file adds a point *inside* the branch's building and states how
confidently it was derived. Columns are identical to `school_buildings.csv`
except that the key is `name` rather than `sid`.

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

`syp8-uezg` carries a building-use label: 65 of the 8,980 footprints in this
extract name a library in `bldg_name1` or `bldg_name2`, most as the City's own
`CHICAGO PUBLIC LIBRARY`. That is the same class of evidence as the address
range the matcher already trusts — a field the publisher of the geometry
attached to the footprint — and a better one, because an address range describes
a whole block face while a use label describes that building.

Checked against the branches the address rule already matched, the label agrees
with the footprint chosen in 56 of 58 cases, and no branch has two labelled
footprints within 60 m. Both disagreements are cases the label gets right and
the address rule gets wrong: Gage Park sits 0.5 m outside the footprint the City
labels `GAGE PARK` and just inside its unlabelled neighbour; Whitney M. Young,
Jr. matched an address range 54.8 m away — inside the cap, but exactly the
block-face collision that cap exists to bound — while its labelled footprint is
18.1 m away. Six further branches are corner sites addressed on the cross
street (Albany Park, Back of the Yards, Bezazian, Douglass, King, North
Pulaski), which the address rule could never reach.

Where label and address agree the row stays `address_exact`: the stronger claim
is kept rather than overwritten. The school footprints carry no comparable
labelling, so `school_buildings.csv` can never contain this value.

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

## `sbhc_publish.csv` — one row per school-based health centre

Grain: one health centre. 38 rows: 32 operating, two closed, one
closed-or-consolidated, and three unverified. Closed centres are retained as
historical records and are not evidence that a host school ceased operating.

The build also emits `sbhc_resolved.csv`, which preserves 36 of the 37 input
columns and adds parallel `resolved_*` values, and `sbhc_discrepancies.csv`,
one row per site-field finding with source values, resolution, confidence,
citations, and access date. Processed CSVs are generated by `build_resolved.py`; do not edit
them directly.

| Column | Type | Notes |
|---|---|---|
| `operational_status` | enum | `operating`, `closed`, `closed_or_consolidated`, or `unverified`; required on every row. |
| `closed_on` | ISO date | Present only when a source supplies an actual date. A closed row may correctly remain blank. |
| `hours_medical_school_year` | text | School-year medical schedule. Blank means not established. |
| `hours_medical_summer` | text | Separate summer schedule where published. Blank never means “same as school year.” |
| `hours_dental` | text | Separate dental schedule where published. |
| `room_or_entrance` | text | Published room or named exterior entrance; present only for `in_building` rows. |
| `sponsor` | text | Canonical public-facing operating unit. |
| `sponsor_legal_name` | text | Legal grantee where it differs and has been established. |
| `resolution_confidence` | enum | Worst confidence among the row's findings: `high`, `medium`, `low`, or `unresolved`. |
| `resolution_sources` | URL list | Visible provenance for resolved fields. |
| `verified_on` | ISO date | Evidence access date, not a claim of manual field verification. |

The input sheet's `manually_verified` column is no longer published in either
processed sheet. It was the pre-publication review gate, it read `false` on all
38 rows, and the gate it served has been replaced. `data/source/sbhc.csv` still
carries it, since the build does not modify its inputs.

Five source fields remain unresolved rather than inferred: Drake's school-year
medical hours and phone conflict across UI Health/CPS pages; Greater Lawndale's
hours conflict with a provider-claimed listing while the operator publishes
none; Hibbard's former combined `hours` value cannot itself be resolved even
though the medical/dental schedules are separated into the new columns; and
Reavis's historical hours are not published because the centre is not
established as operating. See `docs/RESOLUTION_NOTES.md` for full evidence.

The CPS 2025-26 student-health forms booklet p.11 is the only current
CPS-published directory used here, and it covers only the “Open to ALL CPS
Students” subset—not all 33 centres. The CDPH dataset `cjg8-dbka` is a 2014
snapshot last updated 2014-04-22; it is used only to corroborate unchanged
addresses and geocodes, never current status.
