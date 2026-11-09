
CREATE SCHEMA IF NOT EXISTS saarland_staging;

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS saarland_staging.signal_ingest (
    id BIGSERIAL PRIMARY KEY,
    source_id TEXT NOT NULL,
    source_url TEXT NOT NULL,
    title TEXT NOT NULL,
    publication_date DATE,
    signal_type TEXT NOT NULL,
    content TEXT,
    location_text TEXT,
    geom geometry(Point, 25832),
    ingested_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT uq_signal_source UNIQUE (source_url, source_id)
);
