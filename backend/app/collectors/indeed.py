#backend/app/collectors/indeed.py

from app.collectors.base import JobCollector


class IndeedCollector(JobCollector):

    def fetch_jobs(self, city):

        # später:
        # Indeed API / scraping

        return [

            {
                "title":
                    "Backend Developer",

                "company":
                    "Indeed Demo",

                "city":
                    city,

                "salary_min":
                    None,

                "salary_max":
                    None,

                "currency":
                    "EUR",

                "url":
                    "",

                "source":
                    "Indeed"
            }

        ]