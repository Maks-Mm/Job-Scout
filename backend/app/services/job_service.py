#backend/app/service/job_service.py

from typing import List
from sqlalchemy.orm import Session

from app.scraper.indeed import scrape_indeed
#from app.models import Job  # Oder: from app.models.job import Job
from app.models.job import Job


def collect_jobs(city: str = "Munich") -> List[dict]:
    return scrape_indeed(city)


def persist_jobs(db: Session, jobs: List[dict]):
    """Persist jobs into the database. Skips duplicates by URL."""
    seen_urls = set()

    for j in jobs:
        url = j.get("url")

        if not url or url in seen_urls:
            continue

        seen_urls.add(url)

        exists = db.query(Job).filter(Job.url == url).first()
        if exists:
            continue

        job = Job(
            title=j.get("title"),
            company=j.get("company"),
            city=j.get("city"),
            country=j.get("country", "Germany"),
            salary_min=j.get("salary_min"),
            salary_max=j.get("salary_max"),
            currency=j.get("currency", "EUR"),
            category=j.get("category"),
            description=j.get("description"),
            url=url,
            source=j.get("source", "scraper"),
        )

        db.add(job)

    db.commit()