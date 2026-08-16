import requests

from app.collectors.base import JobCollector
from app.core.config import ADZUNA_APP_ID, ADZUNA_API_KEY


class AdzunaCollector(JobCollector):
    """Adzuna job collector"""

    def __init__(self):
        super().__init__()
        self.source = "Adzuna"

    def fetch_jobs(self, filter):

        if not ADZUNA_APP_ID or not ADZUNA_API_KEY:
            print("[AdzunaCollector] Missing API keys")
            return []

        country_codes = {
            "germany": "de",
            "austria": "at",
            "switzerland": "ch",
        }

        country_code = country_codes.get(filter.country.lower(), "de")

        url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/1"

        params = {
            "app_id": ADZUNA_APP_ID,
            "app_key": ADZUNA_API_KEY,
            "results_per_page": 50,
            "where": filter.city,
        }

        if filter.keywords:
            params["what"] = filter.keywords

        if filter.employment_type == "parttime":
            params["contract_time"] = "part_time"
        elif filter.employment_type == "fulltime":
            params["contract_time"] = "full_time"

        if filter.min_salary and filter.min_salary > 0:
            params["salary_min"] = filter.min_salary * 12

        if filter.max_salary and filter.max_salary > 0:
            params["salary_max"] = filter.max_salary * 12

        print(f"[AdzunaCollector] URL: {url}")
        print(f"[AdzunaCollector] Params: {params}")

        try:
            response = requests.get(url, params=params, timeout=20)
            print(f"[AdzunaCollector] Status: {response.status_code}")
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[AdzunaCollector] request failed: {e}")
            return []

        data = response.json()
        print(f"[AdzunaCollector] Found {data.get('count', 0)} jobs")

        jobs = []

        for job in data.get("results", []):
            salary_min = job.get("salary_min")
            salary_max = job.get("salary_max")

            if salary_min:
                salary_min = round(salary_min / 12)
            if salary_max:
                salary_max = round(salary_max / 12)

            location = job.get("location", {})
            city_name = location.get("display_name", filter.city) if isinstance(location, dict) else filter.city

            company = job.get("company", {})
            company_name = company.get("display_name", "Unknown") if isinstance(company, dict) else str(company)

            category = job.get("category", {})
            category_name = category.get("label", "") if isinstance(category, dict) else str(category)

            jobs.append({
                "title": job.get("title", "Unknown"),
                "company": company_name,
                "city": city_name,
                "country": filter.country,
                "language": getattr(filter, "language", "de"),
                "description": job.get("description", ""),
                "category": category_name,
                "employment_type": job.get("contract_time", ""),
                "date": job.get("created") or "",
                "salary_min": salary_min,
                "salary_max": salary_max,
                "currency": "EUR",
                "url": job.get("redirect_url", ""),
                "source": self.source,
            })

        print(f"[AdzunaCollector] Returning {len(jobs)} jobs")
        return jobs