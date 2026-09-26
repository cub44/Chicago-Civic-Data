# Chicago Civic Data

Downloadable data behind projects on [Connor Ulrich Blandford’s website](https://connorblandford.com). Start with a project below for CSV downloads, definitions, sources, and limitations. No software installation is required; open CSVs in a spreadsheet or your preferred analysis tool.

| Project | Release | Downloads | Publication status |
|---|---|---|---|
| [CPS space and co-location](projects/cps-space-colocation/) ([dataset page](https://connorblandford.com/data/cps-space-colocation/)) | Release 2026-09-26; sources pulled 2026-09-09 to 2026-09-21 ([pull table](projects/cps-space-colocation/data/README.md#source-pulls)) | Schools, space utilization and co-located campuses of Chicago Public Schools (CPS), school-based health centers, public library branches, Park District buildings, city health clinics, senior centers, workforce centers, City building-footprint matches, where one was found, for the schools, library branches, park buildings, clinics, senior centers and workforce centers, a community-area summary, the seven Chicago Department of Public Health (CDPH) mental health centers, and the project page's figures (`facts.json`) | Exploratory map and article (part one of three) |

The CPS project's DOI is [https://doi.org/10.5281/zenodo.22972209](https://doi.org/10.5281/zenodo.22972209). Zenodo archives each release from 2026-09-26 on; this DOI stands for all of them and resolves to the latest.

This collection contains curated project data and documentation. Website development, raw source snapshots, third-party pages cited as evidence, historical artifacts, and work in progress are maintained separately; where a project cites a page it does not republish, it publishes the page's URL, access date and SHA-256 instead.

## Reuse and corrections

The data and prose are under [CC BY 4.0](LICENSE): every file under `projects/*/data/` and `projects/*/docs/`, each project's `checksums.sha256`, and every `*.md` file. The code is under [MIT](LICENSE-CODE): every `*.py` file, each `projects/*/Makefile`, and `.github/`. Each license file holds its license text and nothing else.

The CSVs are derived from public records and pages, among them those of Chicago Public Schools, the City of Chicago (its Data Portal, under the portal's Terms of Use, and its own web pages), the Illinois Department of Public Health (IDPH), the U.S. Health Resources and Services Administration (HRSA) and the health-center operators, and from the U.S. Census Bureau's geocoder. The CPS project's [source pull table](projects/cps-space-colocation/data/README.md#source-pulls) lists each source and the date it was pulled. The two licenses cover this repository's selection, derivation and documentation; they do not relicense those records, whose publishers' terms govern their reuse. This repository does not republish third-party pages, PDFs or raw source files, and the licenses above do not cover them. Where a project cites such a source as evidence, it publishes the URL, access date and SHA-256 of the copy it relied on (for example [`evidence_manifest.csv`](projects/cps-space-colocation/data/source/evidence_manifest.csv)); the copies themselves are preserved privately.

Cite the CPS project as:

> Blandford, Connor Ulrich. “CPS space and co-location.” Data set, release 2026-09-26. connorblandford.com. https://connorblandford.com/data/cps-space-colocation/. https://doi.org/10.5281/zenodo.22972209.

Name the CSV you used as well. Each release is a git tag, so the files you cite stay retrievable after the next one, and [`CITATION.cff`](CITATION.cff) carries the same details for reference managers. Report corrections through [Issues](https://github.com/cub44/Chicago-Civic-Data/issues), including the filename, school ID, and disputed value.
