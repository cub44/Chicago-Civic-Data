"""
Hand-researched resolutions for cross-source discrepancies in sbhc.csv.

Each record is one (site_key, field) discrepancy. Values are recorded AS FOUND in
each source; `resolved` is the value the evidence supports, or "" (null) where desk
research could not settle it. Nothing is interpolated: if sources conflict and no
operator statement breaks the tie, `resolved` stays "" and confidence is "unresolved".

site_key matches sbhc.csv site_name exactly.
All URLs accessed 2026-09-12.

confidence:
  high    - operator's own current site, or two independent current official sources agree
  medium  - single credible current source, or operator source with a minor internal conflict
  low     - sources conflict and no operator statement resolves it; value left as-is
  unresolved - recorded for review, no value asserted
"""

ACCESSED = "2026-09-12"

# ---------------------------------------------------------------- source registry
S = {
    "tap_loc":   "https://tap360health.org/location/",
    "tap_senn":  "https://tap360health.org/location/tapestry-senn-high-school/",
    "tap_rename": "https://tap360health.org/new-name-same-quality-care/",
    "blockclub": "https://blockclubchicago.org/2022/10/13/heartland-health-centers-renamed-tapestry-360-health-to-avoid-confusion-with-former-sister-agency/",
    "tap_student": "https://tap360health.org/medical-specialties/student-health/",
    "340b_uplift": "https://340bopais.hrsa.gov/cedetails/21948",
    "340b_hope":   "https://340bopais.hrsa.gov/cedetails/27228",
    "340b_lchc":   "https://340bopais.hrsa.gov/cedetails/19531",
    "rush_sbhc": "https://www.rush.edu/about-us/rush-community/office-community-health-equity-and-engagement/community-based-practices",
    "erie_loc":  "https://www.eriefamilyhealth.org/locations/",
    "erie_amun": "https://www.eriefamilyhealth.org/locations/amundsen/",
    "erie_clem": "https://www.eriefamilyhealth.org/locations/clemente/",
    "erie_john": "https://www.eriefamilyhealth.org/locations/johnson/",
    "erie_lkvw": "https://www.eriefamilyhealth.org/locations/lake-view/",
    "erie_west": "https://www.eriefamilyhealth.org/locations/westside/",
    "msq_sbhc":  "https://hospital.uillinois.edu/mile-square-health-center/locations/school-based-clinics",
    "msq_drake": "https://hospital.uillinois.edu/mile-square-health-center/locations/school-based-clinics/barnes-boyd",
    "msq_davis": "https://hospital.uillinois.edu/mile-square-health-center/locations/school-based-clinics/davis-health-wellness-center",
    "msq_engl":  "https://hospital.uillinois.edu/mile-square-health-center/locations/school-based-clinics/englewood-stem",
    "msq_prim":  "https://hospital.uillinois.edu/mile-square-health-center/care-at-mile-square/services/primary-and-pediatric-care",
    "uic_ocean": "https://oceanhp.uic.edu/programs/community-health/mile-square-community-school-health-centers/",
    "uic_drake_open": "https://nursing.uic.edu/news-stories/school-based-community-health-center-named-for-uic-nursing-alumna-opens",
    "uic_ag":    "https://live.today.uic.edu/grand-opening-of-ui-healths-auburn-gresham-health-center/",
    "alivio_loc": "https://alivio.org/locations/",
    "alivio_peds": "https://alivio.org/services/pediatrics/",
    "alivio_lvlhs": "https://alivio.org/locations/lawndale/",
    "lchc_farragut": "https://lawndale.org/farragut-academy",
    "nnh_loc":   "https://nearnorthhealth.org/locations/",
    "nnh_reavis_archive": "https://www.boardportal.nearnorthhealth.org/reavis-school-based-health-center-",
    "tca_contact": "https://tcahealth.org/contact-us/",
    "tca_carver":  "https://tcahealth.org/carver-military-academy-school-based-health-center/",
    "esp_cult":  "https://www.esperanzachicago.org/location/esperanza-cultivate-collective",
    "cult_hw":   "https://cultivate-collective.org/services/health-wellness",
    "iphca":     "https://www.iphca.org/health-center-locator/",
    "cps_booklet": "https://www.cps.edu/globalassets/cps-pages/sites/back-to-school/student-health-and-school-forms-booklet-english-25-26.pdf",
    "cps_staff": "https://www.cps.edu/strategic-initiatives/healthy-cps/staff/",
    "cps_resources": "https://www.cps.edu/services-and-supports/health-and-wellness/health-resources/",
    # Historical only: cjg8-dbka is a 2014 snapshot (last updated 2014-04-22).
    # It corroborates unchanged addresses/geocodes; never use it for current status.
    "cdph2014":  "https://data.cityofchicago.org/api/views/cjg8-dbka/rows.csv?accessType=DOWNLOAD",
}

# Legal grantee is distinct from the public-facing operating unit. These values
# are emitted separately so neither correct level is discarded.
SPONSOR_LEGAL_NAME = {
    site: "Board of Trustees, U of I at Chicago"
    for site in (
        "Nathan S Davis Elementary School",
        "John B Drake Elementary School",
        "National Teachers Elementary Academy",
        "Englewood STEM High School",
    )
}

# CPS 2025-26 forms booklet, p.11 — "School Based Health Centers (SBHCs) Directory",
# subset headed "CPS' School Based Health Centers - Open to ALL CPS Students".
# This is the only CPS-published directory current as of the access date.
CPS_BOOKLET_NOTE = ("CPS 2025-26 forms booklet p.11; note this directory covers only "
                    "the 'Open to ALL CPS Students' subset, not all 33 SBHCs")

# ---------------------------------------------------------------- resolutions
# (site_key, field, cps, idph, hrsa_or_other, resolved, confidence, sources, note)
R = []


def add(site, field, cps, idph, other, resolved, conf, srcs, note=""):
    R.append(dict(site_name=site, field=field, cps_value=cps, idph_value=idph,
                  other_value=other, resolved=resolved, confidence=conf,
                  sources="; ".join(S[k] for k in srcs), accessed=ACCESSED, note=note))


