
import incremental


def test_first_run_identifies_new_records(tmp_path, monkeypatch):
    monkeypatch.setattr(
        incremental, "STATE_FILE", tmp_path / "state.json"
    )

    records = [
        {"source_id": "TEST-001"},
        {"source_id": "TEST-002"}
    ]

    state = incremental.load_state()
    new_records = incremental.find_new_records(records, state)

    assert len(new_records) == 2


def test_second_run_skips_previously_processed_ids(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(
        incremental, "STATE_FILE", tmp_path / "state.json"
    )

    records = [
        {"source_id": "TEST-001"},
        {"source_id": "TEST-002"}
    ]

    state = incremental.load_state()
    state = incremental.update_state(state, records)
    incremental.save_state(state)

    reloaded_state = incremental.load_state()
    new_records = incremental.find_new_records(
        records, reloaded_state
    )

    assert new_records == []


def test_new_id_is_detected_on_later_run(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(
        incremental, "STATE_FILE", tmp_path / "state.json"
    )

    previous = [{"source_id": "TEST-001"}]
    current = [
        {"source_id": "TEST-001"},
        {"source_id": "TEST-002"}
    ]

    state = incremental.update_state(
        incremental.load_state(), previous
    )
    incremental.save_state(state)

    new_records = incremental.find_new_records(
        current, incremental.load_state()
    )

    assert [r["source_id"] for r in new_records] == ["TEST-002"]
