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
            f"country={user.country} city={user.city}"
        )

        # Ensure collectors don't crash when the DB user schema is missing
        # expected fields. This is a diagnostic runtime shim only — it
        # does not persist new columns to the database. Add safe setattr
        # attempts so collectors can read a consistent contract.
        for _attr, _default in (
            ("employment_type", "all"),
            ("job_category", "all"),
            ("language", "de"),
            ("min_salary", None),
            ("max_salary", None),
        ):
            try:
                if not hasattr(user, _attr) or getattr(user, _attr) is None:
                    setattr(user, _attr, _default)
            except Exception:
                # If the ORM disallows setting unknown attributes, skip
                # and let downstream code use getattr(..., default).
                pass
        try:
            collectors = get_collectors(user.country)

            print(
                f"[Notifier] Found {len(collectors)} collectors "
                f"for {user.country}"
            )

            jobs = []

            for collector in collectors:
                try:
                    print(
                        f"[Notifier] Fetching jobs from "
                        f"{collector.source} for {user.email}"
                    )

                    collected = collector.fetch_jobs(user)

                    if collected:
                        print(
                            f"[Notifier] {collector.source}: "
                            f"{len(collected)} jobs"
                        )
                        jobs.extend(collected)
                    else:
                        print(
                            f"[Notifier] {collector.source}: 0 jobs"
                        )

                except Exception as e:
                    print(
                        f"[Notifier] Collector "
                        f"{getattr(collector, 'source', 'unknown')} "
                        f"error: {e}"
                    )

            print(
                f"[Notifier] Total collected jobs for "
                f"{user.email}: {len(jobs)}"
            )

            if not jobs:
                print(
                    f"[Notifier] No jobs collected for {user.email}"
                )
                continue

            filter_params = JobFilter(
                country=user.country,
                city=user.city,
                keywords=user.keywords or "",
                language=getattr(user, "language", "de"),
                min_salary=getattr(user, "min_salary", None),
                max_salary=getattr(user, "max_salary", None),
            )

            filtered = filter_jobs(jobs, filter_params)

            print(
                f"[Notifier] After filtering: "
                f"{len(filtered)} jobs for {user.email}"
            )

            new_jobs = remove_already_sent(user, filtered)

            print(
                f"[Notifier] New unsent jobs: "
                f"{len(new_jobs)} for {user.email}"
            )

            if not new_jobs:
                continue

            print(
                f"[Notifier] Sending {len(new_jobs)} jobs "
                f"to {user.email}"
            )

            sent = send_job_email(
                user.email,
                new_jobs,
                unsubscribe_token=user.unsubscribe_token,
            )

            print(
                f"[Notifier] send_job_email result: {sent}"
            )

            # Only mark jobs as sent if email sending succeeded.
            if sent is not False:
                save_sent_jobs(user, new_jobs)
            else:
                print(
                    f"[Notifier] Email sending failed for "
                    f"{user.email}; jobs will NOT be marked as sent"
                )

        except Exception as e:
            print(
                f"[Notifier] Error processing "
                f"{user.email}: {e}"
            )


def get_users_with_alerts():
    """
    Return users who have:
    - alerts enabled
    - consent given
    - verified email
    """

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
        print(
            f"[Notifier] Error fetching users: {e}"
        )
        return []

    finally:
        db.close()


def remove_already_sent(user, jobs):
    """
    Remove jobs that have already been sent to this user.
    """

    if not jobs:
        return []

    db = SessionLocal()

    try:
        sent_job_urls = (
            db.query(UserJob.job_url)
            .filter(UserJob.user_id == user.id)
            .all()
        )

        sent_urls = {
            row[0]
            for row in sent_job_urls
            if row[0]
        }

        new_jobs = [
            job
            for job in jobs
            if job.get("url") and job.get("url") not in sent_urls
        ]

        return new_jobs

    except Exception as e:
        print(
            f"[Notifier] Error checking sent jobs: {e}"
        )
        return jobs

    finally:
        db.close()


def save_sent_jobs(user, jobs):
    """
    Save sent jobs so they are not emailed again.
    """

    if not jobs:
        return

    db = SessionLocal()

    try:
        saved_count = 0

        for job in jobs:
            job_url = job.get("url")

            if not job_url:
                print(
                    "[Notifier] Skipping job without URL"
                )
                continue

            existing_job = (
                db.query(Job)
                .filter(Job.url == job_url)
                .first()
            )

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
                    date=job.get(
                        "date",
                        datetime.now().isoformat(),
                    ),
                )

                db.add(existing_job)
                db.flush()

            already_linked = (
                db.query(UserJob)
                .filter(
                    UserJob.user_id == user.id,
                    UserJob.job_url == job_url,
                )
                .first()
            )

            if already_linked:
                continue

            user_job = UserJob(
                user_id=user.id,
                job_id=existing_job.id,
                sent_at=datetime.now(),
                job_url=job_url,
            )

            db.add(user_job)
            saved_count += 1

        db.commit()

        print(
            f"[Notifier] Saved {saved_count} sent jobs "
            f"for user {user.email}"
        )

    except Exception as e:
        db.rollback()

        print(
            f"[Notifier] Error saving sent jobs: {e}"
        )

    finally:
        db.close()