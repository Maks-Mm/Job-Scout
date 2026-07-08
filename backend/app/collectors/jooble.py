#backend/app/collectors/jooble.py

import requests

from app.collectors.base import JobCollector
from app.core.config import JOOBLE_API_KEY


class JoobleCollector(JobCollector):

    def fetch_jobs(self, city):
        if not JOOBLE_API_KEY:
            return []

        url = "https://jooble.org/api/" + JOOBLE_API_KEY

        payload = {
            "keywords": "Teilzeit",  # was "backend developer" — too narrow for this app's purpose
            "location": city,
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[JoobleCollector] request failed: {e}")
            return []

        data = response.json()

        # TEMP DEBUG — remove once results are confirmed flowing
        print(f"[JoobleCollector] city={city} totalCount={data.get('totalCount')} "
              f"jobs_returned={len(data.get('jobs', []))}")

        jobs = []
        for job in data.get("jobs", []):
            jobs.append({
                "title": job.get("title"),
                "company": job.get("company"),
                "city": city,
                "date": job.get("created_at") or job.get("date") or job.get("posted_date"),
                "salary_min": None,
                "salary_max": None,
                "currency": "EUR",
                "url": job.get("link"),
                "source": "Jooble",
            })

        return jobs