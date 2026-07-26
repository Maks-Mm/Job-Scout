# backend/app/collectors/stepstone.py

import requests
from bs4 import BeautifulSoup

from app.collectors.base import JobCollector


# StepStone benutzt in URLs meist die deutschen Städtenamen.
CITY_MAP = {
    "Munich": "münchen",
    "Cologne": "köln",
    "Nuremberg": "nürnberg",
    "Frankfurt": "frankfurt-am-main",
    "Brunswick": "braunschweig",
}


class StepStoneCollector(JobCollector):

    def fetch_jobs(self, filter):

        city = CITY_MAP.get(
            filter.city,
            filter.city
        ).lower()

        keyword = (
            filter.keywords
            if filter.keywords
            else "job"
        )

        # StepStone-Suchpfad: /jobs/<keyword>/in-<stadt>
        url = (
            "https://www.stepstone.de/jobs/"
            f"{keyword.lower().replace(' ', '-')}/in-{city}"
        )

        params = {}

        # StepStone kennt eigene Query-Parameter für Arbeitszeit,
        # die aber nicht immer stabil sind -> zusätzlich lokal filtern.
        if filter.employment_type == "parttime":
            params["workType"] = "PART_TIME"
        elif filter.employment_type == "fulltime":
            params["workType"] = "FULL_TIME"
        # else: kein employment_type-Filter gesetzt -> workType weglassen

        try:
            response = requests.get(
                url,
                params=params,
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Accept-Language": "de-DE,de;q=0.9",
                },
                timeout=10,
            )

            response.raise_for_status()

        except requests.RequestException as e:
            print(f"[StepStoneCollector] request failed: {e}")
            return []

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        jobs = []

        # NOTE: Diese Selektoren sind das fragilste Teil des Collectors.
        # StepStone rendert Suchergebnisse teils über JS/React, daher kann
        # es sein, dass hier ohne Headless-Browser (z.B. Playwright) nichts
        # oder nur ein Teil der Ergebnisse ankommt. Falls das der Fall ist,
        # bitte auf einen Playwright/Requests-HTML basierten Ansatz wechseln.
        listings = soup.select(
            "article[data-testid='job-item'], article.res-1tep7hf"
        )

        for item in listings:

            title_element = item.select_one(
                "[data-testid='job-item-title'], .res-nehv70"
            )

            company_element = item.select_one(
                "[data-testid='job-item-company-name'], .res-btsdnq"
            )

            link_element = item.select_one("a")

            if not title_element:
                continue

            title = title_element.get_text(strip=True)
            company = (
                company_element.get_text(strip=True)
                if company_element
                else None
            )

            # StepStone liefert Arbeitszeit nicht immer strukturiert
            # zurück -> zusätzlich lokal auf Basis des Titels filtern.
            if filter.employment_type == "parttime":
                if "teilzeit" not in title.lower() and "part time" not in title.lower():
                    continue

            if filter.employment_type == "fulltime":
                if "vollzeit" not in title.lower() and "full time" not in title.lower():
                    continue

            # Lokaler Keyword-Filter als zusätzliche Absicherung,
            # falls die Server-seitige Suche zu breit matcht.
            if filter.keywords:
                if filter.keywords.lower() not in title.lower():
                    continue

            href = link_element.get("href") if link_element else None
            job_url = None
            if href:
                job_url = (
                    href
                    if href.startswith("http")
                    else f"https://www.stepstone.de{href}"
                )

            jobs.append(
                {
                    "title": title,
                    "company": company,
                    "city": filter.city,
                    "date": None,
                    "salary_min": None,
                    "salary_max": None,
                    "currency": "EUR",
                    "url": job_url,
                    "source": "StepStone",
                }
            )

        print(f"[StepStoneCollector] Returned {len(jobs)} jobs")

        return jobs