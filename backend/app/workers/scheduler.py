#backend/app/workers/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.database import SessionLocal
from app.models.job import Job
from app.services.job_service import get_jobs
from app.services.filtering import JobFilter
from app.workers.job_notifier import check_recent_jobs


scheduler = BackgroundScheduler()

CITIES = ["Munich", "Berlin", "Hamburg"]


def update_jobs():
    db = SessionLocal()

    try:
        total_new = 0
        total_updated = 0

        # All jobs collected during this scheduler run.
        # These are later evaluated for alerts.
        all_collected_jobs: list[dict] = []

        # Critical:
        # Prevent duplicate URLs inside the same scheduler run.
        seen_urls: set[str] = set()

        for city in CITIES:
            filters = JobFilter(
                country="Germany",
                city=city,
            )

            jobs = get_jobs(filters)

            print(
                f"[Scheduler] {city}: "
                f"{len(jobs)} jobs collected"
            )

            for job in jobs:
                url = job.get("url")

                if not url:
                    print(
                        "[Scheduler] Skipping job without URL: "
                        f"{job.get('title', 'unknown')}"
                    )
                    continue

                # -------------------------------------------------
                # Prevent duplicate processing in this run.
                # -------------------------------------------------
                if url in seen_urls:
                    print(
                        "[Scheduler] Duplicate URL in current run, "
                        f"skipping DB insert: {url}"
                    )
                    continue

                seen_urls.add(url)

                # Keep the collected job for the alert evaluator.
                all_collected_jobs.append(job)

                existing = (
                    db.query(Job)
                    .filter(Job.url == url)
                    .first()
                )

                if existing:
                    existing.title = job.get("title")
                    existing.company = job.get("company")
                    existing.city = job.get("city") or city
                    existing.salary_min = job.get("salary_min")
                    existing.salary_max = job.get("salary_max")
                    existing.currency = job.get(
                        "currency",
                        "EUR",
                    )
                    existing.source = job.get("source")

                    new_date = (
                        job.get("date")
                        or job.get("created_at")
                        or job.get("posted_at")
                    )

                    if new_date:
                        existing.date = new_date

                    total_updated += 1

                else:
                    new_job = Job(
                        title=job.get("title"),
                        company=job.get("company"),
                        city=job.get("city") or city,
                        salary_min=job.get("salary_min"),
                        salary_max=job.get("salary_max"),
                        currency=job.get(
                            "currency",
                            "EUR",
                        ),
                        url=url,
                        source=job.get("source"),
                        date=(
                            job.get("date")
                            or job.get("created_at")
                            or job.get("posted_at")
                        ),
                    )

                    db.add(new_job)
                    total_new += 1

        db.commit()

        print(
            "[Scheduler] Run complete: "
            f"{total_new} new, "
            f"{total_updated} updated, "
            f"{len(all_collected_jobs)} unique collected"
        )

        # IMPORTANT:
        # Always evaluate collected jobs.
        #
        # It does NOT matter whether a job was newly inserted
        # into the database during this run.
        check_recent_jobs(
            all_collected_jobs
        )

    except Exception as e:
        db.rollback()

        print(
            f"[Scheduler] update_jobs failed: {e}"
        )

    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(
        update_jobs,
        "interval",
        minutes=30,
        id="update_jobs",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    scheduler.start()

    print(
        "[Scheduler] running every 30 minutes"
    )

    print(
        "[Scheduler] running initial job immediately on startup"
    )

    update_jobs()