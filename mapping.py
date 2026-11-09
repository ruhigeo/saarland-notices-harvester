
from datetime import datetime


def german_date_to_iso(value):
    if not value:
        return None

    return datetime.strptime(
        value, "%d.%m.%Y"
    ).date().isoformat()


def map_uvp_to_database(record):
    if record.get("relevance") != "IN_SCOPE":
        raise ValueError(
            "Only verified in-scope records may be mapped."
        )

    signal_type = record.get("signal_type")

    allowed_types = {
        "POWER_SUBSTATION_APPROVAL",
        "INDUSTRIAL_RESTRUCTURING_APPROVAL"
    }

    if signal_type not in allowed_types:
        raise ValueError(
            "A verified approval signal_type is required."
        )

    required_fields = [
        "source_id",
        "source_url",
        "title",
        "publication_date"
    ]

    for field in required_fields:
        if not record.get(field):
            raise ValueError(
                "Missing required field: " + field
            )

    return {
        "source_id": record["source_id"],
        "source_url": record["source_url"],
        "title": record["title"],
        "publication_date": german_date_to_iso(
            record["publication_date"]
        ),
        "signal_type": signal_type,
        "content": record.get("content"),
        "location_text": record.get("location_text"),
        "easting": record.get("easting"),
        "northing": record.get("northing")
    }
