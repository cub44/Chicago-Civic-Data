#!/usr/bin/env python3
"""
Emits three new files from sbhc.csv + resolutions.py. Neither input sheet is modified.

  data/processed/sbhc_discrepancies.csv  one row per finding about a (site, field) pair
  data/processed/sbhc_resolved.csv       source columns plus parallel resolved_* columns
  data/processed/sbhc_publish.csv        canonical publication-shaped sheet

Schema additions in this revision:
  operational_status + closed_on      closures become data, not an absence
  hours_medical_school_year
  hours_medical_summer                Mile Square publishes two windows
  hours_dental                        Hibbard runs a second clinic
  room_or_entrance                    strongest in-building evidence available

Conventions carried over from the repo:
  - processed data is script output, never hand-edited
  - unresolved values stay empty; nothing is interpolated or guessed
  - an empty hours_* cell means "not established", never "same as school year"
"""
import csv
from collections import defaultdict
from pathlib import Path

from resolutions import ACCESSED, HOURS, R, ROOM, SID, SPONSOR_LEGAL_NAME, STATUS

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "data" / "source" / "sbhc.csv"
OUT = ROOT / "data" / "processed"

FIELD_TO_COL = {
    "sponsor": "resolved_sponsor",
    "setting": "resolved_setting",
    "site_address": "resolved_site_address",
    "zip": "resolved_zip",
    "phone": "resolved_phone",
    "hours": "resolved_hours",
    "access_text": "resolved_access_text",
    "school_name": "resolved_school_name",
    "operational_status": "resolved_operational_status",
    "lat_lon": "resolved_lat_lon",
}

NEW_SCHEMA_COLS = ["operational_status", "closed_on", "hours_medical_school_year",
                   "hours_medical_summer", "hours_dental", "room_or_entrance",
                   "sponsor_legal_name"]

PROVENANCE_COLS = ["resolution_confidence", "resolution_fields", "resolution_sources",
                   "resolution_note", "verified_on"]

# Columns the new schema supersedes. Dropped from sbhc_publish.csv only; both the
# source sheet and sbhc_resolved.csv keep them so the change stays auditable.
SUPERSEDED = ["hours"]

# Retired columns: dropped from every processed sheet, not just the publication
# one. The input sheet keeps them; this build never modifies its inputs.
#
# manually_verified was the pre-publication review gate. That gate has been
# replaced, so the column no longer means anything - it was "false" on all 38
# rows - and there is nothing in it to audit.
#
# cps_status_2025, cps_adjusted_su and cps_colo were copied into the input sheet
# from an earlier space-utilization file than the SY2026 workbook behind
# utilization.csv, and carry no vintage of their own. Published beside it they
# contradicted it: five host schools (Marquette, National Teachers, Gary Comer,
# Sullivan, Roosevelt) had a different status in each file. utilization.csv is
# the one source of space-use status; join it on sid.
RETIRED = ["manually_verified", "cps_status_2025", "cps_adjusted_su", "cps_colo"]

RANK = {"high": 3, "medium": 2, "low": 1, "unresolved": 0}


def worst(confidences):
    return min(confidences, key=lambda c: RANK[c]) if confidences else ""


