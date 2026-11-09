
-- Total ingested signals
SELECT COUNT(*) AS total_records
FROM saarland_staging.signal_ingest;

-- Records by signal type
SELECT signal_type, COUNT(*) AS record_count
FROM saarland_staging.signal_ingest
GROUP BY signal_type
ORDER BY signal_type;

-- Duplicate source identifiers
SELECT source_url, source_id, COUNT(*) AS occurrences
FROM saarland_staging.signal_ingest
GROUP BY source_url, source_id
HAVING COUNT(*) > 1;

-- Missing mandatory fields
SELECT COUNT(*) AS incomplete_records
FROM saarland_staging.signal_ingest
WHERE source_id IS NULL
   OR TRIM(source_id) = ''
   OR source_url IS NULL
   OR TRIM(source_url) = ''
   OR title IS NULL
   OR TRIM(title) = ''
   OR signal_type IS NULL;

-- Geometry quality
SELECT
    COUNT(*) FILTER (WHERE geom IS NULL) AS unresolved_locations,
    COUNT(*) FILTER (
        WHERE geom IS NOT NULL
        AND ST_SRID(geom) = 25832
        AND ST_IsValid(geom)
    ) AS valid_geometries
FROM saarland_staging.signal_ingest;

-- Publication date range
SELECT
    MIN(publication_date) AS earliest_publication,
    MAX(publication_date) AS latest_publication
FROM saarland_staging.signal_ingest;
