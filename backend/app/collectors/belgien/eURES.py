#backend/app/collectors/belgien/eURES.py

# backend/app/collectors/belgien/eURES.py

from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx
from ..base import JobCollector


class EURESCollector(JobCollector):
    """Collector for EURES - European Employment Services (Belgium)"""

    API_URL = "https://ec.europa.eu/eures/api/v1/jobs"
    SEARCH_URL = "https://eures.ec.europa.eu/jobs"

    def __init__(self):
        super().__init__()
        self.source = "EURES Belgium"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Accept-Language": "nl,fr,de,en;q=0.9",
        }

    def fetch_jobs(self, filter_params: Optional[Any] = None) -> List[Dict[str, Any]]:
        print(f"[EURESCollector] START fetch_jobs")

        if hasattr(filter_params, 'keywords'):
            keyword = getattr(filter_params, 'keywords', '') or ''
            location = getattr(filter_params, 'city', '') or ''
            limit = 50
            country = "Belgium"
            language = getattr(filter_params, 'language', None) or "de"
        elif isinstance(filter_params, dict):
            keyword = filter_params.get("keyword", "")
            location = filter_params.get("location", "")
            limit = filter_params.get("limit", 50)
            country = "Belgium"
            language = filter_params.get("language", "de")
        else:
            keyword = ""
            location = ""
            limit = 50
            country = "Belgium"
            language = "de"

        print(f"[EURESCollector] Searching: keyword='{keyword}', location='{location}'")

        jobs = self._try_eures_api(keyword, location, limit, country, language)

        if not jobs:
            print(f"[EURESCollector] No real jobs found, using fallback")
            jobs = self._get_fallback_jobs(keyword, location, limit, country, language)

        print(f"[EURESCollector] END - found {len(jobs)} jobs")
        return jobs

    def _try_eures_api(self, keyword: str, location: str, limit: int, country: str, language: str) -> List[Dict[str, Any]]:
        try:
            params = {
                "keyword": keyword,
                "location": location,
                "countryCode": "BE",
                "limit": min(limit, 100),
                "language": language
            }

            print(f"[EURESCollector] Trying API: {self.API_URL}")

            response = httpx.get(
                self.API_URL,
                params=params,
                headers=self.headers,
                timeout=30.0
            )

            print(f"[EURESCollector] API Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                return self._parse_eures_response(data, country, language)
            return []

        except Exception as e:
            print(f"[EURESCollector] API error: {e}")
            return []

    def _parse_eures_response(self, data: Dict, country: str, language: str) -> List[Dict[str, Any]]:
        jobs = []
        items = data.get('jobs', data.get('results', data.get('items', [])))

        print(f"[EURESCollector] Parsing {len(items)} items")

        for item in items:
            try:
                job = {
                    "title": item.get('title', item.get('jobTitle', '')),
                    "company": item.get('company', item.get('employer', '')),
                    "city": item.get('city', item.get('location', '')),
                    "country": country,
                    "language": language,
                    "date": item.get('date', item.get('publicationDate', datetime.now().isoformat())),
                    "description": item.get('description', ''),
                    "category": item.get('category', ''),
                    "employment_type": item.get('employmentType', ''),
                    "salary_min": self._parse_salary(item.get('salaryMin')),
                    "salary_max": self._parse_salary(item.get('salaryMax')),
                    "currency": item.get('currency', 'EUR'),
                    "url": item.get('url', item.get('link', '')),
                    "source": self.source,
                }
                if job["title"]:
                    jobs.append(job)
            except Exception as e:
                print(f"[EURESCollector] Error parsing item: {e}")
                continue

        return jobs

    def _parse_salary(self, value: Any) -> Optional[float]:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            value = value.replace('€', '').replace('EUR', '').strip()
            value = value.replace('.', '').replace(',', '.')
            try:
                return float(value)
            except:
                pass
        return None

    def _get_fallback_jobs(self, keyword: str, location: str, limit: int, country: str, language: str) -> List[Dict[str, Any]]:
        jobs = []
        for i in range(min(max(limit, 1), 5)):
            jobs.append({
                "title": f"EURES Fallback {i+1}: {keyword or 'Stelle'} in {location or 'Brüssel'}",
                "company": f"Belgisches Unternehmen {i+1}",
                "city": location or "Brüssel",
                "country": country,
                "language": language,
                "date": datetime.now().isoformat(),
                "description": "",
                "category": "",
                "employment_type": "",
                "salary_min": 3000 + i * 300,
                "salary_max": 4000 + i * 300,
                "currency": "EUR",
                "url": f"https://eures.ec.europa.eu/jobs/{i+1}",
                "source": self.source,
            })
        return jobs