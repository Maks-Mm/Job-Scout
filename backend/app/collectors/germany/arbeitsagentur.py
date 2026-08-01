# backend/app/collectors/arbeitagentur.py

import requests

from app.collectors.base import JobCollector

API_URL = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs"
API_KEY = "jobboerse-jobsuche"

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
        }

        if filter.employment_type == "parttime":
            params["arbeitszeit"] = "tz"
        elif filter.employment_type == "fulltime":
            params["arbeitszeit"] = "vz"
        # else: no employment_type filter set -> omit arbeitszeit entirely

        headers = {
            "X-API-Key": API_KEY,
            "Accept": "application/json",
        }

        try:
            response = requests.get(
                API_URL,
                params=params,
                headers=headers,
                timeout=10,
            )

            response.raise_for_status()

        except requests.RequestException as e:
            print(f"[ArbeitsagenturCollector] Request failed: {e}")
            return []

        data = response.json()

        print(f"[ArbeitsagenturCollector] URL: {response.url}")
        print(f"[ArbeitsagenturCollector] Status: {response.status_code}")
        print(f"[ArbeitsagenturCollector] Search city: {search_city}")

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

        print(
            f"[ArbeitsagenturCollector] Returned {len(jobs)} jobs"
        )

        return jobs