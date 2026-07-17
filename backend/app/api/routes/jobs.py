#backend/app/api/routes/jobs.py

from fastapi import APIRouter
from app.services.job_service import get_jobs
from app.services.filtering import JobFilter

router = APIRouter()


@router.get("/api/jobs")
def jobs(
    city: str = "Munich",
    keywords: str | None = None,
    employment_type: str | None = None,
    source: str | None = None,
    min_salary: int = 0,
    max_salary: int = 0,
):
    filters = JobFilter(
        city=city,
        keywords=keywords,
        employment_type=employment_type,
        source=source,
        min_salary=min_salary or None,
        max_salary=max_salary or None,
    )

    result = get_jobs(filters)

    print("=" * 50)
    print("DEBUGGING JOBS ENDPOINT")
    print(f"City: {city}")
    print(f"Type of result: {type(result)}")
    print(f"Is it a list? {isinstance(result, list)}")
    if isinstance(result, list):
        print(f"Length: {len(result)}")
        if len(result) > 0:
            print(f"First job: {result[0]}")
    else:
        print(f"Result content: {result}")
    print("=" * 50)

    return result