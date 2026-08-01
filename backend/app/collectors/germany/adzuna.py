# backend/app/collectors/adzuna.py

import requests
from app.collectors.base import JobCollector
from app.core.config import ADZUNA_APP_ID, ADZUNA_API_KEY


# Adzuna market/country codes it supports for this app
COUNTRY_CODE_MAP = {
    "germany": "de",
    "austria": "at",
    "switzerland": "ch",  # not actually supported by Adzuna, will fail gracefully
}


class AdzunaCollector(JobCollector):

    def fetch_jobs(self, filter):
        if not ADZUNA_APP_ID or not ADZUNA_API_KEY:
            return []

        country_key = (filter.country or "germany").strip().lower()
        market = COUNTRY_CODE_MAP.get(country_key, "de")

        url = f"https://api.adzuna.com/v1/api/jobs/{market}/search/1"

        params = {
            "app_id": ADZUNA_APP_ID,
            "app_key": ADZUNA_API_KEY,
            "results_per_page": 50,
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
            location_data = job.get("location", {}) or {}
            area = location_data.get("area", []) or []
            # Adzuna's "area" list is usually [country, region, ..., city]
            city_name = area[-1] if area else (location_data.get("display_name") or filter.city)

            company = job.get("company")
            company_name = (
                company.get("display_name", "Unknown")
                if isinstance(company, dict)
                else str(company or "Unknown")
            )

            category = job.get("category")
            category_label = (
                category.get("label", "")
                if isinstance(category, dict)
                else str(category or "")
            )

            jobs.append({
                "title": job.get("title", "Unknown"),
                "company": company_name,
                "city": city_name,
                "country": filter.country,
                "language": getattr(filter, "language", "de"),

                "date": (
                    job.get("created")
                    or job.get("created_at")
                    or job.get("publication_date")
                    or ""
                ),

                "description": job.get("description") or "",
                "category": category_label,
                "employment_type": job.get("contract_time") or "",

                "salary_min": job.get("salary_min"),
                "salary_max": job.get("salary_max"),
                "currency": "EUR",

                "url": job.get("redirect_url") or job.get("url") or "",

                "source": self.source,
            })

        print(f"[AdzunaCollector] ✅ market={market} found {data.get('count', len(jobs))} total, returning {len(jobs)} jobs")

        return jobs