from fastapi import APIRouter, Query
from typing import List

from app.scraper.indeed import scrape_indeed

router = APIRouter(prefix="/api")


@router.get("/jobs")
async def get_jobs(
    city: str = Query("Munich"),
    min_salary: int = Query(0),
    max_salary: int = Query(0),
):
    """Return a list of jobs. For now uses a fake scraper."""
    jobs = scrape_indeed(city)
    return jobs
