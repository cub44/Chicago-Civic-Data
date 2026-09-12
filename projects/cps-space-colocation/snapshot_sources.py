#!/usr/bin/env python3
"""Fetch every cited resolution source into a new dated raw directory.

The script imports URLs from resolutions.S, refuses to overwrite a dated
directory, and records the URL/content type beside each saved response.
"""
from __future__ import annotations

import csv
import mimetypes
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from resolutions import ACCESSED, S

ROOT = Path(__file__).resolve().parent
DEST = ROOT / "data" / "raw" / ACCESSED


def suffix(url: str, content_type: str) -> str:
    path_suffix = Path(urllib.parse.urlparse(url).path).suffix.lower()
    if path_suffix in {".csv", ".html", ".htm", ".json", ".pdf"}:
        return path_suffix
    guessed = mimetypes.guess_extension(content_type.split(";", 1)[0].strip())
    return ".html" if guessed in (None, ".htm") else guessed


def main() -> None:
    if DEST.exists():
        raise SystemExit(f"refusing to overwrite existing snapshot directory: {DEST}")
    DEST.mkdir(parents=True)
    manifest = []
    failures = []
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
            manifest.append((key, name, url, final_url, content_type, len(body)))
            print(f"{key:20} {len(body):9d}  {name}")
        except Exception as exc:
            failures.append((key, url, str(exc)))
            print(f"FAILED {key}: {exc}", file=sys.stderr)
    with (DEST / "manifest.csv").open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(("source_key", "file", "requested_url", "final_url",
                         "content_type", "bytes"))
        writer.writerows(manifest)
    if failures:
        with (DEST / "failures.csv").open("w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(("source_key", "url", "error"))
            writer.writerows(failures)
        raise SystemExit(
            f"{len(failures)} live source snapshots failed; preserve archived official "
            f"responses explicitly and record them in {DEST / 'manifest.csv'}"
        )


if __name__ == "__main__":
    main()
