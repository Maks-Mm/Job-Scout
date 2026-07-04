#backend/app/services/job_service.py

from app.collectors import collectors


def get_jobs(city):

    all_jobs = []
    next_id = 1


    for collector in collectors:

        jobs = collector.fetch_jobs(city)

        for job in jobs:
            job["id"] = next_id
            next_id += 1

        all_jobs.extend(jobs)


    return all_jobs