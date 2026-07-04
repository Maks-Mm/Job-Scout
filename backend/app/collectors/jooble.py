#backend/app/collectors/jooble.py

from app.collectors.base import JobCollector


class JoobleCollector(JobCollector):

    def fetch_jobs(self, city):

        return [

            {
                "title":
                    "Backend Engineer",

                "company":
                    "Siemens",

                "city":
                    city,

                "salary_min":
                    70000,

                "salary_max":
                    None,

                "currency":
                    "EUR",

                "url":
                    "",

                "source":
                    "Jooble"
            }

        ]