# ===== 1. OPERATIONAL STATUS ================================================
add("Uplift Community High School", "operational_status", "not listed",
    "certified (listed)", "340B site BPS-H80-010055 terminated 2024-04-01",
    "closed", "high", ["340b_uplift", "tap_loc", "tap_student"],
    "340B termination reason: 'Business decision by the Covered Entity'. Absent from "
    "Tapestry 360's six-site student-health list. IDPH certified list is stale here.")

add("William C Reavis Math & Science Specialty ES", "operational_status", "not listed",
    "certified (listed)", "absent from operator's current locations page",
    "closed_or_consolidated", "medium", ["nnh_loc", "nnh_reavis_archive", "cdph2014"],
    "Near North Health's locations page (modified 2026-09-11) lists only Winfield Moody, "
    "North Kostner, Oakwood Shores, Komed Holman (select services) and Gage Park WIC; the "
    "former Reavis page URL now resolves to that page, which announces consolidation into "
    "three locations. Absence of evidence, not a closure notice.")

add("Wilma Rudolph Elementary Learning Center", "operational_status", "not listed",
    "certified (listed)", "340B site BPS-H80-010036 terminated 2024-04-01",
    "closed", "high", ["340b_hope", "msq_sbhc", "uic_ag"],
    "340B termination reason: 'Site closure'. Mile Square's current school-based list "
    "has four sites (Davis, Drake, Englewood STEM, NTA) and does not include this one.")

# ===== 2. SCHOOL MATCH ======================================================
add("Wilma Rudolph Elementary Learning Center", "school_name", "not listed",
    "Hope Health & Wellness SHC @ 1628 W. Washington Blvd", "matched to Rudolph by address identity",
    "Hope Institute Learning Academy", "high", ["340b_hope", "uic_ag"],
    "MISMATCH in sbhc.csv: 1628 W Washington Blvd is Hope Institute Learning Academy. "
    "UIC's own announcement lists 'Hope Institute Learning Academy, 1628 W. Washington Blvd.' "
    "as the Mile Square site. The address_identity join attached it to Rudolph.")

add("Military Leadership Academy", "school_name", "MARINE LEADERSHIP AT AMES HS",
    "(center listed as 'Primecare Hamlin')", "CPS geojson label 'Military Leadership Academy'",
    "Marine Leadership Academy at Ames", "high", ["cps_booklet", "cdph2014"],
    "sbhc.csv carries a stale CPS school label for sid 609780. Both the uploaded CPS "
    "sheet and the CPS 2025-26 booklet say Marine Leadership at Ames HS.")

# ===== 3. SPONSOR / PROVIDER NAME ==========================================
_TAP = ["Stephen F Gale Elementary Community Academy", "William G Hibbard Elementary School",
        "Joyce Kilmer International Academy", "Theodore Roosevelt High School",
        "Nicholas Senn High School", "Roger C Sullivan High School"]
for s in _TAP:
    add(s, "sponsor", "Tapestry 360 Health", "Heartland Health Center",
        "HRSA grantee: TAPESTRY 360 HEALTH", "Tapestry 360 Health", "high",
        ["tap_rename", "blockclub", "tap_loc"],
        "Heartland Health Centers rebranded as Tapestry 360 Health in Oct 2022. IDPH "
        "certified list still carries the pre-rename name. CPS sheet is correct.")

add("Paul Laurence Dunbar Career Academy High School", "sponsor",
    "Rush University Medical Center", "Mercy Hospital and Medical Center",
    "not in HRSA school-setting extract", "Rush University Medical Center", "high",
    ["rush_sbhc"],
    "Rush lists 'Rush Health Center at Dunbar Vocational Career Academy High School' among "
    "its five SBHCs and publishes the same phone CPS carries. IDPH's Mercy attribution is stale.")

add("Wendell Phillips Academy High School", "sponsor",
    "Rush University Medical Center", "Mercy Hospital and Medical Center",
    "not in HRSA school-setting extract", "Rush University Medical Center", "high",
    ["rush_sbhc"],
    "Rush lists 'Rush Health Center at Wendell Phillips Academy High School' among its five "
    "SBHCs and publishes the same phone CPS carries. IDPH's Mercy attribution is stale.")

add("Ludwig Van Beethoven Elementary School", "sponsor", "Friend Health",
    "Friend Family Health Center", "HRSA grantee: Friend Family Health Center, Inc.",
    "Friend Health", "high", ["cps_booklet"],
    "Operating name is Friend Health; 'Friend Family Health Center, Inc.' remains the "
    "corporate/grantee name. CPS 2025-26 booklet lists 'BEETHOVEN ES Friend Health'.")

add("Marquette Elementary School", "sponsor", "Esperanza Health Centers",
    "Esperanza Clinic", "HRSA grantee: ESPERANZA HEALTH CENTERS",
    "Esperanza Health Centers", "high", ["cps_booklet", "iphca"],
    "IDPH's 'Esperanza Clinic' is not the organisation's name.")

add("Charles P Steinmetz College Preparatory HS", "sponsor",
    "PCC Community Wellness Center", "PCC Community Center Wellness",
    "HRSA grantee: PCC COMMUNITY WELLNESS CENTER", "PCC Community Wellness Center", "high",
    ["cps_booklet"],
    "IDPH has the words transposed. CPS booklet abbreviates the sponsor 'PCC CWC'.")

add("Military Leadership Academy", "sponsor", "PrimeCareHealth Community Health Centers",
    "Primecare Community Health", "HRSA grantee: PRIMECARE COMMUNITY HEALTH INC",
    "PrimeCare Community Health", "high", ["cps_booklet", "cdph2014"],
    "CPS sheet value looks like a malformed concatenation. CPS booklet abbreviates 'PCH CHC'; "
    "CDPH 2014 names the site 'PrimeCare Ames'.")

add("Noble - Gary Comer College Prep", "sponsor", "ACCESS Community Health Center",
    "Access Community Health Network", "CDPH 2014: 'ACCESS at Gary Comer Youth Center'",
    "Access Community Health Network", "high", ["cps_booklet", "cdph2014"],
    "IDPH carries the correct corporate name; CPS sheet's '...Health Center' is wrong. "
    "CPS booklet uses the brand 'ACCESS'.")

