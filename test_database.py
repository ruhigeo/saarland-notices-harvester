
from unittest.mock import MagicMock
from database import insert_signal


def sample_record():
    return {
        "source_id": "test-001",
        "source_url": "https://example.org/test-001",
        "title": "Test Umspannwerk",
        "publication_date": "2026-10-26",
        "signal_type": "POSSIBLE_SUBSTATION",
        "content": "Synthetic test announcement",
        "location_text": None,
        "easting": None,
        "northing": None
    }


def test_first_insert():
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value.fetchone.return_value = (1,)

    result = insert_signal(conn, sample_record())

    assert result == "INSERTED"
    conn.commit.assert_called_once()


def test_duplicate_insert():
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value.fetchone.return_value = None

    result = insert_signal(conn, sample_record())

    assert result == "DUPLICATE"
    conn.commit.assert_called_once()
