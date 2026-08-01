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

        # WICHTIG: "article.aditem, li.ad-listitem" war ein OR-Selektor.
        # Auf kleinanzeigen.de ist jede Anzeige aktuell ein
        # <article class="aditem">, das INNERHALB eines
        # <li class="ad-listitem"> liegt -> beide Selektoren matchen
        # dieselbe Anzeige, jede wurde also zweimal eingesammelt.
        # Nur noch das äußere li.ad-listitem verwenden und darin
        # gezielt nach article.aditem suchen (falls vorhanden),
        # sonst das li selbst als Container nehmen.
        listings = soup.select("li.ad-listitem")

        # Zusätzliche Absicherung gegen zukünftige HTML-Änderungen:
        # falls li.ad-listitem mal nicht mehr existiert, auf
        # article.aditem zurückfallen, aber dann NICHT beide zugleich.
        if not listings:
            listings = soup.select("article.aditem")

        seen_urls = set()

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

            href = (
                link_element.get("href")
                if link_element
                else None
            )

            job_url = (
                "https://www.kleinanzeigen.de" + href
                if href
                else None
            )

            # Zusätzliche Deduplizierung über die URL als Sicherheitsnetz,
            # falls sich das HTML wieder ändert und erneut Überlappungen
            # zwischen Selektoren auftreten.
            if job_url and job_url in seen_urls:
                continue

            if job_url:
                seen_urls.add(job_url)

            jobs.append(
                {
                    "title": title,
                    "company": None,
                    "city": city,
                    "date": None,
                    "salary_min": None,
                    "salary_max": None,
                    "currency": "EUR",
                    "url": job_url,
                    "source": "Kleinanzeigen",
                }
            )

        print(
            f"[KleinanzeigenCollector] Returned {len(jobs)} jobs"
        )

        return jobs