
from fastapi import APIRouter, Query, Depends
from typing import List
from sqlalchemy.orm import Session

from app.services.job_service import collect_jobs, persist_jobs
from app.api.core.database import get_db
from app.api.models.job import Job

router = APIRouter(prefix="/api")


@router.get("/jobs")
async def get_jobs(
    city: str = Query("Munich"),
    min_salary: int = Query(0),
    max_salary: int = Query(0),
    db: Session = Depends(get_db),
):
    """Collect jobs from scraper, persist new ones, and return current DB rows."""
    scraped = collect_jobs(city)
    persist_jobs(db, scraped)

    # return persisted jobs (basic fields)
    rows = db.query(Job).order_by(Job.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "company": r.company,
            "city": r.city,
            "salary": r.salary,
            "url": r.url,
            "source": r.source,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