for s in ["Roald Amundsen High School", "Roberto Clemente Community Academy High School",
          "James Weldon Johnson STEAM Elementary School", "Lake View High School",
          "Laura S Ward Elementary School"]:
    add(s, "sponsor", "Erie Family Health Centers", "Erie Family Health Center",
        "HRSA grantee: ERIE FAMILY HEALTH CENTER", "Erie Family Health Centers", "high",
        ["erie_loc"], "Operator uses the plural form; IDPH and HRSA carry the older singular.")

for s in ["Nathan S Davis Elementary School", "John B Drake Elementary School",
          "National Teachers Elementary Academy", "Englewood STEM High School"]:
    add(s, "sponsor", "UI Health", "Board of Trustees, U of I at Chicago",
        "HRSA grantee: University of Illinois", "UI Health Mile Square Health Center", "high",
        ["msq_sbhc"],
        "Not a true conflict: IDPH records the legal grantee, CPS the brand. The operating "
        "unit is UI Health Mile Square Health Center.")

add("William C Reavis Math & Science Specialty ES", "sponsor", "",
    "Near North/Komed-Homan Health Center", "CDPH 2014: 'Near North - Reavis'",
    "Near North Health", "high", ["nnh_loc", "cdph2014"],
    "IDPH conflates two separate Near North sites; Komed Holman Health Center is a distinct "
    "site at 4259 S Berkeley Ave. Sponsor is Near North Health (formerly Near North Health "
    "Service Corporation). Sponsor recorded for completeness; the site itself appears closed.")

# ===== 4. SETTING (in school vs school-linked) ==============================
add("David G Farragut Career Academy High School", "setting", "in_building (school address)",
    "3256 W. 24th St. (separate street address)", "HRSA BPS-H80-001032 @ 3256 W 24th St",
    "in_building", "high", ["lchc_farragut", "340b_lchc", "cdph2014"],
    "LCHC states the clinic is 'located within Farragut Career Academy'. The 24th Street "
    "address is the clinic's own entrance on the school's south frontage.")

add("Nathan S Davis Elementary School", "setting", "3050 W 39th Pl (school bldg 3014 W 39th Pl)",
    "3050 W. 39th Pl. Annex", "CDPH 2014: 'UIC- Mile Square at Davis Elementary' @ 3050 W 39th Pl",
    "in_building", "medium", ["uic_ocean", "msq_davis", "cps_booklet", "cdph2014"],
    "sbhc.csv has this as school_linked because the centre address differs from the school "
    "building address. IDPH names it an Annex, i.e. CPS space on the Davis campus, and both "
    "CPS and UI Health publish the centre at 3050 W 39th Pl. For a co-location analysis this "
    "is in-building CPS space. Flagged: depends on whether the annex is a separate structure.")

add("Noble - Gary Comer College Prep", "setting", "7200 S Ingleside Ave (school @ 7131 S South Chicago Ave)",
    "Comer Youth Center @ 7200 S. Ingleside Ave", "CDPH 2014: 'ACCESS at Gary Comer Youth Center'",
    "school_linked", "high", ["cdph2014", "cps_booklet"],
    "Centre is inside the Gary Comer Youth Center, a separate building from Gary Comer "
    "College Prep. school_linked confirmed.")

add("Noble - Gary Comer College Prep", "lat_lon", "", "",
    "CDPH 2014 geocode of 7200 S Ingleside Ave: 41.764002, -87.601896",
    "41.764002,-87.601896", "medium", ["cdph2014"],
    "Fills the null coordinate flagged in sbhc.csv. Basis is a 2014 CDPH geocode of an "
    "address that has not changed, not the centre's own published coordinate. "
    "Set coord_basis='cdph_2014_geocode', not 'cps_school_building'.")

add("Noble Mansueto High School", "setting", "cps_offsite_override @ 4700 S California Ave",
    "not listed", "IPHCA lists 4700 S California Ave as an Esperanza site",
    "school_linked", "high", ["iphca", "esp_cult"],
    "The centre is Esperanza's own Brighton Park clinic at 4700 S California Ave, roughly a "
    "kilometre from Mansueto HS (2911 W 47th St). CPS's off-site override is correct.")

add("Esperanza at Cultivate Collective", "school_name", "not listed", "not listed",
    "HRSA setting 'School' @ 4350 S Laporte Ave",
    "Academy for Global Citizenship", "medium", ["esp_cult", "cult_hw"],
    "Resolves the 'host school unresolved' note. The clinic sits on the Cultivate Collective "
    "campus in LeClaire Courts, which Cultivate describes as an 'on-site Health Clinic "
    "operated by Esperanza Health Centers' serving 'community members and AGC students'. "
    "AGC = Academy for Global Citizenship, a CPS charter.")

add("Esperanza at Cultivate Collective", "setting", "", "",
    "on-campus clinic, community-open FQHC", "in_building", "medium", ["cult_hw", "esp_cult"],
    "On-campus, but the clinic address (4350 S Laporte Ave) differs from Cultivate "
    "Collective's main address (4942 W 44th St), so building-level placement is not certain. "
    "Note this site is neither IDPH-certified nor in CPS's SBHC directory; it may not meet "
    "a strict SBHC definition.")

for s in ["Mobile Oral Health Unit", "Mobile Student Health Clinic, Parking Lot B"]:
    add(s, "setting", "not listed", "not listed",
        "HRSA registers both at TCA's main clinic, 1029 E 130th St",
        "mobile", "high", ["tca_contact"],
        "TCA: 'The Mobile Student Health Clinic travels to various schools on Chicago's far "
        "south side.' No fixed host school exists to resolve; the null is correct, not missing.")

for s in ["Benito Juarez Community Academy High School",
          "Orozco Fine Arts & Sciences Elementary School",
          "Greater Lawndale High School For Social Justice"]:
    add(s, "setting", "in_building", "in_building", "Alivio: 'on-site' at all three schools",
        "in_building", "high", ["alivio_peds"],
        "Alivio: 'We also operate three school-based health centers, providing on-site, "
        "accessible health services to the students and community of Benito Juarez Community "
        "Academy, Orozco Community Academy, and Little Village Lawndale High School.'")

