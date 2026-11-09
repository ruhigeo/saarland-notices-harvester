
import json
import os

from database import insert_signal
from mapping import map_uvp_to_database


def load_eligible_records(report_path):
    with open(report_path, encoding="utf-8") as file:
        records = json.load(file)

    eligible = []
    excluded = []

    for record in records:
        if record.get("relevance") == "IN_SCOPE":
            eligible.append(record)
        else:
            excluded.append(record)

    return eligible, excluded


def ingest_report(conn, report_path):
    eligible, excluded = load_eligible_records(report_path)

    counts = {
        "eligible": len(eligible),
        "excluded": len(excluded),
        "inserted": 0,
        "duplicates": 0,
        "errors": 0
    }

    for record in eligible:
        try:
            mapped_record = map_uvp_to_database(record)
            result = insert_signal(conn, mapped_record)

            if result == "INSERTED":
                counts["inserted"] += 1
            elif result == "DUPLICATE":
                counts["duplicates"] += 1

        except Exception:
            counts["errors"] += 1
            conn.rollback()

    return counts


if __name__ == "__main__":
    report = "output/uvp_relevance_report.json"

    eligible, excluded = load_eligible_records(report)

    print("Eligible:", len(eligible))
    print("Excluded:", len(excluded))

    if eligible:
        print(
            "Database insertion requires a configured "
            "PostgreSQL connection."
        )
    else:
        print("No eligible records. No database writes attempted.")
