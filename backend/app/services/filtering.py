# backend/app/services/filtering.py

from pydantic import BaseModel
from typing import Optional


class JobFilter(BaseModel):
    city: str
    keywords: Optional[str] = None
    employment_type: Optional[str] = None
    source: Optional[str] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None


def filter_jobs(jobs: list, filters: JobFilter):

    result = []

    for job in jobs:

        # Keyword
        if filters.keywords:

            text = (
                f"{job.get('title', '')} "
                f"{job.get('company', '')}"
            ).lower()

            if filters.keywords.lower() not in text:
                continue

        # Source
        if filters.source:

            if job.get("source") != filters.source:
                continue

        # Salary
        if filters.min_salary:
            salary_max = job.get("salary_max")
            if salary_max is not None:
                if salary_max < filters.min_salary:
                    continue

        if filters.max_salary:
            salary_min = job.get("salary_min")
            if salary_min is not None:
                if salary_min > filters.max_salary:
                    continue

        result.append(job)

    return result