from typing import List
from sqlalchemy.orm import Session

from app.scraper.indeed import scrape_indeed
from app.api.models.job import Job


def collect_jobs(city: str = "Munich") -> List[dict]:
    return scrape_indeed(city)


def persist_jobs(db: Session, jobs: List[dict]):
    """Persist jobs into database. Skips duplicate URLs."""
    seen_urls = set()

    for j in jobs:
        url = j.get("url")

        if not url:
            continue

        if url in seen_urls:
            continue

        seen_urls.add(url)

        exists = db.query(Job).filter(Job.url == url).first()

        if exists:
            continue

        job = Job(
            title=j.get("title"),
            company=j.get("company"),
            city=j.get("city"),
            salary=j.get("salary"),
            url=url,
            source=j.get("source", "scraper"),
        )

        db.add(job)

    db.commit()
