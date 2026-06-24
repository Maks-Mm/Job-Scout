from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.job_service import collect_jobs, persist_jobs
from app.models.job import Job


router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/")
def get_jobs(city: str = "Munich", db: Session = Depends(get_db)):
    jobs = collect_jobs(city)
    persist_jobs(db, jobs)
    results = db.query(Job).filter(Job.city == city).all()
    return results


@router.post("/")
def add_job(job: dict, db: Session = Depends(get_db)):
    persist_jobs(db, [job])
    return {"status": "created"}