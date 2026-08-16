# backend/app/workers/job_notifier.py

from datetime import datetime

from app.collectors.collector_registry import get_collectors
from app.services.filtering import filter_jobs, JobFilter
from app.notifications.email_service import send_job_email
from app.core.database import SessionLocal
from app.models.user import User
from app.models.job import Job
from app.models.user_job import UserJob


def check_new_jobs():
    print("[Notifier] checking jobs")

    users = get_users_with_alerts()
    print(f"[Notifier] Found {len(users)} users with active alerts")

    if not users:
        print("[Notifier] No eligible users found")
        return

    for user in users:
        print(
            f"[Notifier] Processing user: {user.email} "
            f"country={user.country} city={user.city} "
            f"employment_type={getattr(user, 'employment_type', None)} "
            f"salary={getattr(user, 'min_salary', None)}-{getattr(user, 'max_salary', None)}"
        )

        try:
            collectors = get_collectors(user.country)
            print(f"[Notifier] Found {len(collectors)} collectors for {user.country}")

            jobs = []
            filter_params = JobFilter(
                country=getattr(user, "country", "Germany") or "Germany",
                city=getattr(user, "city", "") or "",
                keywords=getattr(user, "keywords", "") or "",
                language=getattr(user, "language", "de") or "de",
                employment_type=getattr(user, "employment_type", "all") or "all",
                job_category=getattr(user, "job_category", "all") or "all",
                min_salary=getattr(user, "min_salary", None),
                max_salary=getattr(user, "max_salary", None),
            )

            for collector in collectors:
                try:
                    print(f"[Notifier] Fetching from {collector.source} for {user.email}")
                    collected = collector.fetch_jobs(filter_params)
                    if collected:
                        print(f"[Notifier] {collector.source}: {len(collected)} jobs")
                        jobs.extend(collected)
                    else:
                        print(f"[Notifier] {collector.source}: 0 jobs")
                except Exception as e:
                    print(f"[Notifier] Collector {getattr(collector, 'source', 'unknown')} error: {e}")

            print(f"[Notifier] Total collected: {len(jobs)} jobs for {user.email}")

            if not jobs:
                print(f"[Notifier] No jobs collected for {user.email}")
                continue

            # Build filter with ALL user preferences — including employment type and salary
            filter_params = JobFilter(
                country=getattr(user, "country", "Germany"),
                city=getattr(user, "city", ""),
                keywords=getattr(user, "keywords", "") or "",
                language=getattr(user, "language", "de") or "de",
                employment_type=getattr(user, "employment_type", None),
                job_category=getattr(user, "job_category", None),
                min_salary=getattr(user, "min_salary", None),
                max_salary=getattr(user, "max_salary", None),
            )

            print(f"[Notifier] Filter: {filter_params.model_dump()}")

            filtered = filter_jobs(jobs, filter_params)
            print(f"[Notifier] After filtering: {len(filtered)} jobs for {user.email}")

            new_jobs = remove_already_sent(user, filtered)
            print(f"[Notifier] New unsent jobs: {len(new_jobs)} for {user.email}")

            if not new_jobs:
                print(f"[Notifier] No new jobs for {user.email}, skipping email")
                continue

            # Sort by date descending so freshest jobs appear first in email
            new_jobs = _sort_by_freshness(new_jobs)

            print(f"[Notifier] Sending {len(new_jobs)} jobs to {user.email}")
            sent = send_job_email(
                receiver=user.email,
                jobs=new_jobs,
                unsubscribe_token=user.unsubscribe_token,
                user_filters={
                    "city": getattr(user, "city", ""),
                    "country": getattr(user, "country", "Germany"),
                    "employment_type": getattr(user, "employment_type", None),
                    "min_salary": getattr(user, "min_salary", None),
                    "max_salary": getattr(user, "max_salary", None),
                    "keywords": getattr(user, "keywords", ""),
                },
            )

            print(f"[Notifier] send_job_email result: {sent}")

            if sent is not False:
                save_sent_jobs(user, new_jobs)
            else:
                print(f"[Notifier] Email failed for {user.email}; jobs NOT marked as sent")

        except Exception as e:
            print(f"[Notifier] Error processing {user.email}: {e}")


def _sort_by_freshness(jobs: list[dict]) -> list[dict]:
    """Sort jobs newest-first. Jobs without a parseable date go to the end."""

    def _date_key(job: dict):
        raw = job.get("date") or job.get("created_at") or job.get("posted_at") or ""
        if not raw:
            return ""
        try:
            # Handle ISO strings like "2026-08-14T10:00:00" or "2026-08-14"
            return raw[:10]
        except Exception:
            return ""

    return sorted(jobs, key=_date_key, reverse=True)


def get_users_with_alerts():
    """Return users who have alerts enabled, consent given, and verified email."""
    db = SessionLocal()
    try:
        users = (
            db.query(User)
            .filter(
                User.alerts_enabled.is_(True),
                User.consent_given.is_(True),
                User.verified_email.is_(True),
            )
            .all()
        )
        return users
    except Exception as e:
        print(f"[Notifier] Error fetching users: {e}")
        return []
    finally:
        db.close()


def remove_already_sent(user, jobs: list[dict]) -> list[dict]:
    """Remove jobs already sent to this user."""
    if not jobs:
        return []

    db = SessionLocal()
    try:
        sent_job_urls = (
            db.query(UserJob.job_url)
            .filter(UserJob.user_id == user.id)
            .all()
        )
        sent_urls = {row[0] for row in sent_job_urls if row[0]}
        return [job for job in jobs if job.get("url") and job.get("url") not in sent_urls]
    except Exception as e:
        print(f"[Notifier] Error checking sent jobs: {e}")
        return jobs
    finally:
        db.close()


def save_sent_jobs(user, jobs: list[dict]):
    """Persist sent jobs so they are never emailed again."""
    if not jobs:
        return

    db = SessionLocal()
    try:
        saved_count = 0
        for job in jobs:
            job_url = job.get("url")
            if not job_url:
                continue

            existing_job = db.query(Job).filter(Job.url == job_url).first()
            if not existing_job:
                existing_job = Job(
                    title=job.get("title", ""),
                    company=job.get("company", ""),
                    city=job.get("city", ""),
                    salary_min=job.get("salary_min"),
                    salary_max=job.get("salary_max"),
                    currency=job.get("currency", "EUR"),
                    url=job_url,
                    source=job.get("source", ""),
                    date=job.get("date", datetime.now().isoformat()),
                )
                db.add(existing_job)
                db.flush()

            already_linked = (
                db.query(UserJob)
                .filter(UserJob.user_id == user.id, UserJob.job_url == job_url)
                .first()
            )
            if already_linked:
                continue

            db.add(UserJob(
                user_id=user.id,
                job_id=existing_job.id,
                sent_at=datetime.now(),
                job_url=job_url,
            ))
            saved_count += 1

        db.commit()
        print(f"[Notifier] Saved {saved_count} sent jobs for user {user.email}")
    except Exception as e:
        db.rollback()
        print(f"[Notifier] Error saving sent jobs: {e}")
    finally:
        db.close()