# ===== 5. ADDRESSES =========================================================
add("James Weldon Johnson STEAM Elementary School", "site_address", "1420 S Albany Ave",
    "1504 S. Albany Ave.", "CDPH 2014 and Erie both say 1504 S Albany",
    "1504 S Albany Ave", "medium", ["erie_john", "cdph2014", "cps_booklet"],
    "Operator (Erie), IDPH and CDPH 2014 all say 1504 S Albany; HRSA's coordinate in "
    "sbhc.csv (41.8611) also matches 1504 rather than 1420. CPS gives 1420 S Albany in both "
    "the uploaded sheet and the 2025-26 booklet - that is the school building address.")

add("James Weldon Johnson STEAM Elementary School", "setting", "in_building",
    "separate street address (1504 S. Albany Ave.)",
    "Erie, CDPH 2014 and HRSA's coordinate all place the centre at 1504 S Albany",
    "school_linked", "high", ["erie_john", "cdph2014", "cps_booklet"],
    "CORRECTED from sbhc.csv's in_building. 1504 S Albany is a separate building from the "
    "Johnson school building at 1420 S Albany, confirmed by local knowledge on 2026-09-12. "
    "CPS publishes the school address for this centre in both the uploaded sheet and the "
    "2025-26 booklet, which is what produced the bad in_building classification. "
    "coord_basis stays 'hrsa_site': the existing coordinate (41.861116, -87.703417) is the "
    "centre's own, not the school's, so the school_linked coordinate rule in test_sbhc.py "
    "passes unchanged. Note this row no longer needs to satisfy the in_building/sid rule.")

add("David G Farragut Career Academy High School", "site_address", "2345 S Christiana Ave",
    "3256 W. 24th St.", "HRSA and CDPH 2014 both use 3256 W 24th St",
    "3256 W 24th St", "high", ["lchc_farragut", "340b_lchc", "cdph2014"],
    "Clinic's own published address. School building address remains 2345 S Christiana Ave.")

add("Benito Juarez Community Academy High School", "site_address", "1450 West Cermak Rd",
    "2150 S. Laflin St.", "Alivio publishes 1450 W Cermak Rd",
    "1450 W Cermak Rd", "high", ["alivio_loc", "cps_booklet"],
    "Operator and current CPS booklet agree. Juarez occupies the block; Laflin St is a "
    "secondary frontage.")

add("George Washington Carver Military Academy HS", "site_address", "13100 S Doty Ave, 60827",
    "13100 Doty Rd., 60627-1597", "TCA publishes 13100 S Doty Ave, 60827",
    "13100 S Doty Ave, Chicago, IL 60827", "high", ["tca_carver"],
    "IDPH has both the street type and the ZIP wrong (60627 vs 60827).")

add("Chicago Vocational Career Academy High School", "zip", "60617", "60616",
    "CPS booklet: 60617", "60617", "high", ["cps_booklet"], "IDPH ZIP is wrong.")

add("William G Hibbard Elementary School", "site_address", "3244 W Ainslie St",
    "3244 W. Ainsley St., 60625-1397", "Tapestry: 3244 West Ainslie Street; CDPH 2014: 4930 N Sawyer Ave",
    "3244 W Ainslie St", "high", ["tap_loc", "cdph2014"],
    "IDPH misspells Ainslie and carries Amundsen's ZIP+4 (60625-1397). CDPH's 4930 N Sawyer "
    "Ave is the same building's corner frontage; the operator publishes the Ainslie address.")

add("Roald Amundsen High School", "zip", "60625", "60625-1397", "",
    "60625", "high", ["erie_amun"],
    "IDPH's ZIP+4 suffix is duplicated from the Hibbard entry; treat as a copy error.")

add("National Teachers Elementary Academy", "site_address", "55 W Cermak Rd",
    "55 W. Cermak Ave.", "Mile Square: 55 W. Cermak Rd.", "55 W Cermak Rd", "high",
    ["msq_prim"], "There is no Cermak Ave; IDPH street type is wrong.")

add("Orr Academy High School", "site_address", "730 N Pulaski Rd. Room 109",
    "730 N. Pulaski St.", "Rush's own page: '730 Pulaski Ave. Room 109'",
    "730 N Pulaski Rd, Room 109", "high", ["rush_sbhc", "cdph2014"],
    "Three different street types across sources; Pulaski Rd is correct. Rush's own page is "
    "also wrong here.")

# ===== 6. HOURS =============================================================
add("Roberto Clemente Community Academy High School", "hours", "Mon-Fri: 8:00am-4:00pm", "",
    "Erie: M, T, Th, F 8:00 AM-4:30 PM; W 10:00 AM-4:30 PM",
    "Mon, Tue, Thu, Fri: 8:00am-4:30pm; Wed: 10:00am-4:30pm", "high", ["erie_clem"],
    "CPS sheet misses the Wednesday late open and ends the day 30 min early. Erie publishes "
    "the same pattern at all five of its school sites.")

add("James Weldon Johnson STEAM Elementary School", "hours", "Mon-Fri: 8:00am-4:30pm", "",
    "Erie: M, T, Th, F 8:00 AM-4:30 PM; W 10:00 AM-4:30 PM",
    "Mon, Tue, Thu, Fri: 8:00am-4:30pm; Wed: 10:00am-4:30pm", "high", ["erie_john"],
    "Both CPS sources miss the Wednesday 10am open.")

add("Nicholas Senn High School", "hours", "Mon, Tue, Thur: 8:00 am-4:00 pm", "",
    "Tapestry: Monday - Friday 8:00 am - 4:00 pm",
    "Mon-Fri: 8:00am-4:00pm", "high", ["tap_senn"],
    "Operator page modified 2026-08-17 publishes a five-day week; CPS sheet has three days.")

add("David G Farragut Career Academy High School", "hours", "Monday-Friday: 8:30am-5pm", "",
    "LCHC: Mon 8:30a-5:00p; Tue 8:30a-7:00p; Wed-Fri 8:30a-5:00p",
    "Mon: 8:30am-5:00pm; Tue: 8:30am-7:00pm; Wed-Fri: 8:30am-5:00pm", "high",
    ["lchc_farragut"],
    "Both CPS sources miss the Tuesday evening extension to 7pm.")

