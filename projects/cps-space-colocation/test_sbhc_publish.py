#!/usr/bin/env python3
"""Build-failing assertions for data/processed/sbhc_publish.csv.

Supersedes test_sbhc.py. Three changes of substance beyond the new columns:

1. The hard source counts (34/32/28) remain as snapshot arithmetic, but are no
   longer the liveness check. Liveness is the status-aware operating count.
2. The "asserted by at least one source" check now has to pass for closed rows
   too, because a closed row is deliberately retained. Status carries the
   liveness claim; source presence carries the provenance claim.
3. in_building no longer implies a usable school id in every case, because a
   charter-campus site resolves to a school name rather than a CPS sid.
"""
import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
rows = list(csv.DictReader((ROOT / "data" / "processed" / "sbhc_publish.csv").open()))
fail = []


def check(cond, msg):
    if not cond:
        fail.append(msg)


STATUSES = ("operating", "closed", "closed_or_consolidated", "unverified")

# ---- every source row is still accounted for, at the snapshot's own counts
check(sum(1 for r in rows if r["idph_certified"] == "true") == 34,
      "IDPH Chicago rows in output != 34")
check(sum(1 for r in rows if r["cps_listed"] == "true") == 32,
      "CPS directory rows in output != 32")
check(sum(1 for r in rows if r["hrsa_scope"] == "true") == 28,
      "HRSA Chicago school-setting rows in output != 28")

# ---- the three definitions are never collapsed
for r in rows:
    for f in ("idph_certified", "cps_listed", "hrsa_scope"):
        check(r[f] in ("true", "false"), "bad %s: %s" % (f, r["site_name"]))
    check(any(r[f] == "true" for f in ("idph_certified", "cps_listed", "hrsa_scope")),
          "row asserted by no source: %s" % r["site_name"])

# ---- operational_status: populated everywhere, dated where it claims a closure
for r in rows:
    check(r["operational_status"] in STATUSES,
          "bad operational_status: %s (%s)" % (r["site_name"], r["operational_status"]))
    if r["operational_status"] == "closed":
        check(r["closed_on"], "closed with no closed_on: %s" % r["site_name"])
    if r["closed_on"]:
        check(r["operational_status"].startswith("closed"),
              "closed_on set on a row that is not closed: %s" % r["site_name"])
        check(len(r["closed_on"]) == 10 and r["closed_on"][4] == r["closed_on"][7] == "-",
              "closed_on is not ISO yyyy-mm-dd: %s" % r["site_name"])

# a closed center must not be published as open to anyone
for r in rows:
    if r["operational_status"].startswith("closed"):
        check(r["open_to_public"] != "true",
              "closed center still flagged open_to_public: %s" % r["site_name"])
        check(not any(r[c] for c in ("hours_medical_school_year", "hours_medical_summer",
                                     "hours_dental")),
              "closed center still publishing hours: %s" % r["site_name"])

# the count that actually means "live centers"; CPS publishes 33 citywide.
# The two remaining non-operating-and-not-closed rows are TCA's mobile units,
# which are unverified rather than absent: HRSA registers them, nothing current
# was checked, and no status is asserted either way.
live = sum(1 for r in rows if r["operational_status"] == "operating")
check(live == 33, "operating rows != 33 (got %d)" % live)

# ---- hours: split cleanly, never a concatenation, empty means not established
for r in rows:
    for c in ("hours_medical_school_year", "hours_medical_summer", "hours_dental"):
        check("\n" not in r[c],
              "newline inside %s - two schedules concatenated: %s" % (c, r["site_name"]))
    # a summer or dental schedule with no school-year schedule is a gap worth seeing,
    # but Drake is a known conflict left null on purpose, so this is not fatal there
    if r["hours_medical_summer"] and not r["hours_medical_school_year"]:
        check(r["site_name"] == "John B Drake Elementary School",
              "summer hours with no school-year hours: %s" % r["site_name"])

# ---- room_or_entrance is in-building evidence, so it must not appear on a
# school-linked or mobile row
for r in rows:
    if r["room_or_entrance"]:
        check(r["setting"] == "in_building",
              "room_or_entrance on a %s row: %s" % (r["setting"], r["site_name"]))

# ---- HRSA columns appear only where HRSA asserts the site
for r in rows:
    hrsa_cols = ("hrsa_site_num", "hrsa_site_name", "hrsa_grantee", "hrsa_setting_desc",
                 "hrsa_site_type", "hrsa_status", "hrsa_sbhc_subprogram")
    if r["hrsa_scope"] == "true":
        check(r["hrsa_site_num"], "hrsa_scope true with no BPHC site number: %s" % r["site_name"])
        check(r["hrsa_setting_desc"] == "School",
              "HRSA row whose setting is not School: %s" % r["site_name"])
    else:
        check(all(not r[c] for c in hrsa_cols),
              "HRSA fields populated on a non-HRSA row: %s" % r["site_name"])

nums = [r["hrsa_site_num"] for r in rows if r["hrsa_site_num"]]
check(len(nums) == len(set(nums)), "duplicate BPHC site numbers")

# ---- setting is derived, never blank on a matched row
for r in rows:
    check(r["setting"] in ("in_building", "school_linked", "mobile", ""),
          "bad setting: %s" % r["site_name"])
    if r["setting"] == "in_building":
        # a CPS sid, or a named host school for a charter-campus site
        check(r["sid"] or r["school_name"],
              "in_building row with neither school id nor school name: %s" % r["site_name"])

