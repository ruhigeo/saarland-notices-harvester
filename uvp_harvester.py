from incremental import load_state, save_state, find_new_records, update_state

import json
import os
import re
from urllib.parse import urljoin, urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

SEARCH_URL = (
    "https://www.uvp-verbund.de/freitextsuche"
    "?rstart=0&currentSelectorPage=1"
    "&f=state%3Abw&provider=sl&layer=zv"
)

BASE_URL = "https://www.uvp-verbund.de"


def extract_date(text, label):
    pattern = re.escape(label) + r"\s+(\d{2}\.\d{2}\.\d{4})"
    match = re.search(pattern, text)
    return match.group(1) if match else None


def discover_projects(session):
    response = session.get(SEARCH_URL, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    projects = {}

    for anchor in soup.select("a[href*='trefferanzeige']"):
        heading = anchor.select_one("h2.header")

        if heading is None:
            continue

        url = urljoin(response.url, anchor["href"])
        query = parse_qs(urlparse(url).query)
        source_id = query.get("docuuid", [None])[0]

        if source_id:
            projects[source_id] = {
                "source_id": source_id,
                "title": heading.get_text(" ", strip=True),
                "source_url": (
                    BASE_URL + "/trefferanzeige?docuuid=" + source_id
                )
            }

    return list(projects.values())


def fetch_project(session, project):
    response = session.get(project["source_url"], timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for element in soup(["script", "style", "nav", "footer"]):
        element.decompose()

    main = soup.find("main")
    container = main if main else soup.body

    text = container.get_text("\n", strip=True) if container else ""

    decision_date = extract_date(
        text, "Datum der Entscheidung"
    )

    last_updated = extract_date(
        text, "Zuletzt geändert"
    )

    if "CREOS Wasserstoffleitung" in project["title"]:
        relevance = "RELATED_INFRASTRUCTURE"
    else:
        relevance = "OUT_OF_SCOPE"

    return {
        "source_id": project["source_id"],
        "title": project["title"],
        "source_url": project["source_url"],
        "last_updated": last_updated,
        "decision_date": decision_date,
        "relevance": relevance,
        "geometry": None
    }


def run():
    os.makedirs("output", exist_ok=True)

    session = requests.Session()
    projects = discover_projects(session)

    records = []
    errors = []

    for project in projects:
        try:
            records.append(fetch_project(session, project))
        except requests.RequestException as error:
            errors.append({
                "source_id": project["source_id"],
                "error": str(error)
            })

    with open(
        "output/uvp_relevance_report.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(records, file, ensure_ascii=False, indent=2)

    with open(
        "output/uvp_errors.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(errors, file, ensure_ascii=False, indent=2)

    print("Discovered:", len(projects))
    print("Extracted:", len(records))
    print("Errors:", len(errors))



def write_incremental_output():
    import json
    from pathlib import Path

    report_path = Path("output/uvp_relevance_report.json")

    with report_path.open("r", encoding="utf-8") as file:
        records = json.load(file)

    state = load_state()
    new_records = find_new_records(records, state)

    output_path = Path("output/uvp_new_records.json")
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(new_records, file, indent=2, ensure_ascii=False)

    state = update_state(state, new_records)
    save_state(state)

    print("New records:", len(new_records))
    print("Previously processed:", len(records) - len(new_records))


if __name__ == "__main__":
    run()
    write_incremental_output()
