
import json
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

LISTING_URL = (
    "https://www.saarbruecken.de/rathaus/"
    "stadtverwaltung/bekanntmachungen/"
    "oeffentliche_bekanntmachungen"
)

def discover_links(session):
    response = session.get(LISTING_URL, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    links = set()

    for anchor in soup.select("a[href]"):
        url = urljoin(response.url, anchor["href"])

        if "bekanntmachungen_detail/article-" in url:
            links.add(url)

    return sorted(links)


def run_harvest():
    from extraction import extract_announcement, classify_signal

    session = requests.Session()
    records = []
    errors = []

    try:
        links = discover_links(session)
    except Exception as exc:
        links = []
        errors.append({
            "stage": "discovery",
            "error": str(exc)
        })

    for url in links:
        try:
            record = extract_announcement(url)
            record["classification"] = classify_signal(record)
            records.append(record)
        except Exception as exc:
            errors.append({
                "stage": "extraction",
                "url": url,
                "error": str(exc)
            })

        time.sleep(0.5)

    output = Path("output")
    output.mkdir(exist_ok=True)

    (output / "harvested_announcements.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    (output / "errors.json").write_text(
        json.dumps(errors, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print("Discovered:", len(links))
    print("Extracted:", len(records))
    print("Errors:", len(errors))


if __name__ == "__main__":
    run_harvest()
