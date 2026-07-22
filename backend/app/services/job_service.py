#backend/app/services/job_service.py

from app.services.filtering import JobFilter, filter_jobs
from app.collectors import collectors


def get_jobs(filters: JobFilter):

    all_jobs = []
    next_id = 1

    for collector in collectors[:1]:

        jobs = collector.fetch_jobs(filters)

        for job in jobs:

            job["id"] = next_id
            next_id += 1

            all_jobs.append(job)

    return filter_jobs(all_jobs, filters)