add("George Washington Carver Military Academy HS", "hours", "Mon-Wed: 9:00am-1pm", "",
    "TCA: 9:00 am - 4:00 pm Mon/Tues/Wed/Thurs/Fri (Carver students only)",
    "Mon-Fri: 9:00am-4:00pm", "medium", ["tca_carver"],
    "Operator publishes a five-day 9-4 schedule against CPS's three-day 9-1. Large gap; "
    "operator page last dated 2023, so worth a phone confirm.")

add("Nathan S Davis Elementary School", "hours",
    "Mon, Tue, Wed, Fri: 8:00am-4:30pm, Thur: 10:00am-6:00pm", "",
    "Mile Square: school season M/Tu/W/F 8:30am-4:30pm, Th 10am-6pm; summer (Jun 16-Aug 8) M-F 8am-4:30pm",
    "Mon, Tue, Wed, Fri: 8:30am-4:30pm; Thu: 10:00am-6:00pm", "medium",
    ["msq_davis", "uic_ocean", "cps_booklet"],
    "Operator says 8:30am open in school season; both CPS sources say 8:00am. CPS may be "
    "carrying the summer open time. Day pattern agrees.")

add("John B Drake Elementary School", "hours", "Mon-Fri: 8:00am-4:00pm", "",
    "Mile Square location page: school season M-F 8:30am-4:30pm, summer M-F 7am-3:30pm; "
    "UIC OCEANHP page: M-F 8:00am-4:00pm",
    "", "unresolved", ["msq_drake", "uic_ocean", "cps_booklet"],
    "NOT RESOLVED. UI Health's two own pages disagree with each other. CPS booklet and "
    "OCEANHP both say 8a-4p; the Mile Square location page says 8:30a-4:30p. Left null.")

add("Englewood STEM High School", "hours", "Mon-Fri: 8:00am-4:30pm", "",
    "CPS booklet: M-F 8:00a-4:30p; UIC OCEANHP: M-F 8:00am-4:00pm",
    "Mon-Fri: 8:00am-4:30pm", "medium", ["cps_booklet", "uic_ocean"],
    "Two CPS sources agree on 4:30pm close; UIC's OCEANHP programme page says 4:00pm and "
    "appears to be the older of the two.")

add("Greater Lawndale High School For Social Justice", "hours",
    "Mon-Fri: 8:30am-12:00pm; 1:00pm-4:00pm", "",
    "findhelp listing claimed by Alivio (Feb 2026): Mon 8:30a-3:00p; Tue 8:30a-4:30p; "
    "Wed closed; Thu 9:30a-2:30p; Fri 8:30a-12:30p; closed 12-1p",
    "", "unresolved", ["alivio_lvlhs", "alivio_loc"],
    "NOT RESOLVED. A provider-claimed third-party listing shows a much narrower schedule "
    "including a Wednesday closure; Alivio's own site publishes no hours for this site. "
    "Left null; needs a phone confirm.")

add("William G Hibbard Elementary School", "hours",
    "Mon, Wed, Thur: 8:00am-4:00pm / Mon: 8:00am-2:30pm, Wed: 8:00am-2:00pm", "",
    "Tapestry publishes no hours for this site",
    "", "unresolved", ["tap_loc"],
    "NOT RESOLVED. The CPS field holds two overlapping schedules. The sheet's access note "
    "mentions dental, so these are most likely separate medical and dental schedules that "
    "were concatenated. Needs to be split into two fields, not merged.")

add("Theodore Roosevelt High School", "hours",
    "Mon, Tue, Thur: 8:00am-4:00pm / Thur: 8:00am-4:00pm", "",
    "Tapestry publishes no hours for this site",
    "Mon, Tue, Thu: 8:00am-4:00pm", "low", ["tap_loc"],
    "The CPS field repeats Thursday; the duplicate line is redundant, not a second schedule. "
    "Deduplicated, but day coverage is unverified against the operator.")

add("Esperanza at Cultivate Collective", "hours", "", "",
    "Esperanza: Mon 7:30a-5:00p; Tue 7:30a-4:30p; Wed 7:30a-5:00p; Thu (1st & 3rd) "
    "11:30a-6:30p; Thu (2nd, 4th, 5th) 7:30a-4:30p; Fri 7:30a-4:30p; 4th Sat 7:30a-3:30p",
    "Mon: 7:30am-5:00pm; Tue: 7:30am-4:30pm; Wed: 7:30am-5:00pm; Thu (1st & 3rd): "
    "11:30am-6:30pm; Thu (2nd, 4th, 5th): 7:30am-4:30pm; Fri: 7:30am-4:30pm; "
    "Sat (4th of month): 7:30am-3:30pm", "high", ["esp_cult"],
    "Fills a null. Operator-published.")

add("William C Reavis Math & Science Specialty ES", "hours", "", "",
    "Near North archived page: Monday-Friday 8:00 am - 5:00 pm",
    "", "unresolved", ["nnh_reavis_archive", "nnh_loc"],
    "Historical hours recorded for reference only. Not asserted, because the site appears "
    "to have closed or been consolidated.")

# ===== 7. PHONES ============================================================
add("Roald Amundsen High School", "phone", "312-432-2000", "312-666-3494",
    "Erie publishes 312.666.3494 for every site", "312-666-3494", "medium", ["erie_amun"],
    "Erie routes all sites through central scheduling. CPS sheet's 312-432-2000 is not "
    "published anywhere current.")

add("Roberto Clemente Community Academy High School", "phone", "312-432-7475", "312-432-7475",
    "Erie publishes 312.666.3494", "312-666-3494", "medium", ["erie_clem"],
    "Both sheets carry a 312-432 direct line that Erie no longer publishes.")

add("Benito Juarez Community Academy High School", "phone", "773-254-1400", "773-579-2691",
    "CPS 2025-26 booklet: 773-579-2691", "773-579-2691", "high", ["cps_booklet"],
    "IDPH and the current CPS booklet agree on the site line; the uploaded CPS sheet carries "
    "Alivio's central number instead.")

add("Chicago Vocational Career Academy High School", "phone", "773-816-5081", "773-768-5000",
    "CPS 2025-26 booklet: 773-768-5000", "773-768-5000", "medium", ["cps_booklet", "cdph2014"],
    "IDPH and the current CPS booklet agree; 773-768-5000 is Chicago Family Health Center's "
    "main line, so the site may also have a direct line that is no longer published.")

