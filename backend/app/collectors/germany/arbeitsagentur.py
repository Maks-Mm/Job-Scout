# backend/app/collectors/arbeitagentur.py

import requests

from app.collectors.base import JobCollector

API_URL = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs"
API_KEY = "jobboerse-jobsuche"

_HEADERS = {
    "User-Agent": "Jobsuche/2.9.2 (de.arbeitsagentur.app.ios; build:1077; iOS 17.0)",
    "X-API-Key": API_KEY,
    "OAuthAccessToken": "",
    "Accept": "application/json",
}

CITY_MAP = {
    "Munich": "München",
    "Cologne": "Köln",
    "Nuremberg": "Nürnberg",
    "Frankfurt": "Frankfurt am Main",
    "Brunswick": "Braunschweig",
}


class ArbeitsagenturCollector(JobCollector):

    def fetch_jobs(self, filter):
        search_city = CITY_MAP.get(filter.city, filter.city)

        params = {
            "wo": search_city,
            "size": 50,
            "umkreis": 25,
        }

        if filter.employment_type == "parttime":
            params["arbeitszeit"] = "tz"
        elif filter.employment_type == "fulltime":
            params["arbeitszeit"] = "vz"

        try:
            response = requests.get(
                API_URL,
                params=params,
                headers=_HEADERS,
                timeout=20,
            )
            print(f"[ArbeitsagenturCollector] URL: {response.url}")
            print(f"[ArbeitsagenturCollector] Status: {response.status_code}")
            print(f"[ArbeitsagenturCollector] Search city: {search_city}")

            if response.status_code == 403:
                print(
                    "[ArbeitsagenturCollector] 403 — API rejected the request. "
                    "Falling back to 0 results."
                )
                return []

            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[ArbeitsagenturCollector] Request failed: {e}")
            return []

        data = response.json()

        if data.get("woOutput", {}).get("suchmodus") == "UNGUELTIG":
            print(f"[ArbeitsagenturCollector] Invalid location: {search_city}")
            return []

        jobs = []

        for job in data.get("stellenangebote", []):
            arbeitsort = job.get("arbeitsort") or {}
            refnr = job.get("refnr")

            jobs.append(
                {
                    "title": job.get("beruf"),
                    "company": job.get("arbeitgeber"),
                    "city": arbeitsort.get("ort", search_city),
                    "date": job.get("aktuelleVeroeffentlichungsdatum"),
                    "salary_min": None,
                    "salary_max": None,
                    "currency": "EUR",
                    "url": (
                        job.get("externeUrl")
                        or (
                            f"https://www.arbeitsagentur.de/jobsuche/jobdetail/{refnr}"
                            if refnr
                            else None
                        )
                    ),
                    "source": "Arbeitsagentur",
                }
            )

        print(f"[ArbeitsagenturCollector] Returned {len(jobs)} jobs")
        return jobs