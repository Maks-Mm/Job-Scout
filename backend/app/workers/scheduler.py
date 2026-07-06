#backend/app/workers/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.database import SessionLocal
from app.models.job import Job
from app.services.job_service import get_jobs

scheduler = BackgroundScheduler()

CITIES = ["Munich", "Berlin", "Hamburg"]


def update_jobs():
    db = SessionLocal()

    try:
        total_new = 0
        total_updated = 0

        for city in CITIES:
            jobs = get_jobs(city)

            for job in jobs:
                url = job.get("url")

                # Skip anything without a URL — it's our uniqueness key
                # and the DB column requires it to be unique.
                if not url:
                    continue

                existing = db.query(Job).filter(Job.url == url).first()

                if existing:
                    existing.title = job.get("title")
                    existing.company = job.get("company")
                    existing.city = city
                    existing.salary_min = job.get("salary_min")
                    existing.salary_max = job.get("salary_max")
                    existing.currency = job.get("currency", "EUR")
                    existing.source = job.get("source")
                    total_updated += 1
                else:
                    db.add(Job(
                        title=job.get("title"),
                        company=job.get("company"),
                        city=city,
                        salary_min=job.get("salary_min"),
                        salary_max=job.get("salary_max"),
                        currency=job.get("currency", "EUR"),
                        url=url,
                        source=job.get("source"),
                    ))
                    total_new += 1

            print(f"{city}: {len(jobs)} jobs collected")

        db.commit()
        print(f"Scheduler run complete: {total_new} new, {total_updated} updated")

    except Exception as e:
        db.rollback()
        print(f"[scheduler] update_jobs failed: {e}")
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(update_jobs, "interval", hours=6)
    scheduler.start()