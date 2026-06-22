//backend/app/api/routes/jobs.py


from fastapi import APIRouter

from app.services.job_service import collect_jobs


router = APIRouter()


@router.get("/jobs")
def get_jobs():

    return collect_jobs()