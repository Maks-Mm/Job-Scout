#backend/app/collectors/adzuna.py


import requests

from app.collectors.base import JobCollector
from app.core.config import (
    ADZUNA_APP_ID,
    ADZUNA_API_KEY
)


class AdzunaCollector(JobCollector):

    def fetch_jobs(self, city):

        if not ADZUNA_APP_ID:
            return []


        url = (
            "https://api.adzuna.com/"
            "v1/api/jobs/de/search/1"
        )


        params = {

            "app_id": ADZUNA_APP_ID,
            "app_key": ADZUNA_API_KEY,
            "where": city
        }


        response = requests.get(
            url,
            params=params,
            timeout=10
        )


        data = response.json()


        jobs=[]


        for job in data.get("results", []):

            jobs.append({

                "title":
                    job.get("title"),

                "company":
                    job.get("company", {})
                    .get("display_name"),


                "city":
                    city,


                "salary_min":
                    job.get("salary_min"),


                "salary_max":
                    job.get("salary_max"),


                "currency":
                    "EUR",


                "url":
                    job.get("redirect_url"),


                "source":
                    "Adzuna"
            })


        return jobs