add("Stephen F Gale Elementary Community Academy", "phone", "773-366-7710", "773-336-7710",
    "Tapestry: 773-366-7710", "773-366-7710", "high", ["tap_loc"],
    "IDPH has two digits transposed.")

add("Joyce Kilmer International Academy", "phone", "773-366-7704", "773-761-5309",
    "Tapestry: 773-366-7704", "773-366-7704", "high", ["tap_loc"],
    "IDPH lists the same number for Kilmer and Sullivan; both are wrong.")

add("Roger C Sullivan High School", "phone", "312-517-2590", "773-761-5309",
    "Tapestry: 312-517-2590", "312-517-2590", "high", ["tap_loc"],
    "IDPH lists the same number for Kilmer and Sullivan; both are wrong.")

add("Theodore Roosevelt High School", "phone", "872-268-7545", "773-866-0818",
    "Tapestry: 872-268-7545", "872-268-7545", "high", ["tap_loc"], "IDPH number is stale.")

add("Paul Laurence Dunbar Career Academy High School", "phone", "773-534-0904", "312-225-6592",
    "Rush: (773) 534-0904", "773-534-0904", "high", ["rush_sbhc"],
    "IDPH number is a Mercy Hospital line and is stale along with the sponsor.")

add("Wendell Phillips Academy High School", "phone", "773-535-1837", "773-373-3698",
    "Rush: (773) 535-1837", "773-535-1837", "high", ["rush_sbhc"], "IDPH number is stale.")

add("David G Farragut Career Academy High School", "phone", "872-588-3540", "872-588-3000",
    "CDPH 2014 and CPS booklet: 872-588-3540", "872-588-3540", "high",
    ["cps_booklet", "cdph2014"], "IDPH carries LCHC's main switchboard, not the site line.")

add("Nathan S Davis Elementary School", "phone", "312-413-3090", "773-376-8008",
    "Mile Square and CPS booklet: 312-413-3090", "312-413-3090", "high",
    ["msq_davis", "cps_booklet"],
    "IDPH's number matches the CDPH 2014 snapshot and is stale.")

add("John B Drake Elementary School", "phone", "312-355-5746", "312-355-5746",
    "Mile Square location page and UIC OCEANHP both say 312.355.5745",
    "", "unresolved", ["msq_drake", "uic_ocean", "cps_booklet"],
    "NOT RESOLVED. Both sheets and the CPS booklet say ...5746; both UI Health pages say "
    "...5745. One digit apart, so a typo exists on one side. Left null.")

add("Marquette Elementary School", "phone", "773-584-6200", "773-309-4445",
    "CPS booklet and IPHCA: 773-584-6200", "773-584-6200", "high", ["cps_booklet", "iphca"],
    "IDPH number is not published by the operator.")

# ===== 8. ACCESS ============================================================
add("George Washington Carver Military Academy HS", "access_text",
    "Open to Enrolled Students at the School", "",
    "TCA: '(For Carver Students Only)'", "Open to enrolled students at the school", "high",
    ["tca_carver"], "Operator confirms the restriction CPS records.")

add("Simpson Academy HS for Young Women", "access_text",
    "Open to CPS Students & Family Members Only", "",
    "Rush: serves Simpson students and their children, and via its community door students "
    "from other Chicago schools",
    "Open to CPS students and their children; accessible to students from other CPS schools",
    "high", ["rush_sbhc"], "Operator description is more specific than either sheet.")

add("Nathan S Davis Elementary School", "access_text", "Open to the Community: No Restrictions",
    "", "Mile Square: 'open to students and the community'",
    "Open to the community", "high", ["msq_davis"], "Confirmed.")

add("John B Drake Elementary School", "access_text", "Open to the Community: No Restrictions",
    "", "UIC: 'Services are available to students, their families and the entire community'",
    "Open to the community", "high", ["uic_drake_open"], "Confirmed.")


# ============================================================================
# SCHEMA ADDITIONS
# Three structural changes the findings implied. Each carries the same
# provenance discipline as the field resolutions above: operator-published
# where available, "" where not established, never inferred.
# ============================================================================

# ---- 1. operational_status -------------------------------------------------
# Values: operating | closed | closed_or_consolidated | unverified
#   operating              listed by the operator's current site, or by CPS's 2025-26
#                          directory
#   closed                 dated administrative record of termination
#   closed_or_consolidated absent from the operator's current site, no dated record
#   unverified             no current source checked; do not assert either way
#
# closed_on is populated only where a source carries an actual date.

STATUS = {}


def stat(site, status, closed_on, conf, srcs, note=""):
    STATUS[site] = dict(operational_status=status, closed_on=closed_on,
                        confidence=conf, sources="; ".join(S[k] for k in srcs),
                        accessed=ACCESSED, note=note)


stat("Uplift Community High School", "closed", "2024-04-01", "high",
     ["340b_uplift", "tap_loc", "tap_student"],
     "340B site BPS-H80-010055 terminated; reason 'Business decision by the Covered "
     "Entity'. Absent from Tapestry 360's six-site student-health list.")

stat("Wilma Rudolph Elementary Learning Center", "closed", "2024-04-01", "high",
     ["340b_hope", "msq_sbhc"],
     "340B site BPS-H80-010036 terminated; reason 'Site closure'. Absent from Mile "
     "Square's current four-site school-based list. Row also carries a bad school match.")

stat("William C Reavis Math & Science Specialty ES", "closed_or_consolidated", "", "medium",
     ["nnh_loc", "nnh_reavis_archive"],
     "Absent from Near North Health's locations page (modified 2026-09-11); the former "
     "Reavis page URL now resolves to that page, which announces consolidation into three "
     "locations. No dated closure record found, so closed_on is left empty.")

