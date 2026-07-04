#backend/app/api/routes/jobs.py

from fastapi import APIRouter
from app.services.job_service import get_jobs
import json

router = APIRouter()

@router.get("/api/jobs")
def jobs(city: str = "Munich", min_salary: int = 0, max_salary: int = 0):
    result = get_jobs(city)
    
    # DEBUG: Print the structure
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