
import json
from pathlib import Path

STATE_FILE = Path("output/harvest_state.json")


def load_state():
    if not STATE_FILE.exists():
        return {"processed_ids": []}

    with STATE_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with STATE_FILE.open("w", encoding="utf-8") as file:
        json.dump(state, file, indent=2)


def find_new_records(records, state):
    processed = set(state.get("processed_ids", []))

    return [
        record for record in records
        if record.get("source_id") not in processed
    ]


def update_state(state, records):
    processed = set(state.get("processed_ids", []))

    for record in records:
        if record.get("source_id"):
            processed.add(record["source_id"])

    state["processed_ids"] = sorted(processed)
    return state