_OPERATOR_CONFIRMED = {
    # Erie
    "Roald Amundsen High School": ["erie_amun"],
    "Roberto Clemente Community Academy High School": ["erie_clem"],
    "James Weldon Johnson STEAM Elementary School": ["erie_john"],
    "Lake View High School": ["erie_lkvw"],
    "Laura S Ward Elementary School": ["erie_west"],
    # Tapestry 360
    "Stephen F Gale Elementary Community Academy": ["tap_loc"],
    "William G Hibbard Elementary School": ["tap_loc"],
    "Joyce Kilmer International Academy": ["tap_loc"],
    "Theodore Roosevelt High School": ["tap_loc"],
    "Nicholas Senn High School": ["tap_senn"],
    "Roger C Sullivan High School": ["tap_loc"],
    # Rush
    "Simpson Academy HS for Young Women": ["rush_sbhc"],
    "Orr Academy High School": ["rush_sbhc"],
    "Richard T Crane Medical Preparatory HS": ["rush_sbhc"],
    "Paul Laurence Dunbar Career Academy High School": ["rush_sbhc"],
    "Wendell Phillips Academy High School": ["rush_sbhc"],
    # Alivio
    "Benito Juarez Community Academy High School": ["alivio_loc"],
    "Orozco Fine Arts & Sciences Elementary School": ["alivio_loc"],
    "Greater Lawndale High School For Social Justice": ["alivio_loc"],
    # Lawndale Christian
    "David G Farragut Career Academy High School": ["lchc_farragut"],
    # UI Health Mile Square
    "Nathan S Davis Elementary School": ["msq_davis"],
    "John B Drake Elementary School": ["msq_drake"],
    "Englewood STEM High School": ["msq_engl"],
    "National Teachers Elementary Academy": ["msq_prim"],
    # TCA
    "George Washington Carver Military Academy HS": ["tca_carver"],
    # Esperanza
    "Esperanza at Cultivate Collective": ["esp_cult"],
}
for _s, _src in _OPERATOR_CONFIRMED.items():
    stat(_s, "operating", "", "high", _src,
         "Listed on the operator's current site.")

_CPS_BOOKLET_CONFIRMED = [
    "Ludwig Van Beethoven Elementary School",
    "Chicago Vocational Career Academy High School",
    "Noble - Gary Comer College Prep",
    "Marquette Elementary School",
    "Charles P Steinmetz College Preparatory HS",
    "Military Leadership Academy",
]
for _s in _CPS_BOOKLET_CONFIRMED:
    stat(_s, "operating", "", "high", ["cps_booklet"],
         "Listed in CPS's 2025-26 SBHC directory. " + CPS_BOOKLET_NOTE)

# The centre here is Esperanza's own Brighton Park clinic at 4700 S California
# Ave, which both Esperanza and the IPHCA health-centre locator carry as a
# current site - the same two sources that settle this row's `setting`. Absence
# from the CPS booklet is not evidence against it: that directory covers only the
# "Open to ALL CPS Students" subset, and this centre is school-linked rather than
# in-building, so it would not appear there whether it were operating or not.
# The booklet is therefore not cited on this row at all.
#
# medium, not high: one credible current source. The IPHCA locator is a
# third-party directory of Illinois health centres, not Esperanza's own page, and
# nothing published by the operator or CPS names Mansueto as the school this
# clinic serves - that affiliation rests on the CPS off-site coordinate override.
stat("Noble Mansueto High School", "operating", "", "medium", ["iphca"],
     "Esperanza's Brighton Park clinic at 4700 S California Ave, carried as a current "
     "site by the IPHCA health-centre locator - the same source that settles this "
     "row's setting. CPS supplies an off-site coordinate override linking it to "
     "Mansueto HS; the centre is school-linked, not in the school building.")

for _s in ["Mobile Oral Health Unit",
           "Mobile Student Health Clinic, Parking Lot B"]:
    stat(_s, "unverified", "", "unresolved", ["cps_booklet"],
         "No current operator page or CPS directory entry checked for this site. HRSA "
         "carries hrsa_status='Active' but that field was not independently re-verified, "
         "so no status is asserted.")


# ---- 2. hours split --------------------------------------------------------
# sbhc.csv's single `hours` field cannot represent two facts that turned up
# repeatedly: Mile Square publishes distinct school-season and summer schedules,
# and at least one site runs separate medical and dental clinics.
#
# hours_medical_school_year / hours_medical_summer / hours_dental
# Empty means not established, not "same as school year".

HOURS = {}


def hrs(site, school_year, summer, dental, conf, srcs, note=""):
    HOURS[site] = dict(hours_medical_school_year=school_year,
                       hours_medical_summer=summer, hours_dental=dental,
                       confidence=conf, sources="; ".join(S[k] for k in srcs),
                       accessed=ACCESSED, note=note)


hrs("Nathan S Davis Elementary School",
    "Mon, Tue, Wed, Fri: 8:30am-4:30pm; Thu: 10:00am-6:00pm",
    "Mon-Fri: 8:00am-4:30pm (Jun 16 - Aug 8)", "", "medium", ["msq_davis", "cps_booklet"],
    "Operator publishes both windows. Both CPS sources give an 8:00am school-year open "
    "against the operator's 8:30am; CPS may be carrying the summer open time.")

hrs("John B Drake Elementary School", "", "Mon-Fri: 7:00am-3:30pm (Jun 16 - Aug 8)", "",
    "medium", ["msq_drake", "uic_ocean", "cps_booklet"],
    "Summer window is unambiguous on the operator's location page. School-year hours stay "
    "empty: the Mile Square location page says 8:30am-4:30pm while UIC's OCEANHP page and "
    "the CPS booklet both say 8:00am-4:00pm. Splitting the field isolates the conflict to "
    "one cell instead of discarding the summer value with it.")

hrs("Englewood STEM High School", "Mon-Fri: 8:00am-4:30pm", "", "", "medium",
    ["cps_booklet", "msq_engl", "uic_ocean"],
    "Two CPS sources agree on the 4:30pm close; UIC's OCEANHP page says 4:00pm and appears "
    "older. Mile Square publishes no separate summer window for this site.")

hrs("National Teachers Elementary Academy", "Mon-Fri: 8:30am-4:30pm", "", "", "high",
    ["uic_ocean", "msq_prim"],
    "Operator and CPS sheet agree. No separate summer window published.")

