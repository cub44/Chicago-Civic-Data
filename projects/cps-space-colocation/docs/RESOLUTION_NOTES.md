# SBHC cross-source reconciliation — 2026-09-12

152 field-level findings across all 38 rows of `sbhc.csv`, including the three schema
additions applied in this revision and the `sid` correction added in the 2026-09-21
release. 5 source-field findings are deliberately left null — 9 rows in
`sbhc_discrepancies.csv` carry `confidence = unresolved` once the two derived
`hours_split` rows and the two mobile units' unverified `operational_status`
rows are counted alongside them.

**Revision 2 (2026-09-12):** Johnson resolved to `school_linked` on local knowledge; added
`operational_status` + `closed_on`, split `hours` into `hours_medical_school_year` /
`hours_medical_summer` / `hours_dental`, and added `room_or_entrance`.

Neither input sheet was modified. Outputs:

- `sbhc_discrepancies.csv` — the evidence table, one row per (site, field): each source's
  value as found, the resolved value, confidence, citations, access date.
- `sbhc_resolved.csv` — `sbhc.csv`'s columns untouched (less four retired ones:
  `manually_verified` and the older-vintage `cps_status_2025`, `cps_adjusted_su`, `cps_colo`), plus `resolved_*` columns so the
  two can be diffed, plus per-row citations and confidence. This is the audit artifact.
- `sbhc_publish.csv` — the canonical sheet. Resolved values overlay the canonical columns,
  the superseded `hours` column is dropped, a single `sponsor` column replaces having to
  pick between `sponsor_cps` and `sponsor_idph`, and closed sites are retained with a
  status rather than deleted.
- `test_sbhc_publish.py` — passes against `sbhc_publish.csv`.

## Source hierarchy applied

1. The operator's own current site (Erie, Tapestry, Rush, Alivio, LCHC, UI Health Mile
   Square, TCA, Esperanza, Near North).
2. HRSA administrative records — the 340B OPAIS entity pages carry site-level status and
   termination dates, which is the only source that dates a closure.
3. CPS's current published directory (2025-26 forms booklet, p.11).
4. The IDPH certified list and the uploaded CPS sheet.
5. CDPH's health-center dataset — **note this is a 2014 snapshot** (rows last updated
   2014-04-22). Used only to corroborate addresses that have not changed, never for
   current status or provider names.

Two vintage problems drive most of the conflicts. The IDPH certified list is stale on
provider names and phones by several years. The uploaded CPS sheet's provider column is
named `SY2021_School_Health_Center`, and its hours in particular look like SY2021 values;
CPS's 2025-26 booklet supersedes it where the two differ.

## Three centers in the IDPH list are not currently operating

This is the most consequential finding, because all three are in `sbhc.csv` as live rows
with `idph_certified=true`, and two of them carry a coordinate that would put a dot on a map.

| Center | Evidence | Date |
|---|---|---|
| Uplift SHC (900 W Wilson Ave) | 340B site BPS-H80-010055 terminated, "Business decision by the Covered Entity"; absent from Tapestry 360's six-site student-health list | 2024-04-01 |
| Hope Health & Wellness SHC (1628 W Washington Blvd) | 340B site BPS-H80-010036 terminated, reason **"Site closure"**; absent from Mile Square's current four-site list | 2024-04-01 |
| Reavis SHC (834 E 50th St) | Absent from Near North Health's locations page (modified 2026-09-11); the former Reavis page URL now resolves to that page, which announces consolidation into three locations | — |

Reavis is absence-of-evidence rather than a closure notice, so it is marked
`closed_or_consolidated` at medium confidence. The other two are documented terminations.

CPS states there are **33** SBHCs citywide, which is exactly the number of rows this sheet
marks `operating`. Dropping these three from the IDPH count of 34 leaves 31, which is
consistent with the CPS sheet's 32 rows once Mansueto (CPS-only) is included — the three
IDPH-only rows were the discrepancy, not a coverage gap.

## A bad school match

`Wilma Rudolph Elementary Learning Center` is wrong. 1628 W Washington Blvd is **Hope
Institute Learning Academy** — UIC's own announcement names it directly. `sbhc.csv` joined
the IDPH entry to Rudolph by address identity, and the `match_basis=address_identity` value
is what flagged it. The other two `address_identity` rows (Uplift, Reavis) are the closed
sites. That join rule produced three bad rows out of three; worth retiring.

The 2026-09-21 release also blanks this row's `sid`. `school_name` had already been
corrected to Hope, but `sid` still read `610308`, Rudolph's id, so the published row named
one school and joined to another. Hope Institute Learning Academy has no CPS id in this
release, and UIC's announcement, the only source naming the host, dates from 2014-12-11.
The CPS profile API now places Rudolph at the same address; nothing ties the center, which
closed 2024-04-01, to Rudolph.

