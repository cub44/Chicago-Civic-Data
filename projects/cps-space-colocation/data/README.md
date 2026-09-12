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
| `layer` | text | — | derived | Reconstructed from governance × grade category. Only the district and charter layers are derivable from these sources; the snapshot's private layers have no source at all, so they are absent here rather than manufactured. |
| `governance` | text | — | `cps_school_profiles` (`Governance`) | District, Charter, ALOP, Contract, SAFE. Empty for the one school present only in the space-use file. |
| `school_type` | text | — | `cps_school_profiles` (`SchoolType`) | Empty string in the API for many schools; stored as empty, not as `"nan"`. |
| `grades` | text | — | `cps_school_profiles` (`GradesOffered`) | |
| `community` | text | — | `socrata_igwz-8jzy` | Point-in-polygon assignment. Falls back to the API's own `Community` field only when the point lands outside every polygon. Empty where coordinates are absent. |
| `address` | text | — | `cps_school_profiles` | `AddressStreet` + zip. Empty when unavailable. |
| `lat` / `lon` | float | WGS84 degrees | `socrata_pb6d-zzuh`, falling back to `cps_school_profiles` | See "missing coordinates" below. |
| `provenance` | text | — | derived | `sourced` or `unverified`. Source status. |
| `source` | text | — | derived | Source keys and pull dates that produced the row. |

**Missing coordinates (7 rows).** The profile API returns `0.0 / 0.0` — null
island — for six district schools recently converted from Acero charter
campuses (`610602`–`610607`), and one school (`400105`, Urban Prep –
Bronzeville) appears only in the space-use file with no geometry anywhere.
Zero is recognised as a missing sentinel and stored as empty. It is **not**
interpolated. The set is pinned in `tests/test_validate.py`; a new absence
fails the build.

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

## `sbhc_publish.csv` — one row per school-based health centre

Grain: one health centre. 38 rows: 32 operating, two closed, one
closed-or-consolidated, and three unverified. Closed centres are retained as
historical records and are not evidence that a host school ceased operating.

The build also emits `sbhc_resolved.csv`, which preserves the 37 input columns
and adds parallel `resolved_*` values, and `sbhc_discrepancies.csv`, one row per
site-field finding with source values, resolution, confidence, citations, and
access date. Processed CSVs are generated by `build_resolved.py`; do not edit
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
