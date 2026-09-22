#!/usr/bin/env python3
"""Capture every cited resolution source and record what was captured.

The captures themselves are third-party pages - operator sites, news articles,
agency PDFs - and are not this repository's to republish, so they are written
to data/raw/<date>/, which is gitignored, and preserved privately. What is
published is data/source/evidence_manifest.csv: one row per source with its URL,
the URL actually served, the access date, the size and the SHA-256 of the bytes
captured. Anyone can fetch a URL and compare; the owner of the private copy can
prove what the page said on the day.

    python3 snapshot_sources.py                  fetch into data/raw/<ACCESSED>/
    python3 snapshot_sources.py --manifest DIR   rewrite the manifest from DIR
    python3 snapshot_sources.py --verify DIR     check DIR against the manifest

The script imports URLs from resolutions.S and refuses to overwrite a dated
capture directory.
"""
from __future__ import annotations

import csv
import hashlib
import mimetypes
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from resolutions import ACCESSED, S

ROOT = Path(__file__).resolve().parent
DEST = ROOT / "data" / "raw" / ACCESSED
MANIFEST = ROOT / "data" / "source" / "evidence_manifest.csv"
COLUMNS = ("source_key", "requested_url", "final_url", "accessed", "content_type",
           "bytes", "sha256", "note")

# Annotations the capture log appended to a content type, moved to their own
# column so content_type holds only what the server sent.
NOTES = {
    "embedded Azure Function key redacted":
        "An unrelated client-side credential in the page was replaced with "
        "[REDACTED_AZURE_FUNCTION_KEY] before hashing; the hash is of the redacted capture.",
    "archived official response":
        "The live URL failed on the access date; captured from the Internet Archive's "
        "copy at final_url.",
}


def suffix(url: str, content_type: str) -> str:
    path_suffix = Path(urllib.parse.urlparse(url).path).suffix.lower()
    if path_suffix in {".csv", ".html", ".htm", ".json", ".pdf"}:
        return path_suffix
    guessed = mimetypes.guess_extension(content_type.split(";", 1)[0].strip())
    return ".html" if guessed in (None, ".htm") else guessed


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_notes(content_type: str) -> tuple[str, str]:
    parts = [p.strip() for p in content_type.split(";")]
    kept, notes = [], []
    for p in parts:
        if p in NOTES:
            notes.append(NOTES[p])
        else:
            kept.append(p)
    return "; ".join(kept), " ".join(notes)


def write_manifest(capture_dir: Path) -> None:
    """Build evidence_manifest.csv from a capture directory and its capture log."""
    log = list(csv.DictReader((capture_dir / "manifest.csv").open()))
    keys = {r["source_key"] for r in log}
    missing = sorted(set(S) - keys)
    unknown = sorted(keys - set(S))
    if missing or unknown:
        raise SystemExit(f"capture log disagrees with resolutions.S: "
                         f"missing {missing}, unknown {unknown}")
    out = []
    for r in sorted(log, key=lambda r: r["source_key"]):
        path = capture_dir / r["file"]
        if path.stat().st_size != int(r["bytes"]):
            raise SystemExit(f"{path.name}: size differs from the capture log")
        content_type, note = split_notes(r["content_type"])
        out.append(dict(source_key=r["source_key"], requested_url=r["requested_url"],
                        final_url=r["final_url"], accessed=ACCESSED,
                        content_type=content_type, bytes=r["bytes"],
                        sha256=sha256(path), note=note))
    with MANIFEST.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(out)
    print(f"wrote {len(out)} rows to {MANIFEST.relative_to(ROOT)}")


def verify(capture_dir: Path) -> None:
    log = {r["source_key"]: r["file"] for r in csv.DictReader((capture_dir / "manifest.csv").open())}
    bad = []
    for r in csv.DictReader(MANIFEST.open()):
        path = capture_dir / log.get(r["source_key"], "")
        if not path.is_file():
            bad.append(f"{r['source_key']}: no capture")
        elif sha256(path) != r["sha256"]:
            bad.append(f"{r['source_key']}: hash differs")
    if bad:
        raise SystemExit("FAIL\n" + "\n".join(" - " + b for b in bad))
    print(f"OK  every capture in {capture_dir} matches {MANIFEST.relative_to(ROOT)}")


def fetch() -> None:
    if DEST.exists():
        raise SystemExit(f"refusing to overwrite existing snapshot directory: {DEST}")
    DEST.mkdir(parents=True)
    log, failures = [], []
    for key, url in sorted(S.items()):
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "Chicago-Civic-Data reproducibility snapshot/1.0"},
        )
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                body = response.read()
                content_type = response.headers.get("Content-Type", "application/octet-stream")
                final_url = response.geturl()
            name = key + suffix(final_url, content_type)
            (DEST / name).write_bytes(body)
            log.append((key, name, url, final_url, content_type, len(body)))
            print(f"{key:20} {len(body):9d}  {name}")
        except Exception as exc:
            failures.append((key, url, str(exc)))
            print(f"FAILED {key}: {exc}", file=sys.stderr)
    with (DEST / "manifest.csv").open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(("source_key", "file", "requested_url", "final_url",
                         "content_type", "bytes"))
        writer.writerows(log)
    if failures:
        with (DEST / "failures.csv").open("w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(("source_key", "url", "error"))
            writer.writerows(failures)
        raise SystemExit(
            f"{len(failures)} live source snapshots failed; preserve archived official "
            f"responses explicitly, record them in {DEST / 'manifest.csv'}, then run "
            f"--manifest {DEST}"
        )
    write_manifest(DEST)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] in ("--manifest", "--verify"):
        (write_manifest if sys.argv[1] == "--manifest" else verify)(Path(sys.argv[2]))
    elif len(sys.argv) == 1:
        fetch()
    else:
        raise SystemExit(__doc__)
