#backend/app/collectors/Arbeitnow.py


import requests

from app.collectors.base import JobCollector


class ArbeitnowCollector(JobCollector):


    def fetch_jobs(self, city):


        url="https://www.arbeitnow.com/api/job-board-api"


        response=requests.get(
            url,
            timeout=10
        )


        data=response.json()


        jobs=[]


        for job in data.get(
            "data",
            []
        ):


            if city.lower() in job.get(
                "location",
                ""
            ).lower():


                jobs.append({

                    "title":
                        job.get("title"),


                    "company":
                        job.get("company_name"),


                    "city":
                        city,


                    "url":
                        job.get("url"),


                    "source":
                        "Arbeitnow"

                })


        return jobs