hrs("William G Hibbard Elementary School", "Mon, Wed, Thu: 8:00am-4:00pm", "",
    "Mon: 8:00am-2:30pm; Wed: 8:00am-2:00pm", "medium", ["tap_loc"],
    "The single CPS hours cell held two concatenated schedules. Splitting them is supported "
    "by the sheet's own access note - 'Open to Enrolled Students at School and Tapestry 360 "
    "Health Patients (Dental)' - which is the only site in either sheet that names dental. "
    "Tapestry publishes no hours for this site, so the medical/dental attribution is "
    "inferred from the access note and should be confirmed by phone.")

# Sites where the existing single value is a school-year medical schedule and no
# summer or dental schedule was found. Carried across so the new columns are not
# sparse for no reason; empty summer/dental means not established.
_SCHOOL_YEAR_ONLY = {
    "Roberto Clemente Community Academy High School":
        ("Mon, Tue, Thu, Fri: 8:00am-4:30pm; Wed: 10:00am-4:30pm", ["erie_clem"]),
    "James Weldon Johnson STEAM Elementary School":
        ("Mon, Tue, Thu, Fri: 8:00am-4:30pm; Wed: 10:00am-4:30pm", ["erie_john"]),
    "Roald Amundsen High School":
        ("Mon, Tue, Thu, Fri: 8:00am-4:30pm; Wed: 10:00am-4:30pm", ["erie_amun"]),
    "Lake View High School":
        ("Mon, Tue, Thu, Fri: 8:00am-4:30pm; Wed: 10:00am-4:30pm", ["erie_lkvw"]),
    "Laura S Ward Elementary School":
        ("Mon, Tue, Thu, Fri: 8:00am-4:30pm; Wed: 10:00am-4:30pm", ["erie_west"]),
    "Nicholas Senn High School": ("Mon-Fri: 8:00am-4:00pm", ["tap_senn"]),
    "David G Farragut Career Academy High School":
        ("Mon: 8:30am-5:00pm; Tue: 8:30am-7:00pm; Wed-Fri: 8:30am-5:00pm", ["lchc_farragut"]),
    "George Washington Carver Military Academy HS":
        ("Mon-Fri: 9:00am-4:00pm", ["tca_carver"]),
    "Esperanza at Cultivate Collective":
        ("Mon: 7:30am-5:00pm; Tue: 7:30am-4:30pm; Wed: 7:30am-5:00pm; "
         "Thu (1st & 3rd): 11:30am-6:30pm; Thu (2nd, 4th, 5th): 7:30am-4:30pm; "
         "Fri: 7:30am-4:30pm; Sat (4th of month): 7:30am-3:30pm", ["esp_cult"]),
    "Theodore Roosevelt High School": ("Mon, Tue, Thu: 8:00am-4:00pm", ["tap_loc"]),
}
for _s, (_v, _src) in _SCHOOL_YEAR_ONLY.items():
    hrs(_s, _v, "", "", "high", _src,
        "School-year medical schedule. No summer or dental schedule published.")

# Left entirely empty: operator publishes nothing and the CPS value is contested.
hrs("Greater Lawndale High School For Social Justice", "", "", "", "unresolved",
    ["alivio_lvlhs", "alivio_loc"],
    "Alivio publishes no hours for this site. A provider-claimed third-party listing shows "
    "a much narrower week including a Wednesday closure, against the CPS sheet's Mon-Fri "
    "split-shift value. Needs a phone confirm.")

hrs("William C Reavis Math & Science Specialty ES", "", "", "", "unresolved",
    ["nnh_reavis_archive", "nnh_loc"],
    "Site appears closed; historical value (Mon-Fri 8:00am-5:00pm) is recorded in the "
    "discrepancy table for reference only and is not asserted here.")


# ---- 3. room_or_entrance ---------------------------------------------------
# The strongest in-building evidence available, and four operators publish it.
# A published room number or a named exterior door is a fact about the centre
# occupying school space; a bare street address is not.

ROOM = {}


def room(site, value, conf, srcs, note=""):
    ROOM[site] = dict(room_or_entrance=value, confidence=conf,
                      sources="; ".join(S[k] for k in srcs), accessed=ACCESSED, note=note)


for _s, _v in [("Orr Academy High School", "Room 109"),
               ("Richard T Crane Medical Preparatory HS", "Room 110"),
               ("Paul Laurence Dunbar Career Academy High School", "Room 208"),
               ("Wendell Phillips Academy High School", "Lower Level")]:
    room(_s, _v, "high", ["rush_sbhc"], "Published by Rush.")

room("Simpson Academy HS for Young Women",
     "Entrance immediately left of the main school door; separate community door",
     "high", ["rush_sbhc"],
     "Rush notes the community door is how students from other CPS schools reach the centre, "
     "which is what makes this site all-CPS-accessible rather than enrolled-students-only.")

for _s, _v in [("Stephen F Gale Elementary Community Academy", "Room 107"),
               ("Joyce Kilmer International Academy", "Room 109"),
               ("Theodore Roosevelt High School", "Room 166"),
               ("Nicholas Senn High School", "Room 144"),
               ("Roger C Sullivan High School", "Room 100")]:
    room(_s, _v, "high", ["tap_loc"], "Published by Tapestry 360 Health.")

room("Ludwig Van Beethoven Elementary School", "Room 134", "medium", ["cps_booklet"],
     "From the IDPH certified list ('25 West 47th St., Rm 134'). IDPH is stale on this "
     "site's provider name but the room number is not contradicted anywhere.")

room("Laura S Ward Elementary School", "Entrance on Ridgeway Ave", "high", ["erie_west"],
     "Erie: health centre entrance on the west side of the building off Ridgeway, with "
     "its own parking.")

room("Englewood STEM High School", "Door 2", "high", ["msq_prim"],
     "Mile Square publishes the address as '6835 S. Normal Blvd. Door 2'.")

room("David G Farragut Career Academy High School", "Entrance at 3256 W 24th St",
     "high", ["lchc_farragut", "340b_lchc"],
     "LCHC states the clinic is within Farragut Career Academy; the 24th Street address is "
     "its own entrance on the school's south frontage.")

room("Nathan S Davis Elementary School", "Davis Annex, 3050 W 39th Pl", "medium",
     ["uic_ocean", "msq_davis"],
     "IDPH names the location an Annex. This is the evidence behind reclassifying the site "
     "in_building; flagged because an annex may be a separate structure on the campus.")