def merge_sources(existing, new):
    for s in new.split("; "):
        if s and s not in existing:
            existing.append(s)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(SRC.open()))
    by_site = {r["site_name"]: r for r in rows}

    # every registry key must name a real row, or a join is silently wrong
    for label, keys in (("resolutions", {x["site_name"] for x in R}),
                        ("STATUS", set(STATUS)), ("HOURS", set(HOURS)), ("ROOM", set(ROOM)),
                        ("SID", set(SID))):
        unknown = sorted(keys - set(by_site))
        if unknown:
            raise SystemExit("%s references site_name values not in %s: %s"
                             % (label, SRC, unknown))

    # status is the one column that must be populated for every row: an empty
    # operational_status would reintroduce exactly the ambiguity it exists to remove
    missing = sorted(set(by_site) - set(STATUS))
    if missing:
        raise SystemExit("operational_status missing for: %s" % missing)

    # ---- discrepancy table ---------------------------------------------
    findings = [dict(x) for x in R]
    for site, d in STATUS.items():
        findings.append(dict(site_name=site, field="operational_status",
                             cps_value="", idph_value="", other_value="",
                             resolved=d["operational_status"]
                             + (" (%s)" % d["closed_on"] if d["closed_on"] else ""),
                             confidence=d["confidence"], sources=d["sources"],
                             accessed=d["accessed"], note=d["note"]))
    for site, d in HOURS.items():
        findings.append(dict(
            site_name=site, field="hours_split",
            cps_value=by_site[site]["hours"], idph_value="", other_value="",
            resolved=" || ".join(filter(None, [
                "school_year: " + d["hours_medical_school_year"]
                if d["hours_medical_school_year"] else "",
                "summer: " + d["hours_medical_summer"] if d["hours_medical_summer"] else "",
                "dental: " + d["hours_dental"] if d["hours_dental"] else ""])),
            confidence=d["confidence"], sources=d["sources"], accessed=d["accessed"],
            note=d["note"]))
    for site, d in ROOM.items():
        findings.append(dict(site_name=site, field="room_or_entrance",
                             cps_value="", idph_value="", other_value="",
                             resolved=d["room_or_entrance"], confidence=d["confidence"],
                             sources=d["sources"], accessed=d["accessed"], note=d["note"]))

    for site, d in SID.items():
        findings.append(dict(site_name=site, field="sid",
                             cps_value=by_site[site]["sid"], idph_value="", other_value="",
                             resolved=d["sid"] or "blank: host school has no CPS id",
                             confidence=d["confidence"], sources=d["sources"],
                             accessed=d["accessed"], note=d["note"]))

    # the sid a finding is filed under is the corrected one, so no table in the
    # release associates a center with a school the evidence rules out
    def published_sid(site):
        return SID[site]["sid"] if site in SID else by_site[site]["sid"]

    ev_cols = ["site_name", "sid", "field", "cps_value", "idph_value", "other_value",
               "resolved", "confidence", "sources", "accessed", "note"]
    with (OUT / "sbhc_discrepancies.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=ev_cols)
        w.writeheader()
        for x in sorted(findings, key=lambda d: (d["site_name"], d["field"])):
            x["sid"] = published_sid(x["site_name"])
            w.writerow({c: x.get(c, "") for c in ev_cols})

    # ---- resolved + publish sheets --------------------------------------
    grouped = defaultdict(list)
    for x in R:
        grouped[x["site_name"]].append(x)

    resolved_cols = [c for c in list(rows[0].keys()) if c not in RETIRED] \
        + list(FIELD_TO_COL.values()) + NEW_SCHEMA_COLS + PROVENANCE_COLS
    publish_cols = [c for c in resolved_cols
                    if c not in SUPERSEDED and not c.startswith("resolved_")]

    out_rows = []
    for r in rows:
        o = dict(r)
        for c in list(FIELD_TO_COL.values()) + NEW_SCHEMA_COLS + PROVENANCE_COLS:
            o[c] = ""

        srcs, notes, fields, confs = [], [], [], []

        for x in grouped.get(r["site_name"], []):
            col = FIELD_TO_COL[x["field"]]
            # an unresolved finding contributes evidence, never a value
            if x["confidence"] != "unresolved" and x["resolved"]:
                o[col] = x["resolved"]
            fields.append("%s(%s)" % (x["field"], x["confidence"]))
            confs.append(x["confidence"])
            merge_sources(srcs, x["sources"])
            if x["note"]:
                notes.append("[%s] %s" % (x["field"], x["note"]))

        st = STATUS[r["site_name"]]
        o["operational_status"] = st["operational_status"]
        o["closed_on"] = st["closed_on"]
        fields.append("operational_status(%s)" % st["confidence"])
        confs.append(st["confidence"])
        merge_sources(srcs, st["sources"])
        if st["note"]:
            notes.append("[operational_status] %s" % st["note"])

        if r["site_name"] in HOURS:
            h = HOURS[r["site_name"]]
            for c in ("hours_medical_school_year", "hours_medical_summer", "hours_dental"):
                o[c] = h[c]
            fields.append("hours_split(%s)" % h["confidence"])
            confs.append(h["confidence"])
            merge_sources(srcs, h["sources"])
            if h["note"]:
                notes.append("[hours_split] %s" % h["note"])
        elif r["hours"]:
            # no split established: carry the source value forward as school-year
            # medical rather than silently dropping it
            o["hours_medical_school_year"] = r["hours"]
            fields.append("hours_split(carried)")

        if r["site_name"] in SID:
            sd = SID[r["site_name"]]
            fields.append("sid(%s)" % sd["confidence"])
            confs.append(sd["confidence"])
            merge_sources(srcs, sd["sources"])
            if sd["note"]:
                notes.append("[sid] %s" % sd["note"])

        if r["site_name"] in ROOM:
            rm = ROOM[r["site_name"]]
            o["room_or_entrance"] = rm["room_or_entrance"]
            fields.append("room_or_entrance(%s)" % rm["confidence"])
            confs.append(rm["confidence"])
            merge_sources(srcs, rm["sources"])
            if rm["note"]:
                notes.append("[room_or_entrance] %s" % rm["note"])

        o["resolution_fields"] = " ".join(sorted(fields))
        o["resolution_confidence"] = worst(confs)
        o["resolution_sources"] = " | ".join(srcs)
        o["resolution_note"] = " ".join(notes)
        o["verified_on"] = ACCESSED
        o["sponsor_legal_name"] = SPONSOR_LEGAL_NAME.get(r["site_name"], "")
        out_rows.append(o)

    with (OUT / "sbhc_resolved.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=resolved_cols, extrasaction="ignore")
        w.writeheader()
        for o in out_rows:
            w.writerow(o)

    # The publish sheet is the canonical one, so a resolved value has to land in the
    # canonical column rather than sit in a parallel resolved_* column next to a
    # value now known to be wrong. sbhc_resolved.csv keeps both sides for the diff.
    OVERLAY = {"resolved_setting": "setting",
               "resolved_site_address": "site_address",
               "resolved_zip": "zip",
               "resolved_phone": "phone",
               "resolved_access_text": "access_text",
               "resolved_school_name": "school_name"}
    # The publication sheet exposes the canonical operating-unit name and, where
    # established, the legal grantee. Source-specific sponsor claims remain in
    # sbhc_resolved.csv for audit and are not parallel public sponsor columns.
    publish_cols = ["sponsor"] + [
        c for c in publish_cols if c not in ("sponsor_cps", "sponsor_idph")
    ]

    with (OUT / "sbhc_publish.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=publish_cols, extrasaction="ignore")
        w.writeheader()
        for o in out_rows:
            p = dict(o)
            for rc, canon in OVERLAY.items():
                if o[rc]:
                    p[canon] = o[rc]
            # single canonical sponsor; the two source columns stay for audit
            p["sponsor"] = o["resolved_sponsor"] or o["sponsor_cps"] or o["sponsor_idph"]
            p["sponsor_legal_name"] = o["sponsor_legal_name"]
            # sbhc_resolved.csv keeps the input sid for audit; publication carries
            # the corrected one, which may be blank
            if o["site_name"] in SID:
                p["sid"] = SID[o["site_name"]]["sid"]
            # The address-identity join was wrong for all three rows it created.
            # Preserve it in the audit sheet, but never publish it as a valid basis.
            if p["match_basis"] == "address_identity":
                p["match_basis"] = "evidence_resolution"
            if o["resolved_lat_lon"]:
                lat, lon = o["resolved_lat_lon"].split(",")
                p["lat"], p["lon"] = lat.strip(), lon.strip()
                p["coord_basis"] = "cdph_2014_geocode"
            w.writerow(p)

    # ---- console summary ------------------------------------------------
    per_status = defaultdict(list)
    for o in out_rows:
        per_status[o["operational_status"]].append(o["site_name"])
    print("%d rows, %d findings" % (len(rows), len(findings)))
    for k in ("operating", "closed", "closed_or_consolidated", "unverified"):
        if per_status[k]:
            print("  %-24s %2d  %s"
                  % (k, len(per_status[k]),
                     "" if k == "operating" else ", ".join(sorted(per_status[k]))))
    print("hours: %d researched splits, %d carried forward, %d empty"
          % (len(HOURS),
             sum(1 for o in out_rows if "hours_split(carried)" in o["resolution_fields"]),
             sum(1 for o in out_rows if not any(
                 o[c] for c in ("hours_medical_school_year", "hours_medical_summer",
                                "hours_dental")))))
    print("room_or_entrance populated: %d" % sum(1 for o in out_rows if o["room_or_entrance"]))
    print("unresolved: %s" % ", ".join(sorted(
        "%s/%s" % (x["site_name"], x["field"])
        for x in findings if x["confidence"] == "unresolved")))


if __name__ == "__main__":
    main()
