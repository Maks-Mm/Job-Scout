import requests
from bs4 import BeautifulSoup

from app.collectors.base import JobCollector


CITY_MAP = {
    "Munich": "muenchen",
    "Cologne": "koeln",
    "Nuremberg": "nuernberg",
    "Frankfurt": "frankfurt-am-main",
    "Berlin": "berlin",
    "Hamburg": "hamburg",
}


class StellenanzeigenCollector(JobCollector):

    def fetch_jobs(self, filter):

        city = CITY_MAP.get(
            filter.city,
            filter.city.lower()
        )

        keyword = (
            filter.keywords
            if filter.keywords
            else "jobs"
        )

        url = (
            "https://www.stellenanzeigen.de/"
            f"jobs/{keyword.lower()}/{city}/"
        )

        try:
            response = requests.get(
                url,
                headers={
                    "User-Agent":
                    (
                        "Mozilla/5.0 "
                        "(Windows NT 10.0; Win64; x64)"
                    )
                },
                timeout=10,
            )

            response.raise_for_status()

        except requests.RequestException as e:
            print(
                f"[StellenanzeigenCollector] request failed: {e}"
            )
            return []


        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )


        jobs = []


        # wahrscheinlichster Selektor
        # muss eventuell nach HTML-Prüfung angepasst werden
        listings = soup.select(
            "article, .job-item, .job-card"
        )


        for item in listings:

            title_element = item.select_one(
                "h2, h3, .job-title"
            )


            if not title_element:
                continue


            title = title_element.get_text(
                strip=True
            )


            if filter.keywords:

                if filter.keywords.lower() not in title.lower():
                    continue


            if filter.employment_type == "parttime":

                if (
                    "teilzeit" not in title.lower()
                    and
                    "part time" not in title.lower()
                ):
                    continue


            elif filter.employment_type == "fulltime":

                if (
                    "vollzeit" not in title.lower()
                    and
                    "full time" not in title.lower()
                ):
                    continue


            company_element = item.select_one(
                ".company, .employer"
            )


            link_element = item.select_one(
                "a[href]"
            )


            jobs.append(
                {
                    "title": title,

                    "company": (
                        company_element.get_text(strip=True)
                        if company_element
                        else None
                    ),

                    "city": filter.city,

                    "date": None,

                    "salary_min": None,

                    "salary_max": None,

                    "currency": "EUR",

                    "url": (
                        "https://www.stellenanzeigen.de"
                        + link_element["href"]
                        if link_element
                        and link_element.get("href")
                        and link_element["href"].startswith("/")
                        else (
                            link_element["href"]
                            if link_element
                            else None
                        )
                    ),

                    "source": "Stellenanzeigen.de",
                }
            )


        print(
            f"[StellenanzeigenCollector] Returned {len(jobs)} jobs"
        )


        return jobs 