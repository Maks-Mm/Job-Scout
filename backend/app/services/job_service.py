#backend/app/services/job_service.py

from app.collectors import collectors


def get_jobs(city, min_salary=None, max_salary=None):

    all_jobs = []
    next_id = 1

    for collector in collectors:

        jobs = collector.fetch_jobs(city)

        for job in jobs:

            salary = job.get("salary_min")

            if min_salary is not None:
                if salary is not None and salary < min_salary:
                    continue

            if max_salary is not None:
                if salary is not None and salary > max_salary:
                    continue

            job["id"] = next_id
            next_id += 1

            all_jobs.append(job)
            print(job["source"])

    return all_jobs