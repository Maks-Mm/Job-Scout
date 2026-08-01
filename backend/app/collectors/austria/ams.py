# backend/app/collectors/austria/ams.py

from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx
from ..base import JobCollector  # WICHTIG: Import von JobCollector


class AMSCollector(JobCollector):
    """Collector for Austrian Public Employment Service (AMS) jobs"""

    # Korrigierte AMS API Endpunkte
    API_URL = "https://www.ams.at/api/rest/job/v1/search"
    API_URL_ALT = "https://www.ams.at/arbeitsuchende/jobboerse"
    SEARCH_URL = "https://www.ams.at/arbeitsuchende/jobboerse"

    def __init__(self):
        super().__init__()
        self.source = "AMS"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/xml",
        }

    def fetch_jobs(self, filter_params: Optional[Any] = None) -> List[Dict[str, Any]]:
        print(f"[AMSCollector] START fetch_jobs")

        # Normalisiere die Parameter
        if hasattr(filter_params, 'keywords'):
            keyword = getattr(filter_params, 'keywords', '') or ''
            location = getattr(filter_params, 'city', '') or ''
            limit = 50
            country = getattr(filter_params, 'country', None) or "Austria"
            language = getattr(filter_params, 'language', None) or "de"
        elif isinstance(filter_params, dict):
            keyword = filter_params.get("keyword", "")
            location = filter_params.get("location", "")
            limit = filter_params.get("limit", 50)
            country = filter_params.get("country") or "Austria"
            language = filter_params.get("language") or "de"
        else:
            keyword = ""
            location = ""
            limit = 50
            country = "Austria"
            language = "de"

        print(f"[AMSCollector] Searching: keyword='{keyword}', location='{location}', country='{country}'")

        # Versuche verschiedene API Endpunkte
        jobs = self._try_ams_api(keyword, location, limit, country, language)

        if not jobs:
            jobs = self._try_ams_web_scrape(keyword, location, limit, country, language)

        if not jobs:
            print(f"[AMSCollector] No real jobs found, using fallback")
            jobs = self._get_fallback_jobs(keyword, location, limit, country, language)

        print(f"[AMSCollector] END - found {len(jobs)} jobs")
        return jobs

    def _try_ams_api(self, keyword: str, location: str, limit: int, country: str, language: str) -> List[Dict[str, Any]]:
        """Versuche die AMS API"""
        try:
            # AMS verwendet POST mit JSON Body
            payload = {
                "suchbegriff": keyword,
                "ort": location,
                "maxErgebnisse": min(limit, 100),
                "seite": 1
            }

            print(f"[AMSCollector] Trying API: {self.API_URL}")

            response = httpx.post(
                self.API_URL,
                json=payload,
                headers={**self.headers, "Content-Type": "application/json"},
                timeout=30.0
            )

            print(f"[AMSCollector] API Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                return self._parse_ams_response(data, country, language)
            return []
        except Exception as e:
            print(f"[AMSCollector] API error: {e}")
            return []

    def _try_ams_web_scrape(self, keyword: str, location: str, limit: int, country: str, language: str) -> List[Dict[str, Any]]:
        """Versuche die AMS Webseite zu scrapen"""
        try:
            params = {
                "q": keyword,
                "ort": location,
                "page": 1
            }

            print(f"[AMSCollector] Trying web scrape: {self.SEARCH_URL}")

            response = httpx.get(
                self.SEARCH_URL,
                params=params,
                headers=self.headers,
                timeout=30.0,
                follow_redirects=True
            )

            print(f"[AMSCollector] Web Status: {response.status_code}")

            if response.status_code == 200:
                # Hier würde das HTML-Parsing kommen
                # Für jetzt: gib leere Liste zurück
                return []
            return []
        except Exception as e:
            print(f"[AMSCollector] Web scrape error: {e}")
            return []

    def _parse_ams_response(self, data: Dict, country: str, language: str) -> List[Dict[str, Any]]:
        """Parse AMS API Response"""
        jobs = []
        items = data.get('jobs', data.get('ergebnisse', data.get('items', [])))

        print(f"[AMSCollector] Parsing {len(items)} items from API")

        for item in items:
            try:
                job = {
                    "title": item.get('titel', item.get('title', '')),
                    "company": item.get('firma', item.get('company', item.get('arbeitgeber', ''))),
                    "city": item.get('ort', item.get('city', '')),
                    "country": country,
                    "language": language,
                    "date": item.get('datum', item.get('date', datetime.now().isoformat())),
                    "description": item.get('beschreibung', item.get('description', '')),
                    "category": item.get('kategorie', item.get('category', '')),
                    "employment_type": item.get('anstellungsart', item.get('employment_type', '')),
                    "salary_min": self._parse_salary(item.get('gehalt_von', item.get('salary_min'))),
                    "salary_max": self._parse_salary(item.get('gehalt_bis', item.get('salary_max'))),
                    "currency": "EUR",
                    "url": item.get('link', item.get('url', '')),
                    "source": self.source,
                }
                if job["title"]:
                    jobs.append(job)
            except Exception as e:
                print(f"[AMSCollector] Error parsing item: {e}")
                continue

        return jobs

    def _parse_salary(self, value: Any) -> Optional[float]:
        """Parse salary value to float"""
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
        """Return fallback jobs"""
        jobs = []
        for i in range(min(max(limit, 1), 5)):
            jobs.append({
                "title": f"AMS Fallback {i+1}: {keyword or 'Stelle'} in {location or 'Wien'}",
                "company": f"AMS Partner Unternehmen {i+1}",
                "city": location or "Wien",
                "country": country,
                "language": language,
                "date": datetime.now().isoformat(),
                "description": "",
                "category": "",
                "employment_type": "",
                "salary_min": 2500 + i * 300,
                "salary_max": 3500 + i * 300,
                "currency": "EUR",
                "url": f"https://www.ams.at/jobs/{i+1}",
                "source": self.source,
            })
        return jobs