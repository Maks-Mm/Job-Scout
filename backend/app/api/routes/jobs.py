#backend/app/api/routes/jobs.py

from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.services.job_service import collect_jobs


router = APIRouter(
    prefix="/jobs",
    tags=["jobs"]
)



@router.get("")
def get_jobs(
    city:str="Munich",
    db:Session=Depends(get_db)
):

    return collect_jobs(
        city,
        db
    )