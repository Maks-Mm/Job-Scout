# backend/app/services/job_service.py

from collections import Counter
from concurrent.futures import ThreadPoolExecutor, wait
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
        done, not_done = wait(futures, timeout=25)

        for future in done:
            jobs = future.result()
            for job in jobs:
                job["id"] = next_id
                next_id += 1
                all_jobs.append(job)

        if not_done:
            print("Collectors not finished within 25 seconds:")
            for future in not_done:
                collector = futures[future]
                print(f"  {collector.__class__.__name__}")

    all_sources = Counter(job.get("source", "unknown") for job in all_jobs)
    print("All jobs by source before filtering:", all_sources)

    filtered_jobs = filter_jobs(all_jobs, filters)

    filtered_sources = Counter(job.get("source", "unknown") for job in filtered_jobs)
    print("Jobs by source after filtering:", filtered_sources)

    return filtered_jobs