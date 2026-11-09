
def insert_signal(conn, record):
    sql = """
        INSERT INTO saarland_staging.signal_ingest (
            source_id,
            source_url,
            title,
            publication_date,
            signal_type,
            content,
            location_text,
            geom
        )
        VALUES (
            %(source_id)s,
            %(source_url)s,
            %(title)s,
            %(publication_date)s,
            %(signal_type)s,
            %(content)s,
            %(location_text)s,
            CASE
                WHEN %(easting)s IS NOT NULL
                 AND %(northing)s IS NOT NULL
                THEN ST_SetSRID(
                    ST_MakePoint(
                        %(easting)s,
                        %(northing)s
                    ),
                    25832
                )
                ELSE NULL
            END
        )
        ON CONFLICT (source_url, source_id)
        DO NOTHING
        RETURNING id;
    """

    params = {
        **record,
        "easting": record.get("easting"),
        "northing": record.get("northing")
    }

    with conn.cursor() as cursor:
        cursor.execute(sql, params)
        result = cursor.fetchone()

    conn.commit()

    return "INSERTED" if result else "DUPLICATE"
