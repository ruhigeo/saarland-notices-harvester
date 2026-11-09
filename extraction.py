
import re
from datetime import date
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

GERMAN_MONTHS = {
    "Januar": 1, "Februar": 2, "März": 3,
    "April": 4, "Mai": 5, "Juni": 6,
    "Juli": 7, "August": 8, "September": 9,
    "Oktober": 10, "November": 11,
    "Dezember": 12
}


def extract_announcement(url):
    response = requests.get(url, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    main = soup.select_one("main#content")

    if main is None:
        raise ValueError("Main article container not found")

    heading = main.select_one("h1.headline")
    date_element = main.select_one("small.text-muted")
    content = main.select_one("section.cmp.content")

    if not all([heading, date_element, content]):
        raise ValueError("Required article fields missing")

    date_text = date_element.get_text(" ", strip=True)
    match = re.search(
        r"(\d{1,2})\.\s+(\w+)\s+(\d{4})",
        date_text
    )

    if not match:
        raise ValueError("Publication date not recognized")

    day, month, year = match.groups()

    publication_date = date(
        int(year),
        GERMAN_MONTHS[month],
        int(day)
    ).isoformat()

    return {
        "source_id": urlparse(url).path.rstrip("/").split("/")[-1],
        "title": heading.get_text(" ", strip=True),
        "publication_date": publication_date,
        "source_url": url,
        "content": content.get_text(" ", strip=True),
        "location_text": None,
        "signal_type": None,
        "geometry": None
    }


def classify_signal(record):
    text = (
        record["title"] + " " + record["content"]
    ).lower()

    substation_terms = [
        "umspannwerk",
        "umspannanlage",
        "transformatorenstation"
    ]

    industrial_terms = [
        "industriebetrieb",
        "industriestandort",
        "stahlwerk"
    ]

    restructuring_terms = [
        "umstrukturierung",
        "stilllegung",
        "restrukturierung",
        "standortschließung"
    ]

    if any(term in text for term in substation_terms):
        return "POSSIBLE_SUBSTATION"

    if (
        any(term in text for term in industrial_terms)
        and any(term in text for term in restructuring_terms)
    ):
        return "POSSIBLE_INDUSTRIAL_RESTRUCTURING"

    return "NOT_RELEVANT"
