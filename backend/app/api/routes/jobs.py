#backend/app/api/routes/jobs.py

from fastapi import APIRouter
from app.services.job_service import get_jobs
from app.services.filtering import JobFilter

router = APIRouter()


@router.get("/api/jobs")
def jobs(
    city: str = "Munich",
    keywords: str | None = None,
    job_category: str | None = None,
    employment_type: str | None = None,
    source: str | None = None,
    min_salary: int = 0,
    max_salary: int = 0,
):

    filters = JobFilter(
        city=city,
        keywords=keywords,
        job_category=job_category,
        employment_type=employment_type,
        source=source,
        min_salary=min_salary or None,
        max_salary=max_salary or None,
    )

    print("=" * 50)
    print("DEBUG FILTER")
    print(filters.model_dump())
    print("=" * 50)

    result = get_jobs(filters)

    print("=" * 50)
    print("DEBUGGING JOBS ENDPOINT")
    print(f"City: {city}")
    print(f"Jobs after filter: {len(result)}")
    if result:
        print("First job:", result[0]["title"])
    print("=" * 50)

    return result