# backend/app/services/job_service.py

from concurrent.futures import ThreadPoolExecutor, as_completed
from app.services.filtering import JobFilter, filter_jobs
from app.collectors import collectors


def get_jobs(filters: JobFilter):
    all_jobs = []
    next_id = 1

    def run_collector(collector):
        try:
            return collector.fetch_jobs(filters)
        except Exception as e:
            print(f"{collector.__class__.__name__} failed: {e}")
            return []

    with ThreadPoolExecutor(max_workers=len(collectors)) as executor:
        futures = {executor.submit(run_collector, c): c for c in collectors}
        for future in as_completed(futures, timeout=25):
            jobs = future.result()
            for job in jobs:
                job["id"] = next_id
                next_id += 1
                all_jobs.append(job)

    return filter_jobs(all_jobs, filters)