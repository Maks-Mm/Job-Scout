#backend/app/collectors/arbeitnow.py


import requests
from app.collectors.base import JobCollector


class ArbeitnowCollector(JobCollector):
    def fetch_jobs(self, city):
        url = "https://www.arbeitnow.com/api/job-board-api"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        jobs = []
        for job in data.get("data", []):
            if city.lower() in job.get("location", "").lower():
                jobs.append({
                    "title": job.get("title"),
                    "company": job.get("company_name"),
                    "city": city,
                    "url": job.get("url"),
                    "source": "Arbeitnow",
                    "date": job.get("created_at") or job.get("date") or job.get("publication_date"),
                    # Arbeitnow's API does not provide salary data.
                    # Explicitly set to None so the frontend normalization
                    # layer falls back to "Not specified" instead of
                    # treating a missing key differently from a present-but-empty one.
                    "salary_min": None,
                    "salary_max": None,
                })
        return jobs