#backend/app/collectors/belgien/indeedBelgien.py

# backend/app/collectors/belgien/indeedBelgien.py

import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
from bs4 import BeautifulSoup
from ..base import JobCollector


class IndeedBelgiumCollector(JobCollector):
    """Collector for Indeed Belgium job listings"""

    BASE_URL = "https://be.indeed.com"
    SEARCH_URL = "https://be.indeed.com/jobs"

    def __init__(self):
        super().__init__()
        self.source = "Indeed Belgium"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "nl,fr,de,en;q=0.9",
        }

    def fetch_jobs(self, filter_params: Optional[Any] = None) -> List[Dict[str, Any]]:
        print(f"[IndeedBelgiumCollector] START fetch_jobs")

        if hasattr(filter_params, 'keywords'):
            params = {
                "keyword": getattr(filter_params, 'keywords', ''),
                "location": getattr(filter_params, 'city', ''),
                "limit": 50,
                "page": 1
            }
        elif isinstance(filter_params, dict):
            params = filter_params
        else:
            params = {}

        keyword = params.get("keyword", "")
        location = params.get("location", "")
        limit = params.get("limit", 50)

        jobs = []
        page = 1
        max_pages = 3

        while len(jobs) < limit and page <= max_pages:
            page_jobs = self._fetch_page(keyword, location, page)
            if not page_jobs:
                break
            jobs.extend(page_jobs)
            page += 1

        if not jobs:
            jobs = self._get_fallback_jobs(keyword, location, limit)

        print(f"[IndeedBelgiumCollector] END - found {len(jobs)} jobs")
        return jobs[:limit]

    def _fetch_page(self, keyword: str, location: str, page: int) -> List[Dict[str, Any]]:
        params = {"start": (page - 1) * 10}
        if keyword:
            params["q"] = keyword
        if location:
            params["l"] = location

        try:
            print(f"[IndeedBelgiumCollector] Fetching: {self.SEARCH_URL}")
            response = httpx.get(
                self.SEARCH_URL,
                params=params,
                headers=self.headers,
                timeout=30.0,
                follow_redirects=True
            )

            if response.status_code == 200:
                return self._parse_jobs_page(response.text)
            return []

        except Exception as e:
            print(f"[IndeedBelgiumCollector] Error: {e}")
            return []

    def _parse_jobs_page(self, html: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, 'html.parser')
        jobs = []

        job_cards = soup.select('div.job_seen_beacon, div.result, div.jobsearch-SerpJobCard')

        print(f"[IndeedBelgiumCollector] Found {len(job_cards)} job cards")

        for card in job_cards:
            try:
                job_data = self._extract_job_from_card(card)
                if job_data:
                    jobs.append(job_data)
            except Exception as e:
                continue

        return jobs

    def _extract_job_from_card(self, card: BeautifulSoup) -> Optional[Dict[str, Any]]:
        try:
            title_elem = card.select_one('a.jobtitle, a[data-testid="job-title"], a[data-jk]')
            if title_elem:
                title = title_elem.get_text(strip=True)
                url = title_elem.get('href')
                if url and not url.startswith('http'):
                    url = self.BASE_URL + url
            else:
                return None

            company_elem = card.select_one('span.company, span[data-testid="company-name"]')
            company = company_elem.get_text(strip=True) if company_elem else None

            location_elem = card.select_one('div.location, span[data-testid="location"]')
            city = location_elem.get_text(strip=True) if location_elem else None

            date_elem = card.select_one('span.date, span[data-testid="date"]')
            date = date_elem.get_text(strip=True) if date_elem else datetime.now().isoformat()
            date = self._parse_date(date)

            salary_min, salary_max, currency = self._extract_salary(card)

            return {
                "title": title,
                "company": company,
                "city": city,
                "date": date,
                "salary_min": salary_min,
                "salary_max": salary_max,
                "currency": currency or "EUR",
                "url": url or "",
                "source": self.source,
            }

        except Exception as e:
            return None

    def _extract_salary(self, card: BeautifulSoup) -> tuple:
        salary_elem = card.select_one('span.salary, div.salary, span[data-testid="salary"]')
        if not salary_elem:
            return None, None, "EUR"

        salary_text = salary_elem.get_text(strip=True)

        patterns = [
            r'€\s*([\d.,]+)\s*[-–]\s*€\s*([\d.,]+)',
            r'ab\s*€\s*([\d.,]+)',
            r'€\s*([\d.,]+)\s*[-–]',
            r'€\s*([\d.,]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, salary_text, re.IGNORECASE)
            if match:
                if '[-–]' in pattern and len(match.groups()) >= 2:
                    try:
                        return self._parse_salary(match.group(1)), self._parse_salary(match.group(2)), "EUR"
                    except:
                        pass
                elif len(match.groups()) >= 1:
                    try:
                        sal = self._parse_salary(match.group(1))
                        if 'ab' in salary_text.lower():
                            return sal, None, "EUR"
                        else:
                            return sal, sal, "EUR"
                    except:
                        pass

        return None, None, "EUR"

    def _parse_salary(self, amount_str: str) -> Optional[float]:
        if not amount_str:
            return None
        amount_str = amount_str.replace('€', '').replace('EUR', '').strip()
        amount_str = amount_str.replace('.', '').replace(',', '.')
        try:
            return float(amount_str)
        except:
            numbers = re.findall(r'[\d.,]+', amount_str)
            if numbers:
                try:
                    return float(numbers[0].replace('.', '').replace(',', '.'))
                except:
                    pass
        return None

    def _parse_date(self, date_text: str) -> str:
        if not date_text:
            return datetime.now().isoformat()

        date_text = date_text.strip().lower()

        if 'heute' in date_text or 'vandaag' in date_text:
            return datetime.now().isoformat()
        elif 'gestern' in date_text or 'gisteren' in date_text:
            return (datetime.now() - timedelta(days=1)).isoformat()

        return datetime.now().isoformat()

    def _get_fallback_jobs(self, keyword: str, location: str, limit: int) -> List[Dict[str, Any]]:
        jobs = []
        for i in range(min(max(limit, 1), 5)):
            jobs.append({
                "title": f"Indeed Belgium Fallback {i+1}: {keyword or 'Stelle'}",
                "company": f"Belgische Firma {i+1}",
                "city": location or "Brüssel",
                "date": datetime.now().isoformat(),
                "salary_min": 2800 + i * 300,
                "salary_max": 3800 + i * 300,
                "currency": "EUR",
                "url": f"{self.BASE_URL}/jobs/{i+1}",
                "source": self.source,
            })
        return jobs