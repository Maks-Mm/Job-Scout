#backend/app/collectors/adzuna.py

# backend/app/collectors/adzuna.py

import requests
from app.collectors.base import JobCollector
from app.core.config import ADZUNA_APP_ID, ADZUNA_API_KEY


class AdzunaCollector(JobCollector):

    def fetch_jobs(self, filter):
        if not ADZUNA_APP_ID or not ADZUNA_API_KEY:
            return []

        url = "https://api.adzuna.com/v1/api/jobs/de/search/1"

        params = {
            "app_id": ADZUNA_APP_ID,
            "app_key": ADZUNA_API_KEY,
            "where": filter.city,
        }

        if filter.employment_type == "parttime":
            params["contract_time"] = "part_time"
        elif filter.employment_type == "fulltime":
            params["contract_time"] = "full_time"
        # else: no employment_type filter set -> omit contract_time entirely

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[AdzunaCollector] request failed: {e}")
            return []

        data = response.json()
        jobs = []

        for job in data.get("results", []):
            jobs.append({
                "title": job.get("title"),
                "company": job.get("company", {}).get("display_name"),
                "city": filter.city,
                "date": job.get("created") or job.get("created_at") or job.get("publication_date"),
                "salary_min": job.get("salary_min"),
                "salary_max": job.get("salary_max"),
                "currency": "EUR",
                "url": job.get("redirect_url"),
                "source": "Adzuna",
            })

        return jobs