Separately, `Military Leadership Academy` (sid 609780) is a stale CPS label. Both the
uploaded CPS sheet and the 2025-26 booklet say **Marine Leadership at Ames HS**.

## In school vs linked to one

- **Farragut → in_building.** LCHC states the clinic is "located within Farragut Career
  Academy." The 3256 W 24th St address is the clinic's own entrance on the school's south
  frontage, not a separate building. The center address should be 3256 W 24th St; the school
  address stays 2345 S Christiana Ave.
- **Davis → in_building** (was `school_linked`). IDPH names it "3050 W. 39th Pl. **Annex**",
  i.e. CPS space on the Davis campus; CPS and UI Health both publish the center there. For a
  co-location analysis this is CPS building space. Medium confidence — it turns on whether
  the annex is a separate structure.
- **Comer → school_linked confirmed.** The center is inside the Gary Comer Youth Center
  (7200 S Ingleside Ave), a different building from Gary Comer College Prep (7131 S South
  Chicago Ave). The null coordinate can be filled from CDPH's geocode of that address
  (41.764002, -87.601896) — set `coord_basis='cdph_2014_geocode'`, not
  `cps_school_building`, since `test_sbhc_publish.py` rightly forbids mapping a school-linked
  center at its school's coordinate.
- **Mansueto → school_linked confirmed, and operating.** The center is Esperanza's Brighton
  Park clinic at 4700 S California Ave, about a kilometer from the school. CPS's off-site
  override is right, and the IPHCA locator carries the site as current.
- **Cultivate Collective → host school is Academy for Global Citizenship**, the CPS charter
  on that campus. Note this site is neither IDPH-certified nor in CPS's directory; it may not
  meet a strict SBHC definition at all.
- **Both TCA mobile units → correctly null.** TCA says the Mobile Student Health Clinic
  "travels to various schools on Chicago's far south side." There is no host school to
  resolve; HRSA registers them at TCA's main clinic. The null is the answer, not a gap.
- Rush and Tapestry publish **room numbers** for every site (Dunbar Rm 208, Phillips Lower
  Level, Orr Rm 109, Crane Rm 110, Senn Rm 144, Roosevelt Rm 166, Gale Rm 107, Kilmer Rm 109,
  Sullivan Rm 100), Erie gives Ward an entrance on Ridgeway Ave, and Mile Square gives
  Englewood STEM "Door 2". These are in neither source sheet and are the cleanest available
  evidence of in-building placement.

## Provider names

- **Heartland Health Center → Tapestry 360 Health** (renamed 2022-10) at all six sites:
  Gale, Hibbard, Kilmer, Roosevelt, Senn, Sullivan. IDPH is stale; CPS is right.
- **Dunbar and Phillips are Rush, not Mercy.** Rush lists both among its five SBHCs and
  publishes the same phones CPS carries. This is the one sponsor discrepancy that is a real
  change of operator rather than a rename.
- `Esperanza Clinic` → Esperanza Health Centers. `PCC Community Center Wellness` → PCC
  Community **Wellness Center** (IDPH transposes the words). `Friend Family Health Center`
  → Friend Health (corporate name unchanged). `PrimeCareHealth Community Health Centers`
  → PrimeCare Community Health (the CPS value is a malformed concatenation). `ACCESS
  Community Health Center` → Access Community Health **Network** (here IDPH is right and
  CPS is wrong).
- `Board of Trustees, U of I at Chicago` vs `UI Health` is **not** a conflict — legal
  grantee vs brand. The operating unit is UI Health Mile Square Health Center. Worth a
  separate `sponsor_legal_name` column rather than forcing a single value.
- `Near North/Komed-Homan Health Center` conflates two separate Near North sites; Komed
  Holman is at 4259 S Berkeley Ave and is not the Reavis sponsor.

## Hours

Erie publishes one schedule for all five of its school sites — **M/Tu/Th/F 8:00–4:30,
W 10:00–4:30**. Amundsen, Lake View and Ward match; **Clemente and Johnson do not** and both
CPS sources miss the Wednesday 10am open.

Other corrections: **Senn** is Mon–Fri 8:00–4:00, not the three days CPS lists (operator page
modified 2026-08-17). **Farragut** runs to 7:00pm on Tuesdays, which both CPS sources miss.
**Carver** is Mon–Fri 9:00–4:00 per TCA, against CPS's Mon–Wed 9:00–1:00 — a large gap, and
the TCA page is dated 2023, so this one deserves a phone call.

