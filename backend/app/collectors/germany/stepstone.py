# backend/app/collectors/stepstone.py

import time

import requests
from bs4 import BeautifulSoup

from app.collectors.base import JobCollector


_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "de-DE,de;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

_TIMEOUT = 25
_RETRIES = 2


# StepStone benutzt in URLs meist die deutschen Städtenamen.
CITY_MAP = {
    "Munich": "münchen",
    "Cologne": "köln",
    "Nuremberg": "nürnberg",
    "Frankfurt": "frankfurt-am-main",
    "Brunswick": "braunschweig",
}


class StepStoneCollector(JobCollector):

    def fetch_jobs(self, filter):
        city = CITY_MAP.get(filter.city, filter.city).lower()
        keyword = (filter.keywords or getattr(filter, "job_category", None) or "jobs").lower().replace(" ", "-")

        suffix = ""
        if (getattr(filter, "employment_type", "") or "").lower() in ("parttime", "part_time"):
            suffix = "?employment[0]=part_time"

        url = f"https://www.stepstone.de/jobs/{keyword}/in-{city}.html{suffix}"
        print(f"[StepStoneCollector] GET {url}")

        for attempt in range(1, _RETRIES + 1):
            try:
                response = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
                print(f"[StepStoneCollector] Status: {response.status_code} (attempt {attempt})")
                response.raise_for_status()
                return self._parse(response.text, filter)
            except requests.exceptions.Timeout:
                print(f"[StepStoneCollector] Timeout on attempt {attempt}/{_RETRIES}")
                if attempt < _RETRIES:
                    time.sleep(2)
                else:
                    print("[StepStoneCollector] All attempts timed out, returning 0 jobs")
                    return []
            except requests.RequestException as e:
                print(f"[StepStoneCollector] request failed: {e}")
                return []

        return []

    def _parse(self, html, filter):
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        listings = soup.select(
            "article[data-testid='job-item'], article.res-1tep7hf, article[data-at='job-item']"
        )

        for item in listings:
            title_element = item.select_one(
                "[data-testid='job-item-title'], .res-nehv70, [data-at='job-item-title']"
            )
            company_element = item.select_one(
                "[data-testid='job-item-company-name'], .res-btsdnq, [data-at='job-item-company-name']"
            )
            link_element = item.select_one("a[data-at='job-item-title'], a[data-testid='job-item-title'], a")

            if not title_element:
                continue

            title = title_element.get_text(strip=True)
            company = company_element.get_text(strip=True) if company_element else None

            if filter.employment_type == "parttime":
                if "teilzeit" not in title.lower() and "part time" not in title.lower():
                    continue

            if filter.employment_type == "fulltime":
                if "vollzeit" not in title.lower() and "full time" not in title.lower():
                    continue

            if filter.keywords and filter.keywords.lower() not in title.lower():
                continue

            href = link_element.get("href") if link_element else None
            job_url = None
            if href:
                job_url = href if href.startswith("http") else f"https://www.stepstone.de{href}"

            jobs.append(
                {
                    "title": title,
                    "company": company,
                    "city": filter.city,
                    "date": None,
                    "salary_min": None,
                    "salary_max": None,
                    "currency": "EUR",
                    "url": job_url,
                    "source": "StepStone",
                }
            )

        print(f"[StepStoneCollector] Returned {len(jobs)} jobs")
        return jobs