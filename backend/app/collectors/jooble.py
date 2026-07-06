#backend/app/collectors/jooble.py

import requests

from app.collectors.base import JobCollector
from app.core.config import JOOBLE_API_KEY


class JoobleCollector(JobCollector):

    def fetch_jobs(self, city):

        if not JOOBLE_API_KEY:
            return []


        url = (
            "https://jooble.org/api/"
            + JOOBLE_API_KEY
        )


        payload = {

            "keywords":
                "backend developer",

            "location":
                city
        }


        response = requests.post(
            url,
            json=payload,
            timeout=10
        )


        data=response.json()


        jobs=[]


        for job in data.get(
            "jobs",
            []
        ):

            jobs.append({

                "title":
                    job.get("title"),

                "company":
                    job.get("company"),


                "city":
                    city,


                "salary_min":
                    None,


                "salary_max":
                    None,


                "currency":
                    "EUR",


                "url":
                    job.get("link"),


                "source":
                    "Jooble"

            })


        return jobs