# ---- a coordinate must describe the center, not a school it is merely linked to
for r in rows:
    if r["lat"]:
        check(r["coord_basis"] in ("cps_school_building", "cps_offsite_override",
                                  "hrsa_site", "cdph_2014_geocode"),
              "coordinate with no recorded basis: %s" % r["site_name"])
        check(not (r["setting"] == "school_linked"
                   and r["coord_basis"] == "cps_school_building"),
              "school-linked center mapped at its school's coordinate: %s" % r["site_name"])
    else:
        check(r["coord_basis"] == "", "coord_basis set without a coordinate: %s" % r["site_name"])

# ---- sid uniqueness
sids = [r["sid"] for r in rows if r["sid"]]
dupes = [s for s, n in Counter(sids).items() if n > 1]
check(not dupes, "duplicate school ids: %s" % dupes)

# ---- provenance: anything the build resolved has to carry its citation
for r in rows:
    if r["resolution_fields"]:
        check(r["resolution_sources"], "resolved row with no sources: %s" % r["site_name"])
        check(r["verified_on"], "resolved row with no verified_on: %s" % r["site_name"])
        check(r["resolution_confidence"] in ("high", "medium", "low", "unresolved"),
              "bad resolution_confidence: %s" % r["site_name"])

# ---- the retired review gate stays retired, in both processed sheets.
# manually_verified gated publication before the gate was replaced. It carried
# "false" on every row, so republishing it would assert nothing while reading
# like a verification claim.
resolved_header = next(csv.reader(
    (ROOT / "data" / "processed" / "sbhc_resolved.csv").open()))
check("manually_verified" not in rows[0],
      "retired manually_verified column is back in sbhc_publish.csv")
check("manually_verified" not in resolved_header,
      "retired manually_verified column is back in sbhc_resolved.csv")

# ---- space-use status has one source: utilization.csv, joined on sid. The input
# sheet's status columns come from an earlier file and contradicted it for five
# host schools, so they are retired from both processed sheets.
for col in ("cps_status_2025", "cps_adjusted_su", "cps_colo"):
    check(col not in rows[0], "retired %s column is back in sbhc_publish.csv" % col)
    check(col not in resolved_header, "retired %s column is back in sbhc_resolved.csv" % col)

# ---- source sponsor claims are audit-only; publication has one canonical name
check("sponsor_cps" not in rows[0] and "sponsor_idph" not in rows[0],
      "source-specific sponsor fields leaked into publication sheet")
check(all(r["match_basis"] != "address_identity" for r in rows),
      "address_identity still published as a reviewed join basis")

# ---- load-bearing corrections most likely to disappear in a refactor
by_site = {r["site_name"]: r for r in rows}

def row(site):
    check(site in by_site, "required correction row missing: %s" % site)
    return by_site.get(site, {})

johnson = row("James Weldon Johnson STEAM Elementary School")
check(johnson.get("setting") == "school_linked", "Johnson setting regressed")
check(johnson.get("site_address") == "1504 S Albany Ave", "Johnson address regressed")
check(johnson.get("coord_basis") == "hrsa_site", "Johnson coordinate basis regressed")

hope = row("Wilma Rudolph Elementary Learning Center")
check(hope.get("school_name") == "Hope Institute Learning Academy", "Hope host school regressed")
check(hope.get("operational_status") == "closed" and hope.get("closed_on") == "2024-04-01",
      "Hope closure fields regressed")
# 610308 is Rudolph; the evidence names Hope, which has no CPS id in this release
check(hope.get("sid") == "", "Hope center still carries Rudolph's sid")
discrepancy_sids = {r["sid"] for r in csv.DictReader(
    (ROOT / "data" / "processed" / "sbhc_discrepancies.csv").open())
    if r["site_name"] == "Wilma Rudolph Elementary Learning Center"}
check(discrepancy_sids == {""}, "Hope findings still filed under Rudolph's sid")

uplift = row("Uplift Community High School")
check(uplift.get("operational_status") == "closed" and uplift.get("closed_on") == "2024-04-01",
      "Uplift closure fields regressed")

reavis = row("William C Reavis Math & Science Specialty ES")
check(reavis.get("operational_status") == "closed_or_consolidated" and not reavis.get("closed_on"),
      "Reavis status/date regressed")

comer = row("Noble - Gary Comer College Prep")
check(comer.get("lat") and comer.get("lon") and comer.get("coord_basis") == "cdph_2014_geocode",
      "Comer coordinate correction regressed")

for site in ("Paul Laurence Dunbar Career Academy High School",
             "Wendell Phillips Academy High School"):
    check(row(site).get("sponsor") == "Rush University Medical Center",
          "%s sponsor regressed" % site)

drake = row("John B Drake Elementary School")
check(drake.get("hours_medical_summer") and not drake.get("hours_medical_school_year"),
      "Drake's deliberate school-year-hours null regressed")

if fail:
    print("FAIL\n" + "\n".join(" - " + f for f in fail))
    sys.exit(1)
print("OK  %d rows (%d operating, %d closed/consolidated, %d unverified)"
      % (len(rows), live,
         sum(1 for r in rows if r["operational_status"].startswith("closed")),
         sum(1 for r in rows if r["operational_status"] == "unverified")))