Mile Square publishes separate **school-season and summer** hours (summer window Jun 16 –
Aug 8). `sbhc.csv` has one hours field, so it cannot represent this; Davis and Drake both
need two fields. The CPS 8:00am open for Davis may simply be the summer value.

## Left null on purpose

Five findings where sources conflict and no operator statement breaks the tie. Per the repo
rule, these stay empty rather than being split or averaged:

1. **Drake `hours`** and **`phone`** — UI Health's two own pages disagree with each other
   (8:00–4:00 vs 8:30–4:30; ...5745 vs ...5746).
2. **Little Village Lawndale `hours`** — a provider-claimed third-party listing shows a much
   narrower week including a Wednesday closure; Alivio publishes no hours for the site.
3. **Hibbard `hours_medical_school_year` vs `hours_dental`** — the split is now applied,
   but the medical/dental attribution is inferred from the access note rather than published
   by Tapestry, so it is medium confidence and worth a phone call.
4. **Reavis `hours`** — historical value recorded for reference only, since the site appears
   closed.

## Schema changes applied

### `operational_status` + `closed_on`

Values: `operating` | `closed` | `closed_or_consolidated` | `unverified`. Populated for
every row — the build fails if any row is blank, since an empty status would reintroduce
exactly the ambiguity the column exists to remove. `closed_on` is set only where a source
carries an actual date, so Reavis has a status but no date.

Result: 33 operating, 2 closed (both dated 2024-04-01), 1 closed-or-consolidated,
2 unverified. The two `unverified` rows are TCA's mobile units — HRSA carries
`hrsa_status='Active'` for both but that field was not independently re-verified, so no
status is asserted. This is the column that makes `live == 33` assertable, matching CPS's
published 33 citywide; the old hard counts of 34/32/28 are snapshot arithmetic that still
holds but never meant "live centers."

**Mansueto is operating, at medium confidence.** It was previously `unverified` on the
grounds that no CPS directory entry had been checked for it. That reasoning was wrong:
the CPS 2025-26 booklet covers only the "Open to ALL CPS Students" subset, and this center
is school-linked rather than in-building, so it would not appear there whether it were
operating or not. Its absence is therefore not evidence against it, and the booklet is no
longer cited on that row at all. The IPHCA health-center locator carries 4700 S California
Ave as a current Esperanza site — the same source that settles the row's `setting`. That is
one credible current source, hence medium rather than high: nothing published by the
operator or CPS names Mansueto as the school this clinic serves, and that affiliation rests
on the CPS off-site coordinate override alone.

Closed rows are retained, not deleted. The new test enforces that a closed center is not
published with hours or with `open_to_public=true`.

### `hours` split three ways

`hours_medical_school_year` / `hours_medical_summer` / `hours_dental`. An empty cell means
**not established**, never "same as school year."

- Mile Square publishes two windows (summer runs Jun 16 – Aug 8). Davis and Drake both have
  one. Splitting isolated the Drake conflict to a single cell: its summer window is
  unambiguous and now published, where previously the conflict over its school-year hours
  would have discarded both.
- Hibbard's single CPS cell held two concatenated schedules. The split is supported by that
  row's own access note, the only one in either sheet that names dental.
- The 38 rows partition as 17 researched splits, 17 carrying the source value forward as
  school-year medical, and 4 with no hours finding at all because no source publishes hours
  for them: Uplift, Hope, and the two mobile units. Six rows publish no hours: those 4, plus
  the two researched splits that resolve to empty — Greater Lawndale, where the value is
  contested and needs a phone confirm, and Reavis, where the center appears closed and the
  historical value is recorded for reference rather than asserted. `build_resolved.py` prints
  the same three-way count.
  Mansueto keeps the CPS sheet's hours, carried forward as school-year medical.

### `room_or_entrance`

Populated for 15 rows. Rush, Tapestry, Erie and Mile Square all publish it; IDPH supplied
Beethoven's Room 134. A published room number or a named exterior door is evidence the
center occupies school space, which a street address is not — so the test refuses this
column on any `school_linked` or `mobile` row.

### Still worth doing

- `sponsor_legal_name` alongside `sponsor`. The UI Health rows are the case: IDPH's "Board
  of Trustees, U of I at Chicago" is the grantee and CPS's "UI Health" is the brand, and
  forcing one value loses information that is correct at its own level.
- Retire `match_basis='address_identity'`. All three rows it produced were wrong — two
  closed sites and one bad school match.
- `in_building` no longer requires a CPS `sid`: Cultivate Collective's host school resolves
  to a charter name, so the test accepts a sid **or** a school name.
