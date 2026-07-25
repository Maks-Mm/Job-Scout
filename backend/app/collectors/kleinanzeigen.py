#backend/app/collectors/kleinanzeigen.py

import requests
from bs4 import BeautifulSoup

from app.collectors.base import JobCollector


CITY_MAP = {
    "Munich": "München",
    "Cologne": "Köln",
    "Nuremberg": "Nürnberg",
    "Frankfurt": "Frankfurt am Main",
}


class KleinanzeigenCollector(JobCollector):

    def fetch_jobs(self, filter):

        city = CITY_MAP.get(
            filter.city,
            filter.city
        )

        keyword = (
            filter.keywords
            if filter.keywords
            else "job"
        )

        url = (
            "https://www.kleinanzeigen.de/"
            f"s-jobs/{city.lower()}/{keyword.lower()}/k0"
        )

        try:
            response = requests.get(
                url,
                headers={
                    "User-Agent":
                    "Mozilla/5.0"
                },
                timeout=10,
            )

            response.raise_for_status()

        except requests.RequestException as e:
            print(
                f"[KleinanzeigenCollector] request failed: {e}"
            )
            return []

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        jobs = []

        listings = soup.select(
            "article.aditem, li.ad-listitem"
        )

        for item in listings:

            title_element = item.select_one(
                ".text-module-begin"
            )

            link_element = item.select_one(
                "a"
            )

            if not title_element:
                continue

            title = title_element.get_text(
                strip=True
            )

            if filter.employment_type == "parttime":
                if "teilzeit" not in title.lower():
                    continue

            if filter.employment_type == "fulltime":
                if "vollzeit" not in title.lower():
                    continue


            jobs.append(
                {
                    "title": title,
                    "company": None,
                    "city": city,
                    "date": None,
                    "salary_min": None,
                    "salary_max": None,
                    "currency": "EUR",
                    "url": (
                        "https://www.kleinanzeigen.de"
                        + link_element["href"]
                        if link_element
                        and link_element.get("href")
                        else None
                    ),
                    "source": "Kleinanzeigen",
                }
            )

        print(
            f"[KleinanzeigenCollector] Returned {len(jobs)} jobs"
        )

        return jobs