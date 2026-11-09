
import json
from unittest.mock import MagicMock, patch

from ingest import ingest_report, load_eligible_records


def test_excludes_unrelated_records(tmp_path):
    report = tmp_path / "report.json"
    report.write_text(
        json.dumps([
            {"source_id": "1", "relevance": "OUT_OF_SCOPE"},
            {"source_id": "2", "relevance": "RELATED_INFRASTRUCTURE"}
        ]),
        encoding="utf-8"
    )

    eligible, excluded = load_eligible_records(str(report))

    assert len(eligible) == 0
    assert len(excluded) == 2


def test_insert_and_duplicate_counts(tmp_path):
    report = tmp_path / "report.json"
    report.write_text(
        json.dumps([
            {
                "source_id": "TEST-001",
                "source_url": "https://example.org/approval/001",
                "title": "Synthetic substation approval",
                "publication_date": "01.10.2026",
                "signal_type": "POWER_SUBSTATION_APPROVAL",
                "relevance": "IN_SCOPE"
            },
            {
                "source_id": "TEST-002",
                "source_url": "https://example.org/approval/002",
                "title": "Synthetic industrial restructuring approval",
                "publication_date": "02.10.2026",
                "signal_type": "INDUSTRIAL_RESTRUCTURING_APPROVAL",
                "relevance": "IN_SCOPE"
            }
        ]),
        encoding="utf-8"
    )

    connection = MagicMock()

    with patch(
        "ingest.insert_signal",
        side_effect=["INSERTED", "DUPLICATE"]
    ) as mocked_insert:
        counts = ingest_report(connection, str(report))

    assert counts["eligible"] == 2
    assert counts["inserted"] == 1
    assert counts["duplicates"] == 1
    assert mocked_insert.call_count == 2


def test_database_error_is_counted(tmp_path):
    report = tmp_path / "report.json"
    report.write_text(
        json.dumps([
            {
                "source_id": "TEST-ERROR",
                "source_url": "https://example.org/approval/error",
                "title": "Synthetic substation approval",
                "publication_date": "03.10.2026",
                "signal_type": "POWER_SUBSTATION_APPROVAL",
                "relevance": "IN_SCOPE"
            }
        ]),
        encoding="utf-8"
    )

    connection = MagicMock()

    with patch(
        "ingest.insert_signal",
        side_effect=RuntimeError("Database unavailable")
    ):
        counts = ingest_report(connection, str(report))

    assert counts["errors"] == 1
    connection.rollback.assert_called_once()
