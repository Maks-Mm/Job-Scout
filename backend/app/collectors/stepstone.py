#backend/app/collectors/stepstone.py

from app.collectors.base import JobCollector


class StepstoneCollector(JobCollector):

    def fetch_jobs(self, city):

        return [

            {

                "title":
                    "Python Developer",

                "company":
                    "Stepstone Demo",

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
                    "Stepstone"

            }

        ]