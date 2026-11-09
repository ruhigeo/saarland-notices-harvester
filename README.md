# Saarland Notices Harvester

A small prototype that collects public planning and approval notices in Saarland from HTML sources, flags possible power-substation and industrial-restructuring signals, and stages them in PostgreSQL/PostGIS without creating duplicates.

> **Status: prototype.** It is not a production pipeline. See "Limitations" for what is and isn't done.

## What it does

- **Municipal notices** (`harvester.py`, `extraction.py`): discovers public announcements on the Saarbrücken city site, extracts title, date, text and a stable source ID, and classifies each notice with transparent keyword rules (`POSSIBLE_SUBSTATION`, `POSSIBLE_INDUSTRIAL_RESTRUCTURING`, `NOT_RELEVANT`).
- **UVP-Verbund projects** (`uvp_harvester.py`): discovers Saarland environmental-impact-assessment projects from the UVP portal and keeps their `docuuid` identifiers for traceability.
- **Incremental runs** (`incremental.py`): remembers processed source IDs so repeated runs only return new records.
- **Database staging** (`schema.sql`, `database.py`, `mapping.py`, `ingest.py`): a `saarland_staging.signal_ingest` table with a unique constraint on `(source_url, source_id)`, `geometry(Point, 25832)` for ETRS89 / UTM 32N, and inserts that use `ON CONFLICT DO NOTHING`, with duplicate and error counts.
- **Quality checks** (`validation.sql`): counts by signal type and other sanity queries.

## Source investigation

The Geoportal Saarland (geoportal.saarland.de) was reviewed first. Its pages and search interface are reachable, but the search endpoint returned empty results for the requests I tried, and I found no stable HTML listing of approval notices. I therefore used the municipal and UVP sources above and have documented that deviation rather than hiding it.

## Setup

    python -m pip install -r requirements.txt
    cp .env.example .env     # then set DATABASE_URL; never commit .env
    psql -d saarland_notices -f schema.sql    # requires PostgreSQL with PostGIS

## Run

    python harvester.py          # municipal notices -> output/*.json
    python uvp_harvester.py      # UVP projects, incremental

## Tests

    python -m pytest -q

The tests (database insert, ingestion control flow, incremental state) use mocks. No live PostgreSQL/PostGIS integration test has been run yet.

## Limitations

- No confirmed in-scope approval was found in the records reviewed; the keyword classifier is a heuristic and does not establish approval status.
- No point geometries are assigned. Administrative contact addresses must not be used as project coordinates.
- The municipal harvester does not handle pagination.
- UVP search filters may not give complete Saarland coverage.
- Loading into the database is not yet wired into the harvest scripts.
- The Geoportal source itself is not harvested.

## Data and conduct

Only public pages are requested, with a timeout and a short delay between requests. Check each site's terms and robots rules before running this at scale.
